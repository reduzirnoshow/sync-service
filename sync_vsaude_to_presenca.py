"""Sync vSaude -> Presenca: patients, appointments, status, slots."""

import logging
import time

from api import vsaude_post, presenca_api, extract_items
from config import (VSAUDE_STATUS_MAP, GENDER_MAP, SPEC_PSIQ, SPEC_PSIC,
                     PROF_PROCEDURES, API_DELAY)
from helpers import utc_to_brt, clean_name, is_psicologia

log = logging.getLogger("sync.vs2pr")

STATUS_LABEL = {
    1: "Criado", 10: "Agendado", 11: "CriadoAPI", 20: "Confirmado",
    21: "Reagendado", 30: "Presente", 31: "ConfirmadoAPI", 50: "Cancelado",
    51: "CanceladoAPI", 6: "Faltou", 81: "Finalizado", 82: "FinalizadoAPI",
    90: "EmAtendimento", 100: "Expirado", 110: "Deletado",
}


def sync_professionals(cache):
    """Sync professional data: phone, email, active from vSaude."""
    result = vsaude_post("HealthProfessionalService/GetAll", {"maxResultCount": 100})
    if not result:
        return
    items = result.get("items", result) if isinstance(result, dict) else result
    updated = 0

    for vs in items:
        ext_id = vs.get("id", "")
        pr = cache.get("professionals", {}).get(ext_id)
        if not pr:
            continue

        user = vs.get("user") or {}
        vs_email = user.get("emailAddress", "") or ""
        vs_phone = user.get("phoneNumber", "") or ""
        vs_active = user.get("isActive", True)

        diffs = {}
        if vs_email and (pr.get("email") or "") != vs_email:
            diffs["email"] = vs_email
        if vs_phone and (pr.get("phone") or "") != vs_phone:
            diffs["phone"] = vs_phone
        if pr.get("active") != vs_active:
            diffs["active"] = vs_active

        if diffs:
            name = clean_name(vs.get("name", ""))
            log.info("[VS->PR] PROF UPDATE: %s -> %s", name, diffs)
            time.sleep(API_DELAY)
            presenca_api("PUT", f"professionals/{pr['id']}", diffs)
            updated += 1

    if updated:
        log.info("[VS->PR] Professionals updated: %d", updated)


def sync_procedures(cache):
    """Sync procedure data: price, duration from vSaude."""
    result = vsaude_post("MedicalProcedureService/GetAll", {"maxResultCount": 100})
    if not result:
        return
    items = result.get("items", []) if isinstance(result, dict) else result
    updated = 0

    for vs in items:
        ext_id = str(vs.get("id", ""))
        pr = cache.get("procedures", {}).get(ext_id)
        if not pr:
            continue

        vs_price = vs.get("price", 0)
        vs_duration = vs.get("duration", 30)

        diffs = {}
        pr_price = pr.get("price")
        if pr_price is not None:
            try:
                if abs(float(pr_price) - float(vs_price)) > 0.01:
                    diffs["price"] = vs_price
            except (ValueError, TypeError):
                pass
        pr_dur = pr.get("durationMinutes") or pr.get("duration_minutes")
        if pr_dur is not None and pr_dur != vs_duration:
            diffs["durationMinutes"] = vs_duration

        if diffs:
            name = clean_name(vs.get("name", ""))
            log.info("[VS->PR] PROC UPDATE: %s -> %s", name, diffs)
            time.sleep(API_DELAY)
            presenca_api("PUT", f"procedures/{pr['id']}", diffs)
            updated += 1

    if updated:
        log.info("[VS->PR] Procedures updated: %d", updated)


