#!/usr/bin/env python3
"""
HTTP webhook for cron-job.org (or any scheduler) to trigger scraper cron scripts.

Starts the matching cron_*.sh in the background and returns immediately so
cron-job.org does not time out on long scrapes.

Usage:
  export CRON_WEBHOOK_SECRET="your-long-random-secret"
  python3 webhook_server.py

Endpoints (GET or POST):
  /health              — liveness (no auth)
  /cron/realtime       — forex + energy
  /cron/weekly         — water
  /cron/monthly        — finance, property, employment, health
  /cron/quarterly      — all 10 topics

Auth: query ?token=SECRET or header X-Cron-Token: SECRET
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
LOG = logging.getLogger("webhook")

JOBS: dict[str, str] = {
    "realtime": "cron_realtime.sh",
    "weekly": "cron_weekly.sh",
    "monthly": "cron_monthly.sh",
    "quarterly": "cron_quarterly.sh",
}


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def secret_ok(handler: BaseHTTPRequestHandler) -> bool:
    expected = os.environ.get("CRON_WEBHOOK_SECRET", "").strip()
    if not expected:
        LOG.error("CRON_WEBHOOK_SECRET is not set")
        return False
    token = handler.headers.get("X-Cron-Token", "").strip()
    if not token:
        query = parse_qs(urlparse(handler.path).query)
        token = (query.get("token") or [""])[0].strip()
    return token == expected


def lock_path(job: str) -> Path:
    return ROOT / "logs" / "locks" / f"{job}.lock"


def acquire_lock(job: str, max_age_s: int = 3600) -> bool:
    path = lock_path(job)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            age = time.time() - path.stat().st_mtime
            if age < max_age_s:
                return False
        except OSError:
            pass
    path.write_text(str(int(time.time())))
    return True


def release_lock(job: str) -> None:
    try:
        lock_path(job).unlink(missing_ok=True)
    except OSError:
        pass


def run_job(job: str) -> None:
    script = ROOT / JOBS[job]
    log_file = ROOT / "logs" / f"webhook_{job}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    venv_python = ROOT / ".venv" / "bin" / "python3"
    if venv_python.exists():
        env["PATH"] = f"{ROOT / '.venv' / 'bin'}:{env.get('PATH', '')}"

    def worker() -> None:
        try:
            with open(log_file, "a", encoding="utf-8") as fh:
                fh.write(f"\n--- webhook start {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                subprocess.run(
                    [str(script)],
                    cwd=ROOT,
                    stdout=fh,
                    stderr=subprocess.STDOUT,
                    check=False,
                    env=env,
                )
        finally:
            release_lock(job)

    import threading

    threading.Thread(target=worker, daemon=True).start()


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        LOG.info("%s - %s", self.address_string(), fmt % args)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        self._dispatch()

    def do_POST(self) -> None:
        self._dispatch()

    def _dispatch(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"

        if path == "/health":
            self._json(200, {"ok": True, "service": "libo-insights-webhook"})
            return

        if not path.startswith("/cron/"):
            self._json(404, {"error": "not found"})
            return

        if not secret_ok(self):
            self._json(401, {"error": "unauthorized"})
            return

        job = path.split("/cron/", 1)[1].split("/", 1)[0]
        if job not in JOBS:
            self._json(404, {"error": "unknown job", "jobs": list(JOBS)})
            return

        if not acquire_lock(job):
            self._json(409, {"error": "job already running", "job": job})
            return

        run_job(job)
        self._json(
            202,
            {
                "status": "accepted",
                "job": job,
                "script": JOBS[job],
                "message": "Scraper started in background",
            },
        )


def main() -> None:
    load_env_file()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    if not os.environ.get("CRON_WEBHOOK_SECRET", "").strip():
        LOG.error("Set CRON_WEBHOOK_SECRET in .env or environment before starting.")
        sys.exit(1)

    host = os.environ.get("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.environ.get("WEBHOOK_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), WebhookHandler)
    LOG.info("Webhook listening on http://%s:%s", host, port)
    LOG.info("Jobs: %s", ", ".join(JOBS))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        LOG.info("Shutting down")
        server.server_close()


if __name__ == "__main__":
    main()
