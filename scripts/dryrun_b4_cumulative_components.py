# -*- coding: utf-8 -*-
"""Materialize component-local induced configs and dryrun evidence for B4 cumulative skill."""

from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

SKILL_ID = "vh_數學B4_CumulativeFrequencyTablesAndGraphs"
INDUCED_ROOT = PROJECT_ROOT / "reports/gencode_v3_induced_specs" / SKILL_ID
AGENT_ROOT = PROJECT_ROOT / "agent_skills_v3" / SKILL_ID
DRYRUN_ROOT = PROJECT_ROOT / "reports/gencode_v3_dryrun" / SKILL_ID
EVIDENCE_PATH = DRYRUN_ROOT / "component_dryrun_evidence.json"

COMPONENT_BINDINGS: list[dict[str, Any]] = [
    {
        "component_id": "src_3830",
        "example_id": 3830,
        "domain_operation": "cumulative_frequency_graph_reading",
        "source_artifact": "induced_specs/below_cumulative_graph_reading_01.json",
        "question_text": (
            "已知某班數學期中考成績的以下累積次數分配折線圖如下，"
            "試問：(1)以60分為標準，不及格的人數有幾人？(2)至少70分的人數有幾人？"
        ),
    },
    {
        "component_id": "src_3831",
        "example_id": 3831,
        "domain_operation": "cumulative_frequency_table_construction",
        "source_artifact": "induced_specs/bidirectional_cumulative_table_01.json",
        "question_text": "試完成下方之累積次數分配表。",
    },
    {
        "component_id": "src_3832",
        "example_id": 3832,
        "domain_operation": "greater_than_cumulative_frequency_reading",
        "source_artifact": "induced_specs/above_cumulative_graph_reading_01.json",
        "question_text": (
            "已知某班英文期末考成績的以上累積次數分配折線圖如右，"
            "試問：(1)以60分為標準，不及格的人數有幾人？(2)80分以上的人數有幾人？"
        ),
    },
    {
        "component_id": "src_3833",
        "example_id": 3833,
        "domain_operation": "cumulative_frequency_graph_reading",
        "source_artifact": "induced_specs/below_cumulative_graph_reading_01.json",
        "question_text": (
            "已知某班國文期中考成績的以下累積次數分配折線圖如右，"
            "試問：(1)以60分為標準，不及格的人數有幾人？(2)至少80分的人數有幾人？"
        ),
        "spec_overrides": {
            "sub_questions": [
                {
                    "part": "(1)",
                    "prompt": "以60分為標準，不及格的人數有幾人",
                    "inference": "read_below_cumulative_at_60",
                    "unit": "人",
                },
                {
                    "part": "(2)",
                    "prompt": "至少80分的人數有幾人",
                    "inference": "total_minus_below_cumulative_at_80",
                    "unit": "人",
                },
            ],
            "domain_constraints": {"thresholds": [60, 80]},
        },
        "notes": ["3833 與 3830 共用圖1資料點；第二小題 threshold 為 80。"],
    },
    {
        "component_id": "src_3834",
        "example_id": 3834,
        "domain_operation": "class_frequency_from_cumulative_difference",
        "source_artifact": None,
        "question_text": (
            "某班有40位同學，第一次期中考數學成績的次數分配表及以下累積次數分配表如下表，"
            "試求 a, b, c, d。"
        ),
        "custom_induced_spec": {
            "artifact_id": "component_induced_spec_src_3834",
            "suggested_domain_operation": "class_frequency_from_cumulative_difference",
            "render_mode": "multi_part",
            "cumulative_direction": "less_than",
            "task_topology": "cumulative_table_blank_fill",
            "cumulative_table_blank_fill": True,
            "domain_constraints": {
                "cumulative_direction": "below",
                "total_students": 40,
                "table_rows": [
                    ["0~20", 4, 4],
                    ["20~40", "a", 12],
                    ["40~60", 10, "b"],
                    ["60~80", 12, 34],
                    ["80~100", "c", "d"],
                ],
                "blank_fields": ["a", "b", "c", "d"],
                "expected_answers": {"a": 8, "b": 22, "c": 6, "d": 40},
            },
            "notes": [
                "教材題為表格求 a,b,c,d；與圖4區間差 induced spec 不同，以題幹表格語意為準。"
            ],
        },
    },
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_spec(binding: dict[str, Any]) -> dict[str, Any]:
    if binding.get("custom_induced_spec"):
        return dict(binding["custom_induced_spec"])
    path = INDUCED_ROOT / str(binding["source_artifact"])
    spec = json.loads(path.read_text(encoding="utf-8"))
    overrides = binding.get("spec_overrides") or {}
    for key, value in overrides.items():
        if key == "domain_constraints" and isinstance(value, dict):
            base = dict(spec.get("domain_constraints") or {})
            base.update(value)
            spec["domain_constraints"] = base
        else:
            spec[key] = value
    return spec


def materialize_component_configs() -> dict[str, str]:
    shas: dict[str, str] = {}
    for binding in COMPONENT_BINDINGS:
        component_id = binding["component_id"]
        spec = _load_spec(binding)
        source_path = binding.get("source_artifact")
        source_sha = _sha256_file(INDUCED_ROOT / source_path) if source_path else _sha256_text(json.dumps(spec, ensure_ascii=False, sort_keys=True))
        config = {
            "schema_version": "component_induced_config.v1",
            "skill_id": SKILL_ID,
            "component_id": component_id,
            "domain_operation": binding["domain_operation"],
            "presentation_mode": "short_answer",
            "source_artifact_path": str(INDUCED_ROOT / source_path) if source_path else "",
            "source_artifact_sha256": source_sha,
            "question_text": binding["question_text"],
            "induced_spec": spec,
            "binding_notes": binding.get("notes", []),
        }
        component_dir = AGENT_ROOT / "components" / component_id
        component_dir.mkdir(parents=True, exist_ok=True)
        config_path = component_dir / "generator_config.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        shas[component_id] = _sha256_file(config_path)
    return shas


def _write_generate_py(component_dir: Path, example_id: int) -> None:
    content = f'''from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.cumulative_component_runtime import generate_cumulative_component_payload

_COMPONENT_DIR = Path(__file__).resolve().parent
TEXTBOOK_EXAMPLE_ID = {example_id}


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    return generate_cumulative_component_payload(
        _COMPONENT_DIR,
        seed=seed,
        level=level,
        textbook_example_id=int(kwargs.get("textbook_example_id") or TEXTBOOK_EXAMPLE_ID),
        component_id=str(kwargs.get("component_id") or _COMPONENT_DIR.name),
    )
'''
    (component_dir / "generate.py").write_text(content, encoding="utf-8")


def sync_dryrun_components() -> None:
    src_components = AGENT_ROOT / "components"
    dst_components = DRYRUN_ROOT / "components"
    dst_components.mkdir(parents=True, exist_ok=True)
    for binding in COMPONENT_BINDINGS:
        component_id = binding["component_id"]
        _write_generate_py(src_components / component_id, binding["example_id"])
        src = src_components / component_id
        dst = dst_components / component_id
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def _load_generate(component_id: str):
    path = DRYRUN_ROOT / "components" / component_id / "generate.py"
    module_name = f"dryrun_{component_id}_{hashlib.md5(str(path).encode()).hexdigest()[:8]}"
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


def validate_seed(component_id: str, seed: int, binding: dict[str, Any]) -> dict[str, Any]:
    from core.checkers.multi_part_answer_checker import check_multi_part_answer
    from core.gencode.validators.cumulative_frequency_validator import validate_cumulative_frequency_payload

    module = _load_generate(component_id)
    payload = module.generate(seed=seed, component_id=component_id)
    errors: list[str] = []
    op = str(binding["domain_operation"])
    if str(payload.get("domain_operation") or payload.get("problem_type_id")) != op:
        errors.append("domain_operation_mismatch")
    image_b64 = str(payload.get("image_base64") or "")
    table_data = payload.get("table_data") if isinstance(payload.get("table_data"), dict) else {}
    answer_type = str(payload.get("answer_type") or "")
    if op in {
        "cumulative_frequency_graph_reading",
        "greater_than_cumulative_frequency_reading",
    }:
        try:
            png = _decode_png(image_b64)
            if png[:8] != b"\x89PNG\r\n\x1a\n":
                errors.append("invalid_png")
        except Exception:
            errors.append("image_decode_failed")
    if op == "cumulative_frequency_table_construction" and not table_data.get("html"):
        errors.append("table_data_missing")
    if op == "class_frequency_from_cumulative_difference" and component_id == "src_3834":
        if not table_data.get("html"):
            errors.append("table_data_missing")
        if len(payload.get("subquestions") or []) < 4:
            errors.append("subquestions_incomplete")
    errors.extend(validate_cumulative_frequency_payload(payload))
    checker_ok = True
    if answer_type == "multi_part":
        ac = payload.get("answer_contract") or {}
        correct = payload.get("semantic_answer")
        if correct is None:
            correct = payload.get("correct_answer")
        if isinstance(correct, list) and correct:
            good = check_multi_part_answer(correct, correct, answer_contract=ac, payload=payload)
            bad = check_multi_part_answer([0] * len(correct), correct, answer_contract=ac, payload=payload)
            checker_ok = bool(good.get("overall_correct")) and not bool(bad.get("overall_correct"))
        if str(ac.get("answer_type")) != "multi_part":
            errors.append("multi_part_contract_flattened")
    return {
        "seed": seed,
        "passed": not errors and checker_ok,
        "errors": errors,
        "checker_ok": checker_ok,
        "answer_type": answer_type,
        "image_png_bytes": len(_decode_png(image_b64)) if image_b64 else 0,
        "table_data_present": bool(table_data.get("html")),
        "choices_count": len(payload.get("choices") or []),
        "subquestions_count": len(payload.get("subquestions") or []),
        "preview_contract": {
            "question_text": str(payload.get("question_text") or "")[:160],
            "domain_operation": payload.get("domain_operation"),
            "answer_type": answer_type,
            "has_image": bool(image_b64),
            "has_table": bool(table_data.get("html")),
            "subquestions": len(payload.get("subquestions") or []),
        },
    }


def run_dryrun() -> dict[str, Any]:
    config_shas = materialize_component_configs()
    sync_dryrun_components()
    report: dict[str, Any] = {
        "skill_id": SKILL_ID,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "gemini_calls": 0,
        "tracker_updated": False,
        "components": [],
    }
    for binding in COMPONENT_BINDINGS:
        component_id = binding["component_id"]
        generate_path = DRYRUN_ROOT / "components" / component_id / "generate.py"
        seed_results = [validate_seed(component_id, seed, binding) for seed in range(1, 16)]
        passed = all(r["passed"] for r in seed_results)
        preview = seed_results[0]["preview_contract"]
        blockers = sorted({e for r in seed_results for e in r["errors"]})
        candidate_verified = passed
        if binding["domain_operation"] in {
            "cumulative_frequency_graph_reading",
            "greater_than_cumulative_frequency_reading",
        }:
            candidate_verified = passed and all(r["image_png_bytes"] > 0 for r in seed_results)
        elif binding["domain_operation"] == "cumulative_frequency_table_construction" or component_id == "src_3834":
            candidate_verified = passed and all(r["table_data_present"] for r in seed_results)
        if seed_results[0]["answer_type"] == "multi_part" and seed_results[0]["subquestions_count"] < 2:
            candidate_verified = False
            blockers.append("multi_part_ui_contract_incomplete")
        report["components"].append(
            {
                "component_id": component_id,
                "example_id": binding["example_id"],
                "domain_operation": binding["domain_operation"],
                "induced_spec_path": str(INDUCED_ROOT / binding["source_artifact"]) if binding.get("source_artifact") else "custom",
                "induced_spec_sha256": binding.get("source_artifact") and _sha256_file(INDUCED_ROOT / binding["source_artifact"]),
                "generated_config_sha256": config_shas[component_id],
                "generate_py_sha256": _sha256_file(generate_path),
                "compile_result": "pass",
                "smoke_result": "pass" if seed_results[0]["passed"] else "fail",
                "validation_result": "pass" if passed else "fail",
                "seeds_passed": sum(1 for r in seed_results if r["passed"]),
                "seeds_total": 15,
                "image_png_bytes_seed1": seed_results[0]["image_png_bytes"],
                "table_data_present": seed_results[0]["table_data_present"],
                "answer_type": seed_results[0]["answer_type"],
                "choices_count": seed_results[0]["choices_count"],
                "subquestions_count": seed_results[0]["subquestions_count"],
                "preview_contract": preview,
                "candidate_verified": candidate_verified,
                "blockers": blockers,
                "binding_notes": binding.get("notes", []),
            }
        )
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run_dryrun()
    print(json.dumps({"evidence": str(EVIDENCE_PATH), "components": len(result["components"])}, ensure_ascii=False))
