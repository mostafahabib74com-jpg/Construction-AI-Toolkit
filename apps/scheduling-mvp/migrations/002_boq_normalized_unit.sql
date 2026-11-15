ALTER TABLE boq_items ADD COLUMN normalized_unit TEXT;

INSERT INTO schema_migrations(version, applied_at)
VALUES ('002_boq_normalized_unit', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
