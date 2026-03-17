import json
import logging
import urllib.request
import urllib.error

from config import VSAUDE_API, VSAUDE_KEY, PRESENCA_API, PRESENCA_KEY, PRESENCA_SECRET

log = logging.getLogger("sync")


def vsaude_post(endpoint, body=None):
    url = f"{VSAUDE_API}/{endpoint}"
    headers = {"Content-Type": "application/json", "VSAUDE-API-KEY": VSAUDE_KEY}
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        d = json.loads(resp.read())
        if not d.get("success", True):
            log.warning("vSaude %s: %s", endpoint, d.get("error", {}).get("message", "?"))
            return None
        return d.get("result")
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:200] if e.fp else ""
        log.warning("vSaude %s: HTTP %s - %s", endpoint, e.code, err)
        return None
    except Exception as e:
        log.warning("vSaude %s: %s", endpoint, e)
        return None


def presenca_api(method, path, body=None):
    url = f"{PRESENCA_API}/{path}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": PRESENCA_KEY,
        "X-API-Secret": PRESENCA_SECRET,
        "User-Agent": "PresencaSync/1.0",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:300] if e.fp else ""
        log.warning("[PRESENCA] %s %s: HTTP %s - %s", method, path, e.code, err)
        return None
    except Exception as e:
        log.warning("[PRESENCA] %s %s: %s", method, path, e)
        return None


def extract_items(resp):
    if not resp:
        return []
    if isinstance(resp, list):
        return resp
    if "data" in resp:
        d = resp["data"]
        return d if isinstance(d, list) else [d]
    return []
