from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def discover_generator_candidates(skill_id: str, problem_type_ids: list[str], generator_catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    discovered_candidates: list[dict[str, str]] = []
    missing_candidate_files: list[dict[str, str]] = []
    unsupported_candidate_problem_types: list[str] = []
    for pt in problem_type_ids:
        cfg = generator_catalog.get(pt) or {}
        module_path = str(cfg.get("module_path", "")).strip()
        if not module_path:
            unsupported_candidate_problem_types.append(pt)
            continue
        abs_path = PROJECT_ROOT / module_path
        if abs_path.exists():
            discovered_candidates.append({"problem_type_id": pt, "module_path": module_path})
        else:
            missing_candidate_files.append({"problem_type_id": pt, "module_path": module_path})
    return {
        "skill_id": skill_id,
        "discovered_candidates": discovered_candidates,
        "missing_candidate_files": missing_candidate_files,
        "unsupported_candidate_problem_types": sorted(set(unsupported_candidate_problem_types)),
    }


def verify_generator_candidate(candidate_path: str, expected_skill_id: str, expected_problem_type_id: str, answer_contract: dict[str, Any], sample_count: int = 10) -> dict[str, Any]:
    abs_path = PROJECT_ROOT / candidate_path
    failure_reasons: list[str] = []
    if not abs_path.exists():
        return {"ok": False, "failure_reasons": ["candidate_file_missing"], "sample_count": 0}
    try:
        spec = importlib.util.spec_from_file_location(f"cand_{expected_problem_type_id}", str(abs_path))
        if not spec or not spec.loader:
            return {"ok": False, "failure_reasons": ["candidate_import_spec_invalid"], "sample_count": 0}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        return {"ok": False, "failure_reasons": [f"candidate_import_failed:{e}"], "sample_count": 0}

    generate_fn = getattr(mod, "generate", None)
    check_fn = getattr(mod, "check", None)
    if not callable(generate_fn):
        failure_reasons.append("missing_generate_function")
    if not callable(check_fn):
        failure_reasons.append("missing_check_function")
    if failure_reasons:
        return {"ok": False, "failure_reasons": failure_reasons, "sample_count": 0}

    produced = None
    try:
        produced = generate_fn(level=1, seed=1)
    except Exception as e:
        return {"ok": False, "failure_reasons": [f"generate_crashed:{e}"], "sample_count": 0}
    if not isinstance(produced, dict):
        return {"ok": False, "failure_reasons": ["generate_payload_not_dict"], "sample_count": 1}

    if str(produced.get("skill_id", "")).strip() != expected_skill_id:
        failure_reasons.append("skill_id_mismatch")
    if str(produced.get("problem_type_id", "")).strip() != expected_problem_type_id:
        failure_reasons.append("problem_type_id_mismatch")
    if not (str(produced.get("question_text", "")).strip() or str(produced.get("question", "")).strip()):
        failure_reasons.append("missing_question_text")
    if "answer" not in produced or "correct_answer" not in produced:
        failure_reasons.append("missing_answer_or_correct_answer")
    payload_contract = produced.get("answer_contract", {})
    if not isinstance(payload_contract, dict):
        failure_reasons.append("missing_answer_contract")
    else:
        expected_eq = str((answer_contract or {}).get("equivalence_type", "")).strip()
        got_eq = str(payload_contract.get("equivalence_type", "")).strip()
        if expected_eq and got_eq != expected_eq:
            failure_reasons.append("answer_contract_mismatch")
    try:
        chk = check_fn(produced.get("correct_answer"), produced.get("correct_answer"))
        ok_check = bool(chk.get("correct")) if isinstance(chk, dict) else bool(chk)
        if not ok_check:
            failure_reasons.append("self_check_failed")
    except Exception as e:
        failure_reasons.append(f"check_crashed:{e}")

    generated_samples = 1
    for i in range(sample_count):
        try:
            _ = generate_fn(level=1, seed=100 + i)
            generated_samples += 1
        except Exception as e:
            failure_reasons.append(f"sample_generate_crashed:{e}")
            break

    return {"ok": not failure_reasons, "failure_reasons": failure_reasons, "sample_count": generated_samples}
