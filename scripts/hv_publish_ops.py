# -*- coding: utf-8 -*-
"""受控維運腳本：vh_數學B1_HorizontalAndVerticalLineEquations Production Publish。

用法：
  python scripts/hv_publish_ops.py check      # 發布前檢查
  python scripts/hv_publish_ops.py full        # 全流程：DDL + dryrun + smoke + verify + publish
  python scripts/hv_publish_ops.py verify      # 發布後驗證
  python scripts/hv_publish_ops.py rollback    # 失敗時回滾
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import py_compile
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
HV_SKILL = "vh_數學B1_HorizontalAndVerticalLineEquations"
STAGING_ROOT = str(
    PROJECT_ROOT / "reports" / "gencode_v3_publish_staging" / "hv_line_publish"
)
DRYRUN_DIR = STAGING_ROOT  # publish service 從 staging_path/{skill_id}/components/ 讀取


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:24]


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_tracker_ddl(conn: sqlite3.Connection) -> None:
    """建立 gencode_component_tracker 影子表（若不存在）。"""
    ddl_path = PROJECT_ROOT / "core" / "gencode" / "schema" / "gencode_component_tracker.sql"
    ddl = ddl_path.read_text(encoding="utf-8")
    conn.executescript(ddl)
    conn.commit()
    print("  [DDL] gencode_component_tracker 已確認建立 ✅")


# ---------------------------------------------------------------------------
def cmd_check() -> None:
    print("=" * 60)
    print("任務 A：發布前檢查")
    print("=" * 60)

    conn = _get_conn()
    try:
        _ensure_tracker_ddl(conn)

        # 查詢 tracker
        rows = conn.execute(
            """SELECT textbook_example_id, component_id, gencode_status,
                      induced_spec_payload, updated_at
               FROM gencode_component_tracker
               WHERE skill_id = ?
               ORDER BY textbook_example_id""",
            (HV_SKILL,),
        ).fetchall()
        print(f"\n[1] tracker rows for {HV_SKILL}: {len(rows)}")
        verified_count = 0
        for r in rows:
            status = r["gencode_status"]
            mark = "✅" if status == "verified" else "  "
            payload_raw = r["induced_spec_payload"] or ""
            line_type = "-"
            try:
                line_type = json.loads(payload_raw).get("line_type", "-")
            except Exception:
                pass
            print(f"  {mark} id={r['textbook_example_id']} cid={r['component_id']} "
                  f"status={status} line_type={line_type} updated={r['updated_at']}")
            if status == "verified":
                verified_count += 1
        print(f"  verified 數量: {verified_count}")

        # Allowlist
        from core.gencode.v3_production_publish_service import V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS
        print(f"\n[2] allowlist: {sorted(V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS)}")
        assert HV_SKILL in V3_PRODUCTION_PUBLISH_ALLOWED_SKILLS

        # Snapshot
        facade = PROJECT_ROOT / "skills" / f"{HV_SKILL}.py"
        v3dir = PROJECT_ROOT / "agent_skills_v3" / HV_SKILL
        print(f"\n[3] project_root: {PROJECT_ROOT}")
        print(f"[5] skills/{HV_SKILL}.py exists: {facade.exists()}")
        if facade.exists():
            print(f"    hash[:24]: {_sha256(facade)}, size: {facade.stat().st_size}b")
        print(f"[5] agent_skills_v3/{HV_SKILL}/ exists: {v3dir.exists()}")
        print(f"[4] staging_root: {STAGING_ROOT}")

    finally:
        conn.close()

    print("\n[A] 發布前檢查完成 ✅")


# ---------------------------------------------------------------------------
def cmd_dryrun(conn: sqlite3.Connection) -> None:
    """執行 skill-level batch dryrun（全部 textbook_examples）。"""
    print("\n--- Step 1: batch dryrun ---")
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill

    result = run_admin_v3_dryrun_for_skill(
        conn=conn,
        skill_id=HV_SKILL,
        dryrun_base_dir=DRYRUN_DIR,
        seed=42,
    )
    print(f"  total_examples: {result.get('total_examples')}")
    print(f"  success_count: {result.get('success_count')}")
    print(f"  failed_count: {result.get('failed_count')}")
    if not result.get("success"):
        print("  *** batch dryrun 有失敗題目 ***")
        sys.exit(11)


def cmd_smoke(conn: sqlite3.Connection) -> None:
    """執行 smoke test（對尚未 smoke 的題目）。"""
    print("\n--- Step 2: batch smoke ---")
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill

    result = run_admin_v3_dryrun_for_skill(
        conn=conn,
        skill_id=HV_SKILL,
        dryrun_base_dir=DRYRUN_DIR,
        smoke=True,
        seed=42,
    )
    print(f"  success_count: {result.get('success_count')}")
    print(f"  failed_count: {result.get('failed_count')}")
    if not result.get("success"):
        sys.exit(12)


def cmd_verify_tracker(conn: sqlite3.Connection) -> None:
    """標記 verified（dryrun+smoke+verify）。"""
    print("\n--- Step 3: batch verify ---")
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_skill

    result = run_admin_v3_dryrun_for_skill(
        conn=conn,
        skill_id=HV_SKILL,
        dryrun_base_dir=DRYRUN_DIR,
        smoke=True,
        verify=True,
        seed=42,
    )
    coverage = result.get("coverage") or {}
    print(f"  verified: {coverage.get('verified_count')}/{coverage.get('total_examples')}")
    if not result.get("success"):
        sys.exit(13)


def cmd_do_publish(conn: sqlite3.Connection) -> dict:
    """執行正式發布。"""
    print("\n--- Step 4: production publish ---")
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_publish_for_skill

    # 建立 staging 目錄
    Path(STAGING_ROOT).mkdir(parents=True, exist_ok=True)

    report = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=HV_SKILL,
        project_root=str(PROJECT_ROOT),
        staging_root=STAGING_ROOT,
        force_publish=True,
    )
    print(f"  publish status: {report['status']}")
    print(f"  component_count: {report.get('component_count')}")
    print(f"  smoke_status: {report.get('smoke_status')}")
    print(f"  staging_smoke_status: {report.get('staging_smoke_status')}")
    print(f"  production_smoke_status: {report.get('production_smoke_status')}")
    print(f"  timestamp: {report.get('timestamp')}")
    return report


def cmd_full() -> None:
    print("=" * 60)
    print("任務 B：全流程執行（DDL + dryrun + smoke + verify + publish）")
    print("=" * 60)

    conn = _get_conn()
    try:
        _ensure_tracker_ddl(conn)

        # 重新於 STAGING_ROOT 執行 batch dryrun → smoke → verified
        conn.execute("DELETE FROM gencode_component_tracker WHERE skill_id = ?", (HV_SKILL,))
        conn.commit()

        cmd_dryrun(conn)
        cmd_smoke(conn)
        cmd_verify_tracker(conn)

        report = cmd_do_publish(conn)

        if report["status"] == "production_published":
            print("\n[B] 正式發布成功 ✅")
        elif "rolled_back" in str(report["status"]):
            print(f"\n[B] 自動回滾: {report.get('production_smoke_error')}")
            sys.exit(20)
        else:
            print(f"\n[B] 未預期狀態: {report['status']}")
            sys.exit(21)

    except ValueError as exc:
        print(f"[ERROR] ValueError: {exc}")
        conn.close()
        sys.exit(22)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        conn.close()
        sys.exit(23)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
def cmd_verify() -> None:
    print("=" * 60)
    print("任務 C：發布後驗證")
    print("=" * 60)

    facade = PROJECT_ROOT / "skills" / f"{HV_SKILL}.py"
    backup = facade.with_suffix(f"{facade.suffix}.bak")
    v3dir = PROJECT_ROOT / "agent_skills_v3" / HV_SKILL
    v3init = v3dir / "__init__.py"

    print(f"\n[C-1] 檔案存在性:")
    print(f"  facade:     {facade.exists()}")
    print(f"  backup:     {backup.exists()}")
    print(f"  v3 dir:     {v3dir.exists()}")
    print(f"  __init__.py:{v3init.exists()}")

    assert facade.exists(), "Thin Facade 不存在"
    assert v3dir.exists(), "agent_skills_v3 dir 不存在"
    assert v3init.exists(), "__init__.py 不存在"

    print(f"\n[C-2] Thin Facade 內容特徵:")
    text = facade.read_text(encoding="utf-8")
    has_dispatch = "dispatch_generate" in text
    has_wrapper = "runtime_skill_wrapper" in text
    print(f"  dispatch_generate: {has_dispatch}")
    print(f"  runtime_skill_wrapper: {has_wrapper}")
    assert has_dispatch or has_wrapper

    print(f"\n[C-3] py_compile:")
    py_compile.compile(str(facade), doraise=True)
    print(f"  facade: PASS ✅")
    py_compile.compile(str(v3init), doraise=True)
    print(f"  __init__.py: PASS ✅")

    print(f"\n[C-4] runtime smoke:")
    uid = hashlib.sha256(str(facade).encode()).hexdigest()[:8]
    spec = importlib.util.spec_from_file_location(f"_hv_smoke_{uid}", facade)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    payload = mod.generate(seed=42)
    assert isinstance(payload, dict)
    correct = payload.get("correct_answer", "?")
    print(f"  generate(seed=42): PASS ✅  correct_answer={str(correct)[:50]!r}")

    mod.check("x = 5", "x = 5", question_payload=payload)
    print("  check(): PASS ✅")

    hint = mod.get_hint(1, question_payload=payload)
    assert isinstance(hint, str)
    print(f"  get_hint(1): PASS ✅  hint[:50]={hint[:50]!r}")

    print("\n[C] 發布後驗證全部通過 ✅")


# ---------------------------------------------------------------------------
def cmd_rollback() -> None:
    print("=" * 60)
    print("任務 D：回滾")
    print("=" * 60)

    from core.gencode.skill_wrapper_compiler import rollback_v3_to_v2_facade

    result = rollback_v3_to_v2_facade(HV_SKILL, str(PROJECT_ROOT), trusted_project_root=True)
    print(f"rollback status: {result['status']}")
    print(f"facade_restored: {result.get('facade_restored')}")
    print(f"backup_removed:  {result.get('backup_removed')}")
    print(f"v3_dir_removed:  {result.get('v3_skill_dir_removed')}")

    facade = PROJECT_ROOT / "skills" / f"{HV_SKILL}.py"
    backup = facade.with_suffix(f"{facade.suffix}.bak")
    v3dir = PROJECT_ROOT / "agent_skills_v3" / HV_SKILL
    print(f"\n回滾後狀態:")
    print(f"  facade exists: {facade.exists()}")
    print(f"  backup exists: {backup.exists()}")
    print(f"  v3_dir exists: {v3dir.exists()}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        cmd_check()
    elif cmd == "full":
        cmd_check()
        cmd_full()
        cmd_verify()
    elif cmd == "verify":
        cmd_verify()
    elif cmd == "rollback":
        cmd_rollback()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
