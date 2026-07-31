from __future__ import annotations

from core.backup.backup_registry import (
    build_account_clear_where,
    get_account_ref_checks,
    get_core_account_clear_specs,
    get_core_full_clear_table_names,
    get_core_table_names,
    get_core_table_specs,
)
from core.data_importer import CORE_TABLES


EXPECTED_EXPORT_ORDER = [
    "users",
    "classes",
    "class_students",
    "skills_info",
    "skill_curriculum",
    "questions",
    "progress",
    "student_abilities",
    "quiz_attempts",
    "adaptive_learning_logs",
    "mistake_logs",
    "mistake_notebook_entries",
    "exam_analysis",
    "student_uploaded_questions",
    "node_competency",
    "learning_diagnosis",
    "b4_chap2_visibility_audit_logs",
    "textbook_examples",
    "skill_family_bridge",
    "skill_prerequisites",
    "gencode_component_tracker",
]


def test_registry_export_order_includes_account_learning_tables():
    assert get_core_table_names(include="export") == EXPECTED_EXPORT_ORDER
    assert list(CORE_TABLES) == EXPECTED_EXPORT_ORDER


def test_export_import_clear_membership_aligned():
    assert set(get_core_table_names(include="export")) == set(get_core_table_names(include="import"))
    assert set(get_core_table_names(include="export")) == set(get_core_table_names(include="clear"))


def test_account_clear_never_uses_users_full_wipe():
    specs = {s.table_name: s for s in get_core_table_specs()}
    assert specs["users"].clear_mode == "users_students"
    assert build_account_clear_where(specs["users"]) == "role = 'student'"
    assert specs["classes"].clear_mode == "table_full"
    assert specs["class_students"].clear_mode == "table_full"
    assert specs["skills_info"].clear_mode == "table_full"
    assert specs["skill_curriculum"].clear_mode == "table_full"
    assert specs["textbook_examples"].clear_mode == "table_full"
    assert specs["questions"].clear_mode == "table_full"
    assert build_account_clear_where(specs["progress"]) == (
        '"user_id" IN (SELECT id FROM users WHERE role = \'student\')'
    )
    assert build_account_clear_where(specs["adaptive_learning_logs"]) == (
        '"student_id" IN (SELECT id FROM users WHERE role = \'student\')'
    )


def test_account_clear_delete_order():
    names = [s.table_name for s in get_core_account_clear_specs()]
    assert names == get_core_full_clear_table_names()
    assert names.index("progress") < names.index("class_students")
    assert names.index("class_students") < names.index("classes") < names.index("users")
    assert "skills_info" not in names
    assert "textbook_examples" not in names


def test_textbook_full_clear_delete_order():
    from core.backup.backup_registry import get_core_textbook_clear_specs

    names = [s.table_name for s in get_core_textbook_clear_specs()]
    assert names.index("gencode_component_tracker") < names.index("textbook_examples")
    assert names.index("skill_family_bridge") < names.index("skills_info")
    assert names.index("skill_prerequisites") < names.index("skills_info")
    assert names.index("textbook_examples") < names.index("skills_info")
    assert names.index("questions") < names.index("skills_info")


def test_restore_order_users_before_classes_before_learning():
    order = get_core_table_names(include="import")
    assert order.index("users") < order.index("classes") < order.index("class_students")
    assert order.index("class_students") < order.index("progress")
    assert order.index("questions") < order.index("quiz_attempts")
    assert order.index("skills_info") < order.index("student_abilities")
    assert order.index("progress") < order.index("textbook_examples")


def test_account_ref_checks_cover_user_fks():
    tables = {t for t, *_ in get_account_ref_checks()}
    for name in (
        "progress",
        "student_abilities",
        "quiz_attempts",
        "adaptive_learning_logs",
        "mistake_logs",
        "mistake_notebook_entries",
        "exam_analysis",
        "student_uploaded_questions",
        "node_competency",
        "learning_diagnosis",
        "b4_chap2_visibility_audit_logs",
        "class_students",
        "classes",
    ):
        assert name in tables
