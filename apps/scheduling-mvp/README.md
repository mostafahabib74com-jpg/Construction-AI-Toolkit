# Construction Scheduling MVP

Phase 8 Milestone 2 adds a deterministic construction scheduling workspace to the local Streamlit application. Milestone 1 project setup and Arabic/English CSV/XLSX BOQ intake remain available.

## Current capabilities

- Create and select locally stored project records.
- Import, map, validate, edit, and preserve BOQ drafts.
- Create an editable WBS with stable internal identifiers.
- Create working calendars with weekdays, net productive hours, breaks, and date exceptions.
- Explicitly convert only validated BOQ rows to draft activities.
- Edit activity IDs, names, types, quantities, units, WBS, productivity basis/rate, crew count, calendar, notes, and order.
- Create FS, SS, FF, and SF relationships with signed lag expressed in successor-calendar working hours.
- Detect missing required inputs, invalid values, duplicate IDs or relationships, broken references, self-links, and circular logic.
- Calculate exact durations and deterministic forward-pass planned starts and finishes.
- Store every calculation as an immutable run with a signed completion-date variance.

The engine never invents quantities, productivity values, crew counts, WBS assignments, calendars, or relationships. Displayed duration rounding does not change the exact value used for scheduling.

## Milestone 2 boundary

Milestone 2 does **not** include Gantt charts, Excel/CSV/Primavera exports, backward-pass CPM, float, critical path, resource loading, cost loading, cash flow, or other platform modules. Those remain future milestones.

Synthetic inputs under `sample_data/` are marked demonstration data and are never loaded into user-created projects automatically.

## Typical workflow

1. Create or select a project in **Project setup**.
2. Import and validate a BOQ in **BOQ import and review**.
3. Open **Schedule workspace**.
4. Build the WBS and review/create a project calendar.
5. Convert selected valid BOQ rows or add manual activities.
6. Complete all activity inputs without assumptions.
7. Add and review relationships and lags.
8. Open **Calculate & review**, correct blockers, and calculate a new immutable run.

## Start on Windows

1. Open the repository folder in File Explorer.
2. Double-click `START_SCHEDULING_APP.bat`.
3. Keep the launcher terminal window open while using the application.
4. The launcher opens `http://127.0.0.1:8501` after the health check passes.

The launcher detects the repository from its own location, reuses `.venv-scheduling-mvp`, and installs the pinned local requirements only if imports or `pip check` fail.

## Stop on Windows

Double-click `STOP_SCHEDULING_APP.bat`. It stops only the token-identified Streamlit process created by this repository's launcher.

## Troubleshoot ERR_CONNECTION_REFUSED

`ERR_CONNECTION_REFUSED` means no process is listening on port 8501.

1. Confirm the START terminal remains open; closing it stops the application.
2. Read the status messages in that terminal.
3. Inspect the newest log under `apps/scheduling-mvp/logs/`.
4. Run `STOP_SCHEDULING_APP.bat` once to clear a managed stale session.
5. Run `START_SCHEDULING_APP.bat` again.
6. Open `http://127.0.0.1:8501`.

Manual launch from the repository root:

```powershell
.\.venv-scheduling-mvp\Scripts\python.exe -m streamlit run apps/scheduling-mvp/app.py --server.address 127.0.0.1 --server.port 8501
```

The database defaults to `.local/scheduling-mvp.db`. Set `CONSTRUCTION_AI_DB_PATH` to use an isolated database.

## Tests

```powershell
.\.venv-scheduling-mvp\Scripts\python.exe -m pytest -p no:cacheprovider -c packages/orchestrator/pyproject.toml
```

This runs the complete existing platform suite and the Milestone 1 and Milestone 2 application tests.
