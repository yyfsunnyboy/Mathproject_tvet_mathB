from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PT_SUFFIX = re.compile(r"_\d+$")

SPEC_PATH = Path("configs/problem_type_specs/problem_type_specs.v1.json")
INDUCED_DIR = Path("reports/gencode_closed_loop/induced_specs")
_SPECS_CACHE: dict[tuple[str, str], dict[str, Any]] | None = None
_INDUCED_BY_SKILL: dict[str, list[dict[str, Any]]] = {}


def _load_all_items() -> list[dict[str, Any]]:
    if not SPEC_PATH.exists():
        return []
    data = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else []
    return [x for x in items if isinstance(x, dict)]


def _ensure_cache() -> dict[tuple[str, str], dict[str, Any]]:
    global _SPECS_CACHE
    if _SPECS_CACHE is None:
        _SPECS_CACHE = {}
        for it in _load_all_items():
            sid = str(it.get("skill_id", "")).strip()
            pt = str(it.get("problem_type_id", "")).strip()
            if sid and pt:
                _SPECS_CACHE[(sid, pt)] = it
    return _SPECS_CACHE


def _induced_path(skill_id: str) -> Path:
    safe = skill_id.replace("/", "_").replace("\\", "_")
    return INDUCED_DIR / f"{safe}.json"


def _resolve_induced_path(skill_id: str) -> Path | None:
    path = _induced_path(skill_id)
    if path.exists():
        return path
    tail = str(skill_id).strip().split("_")[-1]
    if tail:
        matches = sorted(INDUCED_DIR.glob(f"*{tail}.json"))
        if matches:
            return matches[0]
    return None


def _problem_type_id_matches(spec_pt: str, query_pt: str) -> bool:
    a = str(spec_pt).strip()
    b = str(query_pt).strip()
    if not a or not b:
        return False
    if a == b:
        return True
    if a.startswith(f"{b}_") or b.startswith(f"{a}_"):
        return True
    return _PT_SUFFIX.sub("", a) == _PT_SUFFIX.sub("", b)


def save_induced_problem_type_specs(skill_id: str, specs: list[dict[str, Any]]) -> Path:
    sid = str(skill_id).strip()
    INDUCED_DIR.mkdir(parents=True, exist_ok=True)
    path = _induced_path(sid)
    payload = {"skill_id": sid, "spec_source": "phase1_induced_draft", "items": [s for s in specs if isinstance(s, dict)]}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _INDUCED_BY_SKILL[sid] = list(payload["items"])
    return path


def load_induced_problem_type_specs(skill_id: str) -> list[dict[str, Any]]:
    sid = str(skill_id).strip()
    if sid in _INDUCED_BY_SKILL and _INDUCED_BY_SKILL[sid]:
        return list(_INDUCED_BY_SKILL[sid])
    path = _resolve_induced_path(sid)
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else []
    specs = [x for x in items if isinstance(x, dict)]
    _INDUCED_BY_SKILL[sid] = specs
    return specs


def list_problem_types_for_skill(skill_id: str, *, prefer: str = "auto") -> list[dict[str, Any]]:
    sid = str(skill_id).strip()
    mode = str(prefer or "auto").strip()
    induced = load_induced_problem_type_specs(sid)
    curated = [spec for (s, _), spec in sorted(_ensure_cache().items()) if s == sid]
    if mode == "induced":
        return induced
    if mode == "curated":
        return curated
    return induced if induced else curated


def load_problem_type_spec(skill_id: str, problem_type_id: str, *, prefer: str = "auto") -> dict[str, Any] | None:
    sid = str(skill_id).strip()
    pt = str(problem_type_id).strip()
    mode = str(prefer or "auto").strip()
    if mode in {"auto", "induced"}:
        for spec in load_induced_problem_type_specs(sid):
            if _problem_type_id_matches(str(spec.get("problem_type_id", "")).strip(), pt):
                return spec
        for spec in _scan_induced_specs_by_problem_type(pt):
            if _problem_type_id_matches(str(spec.get("problem_type_id", "")).strip(), pt):
                return spec
    if mode != "induced":
        return _ensure_cache().get((sid, pt))
    return None


def _scan_induced_specs_by_problem_type(problem_type_id: str) -> list[dict[str, Any]]:
    pt = str(problem_type_id).strip()
    if not pt or not INDUCED_DIR.exists():
        return []
    found: list[dict[str, Any]] = []
    for path in INDUCED_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        items = data.get("items") if isinstance(data, dict) else []
        for it in items:
            if isinstance(it, dict) and _problem_type_id_matches(str(it.get("problem_type_id", "")).strip(), pt):
                found.append(it)
    return found


def get_answer_contract(spec: dict[str, Any]) -> dict[str, Any]:
    ac = spec.get("answer_contract")
    return ac if isinstance(ac, dict) else {}


def get_stem_contract(spec: dict[str, Any]) -> dict[str, Any]:
    sc = spec.get("stem_contract")
    return sc if isinstance(sc, dict) else {}


