from __future__ import annotations

import importlib.util
import random
import re
from pathlib import Path
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.interval_checker import check_interval_answer
from fractions import Fraction

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
VERIFIED_CANDIDATE_MODULES = {'short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2': 'generated_candidates/vocational_math_b1/section_1_1/short_answer_compute_distance_between_two_points_coordinate_point_distance_formu_2/candidate_v1.py', 'short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2': 'generated_candidates/vocational_math_b1/section_1_1/short_answer_solve_unknown_coordinate_from_two_point_distance_coordinate_point_d_2/candidate_v1.py'}
MANUAL_REVIEW_EXCLUSIONS = []
_STATE = {"idx": 0}


def _load_candidate(module_rel_path: str):
    abs_path = PROJECT_ROOT / module_rel_path
    spec = importlib.util.spec_from_file_location("cand_" + abs_path.stem + str(abs_path), str(abs_path))
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot import candidate: {module_rel_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate(
    level: int = 1,
    seed: int | None = None,
    difficulty: int | None = None,
    component_id: str | None = None,
    problem_type_id: str | None = None,
    **kwargs
) -> dict[str, Any]:
    pts = [pt for pt in VERIFIED_CANDIDATE_MODULES.keys() if pt not in set(MANUAL_REVIEW_EXCLUSIONS)]
    if not pts:
        raise RuntimeError("No verified deterministic problem types available.")
        
    # Build dynamic component mapping
    comp_map = {}
    for pt in pts:
        try:
            cand_mod = _load_candidate(VERIFIED_CANDIDATE_MODULES[pt])
            sample = cand_mod.generate(seed=1)
            cid = sample.get("component_id") or (sample.get("metadata") or {}).get("component_id")
            if cid:
                comp_map[str(cid).strip()] = pt
            ex_id = (sample.get("metadata") or {}).get("textbook_example_id")
            if ex_id:
                comp_map[str(ex_id).strip()] = pt
                comp_map[f"src_{ex_id}"] = pt
        except Exception:
            pass

    # Routing logic
    if component_id is not None:
        cid_str = str(component_id).strip()
        if cid_str not in comp_map:
            raise KeyError(f"System routing error: component_id {component_id} is not verified or does not exist.")
        pt = comp_map[cid_str]
    elif problem_type_id is not None:
        pt_str = str(problem_type_id).strip()
        if pt_str not in pts:
            raise KeyError(f"System routing error: problem_type_id {problem_type_id} is not verified or does not exist.")
        pt = pt_str
    else:
        if seed is None:
            idx = _STATE["idx"] % len(pts)
            _STATE["idx"] += 1
        else:
            idx = random.Random(seed).randint(0, len(pts) - 1)
        pt = pts[idx]

    mod = _load_candidate(VERIFIED_CANDIDATE_MODULES[pt])
    payload = mod.generate(level=level, seed=seed, difficulty=difficulty)
    if not isinstance(payload, dict):
        raise RuntimeError("candidate.generate must return dict")
        
    from core.gencode.answer_payload import finalize_generator_payload
    from scripts.gencode_pipeline_phase1_audit import ANSWER_CONTRACT_DEFAULTS
    
    contract = ANSWER_CONTRACT_DEFAULTS.get(SKILL_ID, {}).get(pt)
    if contract:
        payload = finalize_generator_payload(payload, contract)
        
    payload["skill_id"] = SKILL_ID
    payload["metadata"] = payload.get("metadata", {})
    payload["metadata"]["verified_problem_types"] = pts
    payload["metadata"]["manual_review_exclusions"] = MANUAL_REVIEW_EXCLUSIONS
    payload["metadata"]["source"] = "gencode_runtime_binding"
    return payload



def check(user_answer: object, correct_answer: object, current_question: dict[str, Any] | None = None) -> dict[str, Any]:
    cq = current_question or {}
    contract = cq.get("answer_contract", {}) if isinstance(cq, dict) else {}
    eq = str((contract or {}).get("equivalence_type", "")).strip()
    if eq == "interval_set":
        def _norm(v: object) -> str:
            s = str(v)
            def _repl(m):
                try:
                    return str(float(Fraction(m.group(0))))
                except Exception:
                    return m.group(0)
            return re.sub(r"-?\d+/\d+", _repl, s)
        return {"correct": bool(check_interval_answer(_norm(user_answer), _norm(correct_answer)))}
    if eq == "choice_label":
        choices = list(cq.get("choices", [])) if isinstance(cq, dict) else []
        if not choices:
            choices = ["A", "B", "C", "D"]
        return {"correct": bool(check_choice_label(user_answer, correct_answer, choices))}
    return {"correct": str(user_answer).strip() == str(correct_answer).strip()}
