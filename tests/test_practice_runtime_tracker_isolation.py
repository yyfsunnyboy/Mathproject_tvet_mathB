"""A failed student generation attempt must not rewrite Phase 2 evidence."""

from __future__ import annotations

import ast
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_runtime_generation_exception_preserves_verified_tracker() -> None:
    source = Path(__file__).resolve().parents[1] / "core/routes/practice.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    handlers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.name == "generate_exc"
    ]
    assert len(handlers) == 1

    # Execute the actual route exception handler with a failing generator in
    # isolation. This catches future attempts to persist runtime failures in
    # the verification tracker without starting Flask or touching its DB.
    snippet = ast.fix_missing_locations(
        ast.Module(
            body=[
                ast.Try(
                    body=[ast.Raise(exc=ast.Call(func=ast.Name(id="RuntimeError", ctx=ast.Load()), args=[ast.Constant("generation failed")], keywords=[]))],
                    handlers=handlers,
                    orelse=[],
                    finalbody=[],
                )
            ],
            type_ignores=[],
        )
    )
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE gencode_component_tracker (gencode_status TEXT, induced_spec_payload TEXT)")
    conn.execute("INSERT INTO gencode_component_tracker VALUES (?, ?)", ("verified", '{"integrity_gate_passed":true}'))
    before = conn.execute("SELECT * FROM gencode_component_tracker").fetchone()
    logged = []
    context = {
        "current_app": SimpleNamespace(logger=SimpleNamespace(exception=lambda *args: logged.append(args))),
        "skill_id": "test_skill",
        "effective_component_id": "src_1",
        "gen_seed": 7,
        "attempt": 0,
        "db": SimpleNamespace(engine=SimpleNamespace(raw_connection=lambda: conn)),
    }
    with pytest.raises(RuntimeError, match="generation failed"):
        exec(compile(snippet, str(source), "exec"), context)
    assert logged
    assert conn.execute("SELECT * FROM gencode_component_tracker").fetchone() == before
    conn.close()
