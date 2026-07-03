"""V3 Question Integrity Validator — shared gate for shadow bridge, smoke, variation audit, and publish."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from core.gencode.question_semantic_validators import (
    validate_comparison_contract,
    validate_equation_display_text,
    validate_single_choice_scalar_topology,
)

# ---------------------------------------------------------------------------
# Shared constants — import from here; never maintain copies elsewhere
# ---------------------------------------------------------------------------

BLOCKED_STEMS: frozenset[str] = frozenset(
    {
        "請寫出符合題意的直線方程式。",
        "generator draft pending implementation",
        "draft pending implementation",
        "pending implementation",
        "[DRAFT]",
        "implementation pending",
        "implementation_pending",
        "NotImplemented",
    }
)

# (answer_type, checker_key) pairs that are semantically incompatible.
INCOMPATIBLE_PAIRS: frozenset[tuple[str, str]] = frozenset(
    {
        ("numeric_or_undefined", "linear_equation_equivalent_checker"),
        ("rational", "linear_equation_equivalent_checker"),
        ("text_short", "linear_equation_equivalent_checker"),
        ("single_choice", "linear_equation_equivalent_checker"),
        ("single_choice", "rational_checker"),
        ("single_choice", "text_short_checker"),
        ("linear_equation", "rational_checker"),
        ("linear_equation", "text_short_checker"),
    }
)

# Seeds used for multi-seed pre-publish sampling
DEFAULT_INTEGRITY_SEEDS: tuple[int, ...] = (7, 42, 137, 256, 999)

EVIDENCE_DEPENDENCY_FIELDS: frozenset[str] = frozenset(
    {
        "raw_scores",
        "data",
        "values",
        "table_rows",
        "frequency_table",
        "chart_data",
        "figure",
        "matrix",
        "coordinates",
    }
)

# ---------------------------------------------------------------------------
# Required stem-slot tokens by problem_type_id prefix / exact match.
# Keys may be exact problem_type_id strings or prefix patterns ending with '*'.
# Values are lists of token strings, at least one of which must appear in
# question_text when the corresponding givens slot is non-empty.
# ---------------------------------------------------------------------------
_REQUIRED_STEM_SLOT_TOKENS: dict[str, dict[str, list[str]]] = {
    "slope_intercept_equation": {
        "slope": ["斜率", "slope", "$m"],
        "y_intercept": ["截距", "intercept", "$b"],
    },
    "slope_intercept_find_x_intercept": {
        "slope": ["斜率", "slope"],
        "y_intercept": ["截距", "intercept"],
    },
    "slope_intercept_read_slope_and_intercept": {
        "equation": ["方程式", "equation", "="],
    },
    "intercept_form_triangle_area": {
        "x_intercept": ["x 截距", "截距"],
        "y_intercept": ["y 截距", "截距"],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_answer_contract(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the answer contract dict from a payload, tolerating varied layouts."""
    ac = payload.get("answer_contract")
    if isinstance(ac, dict) and ac:
        return ac
    # Fallback: reconstruct minimal contract from top-level keys
    return {
        "answer_type": payload.get("answer_type", ""),
        "checker_key": payload.get("checker_key", payload.get("checker", "")),
        "presentation_mode": payload.get("presentation_mode", ""),
    }


def _extract_givens(payload: dict[str, Any]) -> dict[str, Any]:
    meta = payload.get("metadata")
    if isinstance(meta, dict):
        givens = meta.get("givens")
        if isinstance(givens, dict):
            return givens
        if isinstance(givens, list):
            # List-style givens — not slot-keyed, skip slot checks
            return {}
    return {}


