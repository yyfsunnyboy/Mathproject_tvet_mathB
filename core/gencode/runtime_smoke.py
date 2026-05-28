from __future__ import annotations

import ast
import importlib.util
import py_compile
import re
from pathlib import Path
from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_generator_payload

_REQUIRED_PAYLOAD_KEYS = (
    "question_text",
    "answer",
    "answer_type",
    "choices",
    "explanation",
    "problem_type_id",
    "metadata",
)

_PLACEHOLDER_PATTERNS = (
    "[DRAFT]",
    "generator draft pending implementation",
    "draft pending implementation",
    "pending implementation",
    "placeholder",
    "TODO",
    "NotImplemented",
    "raise NotImplementedError",
    "implementation pending",
    "implementation_pending",
)

_NEGATIVE_CONDITION_UNUSED_PAYLOAD: dict[str, Any] = {
    "question_text": "若 $a<b<0$，且 $Q(12,-8)$，請判斷 $Q$ 位於哪一象限。",
    "answer_type": "short_answer",
    "choices": [],
    "answer": "第四象限",
    "problem_type_id": "short_answer_classify_quadrant_symbolic_condition_coordinate_point",
    "metadata": {
        "givens": [
            {"type": "symbolic_condition", "text": "a<b<0", "variables": ["a", "b"]},
        ],
        "target": {
            "type": "coordinate_point",
            "label": "Q",
            "x_expr": "12",
            "y_expr": "-8",
            "variables": [],
        },
        "derivation": [],
    },
}



def _validate_runtime_payload(payload: dict[str, Any], skill_id: str) -> list[str]:
    blockers: list[str] = []
    if not payload:
        blockers.append("runtime_smoke_empty_output")
        return blockers
    for key in ("question_text", "answer", "answer_type"):
        val = payload.get(key)
        if val is None or str(val).strip() == "":
            blockers.append("runtime_smoke_empty_output")
            break
    if "choices" not in payload:
        blockers.append("runtime_smoke_missing_choices_key")
    meta = payload.get("metadata")
    if not isinstance(meta, dict):
        blockers.append("runtime_smoke_missing_metadata")
    else:
        for mk in ("givens", "target", "derivation"):
            if mk not in meta:
                blockers.append(f"runtime_smoke_missing_metadata_{mk}")
    text_blob = str(payload)
    if any(p in text_blob for p in _PLACEHOLDER_PATTERNS):
        blockers.append("placeholder_output_detected")

    pt = str(payload.get("problem_type_id", "")).strip()
    spec = load_problem_type_spec(skill_id, pt, prefer="auto") if pt else None
    contract_errors = validate_generator_payload(
        payload, skill_id=skill_id, problem_type_spec=spec
    )
    for err in contract_errors:
        if err == "problem_type_spec_missing":
            blockers.append("contract_validation_failed")
        else:
            blockers.append(err)
    if contract_errors and "contract_validation_failed" not in blockers:
        blockers.append("contract_validation_failed")

    return sorted(set(blockers))


def _run_negative_semantic_smoke(skill_id: str) -> list[str]:
    pt = str(_NEGATIVE_CONDITION_UNUSED_PAYLOAD.get("problem_type_id", "")).strip()
    spec = load_problem_type_spec(skill_id, pt, prefer="auto")
    if not spec:
        return []
    payload = dict(_NEGATIVE_CONDITION_UNUSED_PAYLOAD)
    payload["skill_id"] = skill_id
    errors = validate_generator_payload(payload, skill_id=skill_id, problem_type_spec=spec)
    if "condition_unused_by_target" not in errors:
        return ["semantic_negative_case_should_fail"]
    return []


def run_draft_runtime_smoke(
    skill_id: str,
    draft_skill_file_path: str,
    *,
    sample_count: int = 30,
) -> dict[str, Any]:
    draft_path = Path(draft_skill_file_path)
    raw: dict[str, Any] = {
        "status": "not_run",
        "blockers": [],
        "payload_preview": {},
        "interface_check": {},
        "py_compile_status": "not_run",
        "samples_tested": 0,
    }
    if not draft_path.exists():
        raw["status"] = "failed"
        raw["blockers"] = ["draft_skill_file_missing"]
        return raw

    neg_blockers = _run_negative_semantic_smoke(skill_id)
    if neg_blockers:
        raw["status"] = "failed"
        raw["blockers"] = neg_blockers
        raw["negative_semantic_smoke"] = "failed"
        return raw
    raw["negative_semantic_smoke"] = "passed"

    try:
        py_compile.compile(str(draft_path), doraise=True)
        raw["py_compile_status"] = "passed"
    except Exception as ex:
        raw["py_compile_status"] = "failed"
        raw["status"] = "failed"
        raw["blockers"] = ["draft_py_compile_failed"]
        raw["error"] = str(ex)
        return raw

    interface_check: dict[str, Any] = {
        "generate_exists": False,
        "check_exists": False,
        "generate_returns_dict": False,
        "check_callable": False,
    }
    try:
        src = draft_path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn_names = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        interface_check["generate_exists"] = "generate" in fn_names
        interface_check["check_exists"] = "check" in fn_names
        if not interface_check["generate_exists"] or not interface_check["check_exists"]:
            raw["status"] = "failed"
            raw["blockers"] = ["runtime_interface_missing"]
            raw["interface_check"] = interface_check
            return raw

        spec = importlib.util.spec_from_file_location(f"_draft_{skill_id}", str(draft_path))
        if not spec or not spec.loader:
            raise RuntimeError("unable_to_create_import_spec")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        gen = getattr(mod, "generate", None)
        chk = getattr(mod, "check", None)
        interface_check["check_callable"] = callable(chk)
        if not callable(gen):
            raw["status"] = "failed"
            raw["blockers"] = ["generate_not_callable"]
            raw["interface_check"] = interface_check
            return raw

        all_blockers: list[str] = []
        last_payload: dict[str, Any] = {}
        for seed in range(max(1, int(sample_count))):
            payload = gen(level=1, seed=seed)
            if not isinstance(payload, dict):
                all_blockers.append("runtime_smoke_empty_output")
                break
            last_payload = payload
            sample_blockers = _validate_runtime_payload(payload, skill_id)
            if sample_blockers:
                all_blockers.extend(sample_blockers)
                all_blockers.append(f"runtime_smoke_failed_at_seed_{seed}")
                break
            if callable(chk):
                check_ok = chk(payload.get("answer", ""), payload.get("correct_answer", payload.get("answer", "")))
                if check_ok is False:
                    all_blockers.append("runtime_smoke_check_failed")
                    break
            raw["samples_tested"] = seed + 1

        raw["payload_preview"] = {
            "problem_type_id": last_payload.get("problem_type_id"),
            "answer_type": last_payload.get("answer_type"),
            "question_text_len": len(str(last_payload.get("question_text", ""))),
            "answer": last_payload.get("answer"),
            "choices_count": len(last_payload.get("choices") or []),
            "metadata_keys": list((last_payload.get("metadata") or {}).keys())
            if isinstance(last_payload.get("metadata"), dict)
            else [],
        }
        raw["interface_check"] = interface_check
        if all_blockers:
            raw["status"] = "failed"
            raw["blockers"] = sorted(set(all_blockers))
            return raw

        raw["status"] = "passed"
        raw["blockers"] = []
        return raw
    except Exception as ex:
        raw["status"] = "failed"
        if not raw.get("blockers"):
            raw["blockers"] = ["runtime_smoke_failed"]
        raw["error"] = str(ex)
        raw["interface_check"] = interface_check
        return raw
