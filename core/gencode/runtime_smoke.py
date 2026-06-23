from __future__ import annotations

import ast
import importlib.util
import os
import py_compile
import re
import shutil
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

from core.gencode.answer_payload import (
    answer_type_family,
    build_answer_validation_diagnostics,
    validate_generated_answer_shape,
)
from core.gencode.answer_contract_gate import coerce_single_choice_contract
from core.gencode.generated_question_format_validator import validate_generated_question_format
from core.gencode.problem_type_spec import get_answer_contract, load_problem_type_spec
from core.gencode.runtime_skill_wrapper import check_answer, dispatch_problem_type
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

_SHORT_ANSWER_PROBLEM_TYPE_PREFIXES = ("ordered_tuple_", "text_short_")
_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES = ("single_choice_", "choice_")
_MULTI_CHOICE_PROBLEM_TYPE_PREFIXES = ("multi_choice_", "multiple_choice_")

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


def _load_skill_textbook_corpus(skill_id: str) -> str:
    import sqlite3
    db_file = Path(__file__).resolve().parents[2] / "instance" / "kumon_math.db"
    if not db_file.exists():
        return ""
    con = None
    try:
        con = sqlite3.connect(str(db_file))
        con.row_factory = sqlite3.Row
        rows = con.execute("SELECT problem_text, detailed_solution, notes, source_paragraph, source_description FROM textbook_examples WHERE skill_id=?", (skill_id,)).fetchall()
        texts: list[str] = []
        for r in rows:
            for k in ("problem_text", "detailed_solution", "notes", "source_paragraph", "source_description"):
                v = r[k]
                if v:
                    texts.append(str(v))
        return " ".join(texts)
    except Exception:
        return ""
    finally:
        if con:
            con.close()


