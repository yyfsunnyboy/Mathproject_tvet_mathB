"""Canonical table registry for core backup/import/clear flows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupTableSpec:
    table_name: str
    access_mode: str
    include_in_core_export: bool
    include_in_core_import: bool
    include_in_core_clear: bool
    restore_order: int
    delete_order: int
    required: bool
    # DELETE_CORE behavior:
    # - table_full: wipe entire table
    # - student_fk: delete rows whose FK points at role='student' users
    # - users_students: DELETE FROM users WHERE role='student' (never wipe admin/teacher)
    # - none: export/import only
    clear_mode: str = "none"
    # FK column used by student_fk clear_mode (user_id or student_id).
    clear_fk_column: str | None = None


STUDENT_ROLE_SUBQUERY = "(SELECT id FROM users WHERE role = 'student')"

# Textbook / curriculum tables wiped in full on DELETE_CORE (no curriculum/volume/skill WHERE).
CORE_TEXTBOOK_FULL_CLEAR_TABLES: tuple[str, ...] = (
    "gencode_component_tracker",
    "textbook_examples",
    "skill_family_bridge",
    "skill_prerequisites",
    "skill_curriculum",
    "questions",
    "skills_info",
)


# FK audit (sqlite inspector): tables with FK -> users/classes/class_students.
CORE_TABLE_SPECS: tuple[BackupTableSpec, ...] = (
    # --- Account roster ---
    BackupTableSpec("users", "sqlalchemy", True, True, True, 1, 140, False, "users_students", None),
    BackupTableSpec("classes", "sqlalchemy", True, True, True, 2, 130, False, "table_full", None),
    BackupTableSpec("class_students", "sqlalchemy", True, True, True, 3, 120, False, "table_full", None),
    # --- Shared parents for learning records (skills / question bank) ---
    BackupTableSpec("skills_info", "sqlalchemy", True, True, True, 10, 260, True, "table_full", None),
    BackupTableSpec("skill_curriculum", "sqlalchemy", True, True, True, 20, 250, True, "table_full", None),
    BackupTableSpec("questions", "sqlalchemy", True, True, True, 25, 215, False, "table_full", None),
    # --- Account-dependent learning records (FK -> users) ---
    BackupTableSpec("practice_attempts", "sqlalchemy", True, True, True, 29, 102, False, "student_fk", "student_id"),
    # quiz_attempts / student_abilities are table_full so questions/skills_info can wipe cleanly (FK).
    BackupTableSpec("progress", "sqlalchemy", True, True, True, 30, 110, False, "student_fk", "user_id"),
    BackupTableSpec("student_abilities", "sqlalchemy", True, True, True, 31, 100, False, "table_full", None),
    BackupTableSpec("quiz_attempts", "sqlalchemy", True, True, True, 32, 95, False, "table_full", None),
    BackupTableSpec("adaptive_learning_logs", "sqlalchemy", True, True, True, 33, 80, False, "student_fk", "student_id"),
    BackupTableSpec("mistake_logs", "sqlalchemy", True, True, True, 34, 70, False, "student_fk", "user_id"),
    BackupTableSpec("mistake_notebook_entries", "sqlalchemy", True, True, True, 35, 60, False, "student_fk", "student_id"),
    BackupTableSpec("exam_analysis", "sqlalchemy", True, True, True, 36, 50, False, "student_fk", "user_id"),
    BackupTableSpec("student_uploaded_questions", "sqlalchemy", True, True, True, 37, 40, False, "student_fk", "student_id"),
    BackupTableSpec("node_competency", "sqlalchemy", True, True, True, 38, 30, False, "student_fk", "user_id"),
    BackupTableSpec("learning_diagnosis", "sqlalchemy", True, True, True, 39, 20, False, "student_fk", "student_id"),
    BackupTableSpec("b4_chap2_visibility_audit_logs", "sqlalchemy", True, True, True, 40, 10, False, "student_fk", "student_id"),
    # --- Textbook / bridge / tracker (full wipe) ---
    BackupTableSpec("textbook_examples", "sqlalchemy", True, True, True, 50, 220, True, "table_full", None),
    BackupTableSpec("skill_family_bridge", "sqlalchemy", True, True, True, 60, 230, False, "table_full", None),
    BackupTableSpec("skill_prerequisites", "sqlalchemy", True, True, True, 70, 240, False, "table_full", None),
    BackupTableSpec("gencode_component_tracker", "raw_sql", True, True, True, 80, 210, False, "table_full", None),
)


# (table, fk_column, parent_table, parent_column, nullable_ok)
ACCOUNT_REF_CHECKS: tuple[tuple[str, str, str, str, bool], ...] = (
    ("classes", "teacher_id", "users", "id", False),
    ("class_students", "class_id", "classes", "id", False),
    ("class_students", "student_id", "users", "id", False),
    ("progress", "user_id", "users", "id", False),
    ("practice_attempts", "student_id", "users", "id", False),
    ("practice_attempts", "class_id", "classes", "id", True),
    ("student_abilities", "user_id", "users", "id", False),
    ("quiz_attempts", "user_id", "users", "id", False),
    ("quiz_attempts", "question_id", "questions", "id", False),
    ("adaptive_learning_logs", "student_id", "users", "id", False),
    ("mistake_logs", "user_id", "users", "id", False),
    ("mistake_notebook_entries", "student_id", "users", "id", False),
    ("exam_analysis", "user_id", "users", "id", False),
    ("student_uploaded_questions", "student_id", "users", "id", False),
    ("node_competency", "user_id", "users", "id", False),
    ("learning_diagnosis", "student_id", "users", "id", False),
    ("b4_chap2_visibility_audit_logs", "student_id", "users", "id", True),
)


def get_core_table_specs() -> tuple[BackupTableSpec, ...]:
    return CORE_TABLE_SPECS


def get_core_table_names(*, include: str = "export") -> list[str]:
    if include == "export":
        specs = [s for s in CORE_TABLE_SPECS if s.include_in_core_export]
        return [s.table_name for s in sorted(specs, key=lambda s: s.restore_order)]
    if include == "import":
        specs = [s for s in CORE_TABLE_SPECS if s.include_in_core_import]
        return [s.table_name for s in sorted(specs, key=lambda s: s.restore_order)]
    if include == "clear":
        specs = [s for s in CORE_TABLE_SPECS if s.include_in_core_clear]
        return [s.table_name for s in sorted(specs, key=lambda s: s.delete_order)]
    raise ValueError(f"unknown include mode: {include!r}")


def get_core_delete_specs() -> list[BackupTableSpec]:
    """All DELETE_CORE targets in delete_order."""
    modes = {"table_full", "student_fk", "users_students"}
    specs = [
        s
        for s in CORE_TABLE_SPECS
        if s.include_in_core_clear and s.clear_mode in modes
    ]
    return sorted(specs, key=lambda s: s.delete_order)


def get_core_account_clear_specs() -> list[BackupTableSpec]:
    """Account/learning clear targets (excludes textbook full-wipe tables)."""
    textbook = set(CORE_TEXTBOOK_FULL_CLEAR_TABLES)
    return [s for s in get_core_delete_specs() if s.table_name not in textbook]


def get_core_textbook_clear_specs() -> list[BackupTableSpec]:
    """Textbook / curriculum tables wiped in full on DELETE_CORE."""
    textbook = set(CORE_TEXTBOOK_FULL_CLEAR_TABLES)
    return [s for s in get_core_delete_specs() if s.table_name in textbook]


def get_core_full_clear_table_names() -> list[str]:
    """Backward-compatible: account clear tables in delete_order."""
    return [s.table_name for s in get_core_account_clear_specs()]


def get_core_math_b_scoped_table_names() -> list[str]:
    """Deprecated: Math-B scoped clear removed from DELETE_CORE; returns textbook full-clear tables."""
    return [s.table_name for s in get_core_textbook_clear_specs()]


def build_account_clear_where(spec: BackupTableSpec) -> str | None:
    """
    Return SQL WHERE clause for DELETE_CORE clear, or None for full-table delete.
    """
    mode = str(spec.clear_mode or "").strip()
    if mode == "table_full":
        return None
    if mode == "users_students":
        return "role = 'student'"
    if mode == "student_fk":
        col = str(spec.clear_fk_column or "").strip()
        if not col:
            raise ValueError(f"student_fk clear requires clear_fk_column for {spec.table_name}")
        return f'"{col}" IN {STUDENT_ROLE_SUBQUERY}'
    raise ValueError(f"unsupported clear_mode: {mode!r} for {spec.table_name}")


def get_account_ref_checks() -> tuple[tuple[str, str, str, str, bool], ...]:
    return ACCOUNT_REF_CHECKS


def get_core_required_table_names() -> list[str]:
    return [s.table_name for s in CORE_TABLE_SPECS if s.required]


def get_core_optional_table_names() -> list[str]:
    return [s.table_name for s in CORE_TABLE_SPECS if not s.required]


def get_table_spec(table_name: str) -> BackupTableSpec | None:
    key = str(table_name or "").strip()
    for spec in CORE_TABLE_SPECS:
        if spec.table_name == key:
            return spec
    return None


def is_core_table(table_name: str, *, include: str = "import") -> bool:
    return str(table_name or "").strip() in set(get_core_table_names(include=include))
