import os
from datetime import timedelta, timezone

# ─── APIs (OBRIGATÓRIO: setar via .env ou env vars do Railway) ───
VSAUDE_API = os.environ["VSAUDE_API_URL"]
VSAUDE_KEY = os.environ["VSAUDE_API_KEY"]

PRESENCA_API = os.environ["PRESENCA_API_URL"]
PRESENCA_KEY = os.environ["PRESENCA_API_KEY"]
PRESENCA_SECRET = os.environ["PRESENCA_API_SECRET"]

# ─── Constants ───────────────────────────────────────────────
BRT = timezone(timedelta(hours=-3))
SPEC_PSIQ = "042a7ccf-fd89-4e59-a006-06c6a2ef14ac"
SPEC_PSIC = "7909589a-ea09-47dc-8379-7733f9d747e5"
CARE_UNIT_ID = 5273
INSURANCE_COMPANY_ID = 6756

# ─── Intervals ───────────────────────────────────────────────
INTERVAL_VS_TO_PR = int(os.environ.get("INTERVAL_VS_TO_PR", "30"))
INTERVAL_PR_TO_VS = int(os.environ.get("INTERVAL_PR_TO_VS", "60"))
CACHE_REFRESH = int(os.environ.get("CACHE_REFRESH", "300"))
LOOP_SLEEP = int(os.environ.get("LOOP_SLEEP", "5"))
API_DELAY = int(os.environ.get("API_DELAY", "1"))

# ─── Status maps ─────────────────────────────────────────────
VSAUDE_STATUS_MAP = {
    1: ("scheduled", False), 10: ("scheduled", False), 11: ("scheduled", False),
    20: ("confirmed", True), 21: ("rescheduled", False),
    30: ("confirmed", True), 31: ("confirmed", True),
    50: ("cancelled", False), 51: ("cancelled", False),
    6: ("no_show", False),
    81: ("completed", True), 82: ("completed", True),
    90: ("confirmed", True), 100: ("cancelled", False), 110: ("cancelled", False),
}

PRESENCA_TO_VSAUDE_ACTION = {
    "confirmed": ("ScheduleService/Accept", {}),
    "cancelled": ("ScheduleService/Cancel", {"cancellationReason": "Cancelado via Presença IA"}),
    "completed": ("ScheduleService/Finalize", {"comments": "Finalizado via Presença IA"}),
    "no_show": ("ScheduleService/CounterPartDidNotShowUp", {}),
}

VSAUDE_TO_PRESENCA_STATUS = {
    10: "scheduled", 11: "scheduled",
    20: "confirmed", 21: "rescheduled",
    30: "confirmed", 31: "confirmed",
    50: "cancelled", 51: "cancelled",
    6: "no_show", 81: "completed", 82: "completed",
    90: "confirmed", 100: "cancelled",
}

GENDER_MAP = {0: None, 1: "male", 2: "female"}

PROF_PROCEDURES = {
    "2687f702-3947-4910-8d08-b3580120233e": 52100,
    "72aabf00-6d8e-4e49-b169-b358011aea96": 52101,
    "722d485e-8996-410a-ad23-b38c00a47279": 52103,
    "dee22ca9-f224-4b88-a810-b3ec01735613": 52883,
    "a439e002-a945-4018-a7bd-b3ec017f7921": 52884,
    "2481fd0e-9284-478a-9f88-b3e600b9c639": 52763,
    "43ae301b-0b23-468d-87e9-b3e500d9ebcd": 52754,
    "087517bd-9c6e-4852-9f03-b3d2016dd3b8": 52455,
    "e4fe2025-4891-4150-87a9-b38c00c9dc18": 52456,
    "d0e664d6-d171-4b5b-a3d7-b35801314d95": 52411,
    "1aece1e7-56e7-456b-901a-b3d0013a4a1b": 53387,
}
