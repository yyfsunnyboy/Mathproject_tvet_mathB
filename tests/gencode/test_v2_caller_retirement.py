"""Import and sync paths never invoke the retired single-file generator."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_import_and_sync_have_no_v2_generator_calls():
    for relative in (
        "core/textbook_processor.py",
        "scripts/sync_skills_files.py",
        "scripts/sync_unit_pattern_skills.py",
        "core/routes/admin.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "auto_generate_skill_code"
            for node in ast.walk(tree)
        ), relative
        assert not any(
            isinstance(node, ast.ImportFrom)
            and node.module == "core.code_generator"
            and any(alias.name == "auto_generate_skill_code" for alias in node.names)
            for node in ast.walk(tree)
        ), relative


def test_auto_generate_skill_code_entry_removed_from_code_generator():
    source = (ROOT / "core" / "code_generator.py").read_text(encoding="utf-8-sig")
    tree = ast.parse(source)
    assert not any(
        isinstance(node, ast.FunctionDef) and node.name == "auto_generate_skill_code"
        for node in ast.walk(tree)
    )
    import core.code_generator as cg

    assert not hasattr(cg, "auto_generate_skill_code")
