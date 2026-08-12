# -*- coding: utf-8 -*-
"""Materialize B1 1-3/1-4 V3 components from slot generators + reconcile/publish."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.gencode.problem_type_spec import load_problem_type_spec  # noqa: E402
from core.gencode.services.v3_artifact_reconciliation_service import (  # noqa: E402
    reconcile_existing_artifacts,
)
from core.gencode.slot_generators import generate_from_problem_type_spec  # noqa: E402

DRY = ROOT / "reports" / "gencode_v3_dryrun"
PROD = ROOT / "agent_skills_v3"
REPORT = ROOT / "reports" / "gencode_closed_loop" / "b1_13_14_materialize_report.json"

# Explicit example -> problem_type_id (prefer induced_specs; heuristics for gaps)
EXAMPLE_PT: dict[int, tuple[str, str]] = {
    # CompletingTheSquare
    4468: ("vh_數學B1_CompletingTheSquare", "expression_complete_square_to_vertex"),
    4501: ("vh_數學B1_CompletingTheSquare", "integer_quadratic_graph_vertex_axis_choice"),
    # QuadraticFunctionGraph
    4450: ("vh_數學B1_QuadraticFunctionGraph", "integer_quadratic_graph_translation_fill_blank"),
    4460: ("vh_數學B1_QuadraticFunctionGraph", "integer_quadratic_graph_translation_fill_blank"),
    4466: ("vh_數學B1_QuadraticFunctionGraph", "integer_quadratic_graph_translation_fill_blank"),
    4503: ("vh_數學B1_QuadraticFunctionGraph", "integer_quadratic_graph_properties_choice"),
    # VertexForm
    4451: ("vh_數學B1_VertexFormOfQuadraticFunction", "text_quadratic_graph_translation_fill_blank_short_answer"),
    4452: ("vh_數學B1_VertexFormOfQuadraticFunction", "text_quadratic_vertex_form_translation_to_new_function_short_answer"),
    4453: ("vh_數學B1_VertexFormOfQuadraticFunction", "single_choice_quadratic_vertex_form_properties_single_choice"),
    4456: ("vh_數學B1_VertexFormOfQuadraticFunction", "numeric_quadratic_vertex_or_parameter_computation_short_answer"),
    4504: ("vh_數學B1_VertexFormOfQuadraticFunction", "numeric_quadratic_vertex_or_parameter_computation_single_choice"),
    # Extremum
    4454: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4455: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4457: ("vh_數學B1_QuadraticFunctionExtremum", "integer_compute_quadratic_vertex"),
    4458: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4459: ("vh_數學B1_QuadraticFunctionExtremum", "integer_compute_quadratic_vertex"),
    4463: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4464: ("vh_數學B1_QuadraticFunctionExtremum", "text_short_quadratic_vertex_or_parameter_computation"),
    4465: ("vh_數學B1_QuadraticFunctionExtremum", "integer_compute_quadratic_vertex"),
    4469: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4470: ("vh_數學B1_QuadraticFunctionExtremum", "text_short_quadratic_vertex_or_parameter_computation"),
    4471: ("vh_數學B1_QuadraticFunctionExtremum", "integer_compute_quadratic_vertex"),
    4472: ("vh_數學B1_QuadraticFunctionExtremum", "integer_quadratic_vertex_or_parameter_computation"),
    4502: ("vh_數學B1_QuadraticFunctionExtremum", "integer_compute_quadratic_vertex"),
    # Factoring
    4473: ("vh_數學B1_QuadraticInequalityAndFactoring", "integer_factor_quadratic_by_cross_multiplication"),
    4480: ("vh_數學B1_QuadraticInequalityAndFactoring", "integer_factor_quadratic_by_cross_multiplication"),
    4490: ("vh_數學B1_QuadraticInequalityAndFactoring", "integer_factor_quadratic_by_cross_multiplication"),
    # Inequality solution
    4474: ("vh_數學B1_QuadraticInequalitySolution", "integer_reverse_quadratic_inequality_coefficients"),
    4475: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4476: ("vh_數學B1_QuadraticInequalitySolution", "integer_applied_quadratic_inequality_problem"),
    4477: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4478: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4479: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality_parameter_range"),
    4481: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4482: ("vh_數學B1_QuadraticInequalitySolution", "integer_reverse_quadratic_inequality_coefficients"),
    4483: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4484: ("vh_數學B1_QuadraticInequalitySolution", "integer_applied_quadratic_inequality_problem"),
    4485: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4486: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4487: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality_parameter_range"),
    4488: ("vh_數學B1_QuadraticInequalitySolution", "integer_applied_quadratic_inequality_problem"),
    4489: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4491: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4492: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4493: ("vh_數學B1_QuadraticInequalitySolution", "integer_reverse_quadratic_inequality_coefficients"),
    4494: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4495: ("vh_數學B1_QuadraticInequalitySolution", "integer_applied_quadratic_inequality_problem"),
    4496: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4497: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4498: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality_parameter_range"),
    4505: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4506: ("vh_數學B1_QuadraticInequalitySolution", "integer_solve_quadratic_inequality"),
    4507: ("vh_數學B1_QuadraticInequalitySolution", "integer_reverse_quadratic_inequality_coefficients"),
    4508: ("vh_數學B1_QuadraticInequalitySolution", "rational_solve_quadratic_inequality_special_cases"),
    4517: ("vh_數學B1_QuadraticInequalitySolution", "integer_applied_quadratic_inequality_problem"),
    4518: ("vh_數學B1_QuadraticInequalitySolution", "rational_solve_quadratic_inequality_special_cases"),
}

HINT_PY = '''from __future__ import annotations

from typing import Any


def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    payload = question_payload or {}
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    givens = meta.get("givens") or []
    if step == 1:
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return f"先找出已知條件：{given_text}。用一句話說明要求什麼。"
    if step == 2:
        target = str(meta.get("target") or "未知量")
        return f"把條件轉成數學關係，目標是求：{target}。"
    if step == 3:
        derivation = meta.get("derivation") or []
        if derivation:
            return "依序思考：" + " → ".join(str(d) for d in derivation)
        return "寫出核心公式，代入已知數值後化簡得到答案。"
    return ""
'''


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_pt_meta(skill_id: str, problem_type_id: str) -> dict[str, Any]:
    spec = load_problem_type_spec(skill_id, problem_type_id, prefer="auto")
    if not isinstance(spec, dict):
        raise RuntimeError(f"missing_problem_type_spec:{skill_id}:{problem_type_id}")
    ac = spec.get("answer_contract") or {}
    return {
        "spec": spec,
        "target_task": str(spec.get("target_task") or problem_type_id),
        "template_slot": str(spec.get("template_slot") or ac.get("template_slot") or spec.get("target_task") or ""),
        "presentation_mode": str(ac.get("presentation_mode") or "short_answer"),
        "answer_type": str(ac.get("answer_type") or "expression"),
        "checker_key": str(ac.get("checker_key") or ac.get("checker") or "expression_checker"),
        "equivalence_type": str(ac.get("equivalence_type") or ac.get("answer_equivalence") or "exact_string"),
    }


def _write_component(skill_id: str, example_id: int, problem_type_id: str, base: Path) -> dict[str, Any]:
    meta = _resolve_pt_meta(skill_id, problem_type_id)
    # Smoke the generator before writing.
    payload = generate_from_problem_type_spec(skill_id, meta["spec"], seed=42 + example_id % 97)
    if not isinstance(payload, dict) or not payload:
        raise RuntimeError("empty_payload")

    cid = f"src_{example_id}"
    comp_dir = base / skill_id / "components" / cid
    comp_dir.mkdir(parents=True, exist_ok=True)

    generate_py = textwrap.dedent(
        f"""\
        from __future__ import annotations

        from typing import Any

        from core.gencode.problem_type_spec import load_problem_type_spec
        from core.gencode.slot_generators import generate_from_problem_type_spec

        SKILL_ID = {skill_id!r}
        PROBLEM_TYPE_ID = {problem_type_id!r}
        TEXTBOOK_EXAMPLE_ID = {example_id}
        DEFAULT_COMPONENT_ID = {cid!r}
        PRESENTATION_MODE = {meta['presentation_mode']!r}
        ANSWER_TYPE = {meta['answer_type']!r}


        def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
            spec = load_problem_type_spec(SKILL_ID, PROBLEM_TYPE_ID, prefer="auto")
            if not isinstance(spec, dict):
                raise RuntimeError(f"missing_problem_type_spec:{{PROBLEM_TYPE_ID}}")
            payload = generate_from_problem_type_spec(SKILL_ID, spec, seed=seed)
            component_id = str(kwargs.get("component_id") or DEFAULT_COMPONENT_ID or "")
            if component_id:
                payload["component_id"] = component_id
            payload["textbook_example_id"] = TEXTBOOK_EXAMPLE_ID
            payload["seed"] = seed
            payload.setdefault("problem_type_id", PROBLEM_TYPE_ID)
            payload.setdefault("presentation_mode", PRESENTATION_MODE)
            payload.setdefault("answer_type", ANSWER_TYPE)
            return payload
        """
    )
    metadata_py = textwrap.dedent(
        f"""\
        from __future__ import annotations
        from typing import Final

        COMPONENT_ID: Final[str] = {cid!r}
        SKILL_ID: Final[str] = {skill_id!r}
        SOURCE_REF: Final[str] = {cid!r}
        SOURCE_KIND: Final[str] = "example"
        TEXTBOOK_EXAMPLE_ID: Final[int] = {example_id}
        IS_REQUIRED_CORE: Final[bool] = False
        ORDER_WEIGHT: Final[int] = 10
        DIFFICULTY_LEVEL: Final[str] = "easy"
        DOMAIN_OPERATION: Final[str] = {meta['target_task']!r}
        TARGET_TASK: Final[str] = {meta['target_task']!r}
        TEMPLATE_SLOT: Final[str] = {meta['template_slot']!r}
        PROBLEM_TYPE_ID: Final[str] = {problem_type_id!r}
        PRESENTATION_MODE: Final[str] = {meta['presentation_mode']!r}
        RESPONSE_MODE: Final[str] = {meta['presentation_mode']!r}
        INTERACTION_TYPE: Final[str] = {meta['presentation_mode']!r}
        ANSWER_VALUE_TYPE: Final[str] = {meta['answer_type']!r}
        ANSWER_TYPE: Final[str] = {meta['answer_type']!r}
        LEGACY_ANSWER_TYPE: Final[str] = {meta['answer_type']!r}
        DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
            "core.gencode.slot_generators.generate_from_problem_type_spec",
        )
        ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {{
            "checker_key": {meta['checker_key']!r},
            "equivalence_type": {meta['equivalence_type']!r},
            "response_mode": {meta['presentation_mode']!r},
            "interaction_type": {meta['presentation_mode']!r},
            "answer_value_type": {meta['answer_type']!r},
            "answer_type": {meta['answer_type']!r},
            "module": "core.gencode.runtime_skill_wrapper",
        }}
        GENERATOR_READINESS: Final[str] = "runtime_ready"
        """
    )
    (comp_dir / "generate.py").write_text(generate_py, encoding="utf-8")
    (comp_dir / "metadata.py").write_text(metadata_py, encoding="utf-8")
    (comp_dir / "get_hint.py").write_text(HINT_PY, encoding="utf-8")
    return {
        "textbook_example_id": example_id,
        "skill_id": skill_id,
        "problem_type_id": problem_type_id,
        "sample_answer": str(payload.get("correct_answer") or payload.get("answer"))[:80],
        "generate_sha256": _sha(comp_dir / "generate.py"),
    }


def _ensure_skill_scaffold(skill_id: str, base: Path) -> None:
    skill_dir = base / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "components").mkdir(exist_ok=True)
    init_path = skill_dir / "__init__.py"
    if not init_path.exists():
        init_path.write_text("# auto-generated skill package\n", encoding="utf-8")
    manifest = {
        "skill_id": skill_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": "b1_13_14_materialize_quadratic_components",
    }
    (skill_dir / "component_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--skip-write", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    items = list(EXAMPLE_PT.items())
    if args.limit > 0:
        items = items[: args.limit]

    written = []
    failed_write = []
    for eid, (skill_id, pt) in items:
        try:
            if not args.skip_write:
                _ensure_skill_scaffold(skill_id, DRY)
                _ensure_skill_scaffold(skill_id, PROD)
                info = _write_component(skill_id, eid, pt, DRY)
                # Mirror identical files to production for hash alignment.
                src = DRY / skill_id / "components" / f"src_{eid}"
                dst = PROD / skill_id / "components" / f"src_{eid}"
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                info["mirrored_to_production"] = True
                written.append(info)
            else:
                written.append({"textbook_example_id": eid, "skill_id": skill_id, "skipped_write": True})
        except Exception as exc:
            failed_write.append(
                {"textbook_example_id": eid, "skill_id": skill_id, "problem_type_id": pt, "error": f"{type(exc).__name__}:{exc}"}
            )

    targets: dict[str, list[int]] = {}
    for item in written:
        targets.setdefault(item["skill_id"], []).append(int(item["textbook_example_id"]))
    targets_t = {k: tuple(sorted(v)) for k, v in targets.items()}

    reconcile = None
    if targets_t:
        conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
        conn.row_factory = sqlite3.Row
        reconcile = reconcile_existing_artifacts(
            conn=conn,
            targets=targets_t,
            project_root=ROOT,
            commit=bool(args.commit),
        )
        try:
            conn.commit()
        except Exception:
            pass
        conn.close()

    report = {
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "commit": bool(args.commit),
        "written_count": len(written),
        "failed_write": failed_write,
        "written": written,
        "reconcile": {
            "passed_count": (reconcile or {}).get("passed_count"),
            "failed_count": (reconcile or {}).get("failed_count"),
            "synced_count": (reconcile or {}).get("synced_count"),
            "failed_ids": [
                c.get("textbook_example_id")
                for c in ((reconcile or {}).get("components") or [])
                if not c.get("passed")
            ],
            "blockers": {
                str(c.get("textbook_example_id")): c.get("blockers")
                for c in ((reconcile or {}).get("components") or [])
                if not c.get("passed")
            },
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "written_count": report["written_count"],
                "failed_write_count": len(failed_write),
                "failed_write_ids": [x["textbook_example_id"] for x in failed_write],
                "reconcile_passed": report["reconcile"]["passed_count"],
                "reconcile_failed": report["reconcile"]["failed_count"],
                "reconcile_failed_ids": report["reconcile"]["failed_ids"],
                "report": str(REPORT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not failed_write and not report["reconcile"]["failed_ids"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