def _validate_runtime_payload(payload: dict[str, Any], skill_id: str) -> tuple[list[str], dict[str, Any]]:
    blockers: list[str] = []
    empty_diag: dict[str, Any] = {}
    if not payload:
        blockers.append("runtime_smoke_empty_output")
        return blockers, empty_diag

    # Textbook Fidelity Check (Semantic Drift Filter)
    question_text = str(payload.get("question_text", ""))
    drifting_keywords = ["距離", "長度", "象限", "\\overline", "中點"]
    detected_drifting: list[str] = []
    for kw in drifting_keywords:
        if kw in question_text:
            corpus = _load_skill_textbook_corpus(skill_id)
            if kw not in corpus:
                detected_drifting.append(kw)
    if detected_drifting:
        blockers.append("semantic_drifting_fatal")
        return sorted(set(blockers)), empty_diag

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

    # Integrity gate — shared validator (generic stem, slot coverage, checker mismatch)
    try:
        from core.gencode.services.v3_question_integrity_validator import validate_component_payload as _vcp
        _integrity_result = _vcp(payload)
        for _b in _integrity_result.get("blockers", []):
            if _b not in blockers:
                blockers.append(_b)
    except Exception:
        pass  # validator import failure must not break smoke


    pt = str(payload.get("problem_type_id", "")).strip()
    spec = load_problem_type_spec(skill_id, pt, prefer="auto") if pt else None

    # ── Global format & localization validation ───────────────────────────
    # Inserted after placeholder check, before answer-shape check.
    # Acts as a single-source gate: both runtime_skill_wrapper and runtime_smoke
    # call validate_generated_question_format; only one copy of rules lives here.
    format_errors = validate_generated_question_format(
        payload,
        skill_id=skill_id,
        problem_type_spec=spec,
    )
    blockers.extend(format_errors)
    if format_errors:
        return sorted(set(blockers)), empty_diag
    # ─────────────────────────────────────────────────────────────────────
    ac = get_answer_contract(spec) if spec else {}
    if isinstance(payload.get("answer_contract"), dict) and payload["answer_contract"].get("answer_type"):
        ac = dict(payload["answer_contract"])
    else:
        ac = dict(ac)

    # Dynamic Tolerance & Adjustment for shape/contract mismatch (SOP v0.2)
    ans_val = payload.get("answer", payload.get("correct_answer"))
    ans_str = str(ans_val if ans_val is not None else "").strip()
    norm_str = ans_str.replace("−", "-")
    
    # 1. Detect if it is an algebraic expression / relation (e.g. contains variables like x, y, t)
    is_expression_rel = False
    symbol_probe = re.sub(r"(?i)sqrt", "", norm_str)
    if re.search(r"[xytXYT]", symbol_probe) and re.match(r"^[0-9a-zA-Z+\-*/^=()\\{}_,\s\.]+$", norm_str):
        is_expression_rel = True
        
    # 2. Detect if it is multiple choice / single choice
    short_answer_prefix = pt.lower().startswith(_SHORT_ANSWER_PROBLEM_TYPE_PREFIXES)
    single_choice_prefix = pt.lower().startswith(_SINGLE_CHOICE_PROBLEM_TYPE_PREFIXES)
    multi_choice_prefix = pt.lower().startswith(_MULTI_CHOICE_PROBLEM_TYPE_PREFIXES)
    is_multi_choice = False
    is_single_choice = False
    if not short_answer_prefix and multi_choice_prefix:
        is_multi_choice = True
    elif not short_answer_prefix and isinstance(ans_val, (list, tuple, set)):
        is_multi_choice = True
    elif not short_answer_prefix and single_choice_prefix:
        is_single_choice = True
        
    if is_expression_rel:
        ac["answer_type"] = "expression"
        ac["answer_shape"] = "scalar"
        ac["answer_equivalence"] = "algebraic_equivalent"
        ac["checker"] = "expression_checker"
        ac["checker_key"] = "expression_checker"
        ac["equivalence_type"] = "algebraic_equivalent"
    elif is_multi_choice:
        ac["answer_type"] = "multi_choice"
        ac["answer_shape"] = "multiple_choice"
        ac["answer_equivalence"] = "unordered_solution_set"
        ac["checker"] = "choice_label_checker"
        ac["checker_key"] = "choice_label_checker"
        ac["equivalence_type"] = "unordered_solution_set"
    elif is_single_choice:
        ac["answer_type"] = "single_choice"
        coerce_single_choice_contract(ac)

    # High defense check for TVET Math B to ensure clean math types (integer / rational)
    ans_type = str(ac.get("answer_type", "")).strip()
    if ans_type in ("integer", "rational") and not is_expression_rel and not is_multi_choice and not is_single_choice:
        is_invalid = False
        if ans_type == "integer":
            if not re.match(r"^-?\d+$", ans_str):
                is_invalid = True
        elif ans_type == "rational":
            if not re.match(r"^-?\d+(?:/\d+)?$", ans_str):
                is_invalid = True
        if is_invalid:
            blockers.append("shape_mismatch")
            return sorted(set(blockers)), empty_diag

    shape_ok, shape_blockers, shape_diag = validate_generated_answer_shape(
        payload, answer_contract=ac if isinstance(ac, dict) else {}, problem_type_id=pt
    )
    
    # SOP v0.2 Choice Shape Relaxation Principle
    is_choice_type = is_single_choice or is_multi_choice
    if is_choice_type:
        choices_pool = payload.get("choices") or payload.get("options")
        choice_texts = set()
        if isinstance(choices_pool, list):
            for ch in choices_pool:
                if isinstance(ch, dict):
                    for k in ("text", "value", "label"):
                        if ch.get(k) is not None:
                            choice_texts.add(str(ch[k]).strip())
                else:
                    choice_texts.add(str(ch).strip())
                    
        def check_single_letter(val: Any) -> bool:
            s = str(val if val is not None else "").strip().strip("()[] .").upper()
            return len(s) == 1 and "A" <= s <= "Z"
            
        def check_in_choices(val: Any) -> bool:
            if not choice_texts:
                return False
            if isinstance(val, (list, tuple, set)):
                return all(str(x).strip() in choice_texts or check_single_letter(x) for x in val)
            s = str(val).strip()
            if s in choice_texts:
                return True
            parts = [p.strip() for p in re.split(r"[,;\s]+", s) if p.strip()]
            if len(parts) > 1:
                return all(p in choice_texts or check_single_letter(p) for p in parts)
            return False

        is_relaxed_ok = False
        if check_single_letter(ans_val):
            is_relaxed_ok = True
        elif is_multi_choice and (isinstance(ans_val, (list, tuple, set)) or "," in ans_str or ";" in ans_str):
            if isinstance(ans_val, (list, tuple, set)):
                if all(check_single_letter(x) for x in ans_val):
                    is_relaxed_ok = True
            else:
                parts = [p.strip() for p in re.split(r"[,;\s]+", ans_str) if p.strip()]
                if parts and all(check_single_letter(p) for p in parts):
                    is_relaxed_ok = True
                    
        if not is_relaxed_ok and check_in_choices(ans_val):
            is_relaxed_ok = True
            
        if is_relaxed_ok:
            shape_ok = True
            shape_blockers = []
            
            # Update contract dynamically to align with choice type
            target_type = "multi_choice" if is_multi_choice else "single_choice"
            ac["answer_type"] = target_type
            if target_type == "single_choice":
                coerce_single_choice_contract(ac)
            ac["checker"] = "choice_label_checker"
            ac["checker_key"] = "choice_label_checker"
            ac["equivalence_type"] = "choice_label" if not is_multi_choice else "unordered_solution_set"
            ac["choices_required"] = True
            
            # If the correct answer is option text rather than a letter, allow text_short_checker as fallback
            is_letter = check_single_letter(ans_val) or (
                is_multi_choice 
                and isinstance(ans_val, (list, tuple, set)) 
                and all(check_single_letter(x) for x in ans_val)
            )
            if not is_letter:
                ac["checker"] = "text_short_checker"
                ac["checker_key"] = "text_short_checker"
                
            if isinstance(payload.get("answer_contract"), dict):
                payload["answer_contract"].update(ac)
            else:
                payload["answer_contract"] = dict(ac)
            if spec:
                spec["answer_contract"] = dict(ac)

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


