# Construction AI Toolkit — Integrated Local Application

Version 0.3 combines deterministic scheduling, Gantt/exports, sourced unit-rate analysis and the existing repository skills. Project setup and Arabic/English CSV/XLSX BOQ intake remain available.

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
- View a Gantt chart with milestones and critical-activity colors.
- Calculate a CPM backward pass and total/free float for a single shared activity calendar.
- Download schedule CSV, Excel with relationships/calendars/WBS/traces, and a complete JSON snapshot.
- Keep saved run inputs and results unchanged after draft edits and activity deletion; show stale-input warnings.
- Build project estimates from explicit resource consumption and prices, sources and pricing dates.
- Distinguish markup from gross margin, with separate indirects, contingency, overhead, discount and explicit tax.
- Persist estimates per project, copy validated BOQ quantities without prices and export calculation/evidence packages.
- Browse all five repository skills and the original engineering prompts.
- Create a separate, explicitly synthetic demo project with one button.
- Opt into hierarchical BOQ preparation: combine descriptions sharing merged item-code/quantity cells, keep the shared quantity once, and review excluded headings/totals. Preserve original row evidence and source scope through estimating and activity conversion.
- Open a known project directly using `?project=<project-id>&view=boq` (or `estimate`, `schedule`, `workflows`).

The engine never invents quantities, productivity values, crew counts, WBS assignments, calendars, or relationships. Displayed duration rounding does not change the exact value used for scheduling.

## Current calculation boundaries

CPM float uses a single shared activity calendar and the calculated planned finish, not the contractual deadline. Multi-calendar forward scheduling remains supported, with no fabricated float. Contractual completion variance is displayed separately. CSV/Excel are review exports, not native XER files or verified P6 imports. Resource leveling, time-phased cost loading, cash flow and external AI-provider execution are not implemented.

Synthetic inputs under `sample_data/` are marked demonstration data. The sidebar demo button explicitly creates a separate example project; it never fills real project prices. Estimate evidence references still require human verification.

## Typical workflow

1. Create or select a project in **Project setup**.
2. Import and validate a BOQ in **BOQ import and review**.
3. Open **Schedule workspace**.
4. Build the WBS and review/create a project calendar.
5. Convert selected valid BOQ rows or add manual activities.
6. Complete all activity inputs without assumptions.
7. Add and review relationships and lags.
8. Open **Calculate & review**, correct blockers, and calculate a new immutable run.
9. View the Gantt chart and download saved results.
10. Open **Estimating** to enter resource rates and their sources; incomplete costs block the final price.
11. Browse **Engineering workflows** for tender management, quantity takeoff, rate analysis and estimate compilation.

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
