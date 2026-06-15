from __future__ import annotations

import importlib.util
import random
import re
from pathlib import Path
from typing import Any

from core.checkers.choice_label_checker import check_choice_label
from core.checkers.interval_checker import check_interval_answer
from fractions import Fraction

def _find_project_root() -> Path:
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "skills").exists() or (parent / "generated_candidates").exists():
            return parent
    return p.parents[1]

PROJECT_ROOT = _find_project_root()
SKILL_ID = "vh_數學B1_PropertiesOfPerpendicularLines"
VERIFIED_CANDIDATE_MODULES = {'perpendicular_lines_properties': 'generated_candidates/vocational_math_b1/section_2_1/perpendicular_lines_properties/candidate_v1.py'}
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


def generate(level: int = 1, seed: int | None = None, difficulty: int | None = None) -> dict[str, Any]:
    pts = [pt for pt in VERIFIED_CANDIDATE_MODULES.keys() if pt not in set(MANUAL_REVIEW_EXCLUSIONS)]
    if not pts:
        raise RuntimeError("No verified deterministic problem types available.")
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
