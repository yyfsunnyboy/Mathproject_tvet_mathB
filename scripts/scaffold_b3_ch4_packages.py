# -*- coding: utf-8 -*-
"""Write B3 Chapter 4 skill wrappers and thin v3 packages from SOURCE_SPECS.

Skills without legal sources (``ZERO_SOURCE_SKILLS``) get no package.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from core.domain.exponential_logarithmic_domain import (
    SOURCE_SPECS,
    ZERO_SOURCE_SKILLS,
    build_exponential_logarithmic_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
V3 = ROOT / "agent_skills_v3"

GENERATE_PY = '''from __future__ import annotations

from typing import Any

from core.domain.exponential_logarithmic_domain import build_exponential_logarithmic_matrix
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix

PRESENTATION_MODE = {presentation!r}
ANSWER_TYPE = {answer_type!r}
PROBLEM_TYPE_ID = {op!r}
TEXTBOOK_EXAMPLE_ID = {example_id}
DEFAULT_COMPONENT_ID = "src_{example_id}"


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = build_exponential_logarithmic_matrix(
        seed,
        {{
            "skill_id": {skill_id!r},
            "problem_type_id": PROBLEM_TYPE_ID,
            "textbook_example_id": TEXTBOOK_EXAMPLE_ID,
            "presentation": PRESENTATION_MODE,
        }},
    )
    payload = adapt_exponential_logarithmic_matrix(
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
    payload["skill_id"] = {skill_id!r}
    return payload
'''

HINT_PY = '''from __future__ import annotations
from typing import Any

from core.domain.exponential_logarithmic_domain import hint_steps

PROBLEM_TYPE_ID = {op!r}


def get_hint(step: int = 1, question_payload: dict[str, Any] | None = None) -> str:
    steps = hint_steps(PROBLEM_TYPE_ID)
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
    "core.domain.exponential_logarithmic_domain.build_exponential_logarithmic_matrix",
)
'''


def _router(skill_id: str, keys: list[str], specs: list[dict], dispatch: dict[str, str]) -> str:
    return f'''from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILL_ID = {skill_id!r}
GENERATOR_KEYS = {keys!r}
GENERATOR_SPECS = {specs!r}
_COMPONENT_DISPATCH = {dispatch!r}
_V3_ROOT = Path(__file__).resolve().parent


def _load_component_module(component_id: str, module_filename: str) -> Any:
    path = _V3_ROOT / "components" / component_id / module_filename
    spec = importlib.util.spec_from_file_location(f"v3_{{SKILL_ID}}_{{component_id}}_{{module_filename}}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"component_module_not_found:{{component_id}}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate(level: int = 1, seed: int | None = None, component_id: str | None = None, **kwargs: Any) -> dict[str, Any]:
    picked = component_id or kwargs.get("component_id") or GENERATOR_KEYS[0]
    module = _load_component_module(str(picked), "generate.py")
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


def _facade(skill_id: str, keys: list[str], specs: list[dict]) -> str:
    return f'''from __future__ import annotations

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


def main() -> None:
    by_skill: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for example_id, spec in sorted(SOURCE_SPECS.items()):
        if spec["skill_id"] in ZERO_SOURCE_SKILLS:
            raise SystemExit(f"zero_source_skill_has_source:{example_id}")
        by_skill[spec["skill_id"]].append((example_id, spec))
    for skill_id, rows in by_skill.items():
        keys = [f"src_{eid}" for eid, _ in rows]
        specs = []
        dispatch = {}
        for eid, spec in rows:
            matrix = build_exponential_logarithmic_matrix(eid, {"textbook_example_id": eid})
            answer_type = str(matrix["answer_type"])
            specs.append({
                "textbook_example_id": eid,
                "component_id": f"src_{eid}",
                "generator_key": f"src_{eid}",
                "presentation_mode": spec["presentation"],
                "response_mode": spec["presentation"],
                "interaction_type": spec["presentation"],
                "source_kind": spec["source_kind"],
                "line_type": spec["op"],
                "answer_type": answer_type,
                "answer_value_type": answer_type,
                "problem_type_id": spec["op"],
                "checker_key": matrix.get("answer_type"),
                "display_order": eid,
                "source_order": eid,
                "sampling_weight": 10.0,
            })
            dispatch[f"src_{eid}"] = f"components/src_{eid}/generate.py"
            comp = V3 / skill_id / "components" / f"src_{eid}"
            comp.mkdir(parents=True, exist_ok=True)
            (comp / "generate.py").write_text(
                GENERATE_PY.format(
                    presentation=spec["presentation"],
                    answer_type=answer_type,
                    op=spec["op"],
                    example_id=eid,
                    skill_id=skill_id,
                ),
                encoding="utf-8",
            )
            (comp / "get_hint.py").write_text(HINT_PY.format(op=spec["op"]), encoding="utf-8")
            (comp / "metadata.py").write_text(
                METADATA_PY.format(
                    example_id=eid,
                    skill_id=skill_id,
                    source_kind=spec["source_kind"],
                    op=spec["op"],
                    presentation=spec["presentation"],
                    answer_type=answer_type,
                ),
                encoding="utf-8",
            )
        manifest = {
            "skill_id": skill_id,
            "publish_status": "package_ready",
            "component_count": len(rows),
            "components": [
                {
                    "component_id": row["component_id"],
                    "textbook_example_id": row["textbook_example_id"],
                    "status": "verified",
                    "problem_type_id": row["problem_type_id"],
                    "domain_operation": row["line_type"],
                    "presentation_mode": row["presentation_mode"],
                    "answer_type": row["answer_type"],
                    "source_kind": row["source_kind"],
                    "generate_py": dispatch[row["component_id"]],
                }
                for row in specs
            ],
        }
        pkg = V3 / skill_id
        pkg.mkdir(parents=True, exist_ok=True)
        (pkg / "component_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        (pkg / "__init__.py").write_text(_router(skill_id, keys, specs, dispatch), encoding="utf-8")
        (SKILLS / f"{skill_id}.py").write_text(_facade(skill_id, keys, specs), encoding="utf-8")
        print(skill_id, len(rows))


if __name__ == "__main__":
    main()
