"""Sync Presenca -> vSaude: patients, professionals, procedures, appointments, status."""

import json
import logging
import time

from api import vsaude_post, presenca_api, extract_items
from config import (PRESENCA_TO_VSAUDE_ACTION, VSAUDE_TO_PRESENCA_STATUS,
                     PROF_PROCEDURES, CARE_UNIT_ID, INSURANCE_COMPANY_ID, API_DELAY)
from helpers import extract_date_time, brt_to_utc, clean_name

log = logging.getLogger("sync.pr2vs")

PRESENCA_GENDER_TO_VSAUDE = {"male": 1, "female": 2, "other": 0, "prefer_not_to_say": 0}


# ─────────────────────────────────────────────────────────────
# SLOT VALIDATION
# ─────────────────────────────────────────────────────────────

def _check_slot_available(vs_prof_id, vs_proc_id, target_date_brt, target_time_brt):
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


# ─────────────────────────────────────────────────────────────
# PATIENTS
# ─────────────────────────────────────────────────────────────

def _sync_patients(cache, since_date):
    """Create new patients + update existing in vSaude."""
    log.info("[PR->VS] Syncing patients...")

    resp = presenca_api("GET", "patients?limit=1000")
    if not resp or "data" not in resp:
        log.warning("[PR->VS] Presenca API blocked for patients")
        return {"created": 0, "updated": 0}

    all_patients = resp["data"]
    created = 0
    updated = 0

    # Build vSaude patient index for comparison
    vs_attendance = vsaude_post("ReportService/GetAttendance", {"maxResultCount": 1000})
    vs_patients = {}
    if vs_attendance:
        items = vs_attendance.get("items", vs_attendance) if isinstance(vs_attendance, dict) else vs_attendance
        for a in items:
            pat = a.get("patient") or {}
            pid = pat.get("id")
            if pid:
                vs_patients[pid] = pat

    for pr_pat in all_patients:
        ext_id = pr_pat.get("externalId")
        name = clean_name(pr_pat.get("name", ""))
        phone = pr_pat.get("phone", "") or ""
        email = pr_pat.get("email", "") or ""
        cpf = pr_pat.get("cpf", "") or ""
        gender = PRESENCA_GENDER_TO_VSAUDE.get(pr_pat.get("gender", ""), 0)
        birth = pr_pat.get("birthDate")

        if not ext_id:
            # New patient - create in vSaude
            created_at = (pr_pat.get("createdAt") or "")[:10]
            if created_at < since_date:
                continue

            parts = name.split(" ", 1)
            first = parts[0] if parts else name
            surname = parts[1] if len(parts) > 1 else ""

            log.info("[PR->VS] NEW PATIENT: %s cpf=%s", name, cpf or "none")

            body = {
                "name": first,
                "surname": surname,
                "phoneNumber": phone,
                "personalIdentifier": cpf or "00000000000",
                "email": email or f"sem_email@placeholder.com",
                "gender": gender,
                "password": "TempPass@2026",
            }
            if birth and len(str(birth)) >= 10:
                body["birthday"] = f"{str(birth)[:10]}T00:00:00Z"

            result = vsaude_post("PatientService/Create", body)
            if result:
                vs_id = result.get("id") if isinstance(result, dict) else result
                log.info("[PR->VS]   CREATED: %s", vs_id)
                time.sleep(API_DELAY)
                presenca_api("PUT", f"patients/{pr_pat['id']}", {"externalId": str(vs_id)})
                created += 1
            else:
                log.error("[PR->VS]   FAILED to create patient")
    log.info("[PR->VS] Patients: %d created", created)
    return {"created": created, "updated": 0}


# ─────────────────────────────────────────────────────────────
# PROFESSIONALS
# ─────────────────────────────────────────────────────────────

