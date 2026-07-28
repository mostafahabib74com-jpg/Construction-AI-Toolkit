PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    client TEXT NOT NULL,
    contractor TEXT NOT NULL,
    consultant TEXT NOT NULL,
    project_type TEXT NOT NULL,
    location TEXT NOT NULL,
    planned_start_date TEXT NOT NULL,
    required_completion_date TEXT NOT NULL,
    working_days_per_week INTEGER NOT NULL,
    working_hours_per_day REAL NOT NULL,
    working_weekdays_json TEXT NOT NULL,
    workday_start_time TEXT NOT NULL,
    currency TEXT NOT NULL,
    unit_system TEXT NOT NULL,
    time_zone TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS boq_imports (
    import_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    source_file_name TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK (source_type IN ('csv', 'xlsx')),
    source_sheet TEXT,
    imported_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS boq_items (
    row_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    import_id TEXT NOT NULL,
    source_row_number INTEGER NOT NULL,
    item_code TEXT,
    description TEXT,
    quantity REAL,
    quantity_raw_json TEXT,
    unit TEXT,
    validation_status TEXT NOT NULL CHECK (validation_status IN ('valid', 'incomplete', 'invalid')),
    validation_errors_json TEXT NOT NULL,
    raw_data_json TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (import_id) REFERENCES boq_imports(import_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_boq_imports_project ON boq_imports(project_id, imported_at);
CREATE INDEX IF NOT EXISTS idx_boq_items_import ON boq_items(import_id, source_row_number);

INSERT OR IGNORE INTO schema_migrations(version, applied_at)
VALUES ('001_initial', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
