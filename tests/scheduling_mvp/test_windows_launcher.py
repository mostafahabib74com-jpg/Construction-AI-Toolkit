from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


@pytest.fixture()
def launcher(repo_root):
    path = repo_root / "apps/scheduling-mvp/launcher.py"
    specification = importlib.util.spec_from_file_location("scheduling_mvp_launcher", path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_launcher_resolves_repository_and_entry_point(launcher, repo_root):
    assert launcher.REPO_ROOT == repo_root
    assert launcher.APP_ENTRY == repo_root / "apps/scheduling-mvp/app.py"
    assert launcher.URL == "http://127.0.0.1:8501"


def test_stop_is_idempotent_when_nothing_is_running(launcher, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(launcher, "STOP_REQUEST", tmp_path / "stop.request")
    monkeypatch.setattr(launcher, "_port_open", lambda: False)
    assert launcher.stop_application() == 0


def test_stop_refuses_to_terminate_unidentified_port_owner(launcher, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(launcher, "STOP_REQUEST", tmp_path / "stop.request")
    monkeypatch.setattr(launcher, "_port_open", lambda: True)
    assert launcher.stop_application() == 2


def test_start_refuses_to_replace_unrelated_port_owner(launcher, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(launcher, "STOP_REQUEST", tmp_path / "stop.request")
    monkeypatch.setattr(launcher, "_port_open", lambda: True)
    assert launcher.run_application() == 2


def test_verified_stop_request_is_reported_as_clean_shutdown(launcher, tmp_path, monkeypatch):
    class FakeProcess:
        pid = 4321

        def __init__(self):
            self.returncode = None

        def poll(self):
            return self.returncode

        def terminate(self):
            self.returncode = 1

        def wait(self, timeout=None):
            return self.returncode

        def kill(self):
            self.returncode = 1

    app_entry = tmp_path / "app.py"
    app_entry.write_text("# test entry point\n", encoding="utf-8")
    stop_request = tmp_path / "stop.request"
    stop_request.write_text("verified-token", encoding="utf-8")
    fake_process = FakeProcess()

    monkeypatch.setattr(launcher, "APP_ENTRY", app_entry)
    monkeypatch.setattr(launcher, "LOG_DIR", tmp_path)
    monkeypatch.setattr(launcher, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(launcher, "STOP_REQUEST", stop_request)
    monkeypatch.setattr(launcher, "_port_open", lambda: False)
    monkeypatch.setattr(launcher, "_health_ready", lambda: True)
    monkeypatch.setattr(launcher, "_open_browser", lambda: None)
    monkeypatch.setattr(launcher.uuid, "uuid4", lambda: type("Token", (), {"hex": "verified-token"})())
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *args, **kwargs: fake_process)

    assert launcher.run_application() == 0


def test_batch_files_use_their_own_repository_location(repo_root):
    start = (repo_root / "START_SCHEDULING_APP.bat").read_text(encoding="utf-8")
    stop = (repo_root / "STOP_SCHEDULING_APP.bat").read_text(encoding="utf-8")
    assert 'set "REPO_ROOT=%~dp0"' in start
    assert 'set "REPO_ROOT=%~dp0"' in stop
    assert "apps\\scheduling-mvp\\launcher.py" in start
    assert "apps\\scheduling-mvp\\launcher.py" in stop
    assert "requirements-scheduling-mvp.txt" in start
