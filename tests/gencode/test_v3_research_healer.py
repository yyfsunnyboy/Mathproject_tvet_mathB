# -*- coding: utf-8 -*-
"""GenCode V3 Research Healer: provenance, V3 eligibility, adapter guards, modes, telemetry."""

from __future__ import annotations

import ast
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from core.gencode.research_healer import adapter as rh
from core.gencode.research_healer.adapter import (
    MODE_OFF,
    MODE_REPAIR,
    MODE_SHADOW,
    STATUS_ABSTAINED,
    STATUS_REJECTED,
    STATUS_REPAIRED,
    STATUS_UNCHANGED,
    extract_unique_python_fence,
    heal_ai_python_source,
    heal_coder_files,
    record_coder_gate,
    resolve_healer_mode,
)
from core.gencode.research_healer.eligibility import (
    PREFLIGHT_FENCE_RULE_ID,
    RESEARCH_RULE_IDS,
    RULE_ELIGIBILITY,
    STATUS_DISABLED,
    STATUS_ENABLED,
    V3_PRODUCTION_ALLOWLIST,
)
from core.gencode.research_healer.provenance import PORTED_FILES, verify_vendored_files
from core.gencode.research_healer.structure import grouping_alternatives, structural_diff
from core.gencode.research_healer.vendor.runner import EXPERIMENTAL_RULE_REGISTRY, RULE_REGISTRY
from core.gencode.schema.gencode_v3_healer_telemetry_inspection import TABLE_NAME

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FENCE = "`" * 3
CODE = "def generate(seed=0):\n    x = (1 + 2) * 3\n    return {'answer': x}\n"
FENCED = f"Here is the module:\n{FENCE}python\n{CODE}{FENCE}\nIt returns 9.\n"
AMBIGUOUS_PAREN = "def generate():\n    x = (1 + 2 * 3\n    return x\n"
UNIQUE_PAREN = "def generate():\n    y = f(x\n    return y\n"
PAREN_RULE = "L1_CLOSE_UNBALANCED_PARENTHESIS"


def _heal(source: str, **kwargs):
    return heal_ai_python_source(source, skill_id="skill_x", component_id="coder:m.py", **kwargs)


# --- provenance & eligibility ---------------------------------------------------


def test_vendored_sources_match_recorded_research_hashes():
    report = verify_vendored_files()
    assert report["ok"] is True, report
    assert len(PORTED_FILES) == 9
    for meta in PORTED_FILES.values():
        assert len(meta["git_blob"]) == 40 and len(meta["source_sha256_lf"]) == 64


def test_v3_production_allowlist_is_empty_and_every_research_rule_disabled():
    assert V3_PRODUCTION_ALLOWLIST == ()
    by_id = {m.rule_id: m for m in RULE_ELIGIBILITY}
    assert by_id[PREFLIGHT_FENCE_RULE_ID].v3_status == STATUS_ENABLED
    registered = set(RULE_REGISTRY) | set(EXPERIMENTAL_RULE_REGISTRY)
    assert set(RESEARCH_RULE_IDS) == registered
    for rule_id in RESEARCH_RULE_IDS:
        assert by_id[rule_id].v3_status == STATUS_DISABLED
        assert by_id[rule_id].reason and by_id[rule_id].v3_risks


