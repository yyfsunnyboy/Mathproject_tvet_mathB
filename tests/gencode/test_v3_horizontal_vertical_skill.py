# -*- coding: utf-8 -*-
"""Step 7A — V3 沙盒全鏈路整合測試：vh_數學B1_HorizontalAndVerticalLineEquations。

範圍：Taxonomy 白名單、Registry 映射、dryrun → smoke → verified 生命週期、
      發布引擎死鎖保全。生產目錄 100% 零污染。
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import (
    mark_admin_v3_example_verified,
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
    run_admin_v3_smoke_for_example,
)
from core.registry.taxonomy_registry import resolve_domain_for_skill

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"
TAXONOMY_PATH = PROJECT_ROOT / "configs" / "gencode_taxonomy" / "k12_component_taxonomy.yaml"

TARGET_SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"
BENCHMARK_SKILL_ID = "vh_數學B1_PointSlopeForm"
COMPONENT_ID = "src_1"


def _snapshot_paths(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL,
            problem_type_id TEXT,
            line_type TEXT,
            problem_text TEXT
        )
        """
    )
    apply_tracker_ddl(conn)
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id, problem_type_id, line_type, problem_text) VALUES (?, ?, ?, ?, ?)",
        (1, TARGET_SKILL_ID, "vertical_line", "vertical_line", "垂直線"),
    )
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sandbox_root() -> Iterator[Path]:
    base = SANDBOX_ROOT / f"pytest_hv_skill_{uuid.uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ---------------------------------------------------------------------------
# 任務 D-1：行政解析與邊界檢驗
# ---------------------------------------------------------------------------


def test_taxonomy_yaml_contains_new_skill():
    """YAML mvp_scope 必須明確列出新技能。"""
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    v1_scope: list[str] = data["mvp_scope"]["v1"]
    assert TARGET_SKILL_ID in v1_scope, (
        f"YAML 中找不到 {TARGET_SKILL_ID}；請確認 configs/gencode_taxonomy/k12_component_taxonomy.yaml"
    )


def test_taxonomy_yaml_still_contains_benchmark_skill():
    """確保 PointSlopeForm 原有白名單不受本次變更影響。"""
    data = yaml.safe_load(TAXONOMY_PATH.read_text(encoding="utf-8"))
    v1_scope: list[str] = data["mvp_scope"]["v1"]
    assert BENCHMARK_SKILL_ID in v1_scope


def test_registry_resolves_to_line_equation_domain():
    """Registry 必須將新 skill 映射到 line_equation_domain 模組。"""
    entry = resolve_domain_for_skill(TARGET_SKILL_ID)
    assert entry["domain_module"] == "core.domain.coordinate_geometry.line_equation_domain"
    assert entry["entrypoint"] == "build_line_equation_matrix"


def test_registry_allowed_types_contains_horizontal_and_vertical():
    """allowed_types 必須精確包含 horizontal_line 與 vertical_line。"""
    entry = resolve_domain_for_skill(TARGET_SKILL_ID)
    allowed = list(entry.get("allowed_types", []))
    assert "horizontal_line" in allowed
    assert "vertical_line" in allowed


def test_registry_allowed_types_excludes_forbidden_types():
    """allowed_types 絕對不得含 point_slope 或 two_points。"""
    entry = resolve_domain_for_skill(TARGET_SKILL_ID)
    allowed = list(entry.get("allowed_types", []))
    assert "point_slope" not in allowed, "point_slope 不得出現在水平/鉛直線技能的 allowed_types 中"
    assert "two_points" not in allowed, "two_points 不得出現在水平/鉛直線技能的 allowed_types 中"


def test_registry_benchmark_skill_unchanged():
    """PointSlopeForm registry entry 必須完整保存，不受本次增量影響。"""
    entry = resolve_domain_for_skill(BENCHMARK_SKILL_ID)
    assert entry["domain_module"] == "core.domain.coordinate_geometry.line_equation_domain"
    assert entry["entrypoint"] == "build_line_equation_matrix"
    assert entry["default_curriculum_profile"] == "vocational_high_b"


