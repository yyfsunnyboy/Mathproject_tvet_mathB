from __future__ import annotations

from core.backup.backup_registry import get_core_table_names, get_core_table_specs
from core.data_importer import CORE_TABLES


def test_registry_contains_six_core_tables_in_restore_order():
    assert get_core_table_names(include="export") == [
        "skills_info",
        "skill_curriculum",
        "textbook_examples",
        "skill_family_bridge",
        "skill_prerequisites",
        "gencode_component_tracker",
    ]


def test_export_import_clear_use_same_registry_membership():
    export_tables = set(get_core_table_names(include="export"))
    import_tables = set(get_core_table_names(include="import"))
    clear_tables = set(get_core_table_names(include="clear"))
    assert export_tables == import_tables == clear_tables
    assert list(CORE_TABLES) == get_core_table_names(include="export")


def test_tracker_is_raw_sql_optional_core_table():
    specs = {spec.table_name: spec for spec in get_core_table_specs()}
    tracker = specs["gencode_component_tracker"]
    assert tracker.access_mode == "raw_sql"
    assert tracker.include_in_core_export is True
    assert tracker.include_in_core_import is True
    assert tracker.include_in_core_clear is True
    assert tracker.required is False
