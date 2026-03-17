"""Sync vSaude -> Presenca: patients, appointments, status."""

import logging
import time

from api import vsaude_post, presenca_api, extract_items
from config import (VSAUDE_STATUS_MAP, GENDER_MAP, SPEC_PSIQ, SPEC_PSIC, API_DELAY)
from helpers import utc_to_brt, clean_name, is_psicologia

log = logging.getLogger("sync.vs2pr")

STATUS_LABEL = {
    1: "Criado", 10: "Agendado", 11: "CriadoAPI", 20: "Confirmado",
    21: "Reagendado", 30: "Presente", 31: "ConfirmadoAPI", 50: "Cancelado",
    51: "CanceladoAPI", 6: "Faltou", 81: "Finalizado", 82: "FinalizadoAPI",
    90: "EmAtendimento", 100: "Expirado", 110: "Deletado",
}


def run(cache, since_date):
    """Run vSaude -> Presenca sync. Returns stats dict."""
    log.info("=" * 50)
    log.info("[VS->PR] START since=%s", since_date)
    log.info("=" * 50)

    result = vsaude_post("ReportService/GetAttendance", {"maxResultCount": 1000})
    if not result:
        log.warning("[VS->PR] No data from vSaude GetAttendance")
        return {}

    items = result.get("items", result) if isinstance(result, dict) else result
    filtered = [a for a in items if (a.get("date", "") or "")[:10] >= since_date]
    log.info("[VS->PR] vSaude returned %d total, %d since %s", len(items), len(filtered), since_date)

    stats = {"pat_new": 0, "appt_new": 0, "appt_status": 0, "ok": 0, "skip": 0}

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
    log.info("[VS->PR] RESULT: patients_new=%d appts_new=%d status_changed=%d synced=%d skipped=%d",
             stats["pat_new"], stats["appt_new"], stats["appt_status"], stats["ok"], stats["skip"])
    log.info("=" * 50)
    return stats
