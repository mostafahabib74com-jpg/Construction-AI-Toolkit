# Construction Scheduling MVP

Phase 8 Milestone 1 provides a local Streamlit application for creating project records and importing, validating, editing, and storing BOQ data.

## Milestone 1 scope

- Project setup with explicit parties, dates, locale, units, and working-pattern inputs.
- Local SQLite persistence.
- CSV and XLSX BOQ intake with explicit column mapping.
- Editable BOQ review and row-level validation.
- Draft application contracts registered in the shared schema catalog.

Duration calculations, calendar arithmetic, CPM logic, Gantt charts, and schedule exports are intentionally not included in this milestone.

## Local launch

From the repository root on Windows PowerShell:

```powershell
py -3.12 -m venv .venv-scheduling-mvp
.\.venv-scheduling-mvp\Scripts\python.exe -m pip install -r requirements-scheduling-mvp.txt
.\.venv-scheduling-mvp\Scripts\python.exe -m streamlit run apps/scheduling-mvp/app.py
```

If `py` is unavailable, replace it with the path to a Python 3.12 executable.

The database defaults to `.local/scheduling-mvp.db`. Override it for testing or isolated use with the `CONSTRUCTION_AI_DB_PATH` environment variable.

## Tests

```powershell
.\.venv-scheduling-mvp\Scripts\python.exe -m pytest -p no:cacheprovider -c packages/orchestrator/pyproject.toml
```

The command runs both the pre-existing platform suite and the scheduling MVP tests.