# ---------------------------------------------------------------------------
# 任務 D-2：全自動沙盒生命週期前推（dryrun → smoke → verified）
# ---------------------------------------------------------------------------


def test_full_lifecycle_dryrun_smoke_verified(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    """dryrun → smoke → verified 三步驟全鏈路驗收，生產目錄零污染。"""
    production_skills_snapshot = _snapshot_paths(PROJECT_ROOT / "skills")
    production_v3_snapshot = _snapshot_paths(PROJECT_ROOT / "agent_skills_v3")

    # --- 步驟 1：dryrun ---
    dryrun_result = run_admin_v3_dryrun_for_example(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=TARGET_SKILL_ID,
        dryrun_base_dir=str(sandbox_root),
        seed=42,
    )

    assert dryrun_result["status"] == "verified"
    assert dryrun_result["component_id"] == COMPONENT_ID

    # 影子表同步確認
    row = memory_conn.execute(
        "SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row is not None
    assert row["gencode_status"] == "verified"

    # 沙盒三檔與 manifest 存在確認
    component_dir = sandbox_root / TARGET_SKILL_ID / "components" / COMPONENT_ID
    assert (component_dir / "metadata.py").is_file(), "metadata.py 未生成"
    assert (component_dir / "generate.py").is_file(), "generate.py 未生成"
    assert (component_dir / "get_hint.py").is_file(), "get_hint.py 未生成"
    assert (sandbox_root / TARGET_SKILL_ID / "component_manifest.json").is_file(), (
        "component_manifest.json 未生成"
    )

    # 生產目錄零污染
    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot

    # Reset tracker status to 'draft_written' to satisfy smoke test preconditions
    memory_conn.execute(
        "UPDATE gencode_component_tracker SET gencode_status = 'draft_written' WHERE textbook_example_id = 1"
    )
    memory_conn.commit()

    # --- 步驟 2：smoke ---
    smoke_result = run_admin_v3_smoke_for_example(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=TARGET_SKILL_ID,
        dryrun_base_dir=str(sandbox_root),
        seed=42,
    )

    assert smoke_result["status"] == "smoke_passed"

    row = memory_conn.execute(
        "SELECT gencode_status, gencode_error_log FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "smoke_passed"
    assert row["gencode_error_log"] is None

    # 生產目錄仍然零污染
    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot

    # --- 步驟 3：verified ---
    verify_result = mark_admin_v3_example_verified(
        conn=memory_conn,
        textbook_example_id=1,
        skill_id=TARGET_SKILL_ID,
    )

    assert verify_result["status"] == "verified"

    row = memory_conn.execute(
        "SELECT gencode_status FROM gencode_component_tracker WHERE textbook_example_id = 1"
    ).fetchone()
    assert row["gencode_status"] == "verified"

    # 生產目錄最終零污染確認
    assert _snapshot_paths(PROJECT_ROOT / "skills") == production_skills_snapshot
    assert _snapshot_paths(PROJECT_ROOT / "agent_skills_v3") == production_v3_snapshot


# ---------------------------------------------------------------------------
# 任務 D-3：Domain 層水平/鉛直線直接算子驗證
# ---------------------------------------------------------------------------


def test_domain_generates_horizontal_line():
    """直接呼叫 domain 算子確認水平線正確輸出 y = k 形式。"""
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )

    matrix = build_line_equation_matrix(
        seed=7,
        line_type="horizontal_line",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
    )
    canonical = str(matrix["answer"]["canonical_form"])
    assert canonical.startswith("y ="), f"水平線應以 'y =' 開頭，得到：{canonical!r}"
    assert matrix["validation_facts"]["is_horizontal"] is True
    assert matrix["validation_facts"]["is_vertical"] is False


def test_domain_generates_vertical_line():
    """直接呼叫 domain 算子確認鉛直線正確輸出 x = k 形式。"""
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )

    matrix = build_line_equation_matrix(
        seed=13,
        line_type="vertical_line",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
    )
    canonical = str(matrix["answer"]["canonical_form"])
    assert canonical.startswith("x ="), f"鉛直線應以 'x =' 開頭，得到：{canonical!r}"
    assert matrix["validation_facts"]["is_vertical"] is True
    assert matrix["validation_facts"]["is_horizontal"] is False


def test_adapter_converts_hv_matrix_to_valid_payload():
    """domain_matrix_adapter 能正確轉換水平/鉛直矩陣為題目 payload。"""
    from core.domain.coordinate_geometry.line_equation_domain import (
        build_line_equation_matrix,
    )
    from core.gencode.domain_matrix_adapter import (
        convert_line_equation_matrix_to_question_payload,
    )

    for line_type in ("horizontal_line", "vertical_line"):
        matrix = build_line_equation_matrix(
            seed=42,
            line_type=line_type,
            curriculum_profile="vocational_high_b",
            difficulty_profile="easy",
        )
        payload = convert_line_equation_matrix_to_question_payload(matrix)
        assert isinstance(payload["question_text"], str) and payload["question_text"]
        assert isinstance(payload["correct_answer"], str) and payload["correct_answer"]
        assert payload["answer"] == payload["correct_answer"]
        assert payload["choices"] == []
        assert payload["metadata"]["presentation_mode"] == "short_answer"

        choice_payload = convert_line_equation_matrix_to_question_payload(
            matrix,
            presentation_mode="single_choice",
            answer_type="single_choice",
        )
        assert isinstance(choice_payload["choices"], list) and len(choice_payload["choices"]) >= 2
        assert choice_payload["answer"] == choice_payload["correct_answer"]
        assert isinstance(choice_payload["metadata"], dict)


# ---------------------------------------------------------------------------
# 任務 D-4：發布引擎死鎖最高保全
# ---------------------------------------------------------------------------


def test_publish_dead_locked_for_non_allowlist_skill_even_when_verified(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    """非 allowlist skill 即使有 verified 組件，發布引擎也必須死鎖。
    Note: Step 7B 後 vh_數學B1_HorizontalAndVerticalLineEquations 已納入 allowlist，
    本測試改用真正的非 allowlist 假 skill 驗證死鎖邏輯。
    """
    non_allowlist_skill = "vh_fake_NotInAllowlist"
    memory_conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status
        ) VALUES (?, ?, ?, 'verified')
        """,
        (1, non_allowlist_skill, COMPONENT_ID),
    )
    memory_conn.commit()

    with pytest.raises(ValueError, match="taxonomy_not_registered"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=non_allowlist_skill,
            project_root=str(sandbox_root / "project"),
            staging_root=str(sandbox_root / "staging"),
            force_publish=True,
        )


def test_publish_whitelist_still_allows_only_benchmark(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    """驗證 PointSlopeForm 仍受白名單保護（force_publish=False 死鎖）。"""
    with pytest.raises(ValueError, match="production_publish_requires_force_publish"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=BENCHMARK_SKILL_ID,
            project_root=str(sandbox_root / "project"),
            staging_root=str(sandbox_root / "staging"),
            force_publish=False,
        )


# ---------------------------------------------------------------------------
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=non_allowlist_skill,
            project_root=str(sandbox_root / "project"),
            staging_root=str(sandbox_root / "staging"),
            force_publish=True,
        )


def test_publish_whitelist_still_allows_only_benchmark(
    memory_conn: sqlite3.Connection,
    sandbox_root: Path,
):
    """驗證 PointSlopeForm 仍受白名單保護（force_publish=False 死鎖）。"""
    with pytest.raises(ValueError, match="production_publish_requires_force_publish"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=BENCHMARK_SKILL_ID,
            project_root=str(sandbox_root / "project"),
            staging_root=str(sandbox_root / "staging"),
            force_publish=False,
        )


# ---------------------------------------------------------------------------
# 任務 D-5：模板 HTML 契約
# ---------------------------------------------------------------------------


def test_template_publish_button_eligibility_contract():
    """admin_skills.html 的發布按鈕必須使用動態 allowlist context 判斷。"""
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "admin_run_skill_v3_repackage" in content
    assert "gencode.get" in content
    assert "repackageSkillV3" in content
