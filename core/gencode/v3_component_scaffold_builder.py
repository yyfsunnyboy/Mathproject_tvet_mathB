"""Build V3 component scaffold source strings without writing to disk."""

from __future__ import annotations

from typing import Any

from core.gencode.source_kind_resolver import (
    resolve_difficulty_level,
    resolve_order_weight,
    resolve_source_kind_from_textbook_row,
)

_SOURCE_KIND_PROFILES: dict[str, dict[str, object]] = {
    "example": {"order_weight": 10, "difficulty_level": "easy"},
    "quiz": {"order_weight": 20, "difficulty_level": "easy"},
    "test": {"order_weight": 30, "difficulty_level": "hard"},
}

_RESPONSE_MODE_VALUES = frozenset({
    "expression",
    "single_choice",
    "short_answer",
    "text_short",
    "multi_part",
    "multi_blank",
    "table_fill",
    "unordered_set",
})


def build_component_files_from_domain_payload(
    skill_id: str,
    component_id: str,
    source_kind: str,
    domain_meta: dict[str, Any],
    payload_meta: dict[str, Any],
    *,
    textbook_example_id: int | None = None,
    textbook_row: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Return metadata.py / generate.py / get_hint.py source strings only."""
    if textbook_row is not None:
        source_kind = resolve_source_kind_from_textbook_row(textbook_row)
    profile = _resolve_source_kind_profile(source_kind)
    order_weight = resolve_order_weight(source_kind)
    difficulty_level = resolve_difficulty_level(source_kind)

    return {
        "metadata.py": _build_metadata_py(
            skill_id=skill_id,
            component_id=component_id,
            source_kind=source_kind,
            order_weight=order_weight,
            difficulty_level=difficulty_level,
            domain_meta=domain_meta,
            payload_meta=payload_meta,
            textbook_example_id=textbook_example_id,
        ),
        "generate.py": _build_generate_py(
            domain_meta=domain_meta,
            payload_meta=payload_meta,
            difficulty_level=difficulty_level,
        ),
        "get_hint.py": _build_get_hint_py(),
    }


def normalize_v3_component_metadata_fields(payload_meta: dict[str, Any]) -> dict[str, str]:
    """Split legacy answer_type into response-mode and answer-value dimensions."""
    presentation_mode = str(payload_meta.get("presentation_mode") or "short_answer").strip()
    response_mode = str(
        payload_meta.get("response_mode")
        or payload_meta.get("interaction_type")
        or ("single_choice" if presentation_mode == "single_choice" else "expression")
    ).strip()
    legacy_answer_type = str(payload_meta.get("answer_type") or "").strip()
    answer_value_type = str(payload_meta.get("answer_value_type") or "").strip()
    if not answer_value_type and legacy_answer_type == "text_short":
        answer_value_type = legacy_answer_type
    elif not answer_value_type and legacy_answer_type and legacy_answer_type not in _RESPONSE_MODE_VALUES:
        answer_value_type = legacy_answer_type
    if not answer_value_type:
        answer_value_type = "choice_label" if response_mode == "single_choice" else "expression"
    return {
        "presentation_mode": presentation_mode,
        "response_mode": response_mode,
        "interaction_type": response_mode,
        "answer_value_type": answer_value_type,
        "legacy_answer_type": legacy_answer_type or answer_value_type,
    }


def _resolve_source_kind_profile(source_kind: str) -> dict[str, object]:
    normalized = str(source_kind or "").strip().lower()
    for prefix, profile in _SOURCE_KIND_PROFILES.items():
        if normalized == prefix or normalized.startswith(f"{prefix}_"):
            return profile
    raise ValueError(f"Unsupported source_kind: {source_kind!r}")


def _build_metadata_py(
    *,
    skill_id: str,
    component_id: str,
    source_kind: str,
    order_weight: int,
    difficulty_level: str,
    domain_meta: dict[str, Any],
    payload_meta: dict[str, Any],
    textbook_example_id: int | None = None,
) -> str:
    problem_type_id = str(payload_meta.get("problem_type_id") or "").strip()
    target_task = str(payload_meta.get("target_task") or problem_type_id).strip()
    if not problem_type_id:
        problem_type_id = target_task
    if not target_task:
        raise ValueError("payload_meta must include problem_type_id or target_task.")
    template_slot = str(payload_meta.get("template_slot", "line_equation_from_point_slope"))
    normalized = normalize_v3_component_metadata_fields(payload_meta)
    presentation_mode = normalized["presentation_mode"]
    response_mode = normalized["response_mode"]
    interaction_type = normalized["interaction_type"]
    answer_value_type = normalized["answer_value_type"]
    legacy_answer_type = normalized["legacy_answer_type"]
    line_type = str(payload_meta.get("line_type", ""))
    domain_operation = str(
        payload_meta.get("domain_operation") or payload_meta.get("line_type") or target_task
    ).strip()
    answer_schema_key = str(payload_meta.get("answer_schema_key") or "").strip()
    textbook_id = int(textbook_example_id if textbook_example_id is not None else payload_meta.get("textbook_example_id", 0) or 0)

    if presentation_mode == "single_choice":
        checker_key = str(payload_meta.get("checker_key", "choice_label_checker"))
        equivalence_type = str(payload_meta.get("equivalence_type", "choice_label"))
        checker_module = str(payload_meta.get("checker_module", "core.checkers.choice_label_checker"))
    else:
        fixed_domain = str(payload_meta.get("fixed_domain_key") or payload_meta.get("template_domain_key") or "").strip()
        default_checker = "integer_checker"
        default_equiv = "numeric_exact"
        default_module = "core.gencode.runtime_skill_wrapper"

        checker_key = str(payload_meta.get("checker_key") or default_checker)
        equivalence_type = str(payload_meta.get("equivalence_type") or default_equiv)
        checker_module = str(payload_meta.get("checker_module") or default_module)
        if checker_module == "pipeline":
            checker_module = "core.gencode.runtime_skill_wrapper"

    domain_entry = _domain_library_entry(domain_meta)

    if fixed_domain == "algebra.absolute_value":
        default_concepts = ("絕對值", "絕對值方程式")
        default_objects = ("absolute_value", "equation")
        default_taxonomy = "algebra:absolute_value"
    else:
        default_concepts = ()
        default_objects = ()
        default_taxonomy = "algebra"

    semantic_concepts = payload_meta.get("semantic_required_concepts") or default_concepts
    math_objects = payload_meta.get("math_objects") or default_objects
    taxonomy_path = str(payload_meta.get("taxonomy_path") or default_taxonomy)
    concepts_repr = ", ".join(f'"{item}"' for item in semantic_concepts)
    objects_repr = ", ".join(f'"{item}"' for item in math_objects)

    return f'''from __future__ import annotations
from typing import Final

COMPONENT_ID: Final[str] = "{component_id}"
SKILL_ID: Final[str] = "{skill_id}"
SOURCE_REF: Final[str] = "{component_id}"
SOURCE_KIND: Final[str] = "{source_kind}"
TEXTBOOK_EXAMPLE_ID: Final[int] = {textbook_id}
IS_REQUIRED_CORE: Final[bool] = False

ORDER_WEIGHT: Final[int] = {order_weight}
DIFFICULTY_LEVEL: Final[str] = "{difficulty_level}"
DOMAIN_OPERATION: Final[str] = "{domain_operation}"
ANSWER_SCHEMA_KEY: Final[str] = "{answer_schema_key}"
LINE_TYPE: Final[str] = "{line_type}"

TARGET_TASK: Final[str] = "{target_task}"
TEMPLATE_SLOT: Final[str] = "{template_slot}"
PROBLEM_TYPE_ID: Final[str] = "{problem_type_id}"
PRESENTATION_MODE: Final[str] = "{presentation_mode}"
RESPONSE_MODE: Final[str] = "{response_mode}"
INTERACTION_TYPE: Final[str] = "{interaction_type}"
ANSWER_VALUE_TYPE: Final[str] = "{answer_value_type}"
ANSWER_TYPE: Final[str] = "{answer_value_type}"
LEGACY_ANSWER_TYPE: Final[str] = "{legacy_answer_type}"

DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "{domain_entry}",
)

ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {{
    "checker_key": "{checker_key}",
    "equivalence_type": "{equivalence_type}",
    "response_mode": "{response_mode}",
    "interaction_type": "{interaction_type}",
    "answer_value_type": "{answer_value_type}",
    "answer_type": "{answer_value_type}",
    "module": "{checker_module}",
}}

GENERATOR_READINESS: Final[str] = "draft"

SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    {concepts_repr},
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    {objects_repr},
)
TAXONOMY_PATH: Final[str] = "{taxonomy_path}"
'''


def _build_generate_py(
    *,
    domain_meta: dict[str, Any],
    payload_meta: dict[str, Any],
    difficulty_level: str,
) -> str:
    domain_module = str(domain_meta.get("domain_module", ""))
    entrypoint = str(domain_meta.get("entrypoint", ""))
    curriculum_profile = str(
        domain_meta.get(
            "default_curriculum_profile",
            payload_meta.get("curriculum_profile", "vocational_high_b"),
        )
    )
    line_type = str(payload_meta.get("line_type", "point_slope"))
    domain_operation = str(payload_meta.get("domain_operation") or line_type)
    answer_schema_key = str(payload_meta.get("answer_schema_key") or "")
    presentation_mode = str(payload_meta.get("presentation_mode", "short_answer"))
    answer_type = str(payload_meta.get("answer_type", "expression"))
    problem_type_id = str(payload_meta.get("problem_type_id", "write_line_equation_from_point_slope"))
    textbook_example_id = int(payload_meta.get("textbook_example_id", 0) or 0)
    constraints = payload_meta.get("constraints", {})
    if line_type.startswith("slope_intercept_"):
        constraints = {}
    constraints_literal = repr(constraints if isinstance(constraints, dict) else {})
    if entrypoint in {
        "build_coordinate_geometry_matrix",
        "build_parallel_lines_distance_matrix",
        "build_frequency_distribution_table_matrix",
        "build_statistical_chart_reading_matrix",
        "build_descriptive_statistics_matrix",
    }:
        matrix_call = f'''{entrypoint}(
        seed=seed,
        domain_operation="{domain_operation}",
        curriculum_profile="{curriculum_profile}",
        difficulty_profile="{difficulty_level}",
        constraints={constraints_literal},
    )'''
    else:
        matrix_call = f'''{entrypoint}(
        seed=seed,
        line_type="{line_type}",
        curriculum_profile="{curriculum_profile}",
        difficulty_profile="{difficulty_level}",
        constraints={constraints_literal},
    )'''

    return f'''from __future__ import annotations

from typing import Any

from {domain_module} import {entrypoint}
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload

PRESENTATION_MODE = "{presentation_mode}"
ANSWER_TYPE = "{answer_type}"
PROBLEM_TYPE_ID = "{problem_type_id}"
TEXTBOOK_EXAMPLE_ID = {textbook_example_id}
DEFAULT_COMPONENT_ID = "src_{textbook_example_id}" if TEXTBOOK_EXAMPLE_ID else ""


def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    matrix = {matrix_call}
    component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
    payload = convert_domain_matrix_to_question_payload(
        matrix,
        presentation_mode=PRESENTATION_MODE,
        answer_type=ANSWER_TYPE,
        problem_type_id=PROBLEM_TYPE_ID,
        component_id=component_id or None,
        textbook_example_id=TEXTBOOK_EXAMPLE_ID or None,
        answer_schema_key="{answer_schema_key}",
        domain_operation="{domain_operation}",
        seed=seed,
    )
    if component_id:
        payload["component_id"] = component_id
    payload["seed"] = seed
    return payload
'''


def _build_get_hint_py() -> str:
    return '''from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示 — 強制語意骨架。
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    payload = question_payload or {}
    story_ctx = str(payload.get("story_context") or "")
    math_core = payload.get("math_core") or {}
    givens = math_core.get("givens") or payload.get("metadata", {}).get("givens") or []

    if step == 1:
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return (
            f"請先閱讀題目，找出已知條件與要求的量。"
            f"{'情境：' + story_ctx if story_ctx else ''}"
            f"目前已知：{given_text}。請用一句話說明「要求什麼」。"
        )

    if step == 2:
        target = str(math_core.get("target") or payload.get("metadata", {}).get("target") or "未知量")
        objects = math_core.get("math_objects") or []
        obj_text = "、".join(str(o) for o in objects) if objects else "適當的數學關係"
        return (
            f"將文字條件轉成數學語言：設定變數，並指出此題屬於「{obj_text}」類型。"
            f"目標是求：{target}。"
        )

    if step == 3:
        derivation = math_core.get("derivation") or payload.get("metadata", {}).get("derivation") or []
        if derivation:
            return f"依序思考：{' → '.join(str(d) for d in derivation)}。寫出關鍵算式後再化簡。"
        return "寫出本題適用的核心公式，代入已知數值，逐步化簡得到答案。"

    return ""
'''


def _domain_library_entry(domain_meta: dict[str, Any]) -> str:
    domain_module = str(domain_meta.get("domain_module", "")).strip()
    entrypoint = str(domain_meta.get("entrypoint", "")).strip()
    if not domain_module or not entrypoint:
        raise ValueError("domain_meta must include domain_module and entrypoint.")
    return f"{domain_module}.{entrypoint}"


