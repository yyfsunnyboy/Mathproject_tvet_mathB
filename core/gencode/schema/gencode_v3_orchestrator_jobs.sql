-- =============================================================================
-- Gencode V3 one-click orchestrator job table (SQLite 3)
-- =============================================================================
CREATE TABLE IF NOT EXISTS gencode_v3_orchestrator_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL UNIQUE,
    skill_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_gencode_v3_orch_jobs_skill
    ON gencode_v3_orchestrator_jobs(skill_id, updated_at DESC);
