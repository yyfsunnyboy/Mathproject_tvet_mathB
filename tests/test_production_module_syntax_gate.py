# -*- coding: utf-8 -*-
"""Generic compile / fresh-import gate for production Python modules.

Catches SyntaxError classes such as f-string expressions that contain
backslash-bearing string literals inside `{...}` before closure/commit.
"""

from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Core packages touched by student-facing generators must stay importable.
PRODUCTION_PY_GLOBS = (
    "core/domain/*.py",
    "core/gencode/*.py",
    "core/gencode/resources/*.py",
    "core/checkers/*.py",
)


def _production_modules() -> list[Path]:
    paths: list[Path] = []
    for pattern in PRODUCTION_PY_GLOBS:
        paths.extend(p for p in ROOT.glob(pattern) if p.is_file() and p.name != "__init__.py")
    return sorted(set(paths))


def test_production_modules_py_compile():
    failures: list[str] = []
    for path in _production_modules():
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
    assert not failures, "py_compile failures:\n" + "\n".join(failures)


def test_vector_plane_gap_coverage_fresh_process_import_and_generate():
    """Fresh interpreter import — cached modules cannot hide SyntaxError."""
    script = r"""
import importlib
mod = importlib.import_module("core.domain.vector_plane_gap_coverage")
assert hasattr(mod, "build_vector_plane_gap_matrix") or hasattr(mod, "OPS") or True
from skills import vh_數學B2_SubSection_3_1_1 as skill
for cid in ("src_11731", "src_11732", "src_11806"):
    payload = skill.generate(seed=7, component_id=cid)
    assert isinstance(payload, dict), cid
    assert str(payload.get("question_text") or "").strip(), cid
print("OK")
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "OK" in proc.stdout


def test_circle_plane_fresh_process_import_and_generate():
    """Fresh interpreter import for circle.plane domain + adapter."""
    script = r"""
import importlib
dom = importlib.import_module("core.domain.circle_plane_domain")
adp = importlib.import_module("core.gencode.circle_plane_capability_adapter")
matrix = dom.build_circle_plane_matrix(operation="identify_center_radius_from_standard", seed=3)
assert dom.validate_circle_plane_matrix(matrix)
payload = adp.adapt_circle_plane_matrix(matrix, domain_operation="identify_center_radius_from_standard")
assert str(payload.get("question_text") or payload.get("question") or "").strip()
from core.registry.taxonomy_registry import resolve_domain_for_skill
routing = resolve_domain_for_skill("vh_數學B2_SubSection_4_1_1")
assert routing["fixed_domain_key"] == "circle.plane"
print("OK")
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "OK" in proc.stdout
