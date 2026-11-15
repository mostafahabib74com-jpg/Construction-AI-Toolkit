-- Preserve complete immutable results even when editable activities are deleted.
ALTER TABLE schedule_runs ADD COLUMN snapshot_json TEXT;

CREATE TABLE estimate_drafts (
    project_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

INSERT INTO schema_migrations(version, applied_at)
VALUES ('004_integrated_workspaces', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