def test_research_healer_never_imports_legacy_healers():
    code = (
        "import sys, core.gencode.research_healer, core.gencode.services.v3_capability_ai_fill_service\n"
        "bad = sorted(m for m in sys.modules if m.startswith('core.healers') or m in "
        "('core.code_generator', 'core.gencode.v3_healer_adapter', 'core.gencode.v3_healer_rules'))\n"
        "print(bad)\n"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"
    for path in (PROJECT_ROOT / "core" / "gencode" / "research_healer").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not node.module.startswith(("core.healers", "agent_tools", "core.code_generator")), path


def test_no_v3_module_imports_legacy_or_retired_healers():
    banned = ("core.healers", "core.code_generator", "core.engine.scaler", "core.gencode.v3_healer_adapter")
    offenders = []
    for path in (PROJECT_ROOT / "core" / "gencode").rglob("*.py"):
        if path.name in ("v3_healer_adapter.py", "v3_healer_rules.py", "v3_healer_telemetry.py"):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            modules = []
            if isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            elif isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            offenders += [f"{path.name}:{m}" for m in modules if m.startswith(banned)]
    assert offenders == []


def _runtime_python_files():
    roots = [PROJECT_ROOT / "core", PROJECT_ROOT / "scripts"]
    files = [p for root in roots for p in root.rglob("*.py")]
    return files + [PROJECT_ROOT / name for name in ("app.py", "models.py", "config.py") if (PROJECT_ROOT / name).is_file()]


def test_repair_mode_has_no_entry_point_that_bypasses_the_allowlist():
    retired = ("core.gencode.v3_healer_adapter", "core.gencode.v3_healer_rules")
    entry_calls = ("heal_ai_python_source", "heal_coder_files", "run_research_healer", "run_finals_rebuild_healer")
    package = PROJECT_ROOT / "core" / "gencode" / "research_healer"
    retired_importers, allowlist_overrides, coder_callers = [], [], []
    for path in _runtime_python_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if package in path.parents or path.name in ("v3_healer_adapter.py", "v3_healer_rules.py"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except SyntaxError:
            continue  # cannot be imported at runtime either
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(retired):
                retired_importers.append(rel)
            if isinstance(node, ast.Call):
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if name in entry_calls and any(k.arg == "allowlist" for k in node.keywords):
                    allowlist_overrides.append(rel)
                if name == "heal_coder_files":
                    coder_callers.append(rel)
    assert retired_importers == ["core/gencode/v3_healer_telemetry.py"]
    assert allowlist_overrides == []
    assert coder_callers == ["core/gencode/services/v3_capability_ai_fill_service.py"]


def test_dashboard_reports_active_mode_and_allowlist(monkeypatch):
    from core.gencode.v3_healer_telemetry import active_healer_config

    monkeypatch.setenv("GENCODE_V3_HEALER_MODE", "repair")
    config = active_healer_config()
    assert config["mode"] == MODE_REPAIR
    assert config["enabled_rules"] == [PREFLIGHT_FENCE_RULE_ID]
    assert config["v3_production_allowlist"] == []
    monkeypatch.delenv("GENCODE_V3_HEALER_MODE")
    assert active_healer_config()["mode"] == MODE_OFF


def test_mode_resolution_defaults_to_off():
    assert resolve_healer_mode({}) == MODE_OFF
    assert resolve_healer_mode({"GENCODE_V3_HEALER_MODE": "bogus"}) == MODE_OFF
    assert resolve_healer_mode({"GENCODE_V3_HEALER_MODE": " Repair "}) == MODE_REPAIR


# --- adapter decisions ------------------------------------------------------------


def test_parsing_source_is_unchanged_and_runner_is_noop():
    result = _heal(CODE)
    assert result.status == STATUS_UNCHANGED and result.final_code == CODE
    assert result.research_run["final_status"] == "no_op"
    assert result.real_model_calls == 0 and result.research_run["real_model_calls"] == 0


def test_unique_fence_is_extracted_verbatim_with_certificate():
    result = _heal(FENCED)
    assert result.status == STATUS_REPAIRED
    assert result.final_code == CODE and CODE in FENCED
    assert result.semantic_preservation_proven is True
    assert [r["rule_id"] for r in result.rules_applied] == [PREFLIGHT_FENCE_RULE_ID]
    assert result.certificates[0]["proof"] == "output_is_verbatim_substring_of_ai_response"
    assert result.certificate_status == "verified"
    assert result.validation["structure"]["changed"] is False


@pytest.mark.parametrize(
    "source,reason",
    [
        (f"{FENCE}python\n{CODE}", "unterminated_markdown_fence"),
        (f"{FENCE}python\n{CODE}{FENCE}\n{FENCE}python\n{CODE}{FENCE}\n", "multiple_markdown_fences"),
        (f"{FENCE}json\n{{}}\n{FENCE}\n", "non_python_fence"),
        (f"{FENCE}python\n\n{FENCE}\n", "empty_fenced_block"),
        (f"x = 1\n{FENCE}python\n{CODE}{FENCE}\n", "code_like_text_outside_fence"),
        (CODE, "no_markdown_fence"),
    ],
)
def test_fence_extraction_abstains_on_non_unique_shapes(source, reason):
    inner, got, _ = extract_unique_python_fence(source)
    assert inner is None and got == reason


def test_fence_with_residual_syntax_error_abstains_with_original():
    source = f"{FENCE}python\n{AMBIGUOUS_PAREN}{FENCE}\n"
    result = _heal(source)
    assert result.status == STATUS_ABSTAINED and result.final_code == source
    assert result.reason == "residual_syntax_error_after_preflight"


def test_ambiguous_paren_close_is_probe_only_and_abstains():
    result = _heal(AMBIGUOUS_PAREN)
    assert result.status == STATUS_ABSTAINED and result.final_code == AMBIGUOUS_PAREN
    probe = {p["rule_id"]: p for p in result.probe}
    assert probe[PAREN_RULE]["would_change"] is True
    assert probe[PAREN_RULE]["grouping_alternatives"] == 2
    decisions = {a["rule_id"]: a["decision"] for a in result.attempts}
    assert all(decisions[r] == "DISABLED" for r in RESEARCH_RULE_IDS)
    assert result.research_run["stop_reasons"] == ["allowlist_empty"]


def test_allowlisting_a_research_rule_still_rejects_ambiguous_grouping():
    result = _heal(AMBIGUOUS_PAREN, allowlist=(PAREN_RULE,))
    assert result.status == STATUS_REJECTED and result.final_code == AMBIGUOUS_PAREN
    assert result.reason == "research_change_rejected:grouping_ambiguous"


def test_allowlisted_unique_delimiter_insert_is_not_claimed_semantic_safe():
    result = _heal(UNIQUE_PAREN, allowlist=(PAREN_RULE,))
    assert result.status == STATUS_REPAIRED
    assert result.final_code == "def generate():\n    y = f(x)\n    return y\n"
    assert result.semantic_preservation_proven is False


@pytest.mark.parametrize(
    "before,after,key",
    [
        ("x = a + b\n", "x = a - b\n", "math_operator_changed"),
        ("if a:\n    x = 1\n", "x = 1\n", "control_flow_changed"),
        ("def f():\n    return 1\n", "def g():\n    return 1\n", "function_names_changed"),
        ("x = 2\n", "x = 3\n", "constants_changed"),
        ("x = 1\ny = x\n", "x = 1\n", "code_deleted"),
    ],
)
def test_guard_rejects_semantic_edits(before, after, key):
    ok, reason, _ = rh._guard_research_change(before, after)
    assert ok is False and reason == f"edit_scope_violation:{key}"
    assert structural_diff(before, after)[key] is True


def test_grouping_alternatives_counts_distinct_asts():
    assert grouping_alternatives("x = (1 + 2 * 3\n", "x = (1 + 2 * 3)\n") == 2
    assert grouping_alternatives("y = f(x\n", "y = f(x)\n") == 1


def test_unsafe_construct_in_extracted_code_is_rejected():
    source = f"{FENCE}python\nimport os\nos.remove('x')\n{FENCE}\n"
    result = _heal(source)
    assert result.status == STATUS_REJECTED and result.final_code == source
    assert result.reason.startswith("unsafe_construct:")


def test_empty_source_abstains():
    assert _heal("   ").status == STATUS_ABSTAINED


def test_runner_exception_fails_closed(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("runner down")

    monkeypatch.setattr(rh, "run_research_healer", _boom)
    result = _heal(AMBIGUOUS_PAREN)
    assert result.status == STATUS_ABSTAINED and result.final_code == AMBIGUOUS_PAREN
    assert result.research_run["final_status"] == "error"


# --- coder file integration --------------------------------------------------------


def _files():
    return [
        {"path": "mutations/k.yaml", "content": f"{FENCE}python\nnot python\n{FENCE}\n"},
        {"path": "pkg/fenced.py", "content": FENCED},
        {"path": "pkg/ok.py", "content": CODE},
        {"path": "pkg/broken.py", "content": AMBIGUOUS_PAREN},
    ]


def test_off_mode_returns_identical_files_and_writes_nothing(tmp_path):
    files = _files()
    out, results = heal_coder_files(files, skill_id="s", job_id="j", job_dir=tmp_path, round_no=1, mode=MODE_OFF)
    assert out is files and results == []
    assert not any(tmp_path.iterdir())


def test_shadow_mode_records_evidence_and_keeps_ai_output(tmp_path):
    conn = sqlite3.connect(":memory:")
    files = _files()
    out, results = heal_coder_files(
        files, skill_id="s", job_id="j", job_dir=tmp_path, round_no=1, mode=MODE_SHADOW, conn=conn
    )
    assert out == files
    assert [r.status for r in results] == [STATUS_REPAIRED, STATUS_UNCHANGED, STATUS_ABSTAINED]
    assert not any(r.applied_to_pipeline for r in results)
    lines = (tmp_path / rh.EVIDENCE_FILE_NAME).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    rows = conn.execute(f"SELECT event_type, outcome, mode FROM {TABLE_NAME} WHERE event_type='attempt'").fetchall()
    assert sorted(rows) == [("attempt", "ABSTAINED", "shadow"), ("attempt", "REPAIRED", "shadow")]
    blob = json.dumps(conn.execute(f"SELECT * FROM {TABLE_NAME}").fetchall(), ensure_ascii=False)
    for forbidden in ("def generate", "Here is the module", "(1 + 2) * 3", "'answer'"):
        assert forbidden not in blob
    assert "def generate" not in "".join(lines)
    conn.close()


def test_repair_mode_hands_over_only_certified_fence_extraction(tmp_path):
    conn = sqlite3.connect(":memory:")
    files = _files()
    out, results = heal_coder_files(
        files, skill_id="s", job_id="j", job_dir=tmp_path, round_no=2, mode=MODE_REPAIR, conn=conn
    )
    by_path = {f["path"]: f["content"] for f in out}
    assert by_path["pkg/fenced.py"] == CODE
    assert by_path["pkg/broken.py"] == AMBIGUOUS_PAREN
    assert by_path["pkg/ok.py"] == CODE
    assert by_path["mutations/k.yaml"] == files[0]["content"]
    assert [r.applied_to_pipeline for r in results] == [True, False, False]

    record_coder_gate(conn, results, passed=False, blockers=["coverage_matrix_missing"])
    assert results[0].applied_to_pipeline is False
    assert results[0].post_repair_gates.startswith("failed:official_compatibility")
    gate = conn.execute(f"SELECT outcome, gate_stage FROM {TABLE_NAME} WHERE event_type='gate'").fetchall()
    assert gate == [("failed", "official_compatibility")]
    conn.close()


def test_adapter_internal_error_keeps_original_file(tmp_path, monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("bug")

    monkeypatch.setattr(rh, "heal_ai_python_source", _boom)
    files = _files()
    out, results = heal_coder_files(files, skill_id="s", job_id="j", job_dir=tmp_path, round_no=1, mode=MODE_REPAIR)
    assert out == files
    assert all(r.status == STATUS_REJECTED and not r.applied_to_pipeline for r in results)
