from __future__ import annotations

from typing import Any

from core.gencode.problem_type_spec import list_problem_types_for_skill
from core.gencode.spec_phase1_merge import spec_to_answer_contract_proposal, slot_generator_readiness


def _phase1_induced_specs(skill_id: str, phase2_usable: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import json
    from pathlib import Path

    REPORT_DIR = Path("reports/gencode_closed_loop")

    induced_file = list_problem_types_for_skill(skill_id, prefer="induced")
    if induced_file:
        return induced_file
    path = REPORT_DIR / f"{skill_id}_phase1_summary.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        auto = data.get("auto_review_summary") if isinstance(data.get("auto_review_summary"), dict) else {}
        induced = auto.get("induced_problem_type_specs") or data.get("induced_problem_type_specs")
        if isinstance(induced, list) and induced:
            return [s for s in induced if isinstance(s, dict)]
    drafts = [c.get("problem_type_spec_draft") for c in phase2_usable if isinstance(c, dict)]
    return [d for d in drafts if isinstance(d, dict) and d.get("problem_type_id")]


def build_generator_specs_for_phase3(skill_id: str, phase2_usable: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Prefer Phase 1 induced ProblemTypeSpec drafts; curated JSON is fallback."""
    specs = _phase1_induced_specs(skill_id, phase2_usable)
    if not specs:
        specs = list_problem_types_for_skill(skill_id, prefer="curated")
    if not specs:
        specs_out = [
            {
                "problem_type_id": str(x.get("problem_type_id", "")).strip(),
                "checker_key": str(x.get("checker_key", "")).strip(),
                "equivalence_type": str(x.get("equivalence_type", "")).strip(),
            }
            for x in phase2_usable
            if str(x.get("problem_type_id", "")).strip()
        ]
        keys = [str(x.get("generator_key", "")).strip() for x in phase2_usable if str(x.get("generator_key", "")).strip()]
        return specs_out, keys

    phase2_by_pt = {str(x.get("problem_type_id", "")).strip(): x for x in phase2_usable if isinstance(x, dict)}
    specs_out: list[dict[str, Any]] = []
    keys: list[str] = []
    for spec in specs:
        pt = str(spec.get("problem_type_id", "")).strip()
        if not pt:
            continue
        contract = spec_to_answer_contract_proposal(spec)
        g2 = phase2_by_pt.get(pt, {})
        specs_out.append(
            {
                "problem_type_id": pt,
                "checker_key": str(contract.get("checker_key", "")).strip(),
                "equivalence_type": str(contract.get("equivalence_type", "")).strip(),
                "generator_readiness": slot_generator_readiness(spec),
            }
        )
        keys.append(str(g2.get("generator_key", "")).strip() or f"{skill_id}:{pt}:spec_v1")
    return specs_out, keys


def build_phase3_skill_module_code(skill_id: str, generator_specs: list[dict[str, Any]], generator_keys: list[str]) -> str:
    """Emit a thin skill wrapper; generation logic lives in core.gencode.runtime_skill_wrapper."""
    return (
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n"
        "from core.gencode.runtime_skill_wrapper import check_answer, generate_for_skill\n\n"
        f"SKILL_ID = {skill_id!r}\n"
        f"GENERATOR_KEYS = {generator_keys!r}\n"
        f"GENERATOR_SPECS = {generator_specs!r}\n\n"
        "def generate(level: int = 1, seed: int | None = None, difficulty: int | str | None = None, **kwargs) -> dict[str, Any]:\n"
        "    return generate_for_skill(SKILL_ID, GENERATOR_SPECS, level=level, seed=seed, difficulty=difficulty)\n\n"
        "def check(user_answer: Any, correct_answer: Any):\n"
        "    return check_answer(user_answer, correct_answer)\n"
    )
