from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_streamlit_application_loads_project_setup(tmp_path, monkeypatch, repo_root):
    monkeypatch.setenv("CONSTRUCTION_AI_DB_PATH", str(tmp_path / "streamlit.db"))
    app = AppTest.from_file(str(repo_root / "apps/scheduling-mvp/app.py"), default_timeout=15).run()

    assert not app.exception
    assert app.title[0].value == "Construction AI Toolkit"
    assert app.header[0].value == "Project setup"
    assert app.sidebar.radio[0].value == "Project setup"

    app.sidebar.radio[0].set_value("BOQ import and review").run()
    assert not app.exception
    assert app.header[0].value == "BOQ import and review"
    assert "Create or select a saved project" in app.warning[0].value
