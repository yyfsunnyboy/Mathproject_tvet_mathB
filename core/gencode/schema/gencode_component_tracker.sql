-- =============================================================================
-- Gencode × AgentSkillV3 shadow tracker table (SQLite 3)
-- Path derivation: agent_skills_v3/{skill_id}/components/{component_id}/
-- =============================================================================
CREATE TABLE IF NOT EXISTS gencode_component_tracker (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    textbook_example_id     INTEGER NOT NULL,
    skill_id                TEXT    NOT NULL,
    component_id            TEXT    NOT NULL,
    gencode_status          TEXT    NOT NULL DEFAULT 'pending',
    induced_spec_payload    TEXT,
    gencode_error_log       TEXT,
    created_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    CONSTRAINT uq_gencode_tracker_example_id
        UNIQUE (textbook_example_id),
    CONSTRAINT uq_gencode_tracker_namespace_pool
        UNIQUE (skill_id, component_id),
    CONSTRAINT ck_gencode_status_values
        CHECK (gencode_status IN (
            'pending',
            'usable',
            'generating',
            'draft_written',
            'smoke_passed',
            'verified',
            'failed'
        ))
);
