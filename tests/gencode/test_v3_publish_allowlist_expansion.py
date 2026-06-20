# -*- coding: utf-8 -*-
"""Step 7B — Production Publish Allowlist 擴充整合測試。

驗證：
- V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS 集中定義且包含兩個技能
- vh_數學B1_HorizontalAndVerticalLineEquations 全鏈路 production publish 成功
- 非 allowlist skill 仍被死鎖
- 無 verified component 仍被拒絕
- 模板 publish button 契約動態化
- 真實 project_root 零污染
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill
from core.gencode.skill_wrapper_compiler import rollback_v3_to_v2_facade
from core.gencode.v3_production_publish_service import (
    ALLOWED_PRODUCTION_SKILL_ID,
    V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS,
    publish_single_v3_skill_to_production,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SANDBOX_ROOT = PROJECT_ROOT / "reports" / "gencode_v3_dryrun"

HV_SKILL_ID = "vh_數學B1_HorizontalAndVerticalLineEquations"
PS_SKILL_ID = "vh_數學B1_PointSlopeForm"
FAKE_SKILL_ID = "vh_fake_NotAllowedSkill"
COMPONENT_ID = "src_1"
V2_LEGACY_CODE = "V2_LEGACY_CODE"

HV_PAYLOAD = {
    "source_kind": "ex_1",
    "presentation_mode": "short_answer",
    "line_type": "horizontal_line",
    "integrity_gate_passed": True,
    "integrity_gate_version": "v1",
}

STUB_METADATA_PY = f'''from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "{COMPONENT_ID}"
'''

STUB_GENERATE_PY = '''from __future__ import annotations

from typing import Any


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return {
        "question_text": "寫出通過 y = 3 的水平線方程式。",
        "answer": "y = 3",
        "correct_answer": "y = 3",
        "component_id": "src_1",
        "metadata": {"component_id": "src_1"},
    }


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> bool:
    return str(user_answer).strip() == str(correct_answer).strip()
'''

STUB_GET_HINT_PY = '''from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return f"水平線提示 step {step}：y = k，斜率為 0。"
'''


def _snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.fixture
def isolated_roots() -> Iterator[tuple[Path, Path]]:
    base = SANDBOX_ROOT / f"pytest_allowlist_expansion_{uuid.uuid4().hex}"
    project_root = base / "project"
    staging_root = base / "staging"
    project_root.mkdir(parents=True, exist_ok=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    try:
        yield project_root, staging_root
    finally:
        shutil.rmtree(base, ignore_errors=True)


@pytest.fixture
def memory_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT NOT NULL
        )
        """
    )
    apply_tracker_ddl(conn)
    try:
        yield conn
    finally:
        conn.close()


def _insert_verified_hv(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO textbook_examples (id, skill_id) VALUES (?, ?)",
        (1, HV_SKILL_ID),
    )
    conn.execute(
        """
        INSERT INTO gencode_component_tracker (
            textbook_example_id, skill_id, component_id, gencode_status, induced_spec_payload
        ) VALUES (?, ?, ?, 'verified', ?)
        """,
        (1, HV_SKILL_ID, COMPONENT_ID, json.dumps(HV_PAYLOAD, ensure_ascii=False)),
    )
    conn.commit()


def _setup_project_root(project_root: Path) -> None:
    (project_root / "skills").mkdir(parents=True, exist_ok=True)
    (project_root / "agent_skills_v3").mkdir(parents=True, exist_ok=True)
    (project_root / "skills" / f"{HV_SKILL_ID}.py").write_text(V2_LEGACY_CODE, encoding="utf-8")


def _seed_staging_stubs(staging_root: Path) -> None:
    component_dir = staging_root / HV_SKILL_ID / "components" / COMPONENT_ID
    component_dir.mkdir(parents=True, exist_ok=True)
    (component_dir / "metadata.py").write_text(STUB_METADATA_PY, encoding="utf-8")
    (component_dir / "generate.py").write_text(STUB_GENERATE_PY, encoding="utf-8")
    (component_dir / "get_hint.py").write_text(STUB_GET_HINT_PY, encoding="utf-8")