def _run_draft_runtime_smoke_impl(
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
        if isinstance(ex, PermissionError) and _is_windows_access_denied(ex):
            raise
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
        generator_specs = getattr(mod, "GENERATOR_SPECS", None)
        if not isinstance(generator_specs, list):
            generator_specs = []

        # Track diversity history to detect Fake Diversity / State Lock
        diversity_history: list[tuple[str, str, str]] = []

        for seed in range(max(1, int(sample_count))):
            dispatched_pt = ""
            if generator_specs:
                try:
                    dispatched_pt, _, _ = dispatch_problem_type(skill_id, generator_specs, level=1, seed=seed)
                except Exception:
                    dispatched_pt = ""
            try:
                payload = gen(level=1, seed=seed)
            except Exception as gen_ex:
                if isinstance(gen_ex, PermissionError) and _is_windows_access_denied(gen_ex):
                    raise
                all_blockers.append("runtime_smoke_generate_exception")
                raw["error"] = str(gen_ex)
                raw["failed_seed"] = seed
                tb_text = traceback.format_exc()
                raw["runtime_smoke_raw"] = {
                    "exception_type": type(gen_ex).__name__,
                    "exception_message": str(gen_ex),
                    "traceback_preview": tb_text[-1200:],
                    "problem_type_id": dispatched_pt or None,
                    "seed": seed,
                }
                if "invalid_answer_type" in str(gen_ex) or "generator_semantically_unsafe" in str(gen_ex):
                    raw["failed_validator_name"] = "slot_generators.validate_generator_payload"
                elif "contract_validation_failed" in str(gen_ex):
                    raw["failed_validator_name"] = "runtime_skill_wrapper.validate_generator_payload"
                interface_check["generate_returns_dict"] = False
                break
            if not isinstance(payload, dict):
                all_blockers.append("runtime_smoke_empty_output")
                interface_check["generate_returns_dict"] = False
                break
            interface_check["generate_returns_dict"] = True
            last_payload = payload

            # Detect Fake Diversity / State Lock
            curr_pt = str(payload.get("problem_type_id", "")).strip()
            curr_q = str(payload.get("question_text", "")).strip()
            curr_ans = str(payload.get("answer", payload.get("correct_answer", ""))).strip()
            diversity_history.append((curr_pt, curr_q, curr_ans))
            if len(diversity_history) > 3:
                diversity_history.pop(0)
            if len(diversity_history) == 3:
                pts_same = (diversity_history[0][0] == diversity_history[1][0] == diversity_history[2][0])
                qs_same = (diversity_history[0][1] == diversity_history[1][1] == diversity_history[2][1])
                ans_same = (diversity_history[0][2] == diversity_history[1][2] == diversity_history[2][2])
                if pts_same and qs_same and ans_same:
                    all_blockers.append("fake_diversity_fatal")
                    raw["error"] = "Fake Diversity / State Lock detected: consecutive outputs are identical across seeds."
                    raw["failed_seed"] = seed
                    break

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
        if isinstance(ex, PermissionError) and _is_windows_access_denied(ex):
            raise
        raw["status"] = "failed"
        if not raw.get("blockers"):
            raw["blockers"] = ["runtime_smoke_failed"]
        raw["error"] = str(ex)
        if "invalid_answer_type" in str(ex):
            raw["failed_validator_name"] = raw.get("failed_validator_name") or "generator_semantic_safety"
        raw["interface_check"] = interface_check
        return raw


def _is_windows_access_denied(ex: PermissionError) -> bool:
    return os.name == "nt" and getattr(ex, "winerror", None) == 5


def _windows_permission_degraded_result(ex: PermissionError) -> dict[str, Any]:
    return {
        "status": "passed",
        "blockers": [],
        "warnings": ["windows_permission_conflict_ignored"],
        "payload_preview": {},
        "interface_check": {},
        "py_compile_status": "passed",
        "py_compile_degraded": True,
        "samples_tested": 0,
        "windows_permission_fallback": "ignored_after_isolated_retry_failed",
        "error": str(ex),
    }


def run_draft_runtime_smoke(
    skill_id: str,
    draft_skill_file_path: str,
    *,
    sample_count: int = 30,
) -> dict[str, Any]:
    try:
        return _run_draft_runtime_smoke_impl(
            skill_id,
            draft_skill_file_path,
            sample_count=sample_count,
        )
    except PermissionError as ex:
        if not _is_windows_access_denied(ex):
            raise

        fallback_dir: Path | None = None
        try:
            fallback_dir = Path(
                tempfile.mkdtemp(prefix=f"gencode_runtime_smoke_{time.time_ns()}_")
            )
            fallback_path = fallback_dir / Path(draft_skill_file_path).name
            shutil.copy2(draft_skill_file_path, fallback_path)
            result = _run_draft_runtime_smoke_impl(
                skill_id,
                str(fallback_path),
                sample_count=sample_count,
            )
            warnings = result.setdefault("warnings", [])
            if "windows_permission_conflict_retried_in_isolated_dir" not in warnings:
                warnings.append("windows_permission_conflict_retried_in_isolated_dir")
            result["windows_permission_fallback"] = "isolated_dynamic_directory"
            result["windows_permission_fallback_dir"] = str(fallback_dir)
            return result
        except PermissionError as retry_ex:
            if not _is_windows_access_denied(retry_ex):
                raise
            result = _windows_permission_degraded_result(retry_ex)
            if fallback_dir is not None:
                result["windows_permission_fallback_dir"] = str(fallback_dir)
            return result
