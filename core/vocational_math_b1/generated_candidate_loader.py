from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path("configs/generated_registry/b1_section_1_1_verified_registry.v0.1.yaml")
PROBLEM_TYPES_PATH = Path(
    "agent_skills_v2/vocational_math_b1/chapter_1/section_1_1_number_line_absolute_value/problem_types.yaml"
)
GENERATED_BASE = Path("generated_candidates/vocational_math_b1/section_1_1")
REQUIRED_KEYS = {
    "problem_type_id",
    "skill_id",
    "question_text",
    "answer",
    "answer_type",
    "checker_type",
    "solution_steps",
    "metadata",
}
NOT_ENABLED_MESSAGE = "此技能尚未開放自動出題"


def _read_registry_verified_problem_types() -> list[str]:
    if not REGISTRY_PATH.exists():
        return []
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        return list(data.get("verified_problem_types") or [])
    except Exception:
        pass
    m = re.search(r"verified_problem_types:\s*((?:\n\s*-\s*.+)+)", text)
    if not m:
        return []
    return [line.split("-", 1)[1].strip().strip('"').strip("'") for line in m.group(1).splitlines() if "-" in line]


def _read_problem_type_skill_map() -> dict[str, str]:
    if not PROBLEM_TYPES_PATH.exists():
        return {}
    text = PROBLEM_TYPES_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        items = data.get("items") or []
        return {str(item.get("problem_type_id")): str(item.get("skill_id")) for item in items if item.get("problem_type_id")}
    except Exception:
        mapping: dict[str, str] = {}
        blocks = re.split(r"\n\s*-\s*\n", text)
        for b in blocks:
            pt = re.search(r"problem_type_id:\s*\"?([^\n\"]+)\"?", b)
            sid = re.search(r"skill_id:\s*\"?([^\n\"]+)\"?", b)
            if pt and sid:
                mapping[pt.group(1).strip()] = sid.group(1).strip()
        return mapping


def _resolve_latest_candidate(problem_type_id: str) -> Path | None:
    pdir = GENERATED_BASE / problem_type_id
    if not pdir.exists():
        return None
    candidates = sorted(pdir.glob("candidate_v*.py"))
    return candidates[-1] if candidates else None


def load_verified_candidates(skill_id: str) -> list[dict[str, Any]]:
    verified_problem_types = _read_registry_verified_problem_types()
    pt_skill_map = _read_problem_type_skill_map()
    out: list[dict[str, Any]] = []
    for pt in verified_problem_types:
        if pt_skill_map.get(pt) != skill_id:
            continue
        candidate_path = _resolve_latest_candidate(pt)
        if candidate_path is None:
            continue
        out.append(
            {
                "skill_id": skill_id,
                "problem_type_id": pt,
                "candidate_path": str(candidate_path),
                "status": "verified",
            }
        )
    return out


def load_candidate_module(candidate_path: str):
    path = Path(candidate_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load candidate module: {candidate_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_payload(payload: dict[str, Any], expected_skill_id: str) -> None:
    missing = [k for k in REQUIRED_KEYS if k not in payload]
    if missing:
        raise ValueError(f"Generated payload missing keys: {', '.join(missing)}")
    if payload.get("skill_id") != expected_skill_id:
        raise ValueError("Generated payload skill_id mismatch")


def _adapt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    solution_steps = payload.get("solution_steps") or []
    explanation = "\n".join(str(x) for x in solution_steps) if isinstance(solution_steps, list) else str(solution_steps)
    answer = payload.get("answer")
    adapted = dict(payload)
    adapted["question"] = payload.get("question_text", "")
    adapted["correct_answer"] = answer
    adapted["explanation"] = explanation
    if "choices" not in adapted:
        adapted["choices"] = []
    return adapted


def generate_from_verified_candidate(skill_id: str, seed=None, difficulty: str = "easy") -> dict[str, Any]:
    candidates = load_verified_candidates(skill_id)
    if not candidates:
        raise RuntimeError(NOT_ENABLED_MESSAGE)
    selected = candidates[0]
    module = load_candidate_module(selected["candidate_path"])
    if not hasattr(module, "generate"):
        raise RuntimeError("Verified candidate missing generate()")
    payload = module.generate(seed=seed, difficulty=difficulty)
    if not isinstance(payload, dict):
        raise ValueError("Candidate generate() must return dict payload")
    _validate_payload(payload, expected_skill_id=skill_id)
    return _adapt_payload(payload)

