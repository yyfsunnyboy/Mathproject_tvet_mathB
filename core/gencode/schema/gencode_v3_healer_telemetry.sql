-- =============================================================================
-- GenCode V3 component code healer telemetry (SQLite 3), append-only events
-- =============================================================================
-- event_type:
--   attempt  one row per unique healer invocation (generation run x component x mode x original SHA)
--   rule     one row per rule evaluation inside an attempt, ordered by rule_seq
--   gate     final V3 gate outcome of a repair-mode repair handed to the pipeline
--   publish  repaired component published after human approval
-- event_key is deterministic, so retries / resumes are absorbed by ON CONFLICT(event_key) DO NOTHING.
-- No source code, answers, student data or secrets are stored.
CREATE TABLE IF NOT EXISTS gencode_v3_healer_telemetry_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_key TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL CHECK (event_type IN ('attempt', 'rule', 'gate', 'publish')),
    attempt_id TEXT NOT NULL,
    generation_run_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    textbook_example_id INTEGER,
    skill_id TEXT NOT NULL,
    mode TEXT NOT NULL CHECK (mode IN ('shadow', 'repair')),
    environment TEXT NOT NULL CHECK (environment IN ('production', 'staging', 'test')),
    data_origin TEXT NOT NULL CHECK (data_origin IN ('real_world', 'synthetic')),
    failure_category TEXT,
    eligible INTEGER NOT NULL DEFAULT 0,
    rule_seq INTEGER,
    round_index INTEGER,
    tier TEXT,
    rule_id TEXT,
    repair_chain TEXT NOT NULL DEFAULT '[]',
    outcome TEXT NOT NULL,
    reason_code TEXT,
    applied_to_pipeline INTEGER NOT NULL DEFAULT 0,
    original_sha256 TEXT,
    repaired_sha256 TEXT,
    certificate_status TEXT,
    evidence_path TEXT,
    gate_stage TEXT,
    created_at TEXT NOT NULL,
    finished_at TEXT,
    source_version TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gencode_v3_healer_tel_type_created
    ON gencode_v3_healer_telemetry_events(event_type, created_at);
CREATE INDEX IF NOT EXISTS idx_gencode_v3_healer_tel_attempt
    ON gencode_v3_healer_telemetry_events(attempt_id);
CREATE TRIGGER IF NOT EXISTS trg_gencode_v3_healer_tel_no_update
    BEFORE UPDATE ON gencode_v3_healer_telemetry_events
BEGIN
    SELECT RAISE(ABORT, 'gencode_v3_healer_telemetry_events is append-only');
END;
