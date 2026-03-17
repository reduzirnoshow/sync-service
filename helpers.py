import re
from datetime import datetime, timezone, timedelta

from config import BRT


def utc_to_brt(dt_str):
    if not dt_str:
        return None, None
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    dt_brt = dt.astimezone(BRT)
    return dt_brt.strftime("%Y-%m-%d"), dt_brt.strftime("%H:%M")


def brt_to_utc(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_brt = dt.replace(tzinfo=BRT)
    dt_utc = dt_brt.astimezone(timezone.utc)
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_name(name):
    if not name:
        return ""
    return re.sub(r"\s+", " ", name.replace(";", "").strip())


def is_psicologia(name):
    lower = (name or "").lower()
    return any(kw in lower for kw in [
        "psicolog", "psicotera", "pitta", "gabriela bacelar",
        "priscila alencar", "aldinete", "amanda carvalho",
    ])


def extract_date_time(appt):
    sched_date = (appt.get("scheduledDate") or "")[:10]
    raw_time = appt.get("scheduledTime") or ""
    if "T" in raw_time:
        sched_time = raw_time.split("T")[1][:5]
    else:
        sched_time = raw_time[:5]
    return sched_date, sched_time
