# Construction Scheduling MVP

Phase 8 Milestone 1 provides a local Streamlit application for creating project records and importing, validating, editing, and storing BOQ data.

## Milestone 1 scope

- Project setup with explicit parties, dates, locale, units, and working-pattern inputs.
- Local SQLite persistence.
- CSV and XLSX BOQ intake with explicit column mapping.
- Automatic Excel header detection with a selectable header-row override for sheets that contain introductory rows.
- Unicode Arabic and English construction units with the source unit preserved and an internal normalized value.
- Editable BOQ review and row-level validation.
- Draft application contracts registered in the shared schema catalog.

Duration calculations, calendar arithmetic, CPM logic, Gantt charts, and schedule exports are intentionally not included in this milestone.

To re-import a corrected or previously rejected workbook, open **BOQ import and review**, upload the same file, confirm the worksheet and detected Excel header row, review the column mapping, and select **Import draft BOQ**. The re-import is stored as a new draft; the previous import is preserved for traceability.

## Start on Windows

1. Open the repository folder in File Explorer.
2. Double-click `START_SCHEDULING_APP.bat`.
3. Keep the launcher terminal window open while using the application.
4. The launcher opens `http://127.0.0.1:8501` in the default browser after Streamlit passes its health check.

The launcher detects the repository from its own location. It reuses `.venv-scheduling-mvp` when available, creates it with Python 3.12 when missing, and installs the Milestone 1 requirements only when imports or `pip check` fail.

## Stop on Windows

Double-click `STOP_SCHEDULING_APP.bat`. The stop launcher sends a tokenized request to the active launcher, which terminates only the Streamlit child process it created. It refuses to terminate an unidentified process using port 8501.

The START terminal displays confirmation when shutdown completes. It remains open until you press a key so startup or shutdown errors are not lost.

## Troubleshoot ERR_CONNECTION_REFUSED

`ERR_CONNECTION_REFUSED` means no process is listening on port 8501.

1. Confirm the START terminal is still open. Closing it stops the local application.
2. Read the status messages in that terminal.
3. Inspect the newest log under `apps/scheduling-mvp/logs/`.
4. Run `STOP_SCHEDULING_APP.bat` once to clear a managed stale session.
5. Run `START_SCHEDULING_APP.bat` again.
6. Open `http://127.0.0.1:8501`, not an old preview address using a different port.

If Python cannot be found, install Python 3.12 and make either `py -3.12` or `python` available. If dependency installation fails, restore internet access and rerun START.

Advanced manual launch from the repository root:

```powershell
.\.venv-scheduling-mvp\Scripts\python.exe -m streamlit run apps/scheduling-mvp/app.py --server.address 127.0.0.1 --server.port 8501
```

The database defaults to `.local/scheduling-mvp.db`. Override it for testing or isolated use with the `CONSTRUCTION_AI_DB_PATH` environment variable.

## Tests

```powershell
.\.venv-scheduling-mvp\Scripts\python.exe -m pytest -p no:cacheprovider -c packages/orchestrator/pyproject.toml
```

The command runs both the pre-existing platform suite and the scheduling MVP tests.