def _sync_professionals(cache):
    """Create professionals that exist in Presenca but not in vSaude."""
    log.info("[PR->VS] Syncing professionals...")

    resp = presenca_api("GET", "professionals")
    if not resp or "data" not in resp:
        log.warning("[PR->VS] Presenca API blocked for professionals")
        return 0

    # Get vSaude professionals for comparison
    vs_result = vsaude_post("HealthProfessionalService/GetAll", {"maxResultCount": 100})
    vs_profs = {}
    if vs_result:
        vs_items = vs_result.get("items", vs_result) if isinstance(vs_result, dict) else vs_result
        for p in vs_items:
            vs_profs[p.get("id", "")] = p

    created = 0
    for pr_prof in resp["data"]:
        ext_id = pr_prof.get("externalId")
        if ext_id and ext_id in vs_profs:
            continue  # Already exists in vSaude

        if ext_id:
            continue  # Has externalId but not in current vSaude list - skip

        name = clean_name(pr_prof.get("name", ""))
        if not name or not pr_prof.get("active"):
            continue

        email = pr_prof.get("email", "") or ""
        phone = pr_prof.get("phone", "") or ""

        if not email:
            continue  # vSaude requires email for user creation

        parts = name.split(" ", 1)
        first = parts[0] if parts else name
        surname = parts[1] if len(parts) > 1 else ""

        log.info("[PR->VS] NEW PROFESSIONAL: %s email=%s", name, email)

        body = {
            "name": name,
            "discriminator": "Doctor",
            "user": {
                "name": first,
                "surname": surname,
                "emailAddress": email,
                "phoneNumber": phone,
                "userName": email,
                "gender": 1,
                "password": "TempPass@2026",
            }
        }

        result = vsaude_post("HealthProfessionalService/Create", body)
        if result:
            vs_id = result.get("id") if isinstance(result, dict) else result
            log.info("[PR->VS]   CREATED: %s", vs_id)
            time.sleep(API_DELAY)
            presenca_api("PUT", f"professionals/{pr_prof['id']}", {"externalId": str(vs_id)})
            created += 1
        else:
            log.error("[PR->VS]   FAILED to create professional")

    if created:
        log.info("[PR->VS] Professionals created: %d", created)
    return created


# ─────────────────────────────────────────────────────────────
# PROCEDURES
# ─────────────────────────────────────────────────────────────

def _sync_procedures(cache):
    """Create procedures that exist in Presenca but not in vSaude."""
    log.info("[PR->VS] Syncing procedures...")

    resp = presenca_api("GET", "procedures")
    if not resp or "data" not in resp:
        log.warning("[PR->VS] Presenca API blocked for procedures")
        return 0

    # Get vSaude procedures for comparison
    vs_result = vsaude_post("MedicalProcedureService/GetAll", {"maxResultCount": 100})
    vs_procs = {}
    if vs_result:
        vs_items = vs_result.get("items", []) if isinstance(vs_result, dict) else vs_result
        for p in vs_items:
            vs_procs[str(p.get("id", ""))] = p

    created = 0
    for pr_proc in resp["data"]:
        ext_id = pr_proc.get("externalId")
        if ext_id and ext_id in vs_procs:
            continue  # Already exists

        if ext_id:
            continue  # Has externalId but not in vSaude list - skip

        name = clean_name(pr_proc.get("name", ""))
        if not name or not pr_proc.get("active"):
            continue

        price = pr_proc.get("price") or 0
        duration = pr_proc.get("durationMinutes") or pr_proc.get("duration_minutes") or 30

        log.info("[PR->VS] NEW PROCEDURE: %s price=%s dur=%d", name, price, duration)

        body = {
            "name": name,
            "duration": duration,
            "minutesDuration": duration,
            "periodUnit": 0,
            "price": float(price),
            "allowOnlineSchedule": True,
            "remotely": True,
            "isReturn": False,
            "isProfessionalRequired": True,
            "onlinePaymentType": 0,
            "maxNumberOfInstallments": 1,
            "coveredInsuranceCompanies": [],
            "coveredInsurancePlans": [],
            "coveredByProfessionals": [],
            "coveredCareUnits": [],
            "returnParentId": [],
            "responsibilityTerms": [],
        }

        result = vsaude_post("MedicalProcedureService/Create", body)
        if result:
            vs_id = result.get("id") if isinstance(result, dict) else result
            log.info("[PR->VS]   CREATED: %s", vs_id)
            time.sleep(API_DELAY)
            presenca_api("PUT", f"procedures/{pr_proc['id']}", {"externalId": str(vs_id)})
            created += 1
        else:
            log.error("[PR->VS]   FAILED to create procedure")

    if created:
        log.info("[PR->VS] Procedures created: %d", created)
    return created


# ─────────────────────────────────────────────────────────────
# APPOINTMENTS
# ─────────────────────────────────────────────────────────────

