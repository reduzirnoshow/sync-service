#!/usr/bin/env python3
"""
Sync Service - vSaude <-> Presenca IA
Roda continuamente sincronizando agendamentos entre os dois sistemas.
"""

# Load .env before anything else
import os
from pathlib import Path

env_file = Path(__file__).parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

import logging
import signal
import sys
import time
from datetime import datetime

from api import presenca_api, extract_items
from config import (BRT, INTERVAL_VS_TO_PR, INTERVAL_PR_TO_VS,
                     CACHE_REFRESH, LOOP_SLEEP)
import sync_vsaude_to_presenca
import sync_presenca_to_vsaude

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
log = logging.getLogger("sync")

cache = {"professionals": {}, "procedures": {}, "patients": {}, "appointments": {}}
last_cache_refresh = 0
last_vs_to_pr = 0
last_pr_to_vs = 0
running = True


def handle_signal(sig, frame):
    global running
    log.info("SIGNAL %s received, shutting down gracefully...", sig)
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def refresh_cache():
    global cache
    log.info("[CACHE] Refreshing from Presenca API...")

    endpoints = [
        ("professionals", "professionals"),
        ("procedures", "procedures"),
        ("patients", "patients?limit=1000"),
        ("appointments", "appointments?limit=1000"),
    ]

    new_cache = {"professionals": {}, "procedures": {}, "patients": {}, "appointments": {}}
    success = True

    for i, (key, path) in enumerate(endpoints):
        if i > 0:
            time.sleep(5)
        items = extract_items(presenca_api("GET", path))
        if not items:
            log.warning("[CACHE] Failed to load '%s' (rate limit?), keeping previous cache", key)
            success = False
            break
        for item in items:
            ext = item.get("externalId")
            if ext:
                new_cache[key][ext] = item
        log.info("[CACHE] %s: %d items loaded", key, len(new_cache[key]))

    if success:
        cache.clear()
        cache.update(new_cache)
        total = sum(len(v) for v in cache.values())
        log.info("[CACHE] Updated: profs=%d procs=%d pats=%d appts=%d total=%d",
                 len(cache["professionals"]), len(cache["procedures"]),
                 len(cache["patients"]), len(cache["appointments"]), total)
    else:
        total = sum(len(v) for v in cache.values())
        if total > 0:
            log.info("[CACHE] Keeping previous cache (%d items)", total)
        else:
            log.warning("[CACHE] Empty cache, sync limited until API is available")


def main():
    global last_cache_refresh, last_vs_to_pr, last_pr_to_vs

    log.info("=" * 60)
    log.info("Sync Service STARTED")
    log.info("  vSaude -> Presenca (appts+slots): every %ds", INTERVAL_VS_TO_PR)
    log.info("  Presenca -> vSaude: every %ds", INTERVAL_PR_TO_VS)
    log.info("  Cache refresh: every %ds", CACHE_REFRESH)
    log.info("  Loop sleep: %ds", LOOP_SLEEP)
    log.info("=" * 60)

    refresh_cache()
    last_cache_refresh = time.time()

    cycle = 0
    while running:
        now = time.time()
        since = datetime.now(BRT).strftime("%Y-%m-%d")

        if now - last_cache_refresh > CACHE_REFRESH:
            try:
                refresh_cache()
                last_cache_refresh = now
            except Exception as e:
                log.error("[CACHE] Error: %s", e)

        if now - last_vs_to_pr > INTERVAL_VS_TO_PR:
            try:
                sync_vsaude_to_presenca.run(cache, since)
                last_vs_to_pr = now
            except Exception as e:
                log.error("[VS->PR] Error: %s", e, exc_info=True)

        if now - last_pr_to_vs > INTERVAL_PR_TO_VS:
            try:
                sync_presenca_to_vsaude.run(cache, since)
                last_pr_to_vs = now
            except Exception as e:
                log.error("[PR->VS] Error: %s", e, exc_info=True)

        cycle += 1
        if cycle % 60 == 0:
            total = sum(len(v) for v in cache.values())
            log.info("[HEARTBEAT] cycle=%d cache=%d since=%s", cycle, total, since)

        time.sleep(LOOP_SLEEP)

    log.info("=" * 60)
    log.info("Sync Service STOPPED")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
