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


CORE_TABLE_SPECS: tuple[BackupTableSpec, ...] = (
    BackupTableSpec("skills_info", "sqlalchemy", True, True, True, 10, 60, True),
    BackupTableSpec("skill_curriculum", "sqlalchemy", True, True, True, 20, 50, True),
    BackupTableSpec("textbook_examples", "sqlalchemy", True, True, True, 30, 20, True),
    BackupTableSpec("skill_family_bridge", "sqlalchemy", True, True, True, 40, 30, False),
    BackupTableSpec("skill_prerequisites", "sqlalchemy", True, True, True, 50, 40, False),
    BackupTableSpec("gencode_component_tracker", "raw_sql", True, True, True, 60, 10, False),
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
