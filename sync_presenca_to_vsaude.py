"""Sync Presenca -> vSaude: new appointments + status changes."""

import logging

from api import vsaude_post, presenca_api
from config import (PRESENCA_TO_VSAUDE_ACTION, VSAUDE_TO_PRESENCA_STATUS,
                     PROF_PROCEDURES, CARE_UNIT_ID, INSURANCE_COMPANY_ID)
from helpers import extract_date_time, brt_to_utc

log = logging.getLogger("sync.pr2vs")


def _check_slot_available(vs_prof_id, vs_proc_id, target_date_brt, target_time_brt):
    """Check if slot is free in vSaude before creating."""
    result = vsaude_post("ScheduleService/GetAvailabilityWindow", {
        "procedureId": vs_proc_id, "professionalId": vs_prof_id,
    })
    if not result:
        return False
    target_utc = brt_to_utc(target_date_brt, target_time_brt)
    for day in result:
        for slot in day.get("availability", []):
            if slot.get("time") == target_utc:
                return True
    return False


def _sync_new_appointments(cache, since_date):
    """Find Presenca appointments without externalId -> create in vSaude."""
    log.info("[PR->VS] Searching appointments WITHOUT externalId...")

    resp = presenca_api("GET", "appointments?limit=1000")
    if not resp or "data" not in resp:
        log.warning("[PR->VS] Presenca API blocked - cannot fetch appointments without externalId")
        log.warning("[PR->VS] Appointments created in Presenca stay pending until next cycle")
        return 0

    all_appts = resp["data"]
    log.info("[PR->VS] Presenca returned %d appointments total", len(all_appts))

    new_appts = []
    for a in all_appts:
        if a.get("externalId"):
            continue
        sched_date, _ = extract_date_time(a)
        if sched_date < since_date:
            continue
        if a.get("status") in ("cancelled", "no_show"):
            continue
        new_appts.append(a)

    if not new_appts:
        log.info("[PR->VS] No pending appointments (all have externalId)")
        return 0

    log.info("[PR->VS] Found %d appointments WITHOUT externalId since %s:", len(new_appts), since_date)

    # Build lookups
    prof_map = {p.get("id", ""): ext for ext, p in cache.get("professionals", {}).items() if p.get("id")}
    proc_map = {p.get("id", ""): ext for ext, p in cache.get("procedures", {}).items() if p.get("id")}
    pat_map = {p.get("id", ""): ext for ext, p in cache.get("patients", {}).items() if p.get("id")}

    created = 0
    for a in new_appts:
        sched_date, sched_time = extract_date_time(a)
        pat_name = "?"
        patients = a.get("patients")
        if isinstance(patients, dict):
            pat_name = patients.get("name", "?")

        prof_name = ""
        professionals = a.get("professionals")
        if isinstance(professionals, dict):
            prof_name = professionals.get("name", "")

        proc_name = ""
        procedures = a.get("procedures")
        if isinstance(procedures, dict):
            proc_name = procedures.get("name", "")

        vs_prof_id = prof_map.get(a.get("professionalId"))
        vs_proc_ext = proc_map.get(a.get("procedureId"))
        vs_pat_id = pat_map.get(a.get("patientId"))

        if not vs_pat_id and isinstance(patients, dict):
            vs_pat_id = patients.get("externalId")

        log.info("[PR->VS] PENDING: date=%s time=%s prof=%s patient=%s proc=%s",
                 sched_date, sched_time, prof_name or "?", pat_name, proc_name[:30] or "?")

        if not vs_prof_id:
            log.warning("[PR->VS]   SKIP: professional has no vSaude ID")
            continue
        if not vs_pat_id:
            log.warning("[PR->VS]   SKIP: patient has no vSaude ID")
            continue

        vs_proc_id = int(vs_proc_ext) if vs_proc_ext else None

        # Validate slot availability
        check_proc = vs_proc_id or PROF_PROCEDURES.get(vs_prof_id)
        if check_proc:
            slot_free = _check_slot_available(vs_prof_id, check_proc, sched_date, sched_time)
            if not slot_free:
                log.warning("[PR->VS]   SKIP: slot %s %s NOT available in vSaude", sched_date, sched_time)
                continue
            log.info("[PR->VS]   Slot %s %s available in vSaude", sched_date, sched_time)

        log.info("[PR->VS]   Creating in vSaude: patient=%s prof=%s proc=%s",
                 vs_pat_id[:12], vs_prof_id[:12], vs_proc_id)

        body = {
            "patientId": vs_pat_id,
            "professionalId": vs_prof_id,
            "careUnitId": CARE_UNIT_ID,
            "startDate": brt_to_utc(sched_date, sched_time),
            "insuranceCompanyId": INSURANCE_COMPANY_ID,
        }
        if vs_proc_id:
            body["procedureId"] = vs_proc_id

        result = vsaude_post("ScheduleService/Create", body)
        if result:
            vs_appt_id = result.get("id") if isinstance(result, dict) else result
            log.info("[PR->VS]   CREATED in vSaude: id=%s", vs_appt_id)
            save_resp = presenca_api("PUT", f"appointments/{a['id']}", {"externalId": str(vs_appt_id)})
            if save_resp:
                log.info("[PR->VS]   externalId saved back to Presenca")
            else:
                log.warning("[PR->VS]   Created in vSaude but failed to save externalId to Presenca")
            created += 1
        else:
            log.error("[PR->VS]   FAILED to create in vSaude (ScheduleService/Create)")

    log.info("[PR->VS] %d appointments created in vSaude", created)
    return created


