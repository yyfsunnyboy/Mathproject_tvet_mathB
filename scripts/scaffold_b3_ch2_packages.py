# -*- coding: utf-8 -*-
"""Write B3 Ch2 skill wrappers and v3 packages from SOURCE_SPECS."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from core.domain.equation_solving_domain import SOURCE_SPECS

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
V3 = ROOT / "agent_skills_v3"

GENERATE_PY = '''from __future__ import annotations

from typing import Any

from core.domain.equation_solving_domain import build_equation_solving_matrix
from core.gencode.equation_solving_capability_adapter import adapt_equation_solving_matrix

PRESENTATION_MODE = {presentation!r}
ANSWER_TYPE = {answer_type!r}
PROBLEM_TYPE_ID = {op!r}
TEXTBOOK_EXAMPLE_ID = {example_id}
DEFAULT_COMPONENT_ID = "src_{example_id}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    difficulty_profile = "easy"
    if difficulty := kwargs.get("difficulty"):
        try:
            d = int(difficulty)
            difficulty_profile = "hard" if d >= 3 else ("medium" if d == 2 else "easy")
        except Exception:
            difficulty_profile = str(difficulty)
    constraints = {{
        "skill_id": {skill_id!r},
        "problem_type_id": PROBLEM_TYPE_ID,
        "required_capabilities": [PROBLEM_TYPE_ID],
        "source_example_id": TEXTBOOK_EXAMPLE_ID,
        "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
        "presentation_mode": PRESENTATION_MODE,
        "answer_type": ANSWER_TYPE,
    }}
    matrix = build_equation_solving_matrix(
        operation=PROBLEM_TYPE_ID,
        domain_operation=PROBLEM_TYPE_ID,
        constraints=constraints,
        seed=seed,
        curriculum_profile="vocational_high_b",
        difficulty_profile=difficulty_profile,
    )
    payload = adapt_equation_solving_matrix(
        matrix,
        domain_operation=PROBLEM_TYPE_ID,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        component_id=str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID),
        textbook_example_id=TEXTBOOK_EXAMPLE_ID,
        seed=seed,
    )
    payload["component_id"] = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID)
    payload["seed"] = seed
    payload["domain_matrix"] = matrix
    return payload
'''

HINT_PY = '''from __future__ import annotations
from typing import Any


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = [
        "先確認未知數，並把條件寫成等式或不等式。",
        "用精確分數運算；移項時注意係數正負與不等號方向。",
        "代回原條件，確認解的個數與範圍。",
    ]
    idx = max(0, min(int(step) - 1, len(steps) - 1))
    return steps[idx]
'''

METADATA_PY = '''from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "src_{example_id}"
SKILL_ID: Final[str] = {skill_id!r}
SOURCE_REF: Final[str] = "src_{example_id}"
SOURCE_KIND: Final[str] = {source_kind!r}
TEXTBOOK_EXAMPLE_ID: Final[int] = {example_id}
IS_REQUIRED_CORE: Final[bool] = True
ORDER_WEIGHT: Final[int] = 10
DIFFICULTY_LEVEL: Final[str] = "medium"
DOMAIN_OPERATION: Final[str] = {op!r}
ANSWER_SCHEMA_KEY: Final[str] = ""
LINE_TYPE: Final[str] = {op!r}
TARGET_TASK: Final[str] = {op!r}
TEMPLATE_SLOT: Final[str] = {op!r}
PROBLEM_TYPE_ID: Final[str] = {op!r}
PRESENTATION_MODE: Final[str] = {presentation!r}
RESPONSE_MODE: Final[str] = {presentation!r}
INTERACTION_TYPE: Final[str] = {presentation!r}
ANSWER_VALUE_TYPE: Final[str] = {answer_type!r}
ANSWER_TYPE: Final[str] = {answer_type!r}
LEGACY_ANSWER_TYPE: Final[str] = {answer_type!r}
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.equation_solving_domain.build_equation_solving_matrix",
)
'''

ROUTER = r'''from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = {skill_id!r}
GENERATOR_KEYS = {keys!r}
GENERATOR_SPECS = {specs!r}
_COMPONENT_DISPATCH = {dispatch!r}
_V3_ROOT = Path(__file__).resolve().parent
_RR_CURSOR = 0
_SHUFFLED_CYCLE = None


def _component_sampling_weight(component_id: str) -> float:
    for row in GENERATOR_SPECS:
        if str(row.get("component_id") or "") == component_id:
            return float(row.get("sampling_weight", 1) or 1)
    return 1.0


def _ordered_generator_keys() -> list[str]:
    specs_by_id = {{str(row.get("component_id") or ""): row for row in GENERATOR_SPECS}}
    return sorted(GENERATOR_KEYS, key=lambda key: (int((specs_by_id.get(key) or {{}}).get("display_order", 0)), key))


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    module_name = f"v3_{{SKILL_ID}}_{{component_id}}_{{module_filename.replace('.py', '')}}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{{component_id}}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pick_component_id(seed: int | None = None, component_id: str | None = None) -> str:
    if component_id and component_id in _COMPONENT_DISPATCH:
        return component_id
    ordered = _ordered_generator_keys()
    if seed is None:
        global _RR_CURSOR, _SHUFFLED_CYCLE
        import random
        if _SHUFFLED_CYCLE is None or _RR_CURSOR >= len(_SHUFFLED_CYCLE):
            _SHUFFLED_CYCLE = list(ordered)
            random.shuffle(_SHUFFLED_CYCLE)
            _RR_CURSOR = 0
        picked = _SHUFFLED_CYCLE[_RR_CURSOR]
        _RR_CURSOR += 1
        return picked
    return ordered[int(seed) % len(ordered)]


def generate(level: int = 1, seed: int | None = None, component_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
    picked = _pick_component_id(seed=seed, component_id=component_id or kwargs.get("component_id"))
    module = _load_component_module(picked, "generate.py")
    payload = module.generate(level=level, seed=seed, component_id=picked, **kwargs)
    if isinstance(payload, dict):
        payload["component_id"] = picked
        payload.setdefault("skill_id", SKILL_ID)
    return payload


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> Any:
    from core.gencode.runtime_skill_wrapper import check_answer
    return check_answer(user_answer, correct_answer, payload=dict(question_payload or {{}}))


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = dict(question_payload or {{}})
    component_id = str(payload.get("component_id") or "")
    if component_id in _COMPONENT_DISPATCH:
        module = _load_component_module(component_id, "get_hint.py")
        return str(module.get_hint(step, payload) or "")
    return ""
'''

FACADE = '''from __future__ import annotations

from pathlib import Path
from typing import Any

from core.gencode.runtime_skill_wrapper import dispatch_check, dispatch_generate, dispatch_get_hint

SKILL_ID = {skill_id!r}
GENERATOR_KEYS = {keys!r}
GENERATOR_SPECS = {specs!r}


def _resolve_v3_package_root() -> str:
    return str((Path(__file__).resolve().parent.parent / "agent_skills_v3").resolve())


def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs: Any) -> dict[str, Any]:
    return dispatch_generate(
        SKILL_ID, GENERATOR_KEYS, GENERATOR_SPECS,
        v3_package_root=_resolve_v3_package_root(),
        level=level, seed=seed, difficulty=difficulty, **kwargs,
    )


def check(user_answer: Any, correct_answer: Any, question_payload: dict[str, Any] | None = None) -> Any:
    return dispatch_check(user_answer, correct_answer, question_payload=question_payload, v3_package_root=_resolve_v3_package_root(), skill_id=SKILL_ID)


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    return dispatch_get_hint(step, question_payload=question_payload, v3_package_root=_resolve_v3_package_root(), skill_id=SKILL_ID)
'''


def _answer_type(spec: dict) -> str:
    if spec["presentation"] == "single_choice":
        return "single_choice"
    parts = int(spec.get("parts") or 1)
    exprs = spec.get("exprs") or []
    if spec["op"] in {"quadratic_integer_roots", "quadratic_formula_exact"} and spec["presentation"] != "single_choice":
        return "multi_part"
    if spec["op"] in {"linear_word_two_conditions", "linear_word_ratio_sum", "linear_word_three_shares", "quadratic_root_count", "quadratic_vieta_expressions"} and spec["presentation"] != "single_choice":
        if spec["op"] == "quadratic_vieta_expressions" and len(exprs) <= 1:
            return "expression"
        return "multi_part"
    if parts > 1 and spec["presentation"] != "single_choice":
        return "multi_part"
    return "expression"


def main() -> None:
    by_skill: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        by_skill[spec["skill_id"]].append((example_id, spec))
    for skill_id, rows in by_skill.items():
        keys = [f"src_{eid}" for eid, _ in rows]
        specs = []
        dispatch = {}
        for eid, spec in rows:
            at = _answer_type(spec)
            pres = "multiple_inputs" if at == "multi_part" else spec["presentation"]
            checker = "single_choice_checker" if at == "single_choice" else "multi_part_answer_checker" if at == "multi_part" else "expression_checker"
            specs.append({
                "textbook_example_id": eid,
                "component_id": f"src_{eid}",
                "generator_key": f"src_{eid}",
                "presentation_mode": spec["presentation"] if at != "multi_part" else "short_answer",
                "response_mode": spec["presentation"] if at != "multi_part" else "short_answer",
                "interaction_type": spec["presentation"] if at != "multi_part" else "short_answer",
                "source_kind": spec["source_kind"],
                "line_type": spec["op"],
                "answer_type": at,
                "answer_value_type": at,
                "problem_type_id": spec["op"],
                "checker_key": checker,
                "display_order": eid,
                "source_order": eid,
                "sampling_weight": 10.0,
            })
            dispatch[f"src_{eid}"] = f"components/src_{eid}/generate.py"
            comp = V3 / skill_id / "components" / f"src_{eid}"
            comp.mkdir(parents=True, exist_ok=True)
            (comp / "generate.py").write_text(
                GENERATE_PY.format(
                    presentation=spec["presentation"] if at != "multi_part" else "short_answer",
                    answer_type=at,
                    op=spec["op"],
                    example_id=eid,
                    skill_id=skill_id,
                ),
                encoding="utf-8",
            )
            (comp / "get_hint.py").write_text(HINT_PY, encoding="utf-8")
            (comp / "metadata.py").write_text(
                METADATA_PY.format(
                    example_id=eid,
                    skill_id=skill_id,
                    source_kind=spec["source_kind"],
                    op=spec["op"],
                    presentation=spec["presentation"] if at != "multi_part" else "short_answer",
                    answer_type=at,
                ),
                encoding="utf-8",
            )
            _ = pres
        manifest = {
            "skill_id": skill_id,
            "publish_status": "package_ready_candidate",
            "component_count": len(rows),
            "components": [
                {
                    "component_id": s["component_id"],
                    "textbook_example_id": s["textbook_example_id"],
                    "status": "verified",
                    "problem_type_id": s["problem_type_id"],
                    "domain_operation": s["line_type"],
                    "presentation_mode": s["presentation_mode"],
                    "answer_type": s["answer_type"],
                    "source_kind": s["source_kind"],
                    "generate_py": dispatch[s["component_id"]],
                }
                for s in specs
            ],
        }
        pkg = V3 / skill_id
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "component_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (pkg / "__init__.py").write_text(
            ROUTER.format(skill_id=skill_id, keys=keys, specs=specs, dispatch=dispatch),
            encoding="utf-8",
        )
        (SKILLS / f"{skill_id}.py").write_text(
            FACADE.format(skill_id=skill_id, keys=keys, specs=specs),
            encoding="utf-8",
        )
        print(skill_id, len(rows))


if __name__ == "__main__":
    main()
