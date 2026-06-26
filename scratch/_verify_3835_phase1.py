"""One-off local verification for example 3835 Phase 1 preflight (no code changes)."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

SKILL_ID = "vh_數學B4_CentralTendencyMeasures"
EXAMPLE_ID = 3835
DRYRUN_DIR = "reports/gencode_v3_dryrun"


def _parse_payload(raw) -> dict:
    if raw is None or str(raw).strip() == "":
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(str(raw))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _fetch_tracker(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        """
        SELECT gencode_status, gencode_error_log, induced_spec_payload
        FROM gencode_component_tracker
        WHERE textbook_example_id = ?
        """,
        (EXAMPLE_ID,),
    ).fetchone()
    if row is None:
        return None
    return {
        "gencode_status": row[0],
        "gencode_error_log": row[1],
        "induced_spec_payload": _parse_payload(row[2]),
    }


def _fetch_textbook_row(conn: sqlite3.Connection) -> dict | None:
    row = conn.execute(
        "SELECT id, skill_id, problem_type, problem_text, correct_answer FROM textbook_examples WHERE id = ?",
        (EXAMPLE_ID,),
    ).fetchone()
    if row is None:
        return None
    return dict(row) if hasattr(row, "keys") else {
        "id": row[0], "skill_id": row[1], "problem_type": row[2],
        "problem_text": row[3], "correct_answer": row[4],
    }


def run_round(*, force_regenerate: bool, label: str) -> dict:
    from core.gencode.schema.gencode_component_tracker_inspection import apply_tracker_ddl
    from core.gencode.services.admin_gencode_action_service import run_admin_v3_dryrun_for_example
    from core.gencode.pipeline_orchestrator import (
        resolve_v3_admin_induced_spec,
        run_gencode_phase2_raw,
    )

    db_path = PROJECT_ROOT / "instance" / "kumon_math.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    apply_tracker_ddl(conn)

    phase2_calls: list[dict] = []
    preflight_calls: list[dict] = []

    original_resolve = resolve_v3_admin_induced_spec
    original_phase2 = run_gencode_phase2_raw

    preflight_returns: list[dict] = []

    def _spy_resolve(*args, **kwargs):
        preflight_calls.append({"args": args, "kwargs": kwargs})
        result = original_resolve(*args, **kwargs)
        preflight_returns.append(result if isinstance(result, dict) else {})
        return result

    def _spy_phase2(skill_id, **kwargs):
        phase2_calls.append({"skill_id": skill_id, "kwargs": dict(kwargs)})
        return original_phase2(skill_id, **kwargs)

    ai_retry_count = 0
    ai_client_count = 0
    resolve_ai_count = 0

    def _count_retry(*a, **k):
        nonlocal ai_retry_count
        ai_retry_count += 1
        raise RuntimeError("unexpected_gemini_call")

    def _count_client(*a, **k):
        nonlocal ai_client_count
        ai_client_count += 1
        raise RuntimeError("unexpected_gemini_call")

    def _count_resolve_ai(*a, **k):
        nonlocal resolve_ai_count
        resolve_ai_count += 1
        raise RuntimeError("unexpected_gemini_call")

    dryrun_result = None
    exc_info = None

    with (
        patch("core.gencode.services.admin_gencode_action_service.resolve_v3_admin_induced_spec", side_effect=_spy_resolve),
        patch("core.gencode.services.admin_gencode_action_service.run_gencode_phase2_raw", side_effect=_spy_phase2),
        patch("core.ai_wrapper.call_ai_with_retry", side_effect=_count_retry),
        patch("core.ai_wrapper.get_ai_client", side_effect=_count_client),
        patch("core.gencode.gencode_ai_resolve.resolve_gencode_ai_client", side_effect=_count_resolve_ai),
    ):
        try:
            dryrun_result = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=EXAMPLE_ID,
                skill_id=SKILL_ID,
                dryrun_base_dir=DRYRUN_DIR,
                force_regenerate=force_regenerate,
                allow_non_mvp_skill=True,
            )
        except Exception as exc:
            exc_info = f"{exc.__class__.__name__}:{exc}"

    tracker = _fetch_tracker(conn)
    textbook = _fetch_textbook_row(conn)
    conn.close()

    preflight_meta = None
    if preflight_calls:
        last = preflight_calls[-1]
        # re-run resolve to get return without spy side effects on counts - use last spy result from dryrun
        pass

    phase2_induced = None
    if phase2_calls:
        phase2_induced = phase2_calls[0]["kwargs"].get("v3_induced_spec")

    phase1_from_preflight = None
    if isinstance(dryrun_result, dict):
        pf = dryrun_result.get("phase1_preflight") or {}
        phase1_from_preflight = pf

    return {
        "label": label,
        "force_regenerate": force_regenerate,
        "dryrun_result": dryrun_result,
        "exc_info": exc_info,
        "tracker": tracker,
        "textbook": textbook,
        "phase2_calls": phase2_calls,
        "preflight_call_count": len(preflight_calls),
        "preflight_returns": preflight_returns,
        "phase2_induced_spec": phase2_induced,
        "phase1_preflight": phase1_from_preflight,
        "ai_retry_count": ai_retry_count,
        "ai_client_count": ai_client_count,
        "resolve_ai_count": resolve_ai_count,
    }


def main() -> None:
    print("=== ROUND 1 (force_regenerate=False) ===")
    r1 = run_round(force_regenerate=False, label="round1")
    print(json.dumps(r1, ensure_ascii=False, indent=2, default=str))

    print("\n=== ROUND 2 (force_regenerate=False, cache check) ===")
    r2 = run_round(force_regenerate=False, label="round2")
    print(json.dumps(r2, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
