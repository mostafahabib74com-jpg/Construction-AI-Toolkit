"""Windows lifecycle helper used exclusively by the Milestone 1 batch launchers."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ENTRY = REPO_ROOT / "apps" / "scheduling-mvp" / "app.py"
LOG_DIR = REPO_ROOT / "apps" / "scheduling-mvp" / "logs"
STATE_FILE = LOG_DIR / "scheduling-app-state.json"
STOP_REQUEST = LOG_DIR / "scheduling-app-stop.request"
HOST = "127.0.0.1"
PORT = 8501
URL = f"http://{HOST}:{PORT}"
HEALTH_URL = f"{URL}/_stcore/health"


def _read_state() -> dict[str, Any] | None:
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_state(value: dict[str, Any]) -> None:
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(STATE_FILE)


def _process_exists(pid: Any) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        synchronize = 0x00100000
        wait_timeout = 0x00000102
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return False
        try:
            return ctypes.windll.kernel32.WaitForSingleObject(handle, 0) == wait_timeout
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _port_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.5)
        return connection.connect_ex((HOST, PORT)) == 0


def _health_ready() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=1.0) as response:
            return response.status == 200 and response.read().decode("utf-8").strip() == "ok"
    except (OSError, urllib.error.URLError):
        return False


def _cleanup_state(token: str | None = None) -> None:
    state = _read_state()
    if token is None or not state or state.get("token") == token:
        STATE_FILE.unlink(missing_ok=True)
    STOP_REQUEST.unlink(missing_ok=True)


def _tail(path: Path, lines: int = 20) -> str:
    try:
        content = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(content[-lines:])


def _terminate(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _open_browser() -> None:
    if os.environ.get("CONSTRUCTION_AI_LAUNCHER_NO_BROWSER") == "1":
        return
    if not webbrowser.open(URL, new=2):
        print(f"[WARNING] The browser could not be opened automatically. Open {URL} manually.", flush=True)


def run_application() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    existing = _read_state()
    if existing and _process_exists(existing.get("launcher_pid")) and _health_ready():
        print(f"[OK] The Scheduling MVP is already running at {URL}", flush=True)
        print(f"[INFO] Streamlit PID: {existing.get('streamlit_pid')}", flush=True)
        _open_browser()
        return 0
    if existing:
        _cleanup_state()
    if _port_open():
        print(f"[ERROR] Port {PORT} is already used by another process.", flush=True)
        print("[ERROR] This launcher will not stop or replace an unrelated process.", flush=True)
        return 2
    if not APP_ENTRY.is_file():
        print(f"[ERROR] Streamlit entry point not found: {APP_ENTRY}", flush=True)
        return 2

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = LOG_DIR / f"scheduling-app-{timestamp}.log"
    token = uuid.uuid4().hex
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_ENTRY),
        "--server.address",
        HOST,
        "--server.port",
        str(PORT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    environment = os.environ.copy()
    environment["PYTHONUNBUFFERED"] = "1"
    log_handle = log_path.open("a", encoding="utf-8", buffering=1)
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        env=environment,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    state = {
        "application": "construction-ai-scheduling-mvp",
        "token": token,
        "launcher_pid": os.getpid(),
        "streamlit_pid": process.pid,
        "python_executable": sys.executable,
        "app_entry": str(APP_ENTRY),
        "url": URL,
        "log_file": str(log_path),
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_state(state)
    print(f"[INFO] Streamlit PID: {process.pid}", flush=True)
    print(f"[INFO] Log file: {log_path}", flush=True)

    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            exit_code = process.poll()
            if exit_code is not None:
                print(f"[ERROR] Streamlit exited during startup with code {exit_code}.", flush=True)
                recent = _tail(log_path)
                if recent:
                    print("[ERROR] Recent log output:\n" + recent, flush=True)
                return exit_code or 1
            if _health_ready():
                print(f"[OK] Application is ready: {URL}", flush=True)
                _open_browser()
                break
            time.sleep(0.25)
        else:
            print("[ERROR] Streamlit did not become healthy within 45 seconds.", flush=True)
            recent = _tail(log_path)
            if recent:
                print("[ERROR] Recent log output:\n" + recent, flush=True)
            _terminate(process)
            return 1

        stopped_by_request = False
        while process.poll() is None:
            try:
                request_token = STOP_REQUEST.read_text(encoding="utf-8").strip()
            except OSError:
                request_token = None
            if request_token == token:
                print("[STOP] A verified stop request was received.", flush=True)
                stopped_by_request = True
                _terminate(process)
                break
            time.sleep(0.25)
        if stopped_by_request:
            return 0
        return process.returncode or 0
    except KeyboardInterrupt:
        print("\n[STOP] Console interruption received. Stopping Streamlit...", flush=True)
        _terminate(process)
        return 0
    finally:
        _terminate(process)
        log_handle.close()
        _cleanup_state(token)


def stop_application() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    state = _read_state()
    if not state:
        if _port_open():
            print(f"[ERROR] Port {PORT} is open, but no managed Scheduling MVP state exists.", flush=True)
            print("[ERROR] Refusing to stop an unidentified process.", flush=True)
            return 2
        print("[OK] No managed Scheduling MVP process is running.", flush=True)
        return 0

    launcher_pid = state.get("launcher_pid")
    token = state.get("token")
    if not isinstance(token, str) or not token or not _process_exists(launcher_pid):
        if not _port_open():
            _cleanup_state()
            print("[OK] Removed stale launcher state; the application was already stopped.", flush=True)
            return 0
        print("[ERROR] Launcher ownership could not be verified. No process was stopped.", flush=True)
        return 2

    STOP_REQUEST.write_text(token, encoding="utf-8")
    print(f"[STOP] Requested shutdown of managed Streamlit PID {state.get('streamlit_pid')}.", flush=True)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if not STATE_FILE.exists() and not _port_open():
            STOP_REQUEST.unlink(missing_ok=True)
            print("[OK] The Scheduling MVP stopped successfully.", flush=True)
            return 0
        time.sleep(0.25)
    print("[ERROR] The managed launcher did not confirm shutdown within 20 seconds.", flush=True)
    print("[ERROR] No unrelated process was terminated.", flush=True)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage the local Scheduling MVP Streamlit process.")
    parser.add_argument("action", choices=("run", "stop"))
    arguments = parser.parse_args()
    return run_application() if arguments.action == "run" else stop_application()


if __name__ == "__main__":
    raise SystemExit(main())
