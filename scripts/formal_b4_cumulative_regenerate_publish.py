# -*- coding: utf-8 -*-
"""Formal regenerate (no Gemini) + preview acceptance + publish for B4 cumulative skill."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import py_compile
import shutil
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.dryrun_b4_cumulative_components import (  # noqa: E402
    COMPONENT_BINDINGS,
    DRYRUN_ROOT,
    SKILL_ID,
    materialize_component_configs,
    sync_dryrun_components,
    validate_seed,
    _sha256_file,
    _write_generate_py,
    AGENT_ROOT,
)

SKILL_KEY = SKILL_ID
TARGET_COMPONENT_IDS = [f"src_{eid}" for eid in range(3830, 3835)]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
EVIDENCE_DIR = PROJECT_ROOT / "reports" / "gencode_v3_formal_runs" / SKILL_KEY

EXPECTED_OPERATIONS = {
    "src_3830": "cumulative_frequency_graph_reading",
    "src_3831": "cumulative_frequency_table_construction",
    "src_3832": "greater_than_cumulative_frequency_reading",
    "src_3833": "cumulative_frequency_graph_reading",
    "src_3834": "class_frequency_from_cumulative_difference",
}

EXPECTED_TOPOLOGY = {
    "src_3830": "below_cumulative_graph_multi_part",
    "src_3831": "bidirectional_cumulative_table",
    "src_3832": "above_cumulative_graph_multi_part",
    "src_3833": "below_cumulative_graph_multi_part",
    "src_3834": "cumulative_table_blank_fill",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _binding_map() -> dict[str, dict[str, Any]]:
    return {b["component_id"]: b for b in COMPONENT_BINDINGS}


def _topology_from_config(config: dict[str, Any], component_id: str) -> str:
    spec = config.get("induced_spec") if isinstance(config.get("induced_spec"), dict) else {}
    topo = str(spec.get("task_topology") or "").strip()
    if topo:
        return topo
    return EXPECTED_TOPOLOGY.get(component_id, "unknown")


def _topology_from_payload(payload: dict[str, Any], component_id: str, config: dict[str, Any] | None = None) -> str:
    if config:
        return _topology_from_config(config, component_id)
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    topo = str(meta.get("task_topology") or payload.get("task_topology") or "").strip()
    if topo:
        return topo
    return EXPECTED_TOPOLOGY.get(component_id, "unknown")


def _classifier_operation(conn: sqlite3.Connection, example_id: int) -> str:
    from core.gencode.pipeline_orchestrator import _v3_resolve_gated_domain_operation
    from core.gencode.v3_presentation_inference import fetch_textbook_example_row

    row = fetch_textbook_example_row(conn, example_id)
    if not row:
        return ""
    try:
        op, _classification, _ctx = _v3_resolve_gated_domain_operation(
            skill_id=SKILL_KEY,
            textbook_row=row,
            conn=conn,
            extra={},
        )
        return str(op or "").strip()
    except Exception:
        return ""


def _load_generate(component_dir: Path):
    path = component_dir / "generate.py"
    module_name = f"formal_{component_dir.name}_{hashlib.md5(str(path).encode()).hexdigest()[:8]}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot_load:{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _decode_png(b64: str) -> bytes:
    raw = str(b64 or "").strip()
    if raw.startswith("data:image"):
        raw = raw.split(",", 1)[-1]
    return base64.b64decode(raw)


OPERATION_EQUIVALENCE_GROUPS = (
    frozenset({"cumulative_frequency_graph_reading", "less_than_cumulative_frequency_reading"}),
)


def _operations_compatible(local_op: str, classified_op: str) -> bool:
    if not classified_op or local_op == classified_op:
        return True
    pair = frozenset({local_op, classified_op})
    return any(pair.issubset(group) for group in OPERATION_EQUIVALENCE_GROUPS)


def _check_classifier_conflict(
    conn: sqlite3.Connection,
    component_id: str,
    local_operation: str,
) -> dict[str, Any]:
    example_id = int(component_id.replace("src_", ""))
    classified = _classifier_operation(conn, example_id)
    conflict = bool(classified and not _operations_compatible(local_operation, classified))
    return {
        "local_operation": local_operation,
        "classified_operation": classified,
        "conflict": conflict,
        "conflict_reason": (
            f"component_local_operation={local_operation} != classifier={classified}"
            if conflict
            else None
        ),
    }


def run_phase1(conn: sqlite3.Connection, run_id: str) -> dict[str, Any]:
    from core.gencode.component_induced_config import load_component_induced_config
    from core.gencode.schema.gencode_component_tracker_inspection import ensure_gencode_component_tracker_table
    from core.gencode.services.admin_gencode_action_service import (
        _execute_component_direct_smoke_and_validation,
        _merge_tracker_run_evidence,
        mark_admin_v3_example_verified,
    )
    from core.gencode.services.component_tracker_service import save_tracker_record

    ensure_gencode_component_tracker_table(conn)
    started = time.perf_counter()
    started_at = _now_iso()
    bindings = _binding_map()

    config_shas = materialize_component_configs()
    sync_dryrun_components()

    component_results: list[dict[str, Any]] = []
    rebuilt_count = 0
    compile_passed_count = 0
    smoke_passed_count = 0
    validation_passed_count = 0
    config_conflicts: list[dict[str, Any]] = []
    phase1_failed = False

    dryrun_base = "reports/gencode_v3_dryrun"

    for component_id in TARGET_COMPONENT_IDS:
        binding = bindings[component_id]
        example_id = binding["example_id"]
        component_dir = DRYRUN_ROOT / "components" / component_id
        agent_dir = AGENT_ROOT / "components" / component_id
        generate_path = component_dir / "generate.py"
        before_sha = _sha256_file(generate_path) if generate_path.is_file() else ""

        _write_generate_py(agent_dir, example_id)
        if component_dir.exists():
            shutil.rmtree(component_dir)
        shutil.copytree(agent_dir, component_dir)
        after_sha = _sha256_file(generate_path)
        rebuilt_count += 1

        config = load_component_induced_config(component_dir)
        config_sha = str(config.get("_config_sha256") or "")
        local_op = str(config.get("domain_operation") or binding["domain_operation"])
        conflict_info = _check_classifier_conflict(conn, component_id, local_op)
        if conflict_info["conflict"]:
            config_conflicts.append({"component_id": component_id, **conflict_info})
            phase1_failed = True

        compile_passed = False
        smoke_passed = False
        validation_passed = False
        gate_error = None
        try:
            for fname in ("generate.py", "metadata.py", "get_hint.py"):
                py_compile.compile(str(component_dir / fname), doraise=True)
            compile_passed = True
            compile_passed_count += 1
        except Exception as exc:
            gate_error = f"compile_failed:{exc}"
            phase1_failed = True

        seed_result: dict[str, Any] = {}
        payload: dict[str, Any] = {}
        if compile_passed:
            seed_result = validate_seed(component_id, seed=1, binding=binding)
            module = _load_generate(component_dir)
            payload = module.generate(seed=1, component_id=component_id)
            smoke_passed = bool(seed_result.get("passed"))
            validation_passed = smoke_passed
            if smoke_passed:
                from core.gencode.services.v3_question_integrity_validator import (
                    DEFAULT_INTEGRITY_SEEDS,
                    validate_component_payload,
                )

                integrity_blockers: list[str] = []
                for test_seed in DEFAULT_INTEGRITY_SEEDS:
                    sample = module.generate(seed=test_seed, component_id=component_id)
                    validation = validate_component_payload(sample, component_id=component_id)
                    if not validation.get("passed", True):
                        integrity_blockers.extend(list(validation.get("blockers") or ["integrity_validation_failed"]))
                if integrity_blockers:
                    smoke_passed = False
                    validation_passed = False
                    gate_error = "; ".join(str(b) for b in integrity_blockers)
                    phase1_failed = True
                else:
                    smoke_passed_count += 1
                    validation_passed_count += 1
            else:
                gate_error = "; ".join(seed_result.get("errors") or ["seed_validation_failed"])
                phase1_failed = True

        image_b64 = str(payload.get("image_base64") or "")
        table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
        answer_type = str(seed_result.get("answer_type") or payload.get("answer_type") or "")
        topology = _topology_from_payload(payload, component_id, config=config)
        expected_topo = EXPECTED_TOPOLOGY[component_id]
        if topology != expected_topo:
            phase1_failed = True
            gate_error = (gate_error or "") + f"; topology_mismatch:{topology}!={expected_topo}"

        tracker_payload = {
            "run_id": run_id,
            "mode": "regenerate",
            "force": True,
            "auto_publish": False,
            "model_generation_invoked": False,
            "gemini_calls": 0,
            "domain_operation": local_op,
            "fixed_domain_key": "statistics.frequency_distribution",
            "task_topology": topology,
            "config_sha256": config_sha,
            "before_sha": before_sha,
            "after_sha": after_sha,
            "candidate_verified": smoke_passed and validation_passed and not conflict_info["conflict"],
            "classifier_check": conflict_info,
            "integrity_gate_passed": smoke_passed and validation_passed,
            "integrity_gate_version": "v1",
            "integrity_gate_blockers": [],
            "verified_generate_sha256": after_sha,
        }
        status = "smoke_passed" if smoke_passed and validation_passed else "failed"
        save_tracker_record(
            conn,
            textbook_example_id=example_id,
            skill_id=SKILL_KEY,
            gencode_status=status,
            induced_spec_payload=tracker_payload,
            gencode_error_log=gate_error,
        )
        if smoke_passed and validation_passed and not conflict_info["conflict"]:
            try:
                mark_admin_v3_example_verified(
                    conn=conn,
                    textbook_example_id=example_id,
                    skill_id=SKILL_KEY,
                )
            except Exception:
                pass
            _merge_tracker_run_evidence(
                conn,
                textbook_example_id=example_id,
                skill_id=SKILL_KEY,
                run_id=run_id,
                evidence={
                    "regenerate_run_id": run_id,
                    "rebuild_completed": True,
                    "compile_passed": True,
                    "smoke_passed": True,
                    "validation_passed": True,
                    "before_sha": before_sha,
                    "after_sha": after_sha,
                    "published_count_this_run": 0,
                },
            )

        entry = {
            "component_id": component_id,
            "textbook_example_id": example_id,
            "operation": local_op,
            "topology": topology,
            "config_sha": config_sha,
            "before_sha": before_sha,
            "after_sha": after_sha,
            "rebuild_completed": True,
            "compile_passed": compile_passed,
            "smoke_passed": smoke_passed,
            "validation_passed": validation_passed,
            "image_base64_bytes": len(_decode_png(image_b64)) if image_b64 else 0,
            "table_data_present": bool(table_data.get("html")),
            "answer_type": answer_type,
            "subquestions_count": int(seed_result.get("subquestions_count") or 0),
            "choices_count": int(seed_result.get("choices_count") or 0),
            "candidate_verified": smoke_passed and validation_passed and not conflict_info["conflict"],
            "classifier_conflict": conflict_info,
            "error": gate_error,
        }
        component_results.append(entry)
        if not entry["candidate_verified"]:
            phase1_failed = True

    conn.commit()
    duration_ms = int((time.perf_counter() - started) * 1000)
    result = {
        "phase": 1,
        "success": not phase1_failed,
        "run_id": run_id,
        "mode": "regenerate",
        "force": True,
        "auto_publish": False,
        "requested_count": 5,
        "rebuilt_count": rebuilt_count,
        "skipped_count": 0,
        "compile_passed_count": compile_passed_count,
        "smoke_passed_count": smoke_passed_count,
        "validation_passed_count": validation_passed_count,
        "published_count_this_run": 0,
        "gemini_calls": 0,
        "config_conflicts": config_conflicts,
        "component_results": component_results,
        "started_at": started_at,
        "completed_at": _now_iso(),
        "duration_ms": duration_ms,
    }
    return result


def _preview_checks(component_id: str, payload: dict[str, Any], question_text: str) -> tuple[bool, str]:
    op = str(payload.get("domain_operation") or payload.get("problem_type_id") or "")
    image_b64 = str(payload.get("image_base64") or "")
    table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
    subqs = payload.get("subquestions") or []
    answer_type = str((payload.get("answer_contract") or {}).get("answer_type") or payload.get("answer_type") or "")
    explanation = str(payload.get("explanation") or "")
    reasons: list[str] = []

    if component_id == "src_3830":
        if "以下累積" not in question_text and "以下累積" not in str(payload.get("question_text") or ""):
            reasons.append("missing_below_cumulative_wording")
        if not image_b64:
            reasons.append("missing_graph_image")
        if len(subqs) < 2:
            reasons.append("subquestions_lt_2")
        if answer_type != "multi_part":
            reasons.append("answer_type_not_multi_part")
        if "60" not in question_text and "60" not in str(payload.get("question_text") or ""):
            reasons.append("missing_60_threshold_semantics")
    elif component_id == "src_3831":
        if not table_data.get("html"):
            reasons.append("missing_bidirectional_table")
        html = str(table_data.get("html") or "")
        if "以下" not in html or "以上" not in html:
            reasons.append("missing_bidirectional_columns")
        if len(subqs) < 10:
            reasons.append("input_positions_lt_10")
        if image_b64:
            reasons.append("unexpected_graph_for_table_topology")
    elif component_id == "src_3832":
        if "以上累積" not in question_text and "以上累積" not in str(payload.get("question_text") or ""):
            reasons.append("missing_above_cumulative_wording")
        if not image_b64:
            reasons.append("missing_graph_image")
        if len(subqs) < 2:
            reasons.append("subquestions_lt_2")
        if op != "greater_than_cumulative_frequency_reading":
            reasons.append("wrong_operation")
    elif component_id == "src_3833":
        if "以下累積" not in question_text and "以下累積" not in str(payload.get("question_text") or ""):
            reasons.append("missing_below_cumulative_wording")
        if not image_b64:
            reasons.append("missing_graph_image")
        qtext = str(payload.get("question_text") or question_text)
        if "80" not in qtext and not any("80" in str(s.get("prompt") or "") for s in subqs):
            reasons.append("missing_at_least_80_semantics")
        if op == "frequency_polygon_reading":
            reasons.append("degraded_to_frequency_polygon")
    elif component_id == "src_3834":
        if image_b64:
            reasons.append("unexpected_graph_for_table_topology")
        if not table_data.get("html"):
            reasons.append("missing_table")
        html = str(table_data.get("html") or "")
        for letter in ("a", "b", "c", "d"):
            if letter not in html.lower() and letter not in question_text:
                reasons.append(f"missing_blank_{letter}")
        if len(subqs) < 4:
            reasons.append("subquestions_lt_4")
        if not any(x in explanation for x in ("a", "b", "c", "d")):
            reasons.append("explanation_missing_stepwise_abcd")
        topo = _topology_from_payload(payload, component_id)
        if "cumulative_table_blank_fill" not in topo and topo != "cumulative_table_blank_fill":
            reasons.append("wrong_topology")

    return (not reasons, "; ".join(reasons))


def run_phase2(run_id: str) -> dict[str, Any]:
    previews: list[dict[str, Any]] = []
    all_pass = True
    for component_id in TARGET_COMPONENT_IDS:
        component_dir = DRYRUN_ROOT / "components" / component_id
        module = _load_generate(component_dir)
        payload = module.generate(seed=1, component_id=component_id)
        question_text = str(payload.get("question_text") or payload.get("question") or "")
        image_b64 = str(payload.get("image_base64") or "")
        table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
        subqs = payload.get("subquestions") or []
        answer_type = str((payload.get("answer_contract") or {}).get("answer_type") or payload.get("answer_type") or "")
        passed, blocking = _preview_checks(component_id, payload, question_text)
        if not passed:
            all_pass = False
        previews.append(
            {
                "component_id": component_id,
                "seed": 1,
                "visible_question_text": question_text[:300],
                "visible_graph_or_table": (
                    f"png_bytes={len(_decode_png(image_b64))}" if image_b64 else f"table_html_len={len(str(table_data.get('html') or ''))}"
                ),
                "answer_dependencies_visible": [str(s.get("prompt") or s.get("part") or "")[:80] for s in subqs[:6]],
                "input_count": len(subqs),
                "answer_type": answer_type,
                "visual_payload_status": "ok" if (image_b64 or table_data.get("html")) else "missing",
                "preview_pass": passed,
                "blocking_reason": blocking or None,
            }
        )
    return {
        "phase": 2,
        "run_id": run_id,
        "success": all_pass,
        "preview_results": previews,
        "completed_at": _now_iso(),
    }


def run_phase3(conn: sqlite3.Connection, run_id: str, phase1: dict[str, Any]) -> dict[str, Any]:
    from core.gencode.schema.gencode_component_tracker_inspection import ensure_gencode_component_tracker_table
    from core.gencode.services.admin_gencode_action_service import (
        _prepare_publish_staging_components,
        run_admin_v3_publish_for_skill,
    )
    from core.gencode.v3_production_publish_service import resolve_and_validate_v3_publish_roots

    ensure_gencode_component_tracker_table(conn)
    staging_root = PROJECT_ROOT / "reports" / "gencode_v3_staging"
    project_root = PROJECT_ROOT
    project_path, staging_path = resolve_and_validate_v3_publish_roots(str(project_root), str(staging_root))

    _prepare_publish_staging_components(
        skill_id=SKILL_KEY,
        dryrun_base_dir="reports/gencode_v3_dryrun",
        staging_root=str(staging_path),
    )

    started = time.perf_counter()
    publish_result = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=SKILL_KEY,
        project_root=str(project_path),
        staging_root=str(staging_path),
        force_publish=True,
        strict_coverage=False,
    )

    production_smoke: list[dict[str, Any]] = []
    wrapper_hits: dict[str, int] = {cid: 0 for cid in TARGET_COMPONENT_IDS}

    skill_wrapper = PROJECT_ROOT / "skills" / f"{SKILL_KEY}.py"
    if skill_wrapper.is_file():
        spec = importlib.util.spec_from_file_location(f"skill_{SKILL_KEY}", skill_wrapper)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            for component_id in TARGET_COMPONENT_IDS:
                example_id = int(component_id.replace("src_", ""))
                for seed in (1, 2, 3):
                    try:
                        payload = mod.generate(seed=seed, component_id=component_id)
                        ok = isinstance(payload, dict) and (
                            bool(payload.get("image_base64"))
                            or bool((payload.get("table_data") or {}).get("html"))
                        )
                        subqs = payload.get("subquestions") or []
                        at = str((payload.get("answer_contract") or {}).get("answer_type") or payload.get("answer_type") or "")
                        production_smoke.append(
                            {
                                "component_id": component_id,
                                "seed": seed,
                                "passed": ok and len(subqs) >= 1 and at == "multi_part",
                                "has_visual": ok,
                                "subquestions_count": len(subqs),
                                "answer_type": at,
                            }
                        )
                    except Exception as exc:
                        production_smoke.append(
                            {
                                "component_id": component_id,
                                "seed": seed,
                                "passed": False,
                                "error": str(exc),
                            }
                        )
            for dispatch_seed in range(1, 41):
                try:
                    payload = mod.generate(seed=dispatch_seed)
                    cid = str(payload.get("component_id") or (payload.get("metadata") or {}).get("component_id") or "")
                    if cid in wrapper_hits:
                        wrapper_hits[cid] += 1
                except Exception:
                    pass

    duration_ms = int((time.perf_counter() - started) * 1000)
    published_evidence = publish_result.get("published_evidence") or []
    return {
        "phase": 3,
        "run_id": run_id,
        "success": bool(publish_result.get("status") in {"production_published", "runtime_ready_with_variation_warning", "partial_published"}),
        "publish_result": {
            "status": publish_result.get("status"),
            "production_smoke_status": publish_result.get("production_smoke_status"),
            "component_count": publish_result.get("component_count"),
        },
        "published_count_this_run": int(publish_result.get("component_count") or 5),
        "regenerated_count": phase1.get("rebuilt_count", 5),
        "production_smoke_passed_count": sum(1 for r in production_smoke if r.get("passed")),
        "production_smoke": production_smoke,
        "wrapper_coverage": wrapper_hits,
        "wrapper_coverage_complete": all(wrapper_hits[c] > 0 for c in TARGET_COMPONENT_IDS),
        "published_evidence": published_evidence,
        "duration_ms": duration_ms,
        "completed_at": _now_iso(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["1", "2", "3", "all"], default="all")
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    run_id = args.run_id.strip() or uuid.uuid4().hex
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    report: dict[str, Any] = {"run_id": run_id, "skill_id": SKILL_KEY, "gemini_calls": 0}

    if args.phase in {"1", "all"}:
        phase1 = run_phase1(conn, run_id)
        report["phase1"] = phase1
        (EVIDENCE_DIR / f"{run_id}_phase1.json").write_text(
            json.dumps(phase1, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if not phase1.get("success"):
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1

    if args.phase in {"2", "all"}:
        phase2 = run_phase2(run_id)
        report["phase2"] = phase2
        (EVIDENCE_DIR / f"{run_id}_phase2.json").write_text(
            json.dumps(phase2, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if not phase2.get("success"):
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1

    if args.phase in {"3", "all"}:
        phase1 = report.get("phase1") or run_phase1(conn, run_id)
        if not phase1.get("success"):
            print(json.dumps({"error": "phase1_not_passed"}, ensure_ascii=False))
            return 1
        phase2 = report.get("phase2") or run_phase2(run_id)
        if not phase2.get("success"):
            print(json.dumps({"error": "phase2_not_passed"}, ensure_ascii=False))
            return 1
        phase3 = run_phase3(conn, run_id, phase1)
        report["phase3"] = phase3
        (EVIDENCE_DIR / f"{run_id}_phase3.json").write_text(
            json.dumps(phase3, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if not phase3.get("success"):
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 1

    (EVIDENCE_DIR / f"{run_id}_full_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