def get_dependency_contract(spec: dict[str, Any]) -> dict[str, Any]:
    dc = spec.get("dependency_contract")
    return dc if isinstance(dc, dict) else {}


def get_semantic_contract(spec: dict[str, Any]) -> dict[str, Any]:
    sc = spec.get("semantic_contract")
    return sc if isinstance(sc, dict) else {}


def get_generator_contract(spec: dict[str, Any]) -> dict[str, Any]:
    gc = spec.get("generator_contract")
    return gc if isinstance(gc, dict) else {}


def get_template_slot(spec: dict[str, Any]) -> str:
    gc = get_generator_contract(spec)
    slots = gc.get("template_slots") if isinstance(gc.get("template_slots"), dict) else {}
    return str(slots.get("stem", "")).strip()


# build_generator_plan_prompt and build_generator_code_prompt are defined here
# and re-exported via problem_type_contracts.py as a backward-compatible facade.


def build_generator_plan_prompt(spec: dict[str, Any]) -> str:
    pt = str(spec.get("problem_type_id", ""))
    return (
        f"problem_type_id={pt}\n"
        f"answer_contract={json.dumps(get_answer_contract(spec), ensure_ascii=False)}\n"
        f"stem_contract={json.dumps(get_stem_contract(spec), ensure_ascii=False)}\n"
        f"dependency_contract={json.dumps(get_dependency_contract(spec), ensure_ascii=False)}\n"
        f"semantic_contract={json.dumps(get_semantic_contract(spec), ensure_ascii=False)}\n"
        f"generator_contract={json.dumps(get_generator_contract(spec), ensure_ascii=False)}\n"
    )


def build_generator_code_prompt(spec: dict[str, Any], examples_context: str = "") -> str:
    ac = get_answer_contract(spec)
    gc = get_generator_contract(spec)
    return (
        "=== SYSTEM PROMPT CONSTRAINTS ===\n"
        "1. STRICT SKELETAL ALIGNMENT: The generated question text, math structure, and core formula must 100% strictly align with the core textual and structural features of the provided source_examples.\n"
        "2. ZERO UNRELATED MATH CONSTRUCTS: You are strictly forbidden from introducing math formulas or concepts that are outside the current ProblemTypeSpec definition. For example, in a linear function unit, you must NOT generate code involving 'distance between two points', 'midpoint coordinates', or 'determining quadrants'.\n"
        "3. SAFE RANDOMIZATION ONLY: Randomization is strictly limited to numeric constants, coefficients, and scenario wording. You must NOT alter the mathematical skeleton, target task, or formula structure of the question.\n"
        "4. MULTI-TEMPLATE PRINCIPLE: You must NEVER generate only a single default stem. If the source examples have graph features (has_graph) or contextual applications (contextual_application), you MUST declare multiple template_slots (e.g., plot_graph_slot, intercept_judge_slot, word_problem_slot) in the generated Python code. Randomization of scenarios is allowed and encouraged to replace contexts (e.g. mobile phone tariff -> water tariff or internet data tariff), maintaining the overall structural context of the textbook.\n"
        "5. STEM COMPLETENESS & SOUL TOKENS: Any generated string for question_text must be a fully cohesive, human-readable textbook problem. It is strictly forbidden to output truncated stubs or generic placeholders. For choice-based or fallback problem types (e.g., 4515 single choice, 4500 word problems), the question_text must explicitly construct the mathematical conditions (e.g., passing coordinates, full contextual application stories) and must contain the soul mathematical tokens of the unit (such as '線型函數', 'f(x)', '通過'). The total length of question_text must be robust enough to reflect a complete and verbose mathematical scenario. EVERY random branch, scenario conditional, or fallback string assignment within the generated generate(seed) function MUST explicitly construct a fully descriptive problem. Truncating text in ANY code path is strictly prohibited. The final runtime length of question_text for EVERY generated seed MUST be robust and naturally exceed 30 characters under all randomization paths, ensuring no empty or minimalist stubs can ever be evaluated.\n"
        "=================================\n\n"
        "Generate Python generate() using this ProblemTypeSpec only.\n"
        "Flow: generator_plan comment -> generate() implementation.\n"
        f"problem_type_id: {spec.get('problem_type_id')}\n"
        f"display_name: {spec.get('display_name')}\n"
        f"answer_contract: {json.dumps(ac, ensure_ascii=False)}\n"
        f"stem_contract: {json.dumps(get_stem_contract(spec), ensure_ascii=False)}\n"
        f"dependency_contract: {json.dumps(get_dependency_contract(spec), ensure_ascii=False)}\n"
        f"semantic_contract: {json.dumps(get_semantic_contract(spec), ensure_ascii=False)}\n"
        f"generator_contract: {json.dumps(gc, ensure_ascii=False)}\n"
        "Return dict keys: question_text, answer, answer_type, choices, explanation, "
        "problem_type_id, diagnosis_tags, metadata.givens, metadata.target, metadata.derivation.\n"
        "Do not embed (A)(B)(C)(D) in question_text when choices is non-empty.\n"
        f"examples:\n{examples_context}\n"
    )