def _facade_paths(project_root: Path) -> tuple[Path, Path]:
    facade = project_root / "skills" / f"{HV_SKILL_ID}.py"
    backup = facade.with_suffix(f"{facade.suffix}.bak")
    return facade, backup


# ---------------------------------------------------------------------------
# 任務 C-1：Allowlist 集中定義驗證
# ---------------------------------------------------------------------------


def test_allowlist_contains_point_slope():
    assert PS_SKILL_ID in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS


def test_allowlist_contains_horizontal_vertical():
    assert HV_SKILL_ID in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS


def test_allowlist_does_not_contain_fake_skill():
    assert FAKE_SKILL_ID not in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS


def test_allowed_production_skill_id_backward_compat():
    """舊有 ALLOWED_PRODUCTION_SKILL_ID 向後相容別名保持正確值。"""
    assert ALLOWED_PRODUCTION_SKILL_ID == PS_SKILL_ID


def test_allowlist_is_frozenset():
    """allowlist 必須為 frozenset，防止意外修改。"""
    assert isinstance(V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS, frozenset)


# ---------------------------------------------------------------------------
# 任務 C-2：HV skill 全鏈路 production publish 成功
# ---------------------------------------------------------------------------


def test_hv_skill_full_publish_backup_promote_rollback(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """vh_數學B1_HorizontalAndVerticalLineEquations 完整發布 → 驗證 → 手動回滾。"""
    project_root, staging_root = isolated_roots
    _insert_verified_hv(memory_conn)
    _setup_project_root(project_root)
    _seed_staging_stubs(staging_root)

    real_skills_snapshot = _snapshot(PROJECT_ROOT / "skills")
    real_v3_snapshot = _snapshot(PROJECT_ROOT / "agent_skills_v3")

    result = run_admin_v3_publish_for_skill(
        conn=memory_conn,
        skill_id=HV_SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
        force_publish=True,
    )

    assert result["status"] == "production_published", (
        f"期望 production_published，實際得到：{result['status']}"
    )
    assert result["component_count"] == 1
    assert result["verified_component_count"] == 1

    # .bak 備份確認
    facade_path, backup_path = _facade_paths(project_root)
    assert backup_path.exists(), ".py.bak 備份檔未建立"
    assert backup_path.read_text(encoding="utf-8") == V2_LEGACY_CODE, ".bak 內容不符"

    # V3 Thin Facade 替換確認
    promoted_facade = facade_path.read_text(encoding="utf-8")
    assert promoted_facade != V2_LEGACY_CODE, "舊版 V2 code 未被替換"
    assert "dispatch_generate" in promoted_facade or "runtime_skill_wrapper" in promoted_facade

    # agent_skills_v3 新屋確認
    v3_skill_dir = project_root / "agent_skills_v3" / HV_SKILL_ID
    assert v3_skill_dir.exists(), "agent_skills_v3/vh_HV/ 目錄未建立"
    assert (v3_skill_dir / "__init__.py").exists(), "__init__.py 不存在"
    assert (v3_skill_dir / "components" / COMPONENT_ID / "generate.py").exists()

    # 真實 project_root 零污染
    assert _snapshot(PROJECT_ROOT / "skills") == real_skills_snapshot
    assert _snapshot(PROJECT_ROOT / "agent_skills_v3") == real_v3_snapshot

    # 手動回滾後還原
    rollback_result = rollback_v3_to_v2_facade(
        HV_SKILL_ID,
        str(project_root),
        trusted_project_root=True,
    )
    assert rollback_result["status"] == "rolled_back"
    assert facade_path.read_text(encoding="utf-8") == V2_LEGACY_CODE, "回滾後未還原 V2 code"
    assert not backup_path.exists(), ".bak 在回滾後應已刪除"
    assert not v3_skill_dir.exists(), "V3 skill dir 在回滾後應已刪除"
    assert (project_root / "agent_skills_v3").exists(), "agent_skills_v3 根目錄應保留"


def test_hv_skill_publish_via_publish_single_directly(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """直接透過底層 publish_single_v3_skill_to_production 呼叫，確認 HV skill 被允許。"""
    project_root, staging_root = isolated_roots
    _insert_verified_hv(memory_conn)
    _setup_project_root(project_root)
    _seed_staging_stubs(staging_root)

    result = publish_single_v3_skill_to_production(
        conn=memory_conn,
        skill_id=HV_SKILL_ID,
        project_root=str(project_root),
        staging_root=str(staging_root),
    )
    assert result["status"] == "production_published"


# ---------------------------------------------------------------------------
# 任務 C-3：邊界拒絕驗證
# ---------------------------------------------------------------------------


def test_fake_skill_rejected_when_taxonomy_not_registered(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """非 allowlist skill 仍必須被死鎖。"""
    project_root, staging_root = isolated_roots
    with pytest.raises(ValueError, match="taxonomy_not_registered"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=FAKE_SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=True,
        )


def test_hv_skill_rejected_without_verified_components(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """HV skill 無 verified component 時必須被拒絕。"""
    project_root, staging_root = isolated_roots
    # 不插入任何 verified 組件
    with pytest.raises(ValueError, match="no_textbook_examples"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=HV_SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=True,
        )


def test_force_publish_false_still_rejected(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """force_publish=False 防線對 HV skill 同樣有效。"""
    project_root, staging_root = isolated_roots
    _insert_verified_hv(memory_conn)
    with pytest.raises(ValueError, match="production_publish_requires_force_publish"):
        run_admin_v3_publish_for_skill(
            conn=memory_conn,
            skill_id=HV_SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
            force_publish=False,
        )


def test_direct_publish_rejects_fake_skill_when_taxonomy_not_registered(
    memory_conn: sqlite3.Connection,
    isolated_roots: tuple[Path, Path],
):
    """底層 publish_single_v3_skill_to_production 也必須拒絕非 allowlist skill。"""
    project_root, staging_root = isolated_roots
    with pytest.raises(ValueError, match="taxonomy_not_registered"):
        publish_single_v3_skill_to_production(
            conn=memory_conn,
            skill_id=FAKE_SKILL_ID,
            project_root=str(project_root),
            staging_root=str(staging_root),
        )


# ---------------------------------------------------------------------------
# 任務 C-4：模板 publish button 動態化契約
# ---------------------------------------------------------------------------


def test_template_uses_eligibility_context():
    """模板必須保留既有 V3 repackage 入口，不在老師主畫面要求工程狀態詞。"""
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "repackageSkillV3" in content
    assert "core.admin_run_skill_v3_repackage" in content
    # 確認舊的硬編碼條件已消失
    assert "skill.skill_id == 'vh_數學B1_PointSlopeForm'" not in content, (
        "模板仍有舊的硬編碼 PointSlopeForm 條件，應已改為動態 allowlist 檢查"
    )


def test_template_publish_button_present():
    """模板仍含有正式發布按鈕的關鍵元素。"""
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "admin_run_skill_v3_repackage" in content
    assert "更新到學生端" in content
    assert "repackageSkillV3" in content


def test_template_eligibility_membership_check_removed():
    """模板發布按鈕條件必須含 'in' 語義（membership check）。"""
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "in (v3_publish_allowed_skill_ids or [])" not in content, (
        "模板應使用 'skill.skill_id in (v3_publish_allowed_skill_ids or [])' 語義"
    )


def test_template_verified_component_condition_preserved():
    """verified component 條件必須保留。"""
    content = (PROJECT_ROOT / "templates" / "admin_skills.html").read_text(encoding="utf-8")
    assert "gencode.get('publish_ready')" in content


def test_admin_route_does_not_import_allowlist():
    """admin.py 的 admin_skills route 必須傳入 v3_publish_allowed_skill_ids。"""
    content = (PROJECT_ROOT / "core" / "routes" / "admin.py").read_text(encoding="utf-8")
    assert "v3_publish_allowed_skill_ids" not in content
    assert "V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS" not in content
