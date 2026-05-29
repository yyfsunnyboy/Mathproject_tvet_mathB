from __future__ import annotations

import ast
import importlib.util
import py_compile
import re
from pathlib import Path
from typing import Any

from core.gencode.answer_payload import (
    answer_type_family,
    build_answer_validation_diagnostics,
    validate_generated_answer_shape,
)
from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec
from core.gencode.runtime_skill_wrapper import check_answer
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



def _answer_nonempty(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, (list, tuple, set)):
        return len(val) > 0
    return str(val).strip() != ""


def _solution_set_checker_smoke(payload: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    ac = get_answer_contract(spec)
    checker = str(ac.get("checker", "")).strip()
    family = answer_type_family(str(ac.get("answer_type", "")))
    if checker != "solution_set_checker" and family != "solution_set":
        return []
    ca = payload.get("correct_answer", payload.get("answer"))
    if isinstance(ca, (list, tuple, set)):
        user_variants = [
            ",".join(str(x) for x in ca),
            ",".join(str(x) for x in reversed(list(ca))),
            " 或 ".join(str(x) for x in ca),
        ]
    else:
        user_variants = [str(ca)]
    for ua in user_variants:
        if not check_answer(ua, ca, payload=payload, skill_id=str(payload.get("skill_id", ""))):
            return ["solution_set_checker_smoke_failed"]
    if isinstance(ca, (list, tuple, set)) and len(ca) >= 2:
        if check_answer("7", ca, payload=payload, skill_id=str(payload.get("skill_id", ""))):
            return ["solution_set_checker_smoke_false_positive"]
    return []


def _validate_runtime_payload(payload: dict[str, Any], skill_id: str) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    empty_diag: dict[str, Any] = {}
    if not payload:
        blockers.append("runtime_smoke_empty_output")
        return blockers, empty_diag
    for key in ("question_text", "answer_type"):
        val = payload.get(key)
        if val is None or str(val).strip() == "":
            blockers.append("runtime_smoke_empty_output")
            break
    if not _answer_nonempty(payload.get("answer", payload.get("correct_answer"))):
        blockers.append("runtime_smoke_empty_output")
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
    ac = get_answer_contract(spec) if spec else {}
    if isinstance(payload.get("answer_contract"), dict) and payload["answer_contract"].get("answer_type"):
        ac = payload["answer_contract"]
    shape_ok, shape_blockers, shape_diag = validate_generated_answer_shape(
        payload, answer_contract=ac if isinstance(ac, dict) else {}, problem_type_id=pt
    )
    if not shape_ok:
        blockers.extend(shape_blockers)
        return sorted(set(blockers)), shape_diag

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

    if spec and not contract_errors:
        blockers.extend(_solution_set_checker_smoke(payload, spec))

    diag = build_answer_validation_diagnostics(
        payload,
        answer_contract=ac if isinstance(ac, dict) else {},
        failed_validator_name="" if not blockers else "validate_generator_payload",
    )
    return sorted(set(blockers)), diag


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
        last_diagnostics: dict[str, Any] = {}
        for seed in range(max(1, int(sample_count))):
            try:
                payload = gen(level=1, seed=seed)
            except Exception as gen_ex:
                all_blockers.append("runtime_smoke_generate_exception")
                raw["error"] = str(gen_ex)
                raw["failed_seed"] = seed
                if "invalid_answer_type" in str(gen_ex) or "generator_semantically_unsafe" in str(gen_ex):
                    raw["failed_validator_name"] = "slot_generators.validate_generator_payload"
                interface_check["generate_returns_dict"] = False
                break
            if not isinstance(payload, dict):
                all_blockers.append("runtime_smoke_empty_output")
                interface_check["generate_returns_dict"] = False
                break
            interface_check["generate_returns_dict"] = True
            last_payload = payload
            sample_blockers, sample_diag = _validate_runtime_payload(payload, skill_id)
            last_diagnostics = sample_diag
            if sample_blockers:
                all_blockers.extend(sample_blockers)
                all_blockers.append(f"runtime_smoke_failed_at_seed_{seed}")
                raw["validation_diagnostics"] = sample_diag
                break
            if callable(chk):
                ua = payload.get("answer", "")
                ca = payload.get("correct_answer", payload.get("answer", ""))
                try:
                    check_ok = chk(ua, ca, question_payload=payload)
                except TypeError:
                    check_ok = chk(ua, ca)
                if check_ok is False:
                    all_blockers.append("runtime_smoke_check_failed")
                    break
            raw["samples_tested"] = seed + 1

        raw["payload_preview"] = {
            "problem_type_id": last_payload.get("problem_type_id"),
            "answer_type": last_payload.get("answer_type"),
            "answer_contract_answer_type": (last_payload.get("answer_contract") or {}).get("answer_type")
            if isinstance(last_payload.get("answer_contract"), dict)
            else None,
            "checker": last_payload.get("checker"),
            "equivalence": last_payload.get("equivalence"),
            "question_text_len": len(str(last_payload.get("question_text", ""))),
            "answer": last_payload.get("answer"),
            "correct_answer": last_payload.get("correct_answer"),
            "choices_count": len(last_payload.get("choices") or []),
            "metadata_keys": list((last_payload.get("metadata") or {}).keys())
            if isinstance(last_payload.get("metadata"), dict)
            else [],
        }
        if last_diagnostics:
            raw["validation_diagnostics"] = last_diagnostics
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
        if "invalid_answer_type" in str(ex):
            raw["failed_validator_name"] = raw.get("failed_validator_name") or "generator_semantic_safety"
        raw["interface_check"] = interface_check
        return raw
