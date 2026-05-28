from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

from core.gencode.problem_type_spec import load_problem_type_spec
from core.gencode.validators import validate_generator_payload

REGISTRY_PATH = Path("configs/generated_registry/b1_section_1_1_verified_registry.v0.1.yaml")
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
_LAST_INDEX_BY_SKILL: dict[str, int] = {}


def _read_registry_verified_entries() -> list[dict[str, Any]]:
    if not REGISTRY_PATH.exists():
        return []
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        entries = data.get("verified_problem_types") or []
        if isinstance(entries, list):
            out: list[dict[str, Any]] = []
            for it in entries:
                if isinstance(it, dict):
                    out.append(it)
                elif isinstance(it, str):
                    out.append({"problem_type_id": it})
            return out
    except Exception:
        pass

    # fallback for simple yaml-like text
    blocks = re.split(r"\n\s*-\s*\n", text)
    out: list[dict[str, Any]] = []
    for b in blocks:
        if "problem_type_id:" not in b:
            continue
        pt = re.search(r"problem_type_id:\s*\"?([^\n\"]+)\"?", b)
        sid = re.search(r"skill_id:\s*\"?([^\n\"]+)\"?", b)
        cp = re.search(r"candidate_path:\s*\"?([^\n\"]+)\"?", b)
        if pt:
            out.append(
                {
                    "problem_type_id": pt.group(1).strip(),
                    "skill_id": sid.group(1).strip() if sid else "",
                    "candidate_path": cp.group(1).strip() if cp else "",
                    "status": "verified",
                }
            )
    return out


def _resolve_candidate(entry: dict[str, Any]) -> Path | None:
    cp = entry.get("candidate_path")
    if isinstance(cp, str) and cp.strip():
        p = Path(cp)
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.exists():
            return p
    pt = entry.get("problem_type_id")
    if not isinstance(pt, str):
        return None
    pdir = GENERATED_BASE / pt
    cands = sorted(pdir.glob("candidate_v*.py"))
    return cands[-1] if cands else None


def load_verified_candidates(skill_id: str) -> list[dict[str, Any]]:
    entries = _read_registry_verified_entries()
    out: list[dict[str, Any]] = []
    for e in entries:
        if e.get("skill_id") and e.get("skill_id") != skill_id:
            continue
        candidate = _resolve_candidate(e)
        if candidate is None:
            continue
        out.append(
            {
                "skill_id": skill_id,
                "problem_type_id": str(e.get("problem_type_id", "")),
                "candidate_path": str(candidate),
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
    pt = str(payload.get("problem_type_id", "")).strip()
    spec = load_problem_type_spec(expected_skill_id, pt)
    if spec:
        errors = validate_generator_payload(payload, problem_type_spec=spec)
        if errors:
            raise ValueError(f"ProblemType contract validation failed: {','.join(errors)}")


def _adapt_payload(payload: dict[str, Any]) -> dict[str, Any]:
    solution_steps = payload.get("solution_steps") or []
    explanation = "\n".join(str(x) for x in solution_steps) if isinstance(solution_steps, list) else str(solution_steps)
    adapted = dict(payload)
    adapted["question"] = payload.get("question_text", "")
    adapted["correct_answer"] = payload.get("answer")
    adapted["explanation"] = explanation
    adapted.setdefault("choices", [])
    return adapted


def generate_from_verified_candidate(skill_id: str, seed=None, difficulty: str = "easy") -> dict[str, Any]:
    candidates = load_verified_candidates(skill_id)
    if not candidates:
        raise RuntimeError(NOT_ENABLED_MESSAGE)
    idx = _LAST_INDEX_BY_SKILL.get(skill_id, -1)
    idx = (idx + 1) % len(candidates)
    _LAST_INDEX_BY_SKILL[skill_id] = idx
    selected = candidates[idx]
    module = load_candidate_module(selected["candidate_path"])
    if not hasattr(module, "generate"):
        raise RuntimeError("Verified candidate missing generate()")
    payload = module.generate(seed=seed, difficulty=difficulty)
    if not isinstance(payload, dict):
        raise ValueError("Candidate generate() must return dict payload")
    _validate_payload(payload, expected_skill_id=skill_id)
    return _adapt_payload(payload)