def _metadata_dict(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _visible_payload_text(payload: dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if field == "metadata":
        value = payload.get("metadata")
    if value is None:
        return ""
    return str(value)


def _evidence_values_rendered(payload: dict[str, Any], evidence: dict[str, Any]) -> bool:
    field = str(evidence.get("field") or "").strip()
    values = evidence.get("values")
    if not field or values is None:
        return False

    visible_text = _visible_payload_text(payload, field)
    if not visible_text:
        return False

    if isinstance(values, (list, tuple)):
        separator = str(evidence.get("separator") or "、")
        rendered_sequence = separator.join(str(value) for value in values)
        return rendered_sequence in visible_text

    return str(values) in visible_text


def _validate_required_evidence_visibility(payload: dict[str, Any]) -> list[str]:
    metadata = _metadata_dict(payload)
    dependencies = metadata.get("answer_dependencies")
    if not isinstance(dependencies, list):
        return []

    visible_evidence = metadata.get("visible_evidence")
    if not isinstance(visible_evidence, dict):
        visible_evidence = {}

    blockers: list[str] = []
    for dep in dependencies:
        dep_name = str(dep or "").strip()
        if dep_name not in EVIDENCE_DEPENDENCY_FIELDS:
            continue
        evidence = visible_evidence.get(dep_name)
        if not isinstance(evidence, dict) or not _evidence_values_rendered(payload, evidence):
            blockers.append(f"REQUIRED_EVIDENCE_NOT_RENDERED:{dep_name}")
    return blockers


# ---------------------------------------------------------------------------
# Core validator
# ---------------------------------------------------------------------------

def validate_component_payload(
    payload: dict[str, Any],
    component_id: str | None = None,
) -> dict[str, Any]:
    """
    Validate a single generate() payload for integrity.

    Returns:
        {
            "passed": bool,
            "component_id": str | None,
            "blockers": list[str],
            "warnings": list[str],
        }
    """
    blockers: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload, dict) or not payload:
        blockers.append("generic_stem_detected")
        return {"passed": False, "component_id": component_id, "blockers": blockers, "warnings": warnings}

    question_text = str(payload.get("question_text") or "").strip()
    presentation_mode = str(payload.get("presentation_mode") or "").strip()
    ac = _extract_answer_contract(payload)
    answer_type = str(ac.get("answer_type") or payload.get("answer_type") or "").strip()
    checker_key = str(ac.get("checker_key") or ac.get("checker") or "").strip()

    # ── 1. Generic stem detection ─────────────────────────────────────────
    for stem in BLOCKED_STEMS:
        if stem and stem in question_text:
            blockers.append("generic_stem_detected")
            break

    # ── 2. Required stem slot checks ─────────────────────────────────────
    problem_type_id = str(payload.get("problem_type_id") or "").strip()
    if problem_type_id:
        required_slots = _REQUIRED_STEM_SLOT_TOKENS.get(problem_type_id, {})
        if required_slots:
            givens = _extract_givens(payload)
            for slot_name, tokens in required_slots.items():
                slot_val = givens.get(slot_name)
                if slot_val is not None and slot_val != "":
                    # The given is populated; verify at least one token appears in stem
                    if not any(tok in question_text for tok in tokens):
                        blockers.append(f"required_stem_slot_missing:{slot_name}")

    # ── 3. Checker / answer_type semantic compatibility ───────────────────
    # Skip for single_choice presentation — the contract is always choice_label_checker
    if presentation_mode != "single_choice" and answer_type and checker_key:
        if (answer_type, checker_key) in INCOMPATIBLE_PAIRS:
            blockers.append(
                f"checker_answer_type_mismatch:{answer_type}:{checker_key}"
            )

    # ── 4. Strict Semantic Gate ──────────────────────────────────────────
    # Ensure returned problem_type_id and answer_value_type match actual returned payload structures
    if problem_type_id:
        # Check semantic consistency for line_equation related problem_type_ids
        if problem_type_id == "slope_from_general_or_intercept_form" and "斜率" not in question_text:
            blockers.append("semantic_component_mismatch:slope_from_general_or_intercept_form_missing_slope")
        elif problem_type_id == "slope_from_general_form" and ("斜率" not in question_text or "x截距" in question_text or "y截距" in question_text):
            blockers.append("semantic_component_mismatch:slope_from_general_form_incorrect_question")
        elif problem_type_id == "slope_of_horizontal_or_vertical_line" and "斜率" not in question_text:
            blockers.append("semantic_component_mismatch:slope_of_horizontal_or_vertical_line_missing_slope")
        elif problem_type_id == "line_through_point_parallel_to_line" and "平行" not in question_text:
            blockers.append("semantic_component_mismatch:line_through_point_parallel_to_line_missing_parallel")
        elif problem_type_id == "line_through_point_perpendicular_to_line" and "垂直" not in question_text:
            blockers.append("semantic_component_mismatch:line_through_point_perpendicular_to_line_missing_perpendicular")
        elif problem_type_id == "parallel_line_slope" and ("平行" not in question_text or "斜率" not in question_text):
            blockers.append("semantic_component_mismatch:parallel_line_slope_incorrect")
        elif problem_type_id == "perpendicular_line_slope" and ("垂直" not in question_text or "斜率" not in question_text):
            blockers.append("semantic_component_mismatch:perpendicular_line_slope_incorrect")
        elif problem_type_id == "perpendicular_condition_parameter" and ("垂直" not in question_text and "\\bot" not in question_text):
            blockers.append("semantic_component_mismatch:perpendicular_condition_parameter_missing_perpendicular")
        elif problem_type_id == "compare_line_slopes" and "最大斜率" not in question_text:
            blockers.append("semantic_component_mismatch:compare_line_slopes_missing_max_slope")
        elif problem_type_id == "line_through_intersection_parallel_to_line" and ("交點" not in question_text or "平行" not in question_text):
            blockers.append("semantic_component_mismatch:line_through_intersection_parallel_to_line_incorrect")
        elif problem_type_id == "perpendicular_bisector_application" and ("垂直平分線" not in question_text and "距離相等" not in question_text and "中垂線" not in question_text):
            blockers.append("semantic_component_mismatch:perpendicular_bisector_application_incorrect")
        elif problem_type_id == "distance_from_point_to_line" and "距離" not in question_text:
            blockers.append("semantic_component_mismatch:distance_from_point_to_line_missing_distance")
        elif problem_type_id == "distance_from_point_to_line_parameter" and "距離" not in question_text:
            blockers.append("semantic_component_mismatch:distance_from_point_to_line_parameter_missing_distance")
        elif problem_type_id == "compare_point_to_line_distances" and "距離" not in question_text:
            blockers.append("semantic_component_mismatch:compare_point_to_line_distances_missing_distance")

    blockers.extend(validate_equation_display_text(payload))
    blockers.extend(validate_comparison_contract(payload))
    blockers.extend(validate_single_choice_scalar_topology(payload))
    blockers.extend(_validate_required_evidence_visibility(payload))

    from core.gencode.choice_contract_validator import validate_choice_contract

    choice_result = validate_choice_contract(payload)
    if not choice_result.get("ok"):
        blockers.extend(choice_result.get("blockers") or [choice_result.get("error_code") or "CHOICE_CONTRACT_INCOMPLETE"])

    passed = len(blockers) == 0
    return {
        "passed": passed,
        "component_id": component_id,
        "blockers": list(dict.fromkeys(blockers)),  # preserve order, deduplicate
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Multi-seed sampler for pre-publish gate
# ---------------------------------------------------------------------------

def validate_skill_samples(
    skill_key: str,
    n_seeds: int = 5,
    source: str = "pre_publish",
    project_root: str | None = None,
    staging_root: str | None = None,
    conn: Any = None,
    seeds: tuple[int, ...] | None = None,
) -> dict[str, Any]:
    """
    Run validate_component_payload over n_seeds for each verified component
    found in the standard locations.

    Returns:
        {
            "passed": bool,
            "skill_id": str,
            "component_results": dict[component_id, dict],
            "blockers_summary": list[str],
        }
    """
    import sqlite3

    _project_root = Path(project_root) if project_root else Path(__file__).resolve().parents[3]
    _seeds = seeds if seeds is not None else DEFAULT_INTEGRITY_SEEDS[:n_seeds]

    # Resolve component directories
    if source == "dryrun":
        base = _project_root / "reports" / "gencode_v3_dryrun" / skill_key / "components"
    elif source == "staging" and staging_root:
        base = Path(staging_root) / "agent_skills_v3" / skill_key / "components"
    elif source == "production":
        base = _project_root / "agent_skills_v3" / skill_key / "components"
    else:
        # pre_publish: try dryrun first, fallback to production
        base_dryrun = _project_root / "reports" / "gencode_v3_dryrun" / skill_key / "components"
        base_prod = _project_root / "agent_skills_v3" / skill_key / "components"
        base = base_dryrun if base_dryrun.is_dir() else base_prod

    component_results: dict[str, dict[str, Any]] = {}
    all_passed = True
    blockers_summary: list[str] = []
    verified_component_ids: set[str] | None = None
    if conn is not None:
        try:
            rows = conn.execute(
                """
                SELECT component_id
                FROM gencode_component_tracker
                WHERE skill_id = ? AND gencode_status = 'verified'
                """,
                (skill_key,),
            ).fetchall()
            verified_component_ids = {str(row[0] if not hasattr(row, "keys") else row["component_id"]) for row in rows}
        except Exception:
            verified_component_ids = None

    if not base.is_dir():
        return {
            "passed": True,  # no components to validate → not a failure at this level
            "skill_id": skill_key,
            "component_results": {},
            "blockers_summary": [],
            "note": "no_component_dir_found",
        }

    for comp_dir in sorted(base.iterdir()):
        if not comp_dir.is_dir():
            continue
        comp_id = comp_dir.name
        if verified_component_ids is not None and comp_id not in verified_component_ids:
            continue
        gen_py = comp_dir / "generate.py"
        if not gen_py.is_file():
            continue

        import sys
        if "core.gencode.domain_matrix_adapter" in sys.modules:
            import importlib
            try:
                importlib.reload(sys.modules["core.gencode.domain_matrix_adapter"])
            except Exception:
                pass
        spec = importlib.util.spec_from_file_location(f"_integ_{comp_id}", gen_py)
        if spec is None or spec.loader is None:
            continue
        try:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        except Exception as exc:
            component_results[comp_id] = {
                "passed": False,
                "blockers": [f"import_error:{exc}"],
                "seeds_checked": 0,
            }
            all_passed = False
            blockers_summary.append(f"{comp_id}:import_error:{exc}")
            continue

        generate_fn = getattr(mod, "generate", None)
        if not callable(generate_fn):
            continue

        seed_results: list[dict[str, Any]] = []
        comp_passed = True
        for seed in _seeds:
            try:
                pl = generate_fn(seed=seed, component_id=comp_id)
            except Exception as exc:
                seed_results.append({"seed": seed, "passed": False, "blockers": [f"generate_error:{exc}"]})
                comp_passed = False
                blockers_summary.append(
                    f"integrity_gate_failed_pre_smoke:component_id={comp_id}:seed={seed}:blockers=[generate_error:{exc}]"
                )
                continue
            vr = validate_component_payload(pl, component_id=comp_id)
            seed_results.append({"seed": seed, **vr})
            if not vr["passed"]:
                comp_passed = False
                blockers_summary.append(
                    f"integrity_gate_failed_pre_smoke:component_id={comp_id}:seed={seed}:blockers={vr['blockers']}"
                )

        if not comp_passed:
            all_passed = False

        component_results[comp_id] = {
            "passed": comp_passed,
            "seed_results": seed_results,
            "seeds_checked": len(seed_results),
        }

    return {
        "passed": all_passed,
        "skill_id": skill_key,
        "component_results": component_results,
        "blockers_summary": blockers_summary,
    }
