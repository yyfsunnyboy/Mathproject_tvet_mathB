from __future__ import annotations

from copy import deepcopy
from typing import Any

from core.gencode.registered_operation_dispatch import dispatch_registered_operation
from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

PRESENTATION_MODE = "multiple_inputs"
ANSWER_TYPE = "expression"
PROBLEM_TYPE_ID = "evaluate_scientific_notation_expression"
TEXTBOOK_EXAMPLE_ID = 12377
DEFAULT_COMPONENT_ID = "src_12377" if TEXTBOOK_EXAMPLE_ID else ""
SKILL_ID = "gh_ScientificNotationAndItsOperations"
FIXED_DOMAIN_KEY = "algebra.exponent_laws"
DOMAIN_OPERATION = "evaluate_scientific_notation_expression"


def _materialize_generation_constraints(raw_constraints: dict[str, Any], seed: int | None) -> dict[str, Any]:
    constraints = deepcopy(raw_constraints)
    generation_constraints = constraints.pop("generation_constraints", None)
    if generation_constraints is None:
        return constraints
    if not isinstance(generation_constraints, dict):
        raise ValueError("generation_constraints must be a dict")
    variants = generation_constraints.get("variants")
    if not isinstance(variants, list) or not variants:
        raise ValueError("generation_constraints.variants must be a non-empty list")
    index = 0 if seed is None else int(seed) % len(variants)
    selected = variants[index]
    if not isinstance(selected, dict):
        raise ValueError("generation_constraints variant must be a dict")
    selected_constraints = selected.get("constraints", selected)
    if not isinstance(selected_constraints, dict):
        raise ValueError("generation_constraints variant constraints must be a dict")
    forbidden = {"answer", "correct_answer", "canonical_answer", "answer_contract", "checker", "checker_key"}
    if forbidden & set(selected_constraints):
        raise ValueError("generation_constraints must not define answer or checker authority")
    constraints.update(deepcopy(selected_constraints))
    return constraints


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    resolution = resolve_domain_authority(SKILL_ID, selected_operation=DOMAIN_OPERATION)
    if (
        resolution.binding_status != "confirmed"
        or resolution.fixed_domain_key != FIXED_DOMAIN_KEY
        or resolution.selected_operation != DOMAIN_OPERATION
    ):
        raise RuntimeError(
            "domain_binding_mismatch:"
            f"{resolution.binding_status}:{resolution.fixed_domain_key}:{resolution.selected_operation}"
        )

    constraints = _materialize_generation_constraints(dict({'generation_constraints': {'variants': [{'stem': '已知 $2018$ 年美國的人口數為 $329976959$ 人。', 'items': [{'kind': 'value', 'value': '329976959', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '329976959', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2020$ 年美國的人口數為 $664553458$ 人。', 'items': [{'kind': 'value', 'value': '664553458', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '664553458', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2014$ 年美國的人口數為 $2321774895$ 人。', 'items': [{'kind': 'value', 'value': '2321774895', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '2321774895', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2011$ 年美國的人口數為 $258865200$ 人。', 'items': [{'kind': 'value', 'value': '258865200', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '258865200', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2013$ 年美國的人口數為 $3719714315$ 人。', 'items': [{'kind': 'value', 'value': '3719714315', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '3719714315', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2019$ 年美國的人口數為 $610480886$ 人。', 'items': [{'kind': 'value', 'value': '610480886', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '610480886', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2022$ 年美國的人口數為 $557994535$ 人。', 'items': [{'kind': 'value', 'value': '557994535', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '557994535', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2022$ 年美國的人口數為 $81838782$ 人。', 'items': [{'kind': 'value', 'value': '81838782', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '81838782', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2019$ 年美國的人口數為 $8334873852$ 人。', 'items': [{'kind': 'value', 'value': '8334873852', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '8334873852', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2017$ 年美國的人口數為 $853300311$ 人。', 'items': [{'kind': 'value', 'value': '853300311', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '853300311', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2017$ 年美國的人口數為 $7056148830$ 人。', 'items': [{'kind': 'value', 'value': '7056148830', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '7056148830', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2014$ 年美國的人口數為 $7623996586$ 人。', 'items': [{'kind': 'value', 'value': '7623996586', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '7623996586', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2018$ 年美國的人口數為 $399570164$ 人。', 'items': [{'kind': 'value', 'value': '399570164', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '399570164', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2017$ 年美國的人口數為 $517890397$ 人。', 'items': [{'kind': 'value', 'value': '517890397', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '517890397', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2021$ 年美國的人口數為 $310306923$ 人。', 'items': [{'kind': 'value', 'value': '310306923', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '310306923', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2022$ 年美國的人口數為 $7227803066$ 人。', 'items': [{'kind': 'value', 'value': '7227803066', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '7227803066', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2019$ 年美國的人口數為 $1573258964$ 人。', 'items': [{'kind': 'value', 'value': '1573258964', 'sig': 1, 'prompt': '將人口數取 $1$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '1573258964', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2022$ 年美國的人口數為 $5070630272$ 人。', 'items': [{'kind': 'value', 'value': '5070630272', 'sig': 3, 'prompt': '將人口數取 $3$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '5070630272', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2018$ 年美國的人口數為 $323766404$ 人。', 'items': [{'kind': 'value', 'value': '323766404', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '323766404', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}, {'stem': '已知 $2016$ 年美國的人口數為 $5887520306$ 人。', 'items': [{'kind': 'value', 'value': '5887520306', 'sig': 2, 'prompt': '將人口數取 $2$ 位有效數字並以科學記號表示。'}, {'kind': 'value', 'value': '5887520306', 'sig': 4, 'prompt': '將人口數取 $4$ 位有效數字並以科學記號表示。'}]}]}}), seed)
    constraints["skill_id"] = SKILL_ID
    _matrix, payload = dispatch_registered_operation(
        resolution.fixed_domain_key,
        DOMAIN_OPERATION,
        seed=seed,
        constraints=constraints,
    )
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    if component_id:
        payload["component_id"] = component_id
    payload["skill_id"] = SKILL_ID
    payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
    payload["domain_resolution"] = {
        "fixed_domain_key": resolution.fixed_domain_key,
        "resolution_source": resolution.resolution_source,
        "binding_status": resolution.binding_status,
        "selected_operation": resolution.selected_operation,
        "registry_revision": resolution.registry_revision,
    }
    payload["seed"] = seed
    return payload