def run(cache, since_date):
    """Run vSaude -> Presenca sync. Returns stats dict."""
    log.info("=" * 50)
    log.info("[VS->PR] START since=%s", since_date)
    log.info("=" * 50)

    # Sync professionals and procedures (data updates)
    sync_professionals(cache)
    sync_procedures(cache)

    result = vsaude_post("ReportService/GetAttendance", {"maxResultCount": 1000})
    if not result:
        log.warning("[VS->PR] No data from vSaude GetAttendance")
        return {}

    items = result.get("items", result) if isinstance(result, dict) else result
    filtered = [a for a in items if (a.get("date", "") or "")[:10] >= since_date]
    log.info("[VS->PR] vSaude returned %d total, %d since %s", len(items), len(filtered), since_date)

    stats = {"pat_new": 0, "pat_upd": 0, "appt_new": 0, "appt_status": 0, "ok": 0, "skip": 0}

    for a in sorted(filtered, key=lambda x: x.get("date", "")):
        vs_hp = a.get("healthProfessional")
        if not vs_hp:
            stats["skip"] += 1
            continue

        vs_patient = a.get("patient") or {}
        vs_proc = a.get("procedure") or {}
        vs_appt_id = a.get("id", "")
        vs_date_raw = a.get("date", "")
        vs_status_code = a.get("status", 0)
        vs_price = a.get("price", 0)
        vs_duration = a.get("plannedDuration") or a.get("duration") or 30
        vs_remotely = a.get("remotely", False)
        vs_care_unit = (a.get("careUnit") or {}).get("name", "")
        vs_insurance = (a.get("insuranceCompany") or {}).get("name", "")

        sched_date, sched_time = utc_to_brt(vs_date_raw)
        if not sched_date:
            stats["skip"] += 1
            continue

        pr_status, pr_confirmed = VSAUDE_STATUS_MAP.get(vs_status_code, ("scheduled", False))
        prof_name = clean_name(vs_hp.get("name", ""))
        pat_name = clean_name(vs_patient.get("name", ""))
        vs_status_label = STATUS_LABEL.get(vs_status_code, f"?{vs_status_code}")
        proc_name = clean_name(vs_proc.get("name", ""))

        # Patient
        pat_ext_id = vs_patient.get("id", "")
        pr_patient = cache["patients"].get(pat_ext_id)

        if not pr_patient and pat_ext_id:
            log.info("[VS->PR] NEW PATIENT: name=%s cpf=%s phone=%s vsaude_id=%s",
                     pat_name, vs_patient.get("personalIdentifier", "?"),
                     vs_patient.get("phoneNumber", "?"), pat_ext_id[:12])
            time.sleep(API_DELAY)
            pat_gender = GENDER_MAP.get(vs_patient.get("gender"), None)
            pat_body = {
                "name": pat_name,
                "phone": vs_patient.get("phoneNumber", "") or "",
                "cpf": vs_patient.get("personalIdentifier", "") or "",
                "email": vs_patient.get("email", "") or "",
                "whatsappPhone": vs_patient.get("phoneNumber", "") or "",
                "externalId": pat_ext_id,
            }
            if pat_gender:
                pat_body["gender"] = pat_gender
            if not pat_body["cpf"]:
                pat_body.pop("cpf")
            resp = presenca_api("POST", "patients", pat_body)
            if resp:
                for p in extract_items(resp):
                    cache["patients"][pat_ext_id] = p
                    pr_patient = p
                log.info("[VS->PR] Patient created in Presenca: %s", pr_patient.get("id", "?")[:12])
            else:
                log.error("[VS->PR] Failed to create patient %s", pat_name)
            stats["pat_new"] += 1
        elif pr_patient:
            # Patient exists - check for updates
            pat_diffs = {}
            vs_phone = vs_patient.get("phoneNumber", "") or ""
            vs_email = vs_patient.get("email", "") or ""
            if pat_name and (pr_patient.get("name") or "") != pat_name:
                pat_diffs["name"] = pat_name
            if vs_phone and (pr_patient.get("phone") or "") != vs_phone:
                pat_diffs["phone"] = vs_phone
                pat_diffs["whatsappPhone"] = vs_phone
            if vs_email and (pr_patient.get("email") or "") != vs_email:
                pat_diffs["email"] = vs_email
            if pat_diffs:
                log.info("[VS->PR] PAT UPDATE: %s -> %s", pat_name, list(pat_diffs.keys()))
                time.sleep(API_DELAY)
                presenca_api("PUT", f"patients/{pr_patient['id']}", pat_diffs)
                stats["pat_upd"] += 1

        patient_id = pr_patient.get("id") if pr_patient else None
        if not patient_id:
            stats["skip"] += 1
            continue

        # FKs
        pr_prof = cache["professionals"].get(vs_hp.get("id", ""))
        professional_id = pr_prof.get("id") if pr_prof else None

        proc_ext = str(vs_proc.get("id", "")) if vs_proc.get("id") else None
        pr_proc = cache["procedures"].get(proc_ext) if proc_ext else None
        procedure_id = pr_proc.get("id") if pr_proc else None

        specialty_id = SPEC_PSIC if is_psicologia(vs_proc.get("name", "") or prof_name) else SPEC_PSIQ
        modality = "telemedicine" if vs_remotely else "outpatient"

        # Appointment
        pr_appt = cache["appointments"].get(vs_appt_id)

        if not pr_appt:
            log.info("[VS->PR] NEW APPOINTMENT: date=%s time=%s prof=%s patient=%s proc=%s price=%s vsaude_status=%s(%d) prof_id=%s proc_id=%s",
                     sched_date, sched_time, prof_name, pat_name,
                     proc_name[:30], vs_price, vs_status_label, vs_status_code,
                     professional_id, procedure_id)
            time.sleep(API_DELAY)
            resp = presenca_api("POST", "appointments", {
                "patientId": patient_id,
                "professionalId": professional_id,
                "specialtyId": specialty_id,
                "procedureId": procedure_id,
                "scheduledDate": sched_date,
                "scheduledTime": sched_time,
                "durationMinutes": vs_duration,
                "status": pr_status,
                "confirmed": pr_confirmed,
                "price": vs_price,
                "appointmentType": "follow_up",
                "serviceModality": modality,
                "healthInsuranceName": vs_insurance,
                "location": vs_care_unit,
                "schedulingSource": "api",
                "externalId": vs_appt_id,
            })
            if resp:
                for item in extract_items(resp):
                    cache["appointments"][vs_appt_id] = item
                log.info("[VS->PR] Appointment created in Presenca as '%s'", pr_status)
            else:
                log.error("[VS->PR] Failed to create appointment in Presenca")
            stats["appt_new"] += 1
        else:
            pr_cur = pr_appt.get("status", "")
            if pr_cur != pr_status:
                log.info("[VS->PR] STATUS CHANGED: date=%s patient=%s prof=%s presenca=%s -> vsaude=%s(%d)",
                         sched_date, pat_name, prof_name, pr_cur, vs_status_label, vs_status_code)
                time.sleep(API_DELAY)
                appt_id = pr_appt.get("id")
                if pr_status == "cancelled":
                    resp = presenca_api("POST", f"appointments/{appt_id}/cancel", {
                        "reason": f"Cancelado no vSaude (status {vs_status_code}: {vs_status_label})"
                    })
                else:
                    resp = presenca_api("PUT", f"appointments/{appt_id}", {
                        "status": pr_status, "confirmed": pr_confirmed,
                    })
                if resp:
                    log.info("[VS->PR] Status updated in Presenca")
                else:
                    log.error("[VS->PR] Failed to update status in Presenca")
                stats["appt_status"] += 1
            else:
                stats["ok"] += 1

    log.info("-" * 50)
    log.info("[VS->PR] RESULT: patients_new=%d patients_updated=%d appts_new=%d status_changed=%d synced=%d skipped=%d",
             stats["pat_new"], stats["pat_upd"], stats["appt_new"], stats["appt_status"], stats["ok"], stats["skip"])

    # Sync slots as part of the same cycle
    slot_stats = sync_slots(cache)
    stats["slots"] = slot_stats

    log.info("=" * 50)
    return stats