def _sync_status(cache, since_date):
    """Compare status between Presenca and vSaude, push differences."""
    log.info("[PR->VS] Comparing status Presenca vs vSaude...")

    pr_appts = list(cache.get("appointments", {}).values())
    if not pr_appts:
        log.warning("[PR->VS] No appointments in cache")
        return 0

    vs_result = vsaude_post("ReportService/GetAttendance", {"maxResultCount": 1000})
    if not vs_result:
        log.warning("[PR->VS] No data from vSaude GetAttendance")
        return 0
    vs_items = vs_result.get("items", vs_result) if isinstance(vs_result, dict) else vs_result
    vs_index = {a.get("id", ""): a for a in vs_items}
    log.info("[PR->VS] Presenca cache: %d appointments | vSaude: %d appointments", len(pr_appts), len(vs_index))

    checked = 0
    changes = 0
    synced = 0

    for a in pr_appts:
        ext_id = a.get("externalId")
        if not ext_id:
            continue
        sched_date, _ = extract_date_time(a)
        if sched_date < since_date:
            continue

        pr_status = a.get("status", "")
        vs_appt = vs_index.get(ext_id)
        if not vs_appt:
            continue

        vs_status_code = vs_appt.get("status", 0)
        vs_status_str = VSAUDE_TO_PRESENCA_STATUS.get(vs_status_code, "?")
        checked += 1

        if pr_status == vs_status_str:
            synced += 1
            continue

        action_info = PRESENCA_TO_VSAUDE_ACTION.get(pr_status)
        if not action_info:
            continue

        endpoint, extra_body = action_info
        pat_name = "?"
        patients = a.get("patients")
        if isinstance(patients, dict):
            pat_name = patients.get("name", "?")

        log.info("[PR->VS] STATUS DIVERGENT: date=%s patient=%s presenca=%s vsaude=%s(%d)",
                 sched_date, pat_name, pr_status, vs_status_str, vs_status_code)
        log.info("[PR->VS]   Action: %s", endpoint)

        body = {"id": ext_id, **extra_body}
        result = vsaude_post(endpoint, body)
        if result is not None:
            log.info("[PR->VS]   %s executed in vSaude", endpoint)
            changes += 1
        else:
            log.error("[PR->VS]   %s FAILED in vSaude", endpoint)

    log.info("[PR->VS] %d compared: %d synced, %d changes", checked, synced, changes)
    return changes


def run(cache, since_date):
    """Run Presenca -> vSaude sync."""
    log.info("=" * 50)
    log.info("[PR->VS] START since=%s", since_date)
    log.info("=" * 50)

    created = _sync_new_appointments(cache, since_date)
    status_changes = _sync_status(cache, since_date)

    log.info("-" * 50)
    log.info("[PR->VS] RESULT: appointments_created=%d status_updated=%d", created, status_changes)
    log.info("=" * 50)
    return {"created": created, "status_changes": status_changes}
