CREATE TABLE schedules (
    schedule_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'ready', 'calculated', 'blocked')),
    calculation_mode TEXT NOT NULL CHECK (calculation_mode = 'forward_pass'),
    rounding_precision INTEGER NOT NULL CHECK (rounding_precision BETWEEN 0 AND 6),
    rounding_mode TEXT NOT NULL CHECK (rounding_mode IN ('ROUND_HALF_UP', 'ROUND_HALF_EVEN', 'ROUND_UP', 'ROUND_DOWN')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

CREATE TABLE wbs_nodes (
    wbs_id TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    parent_wbs_id TEXT,
    sort_order INTEGER NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (schedule_id, code),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_wbs_id) REFERENCES wbs_nodes(wbs_id) ON DELETE RESTRICT
);

CREATE TABLE project_calendars (
    calendar_id TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    time_zone TEXT NOT NULL,
    working_weekdays_json TEXT NOT NULL,
    workday_start_time TEXT NOT NULL,
    working_hours_per_day_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (schedule_id, code),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE
);

CREATE TABLE calendar_breaks (
    break_id TEXT PRIMARY KEY,
    calendar_id TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    FOREIGN KEY (calendar_id) REFERENCES project_calendars(calendar_id) ON DELETE CASCADE
);

CREATE TABLE calendar_exceptions (
    exception_id TEXT PRIMARY KEY,
    calendar_id TEXT NOT NULL,
    exception_date TEXT NOT NULL,
    working INTEGER NOT NULL CHECK (working IN (0, 1)),
    workday_start_time TEXT,
    working_hours_text TEXT,
    reason TEXT,
    UNIQUE (calendar_id, exception_date),
    FOREIGN KEY (calendar_id) REFERENCES project_calendars(calendar_id) ON DELETE CASCADE
);

CREATE TABLE schedule_activities (
    activity_pk TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    activity_id TEXT NOT NULL,
    activity_name TEXT NOT NULL,
    activity_type TEXT NOT NULL CHECK (activity_type IN ('task_dependent', 'start_milestone', 'finish_milestone')),
    source_boq_row_id TEXT,
    boq_item_code TEXT,
    boq_description TEXT,
    source_row_number INTEGER,
    quantity_text TEXT,
    unit TEXT,
    normalized_unit TEXT,
    wbs_id TEXT,
    productivity_rate_text TEXT,
    productivity_basis TEXT CHECK (productivity_basis IS NULL OR productivity_basis IN ('per_day', 'per_hour')),
    crew_count INTEGER,
    calendar_id TEXT,
    notes TEXT,
    assumptions_json TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (schedule_id, activity_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (source_boq_row_id) REFERENCES boq_items(row_id) ON DELETE SET NULL,
    FOREIGN KEY (wbs_id) REFERENCES wbs_nodes(wbs_id) ON DELETE RESTRICT,
    FOREIGN KEY (calendar_id) REFERENCES project_calendars(calendar_id) ON DELETE RESTRICT
);

CREATE TABLE activity_relationships (
    relationship_id TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    predecessor_activity_pk TEXT NOT NULL,
    successor_activity_pk TEXT NOT NULL,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('FS', 'SS', 'FF', 'SF')),
    lag_hours_text TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (schedule_id, predecessor_activity_pk, successor_activity_pk, relationship_type, lag_hours_text),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE,
    FOREIGN KEY (predecessor_activity_pk) REFERENCES schedule_activities(activity_pk) ON DELETE CASCADE,
    FOREIGN KEY (successor_activity_pk) REFERENCES schedule_activities(activity_pk) ON DELETE CASCADE
);

CREATE TABLE schedule_runs (
    run_id TEXT PRIMARY KEY,
    schedule_id TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('blocked', 'calculated')),
    calculated_at TEXT NOT NULL,
    project_planned_finish TEXT,
    completion_variance_days INTEGER,
    validation_issues_json TEXT NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE
);

CREATE TABLE schedule_activity_results (
    run_id TEXT NOT NULL,
    activity_pk TEXT NOT NULL,
    exact_duration_hours_text TEXT NOT NULL,
    exact_duration_days_text TEXT NOT NULL,
    display_duration_days_text TEXT NOT NULL,
    early_start TEXT NOT NULL,
    early_finish TEXT NOT NULL,
    formula TEXT NOT NULL,
    calculation_trace_json TEXT NOT NULL,
    PRIMARY KEY (run_id, activity_pk),
    FOREIGN KEY (run_id) REFERENCES schedule_runs(run_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_pk) REFERENCES schedule_activities(activity_pk) ON DELETE CASCADE
);

CREATE INDEX idx_wbs_nodes_schedule ON wbs_nodes(schedule_id, sort_order, code);
CREATE INDEX idx_project_calendars_schedule ON project_calendars(schedule_id, code);
CREATE INDEX idx_schedule_activities_schedule ON schedule_activities(schedule_id, sort_order, activity_id);
CREATE INDEX idx_schedule_activities_boq ON schedule_activities(source_boq_row_id);
CREATE INDEX idx_activity_relationships_schedule ON activity_relationships(schedule_id);
CREATE INDEX idx_schedule_runs_schedule ON schedule_runs(schedule_id, calculated_at DESC);

INSERT INTO schema_migrations(version, applied_at)
VALUES ('003_scheduling_engine', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