def _sync_new_appointments(cache, since_date):
    """Find Presenca appointments without externalId -> create in vSaude."""
    log.info("[PR->VS] Searching appointments WITHOUT externalId...")

    resp = presenca_api("GET", "appointments?limit=1000")
    if not resp or "data" not in resp:
        log.warning("[PR->VS] Presenca API blocked for appointments")
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
        log.info("[PR->VS] No pending appointments")
        return 0

    log.info("[PR->VS] Found %d appointments WITHOUT externalId since %s", len(new_appts), since_date)

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

        vs_prof_id = prof_map.get(a.get("professionalId"))
        vs_proc_ext = proc_map.get(a.get("procedureId"))
        vs_pat_id = pat_map.get(a.get("patientId"))

        if not vs_pat_id and isinstance(patients, dict):
            vs_pat_id = patients.get("externalId")

        log.info("[PR->VS] PENDING: date=%s time=%s prof=%s patient=%s",
                 sched_date, sched_time, prof_name or "?", pat_name)

        if not vs_prof_id:
            log.warning("[PR->VS]   SKIP: professional has no vSaude ID")
            continue
        if not vs_pat_id:
            log.warning("[PR->VS]   SKIP: patient has no vSaude ID")
            continue

        vs_proc_id = int(vs_proc_ext) if vs_proc_ext else None

        check_proc = vs_proc_id or PROF_PROCEDURES.get(vs_prof_id)
        if check_proc:
            if not _check_slot_available(vs_prof_id, check_proc, sched_date, sched_time):
                log.warning("[PR->VS]   SKIP: slot %s %s not available in vSaude (may be occupied by this appointment or blocked by doctor)", sched_date, sched_time)
                continue
            log.info("[PR->VS]   Slot %s %s available", sched_date, sched_time)

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
            log.info("[PR->VS]   CREATED in vSaude: %s", vs_appt_id)
            presenca_api("PUT", f"appointments/{a['id']}", {"externalId": str(vs_appt_id)})
            created += 1
        else:
            log.error("[PR->VS]   FAILED to create in vSaude")

    return created


# ─────────────────────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────────────────────

def _sync_status(cache, since_date):
    """Compare status Presenca vs vSaude, push differences."""
    log.info("[PR->VS] Comparing status...")

    pr_appts = list(cache.get("appointments", {}).values())
    if not pr_appts:
        log.warning("[PR->VS] No appointments in cache")
        return 0

    vs_result = vsaude_post("ReportService/GetAttendance", {"maxResultCount": 1000})
    if not vs_result:
        return 0
    vs_items = vs_result.get("items", vs_result) if isinstance(vs_result, dict) else vs_result
    vs_index = {a.get("id", ""): a for a in vs_items}
    log.info("[PR->VS] Presenca cache: %d | vSaude: %d", len(pr_appts), len(vs_index))

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

        log.info("[PR->VS] STATUS: date=%s patient=%s presenca=%s vsaude=%s(%d)",
                 sched_date, pat_name, pr_status, vs_status_str, vs_status_code)

        body = {"id": ext_id, **extra_body}
        result = vsaude_post(endpoint, body)
        if result is not None:
            log.info("[PR->VS]   %s OK", endpoint)
            changes += 1
        else:
            log.error("[PR->VS]   %s FAILED", endpoint)

    log.info("[PR->VS] %d compared: %d synced, %d changes", checked, synced, changes)
    return changes


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────

def run(cache, since_date):
    """Run Presenca -> vSaude sync."""
    log.info("=" * 50)
    log.info("[PR->VS] START since=%s", since_date)
    log.info("=" * 50)

    pat_stats = _sync_patients(cache, since_date)
    profs_created = _sync_professionals(cache)
    procs_created = _sync_procedures(cache)
    appts_created = _sync_new_appointments(cache, since_date)
    status_changes = _sync_status(cache, since_date)

    log.info("-" * 50)
    log.info("[PR->VS] RESULT: patients=%d/%d profs=%d procs=%d appts=%d status=%d",
             pat_stats["created"], pat_stats["updated"],
             profs_created, procs_created, appts_created, status_changes)
    log.info("=" * 50)
    return {
        "patients": pat_stats,
        "professionals_created": profs_created,
        "procedures_created": procs_created,
        "appointments_created": appts_created,
        "status_changes": status_changes,
    }