def _load_presenca_slots(prof_presenca_id):
    """Load ALL slots for a professional from Presenca in one call.
    Returns dict of (date, time) -> slot object."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    resp = presenca_api("GET", f"slots?professionalId={prof_presenca_id}&dateFrom={today}&limit=1000")
    slots = {}
    if resp and "data" in resp:
        for s in resp["data"]:
            s_date = (s.get("slotDate") or "")[:10]
            raw_time = s.get("slotTime") or ""
            if "T" in raw_time:
                s_time = raw_time.split("T")[1][:5]
            else:
                s_time = raw_time[:5]
            if s_date and s_time:
                slots[(s_date, s_time)] = s
    return slots


def sync_slots(cache):
    """Sync slots from vSaude availability to Presenca.

    For each professional:
    1. Load ALL existing Presenca slots in one GET call
    2. Get free slots from vSaude (GetAvailabilityWindow)
    3. Compare locally - only call API when something needs to change:
       - vSaude free + not in Presenca -> create
       - vSaude free + Presenca blocked -> unblock
       - vSaude free + Presenca available -> skip (no API call)
    """
    log.info("[SLOTS] START")

    total_created = 0
    total_unblocked = 0
    total_skipped = 0

    for ext_id, prof in cache.get("professionals", {}).items():
        proc_id = PROF_PROCEDURES.get(ext_id)
        if not proc_id:
            continue

        prof_name = prof.get("name", "?")
        prof_presenca_id = prof.get("id")

        # 1. Load existing Presenca slots for this professional (ONE call)
        time.sleep(API_DELAY)
        pr_slots = _load_presenca_slots(prof_presenca_id)

        # 2. Get FREE slots from vSaude
        result = vsaude_post("ScheduleService/GetAvailabilityWindow", {
            "procedureId": proc_id, "professionalId": ext_id,
        })
        if not result:
            continue

        pr_proc = cache.get("procedures", {}).get(str(proc_id))
        spec_id = pr_proc.get("specialtyId", SPEC_PSIQ) if pr_proc else SPEC_PSIQ
        proc_uuid = pr_proc.get("id") if pr_proc else None

        created = 0
        unblocked = 0
        skipped = 0

        # 3. Compare locally
        for day in result:
            for slot in day.get("availability", []):
                slot_date, slot_time = utc_to_brt(slot.get("time", ""))
                if not slot_date:
                    continue

                existing = pr_slots.get((slot_date, slot_time))

                if existing:
                    if not existing.get("isAvailable") or existing.get("isBlocked"):
                        # Blocked -> unblock
                        time.sleep(API_DELAY)
                        presenca_api("PUT", f"slots/{existing['id']}", {
                            "isAvailable": True, "isBlocked": False,
                        })
                        unblocked += 1
                    else:
                        skipped += 1  # Already available, no API call needed
                else:
                    # Slot not in Presenca -> create
                    ext_slot_id = f"{ext_id}_{slot_date}_{slot_time}"
                    slot_body = {
                        "professionalId": prof_presenca_id,
                        "specialtyId": spec_id,
                        "slotDate": slot_date,
                        "slotTime": slot_time,
                        "durationMinutes": 30,
                        "isAvailable": True,
                        "isBlocked": False,
                        "externalId": ext_slot_id,
                    }
                    if proc_uuid:
                        slot_body["procedureId"] = proc_uuid
                    time.sleep(API_DELAY)
                    presenca_api("POST", "slots", slot_body)
                    created += 1

        if created or unblocked:
            log.info("[SLOTS] %s: +%d created, %d unblocked, %d skipped",
                     prof_name, created, unblocked, skipped)

        total_created += created
        total_unblocked += unblocked
        total_skipped += skipped

    log.info("[SLOTS] RESULT: created=%d unblocked=%d skipped=%d",
             total_created, total_unblocked, total_skipped)
    return {"created": total_created, "unblocked": total_unblocked}
