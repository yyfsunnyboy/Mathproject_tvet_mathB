"""Build the reviewed-capability workspace for statistics.univariate_descriptive.

Writes only ``reports/domain_operation_workspaces/capability_statistics_univariate_descriptive_<id>/revision_<N>``
(N = BUNDLE_REVISION, default 4; revision_0001-0003 are never rebuilt). The bundle uses the formal
``reviewed_capability_bundle.v1`` schema read by core/gencode/reviewed_capability_promotion.py.
The review block stays ``ready_for_human_review``. This script does not approve, promote, or publish.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.univariate_statistics import build_sandbox as B  # noqa: E402
from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.univariate_statistics.univariate_statistics_specs import (  # noqa: E402
    CHART_COMPONENTS,
    COMPONENTS,
    FAMILY,
    FIXED_CONCEPT,
    FIXED_ROWS,
    OP,
    SKILL_OPERATIONS,
    SKILLS,
    VISUAL_CAPABILITY_GAP,
)

PROPOSAL_ID = "capability_statistics_univariate_descriptive_" + hashlib.sha256(
    b"statistics.univariate_descriptive:math2unit8"
).hexdigest()[:8]
SOURCE = ROOT / "agent_domains_candidate" / "univariate_statistics"
REVISION = int(os.environ.get("BUNDLE_REVISION", "4"))
REVISION_4_CHANGE = {
    12926: "chart renderer is thread-safe (no rcParams / warnings-filter changes; cmap glyph check, font and pixel checks) "
           "and the charts are landscape 560x340 so the student grid shows them at ~0.62 on 430 px and 1280 px",
    12930: "same renderer change as 12926",
}
CHART_CHANGE = {
    12926: "generated 國文/數學 grade 0-15 percentage bar charts (two PNGs, shared axis); seed0 = 109 學測 data, other "
           "variants simulated (labelled 模擬測驗, exact 100.00%); four parameterised claims and P88 graded from the chart data",
    12930: "same generated charts shown in full on every draw (no 承例題9 dependency); P75 前標 graded from the chart data",
}
REPAIRED = {
    12923: "stem prints n, mean, Q1, Q3 and every statement value; statement (2) 'about n/4 above Q3' is false (ties)",
    12941: "stem prints the rescale formula, mean, sd, k and thresholds; truths derived from the scenario",
    12931: "stem prints the actual n; variants with a stated original mean make the claim true or false",
    12946: "percentile claims vary multiplier sign, shift/square and range/mean claims; truths checked by counterexample search",
    12932: "textbook universal claim plus concrete constant-data instances with computed sd",
    12933: "y=ax+b with a of either sign and stated factor a or -a; truth = (stated == |a|)",
    12934: "textbook universal claim plus concrete data sets comparing median and mean",
    12928: "three five-value groups in random order; the largest-sd position moves",
    12940: "five ascending integers with integer population sd, fourth value hidden",
    12914: "stem states rounding to 3 decimals (domain decimals)",
    12937: "stem states rounding to 3 decimals (domain decimals)",
    12917: "third-year rate restricted to exact terminating decimals (stem asks for a decimal)",
    12913: "LaTeX table + original column labels",
    12936: "LaTeX table + original column labels",
    12916: "LaTeX table + original scenario wording",
    12919: "LaTeX table + 投籃 scenario labels, N printed",
    12922: "LaTeX table + 呼吸次數 scenario labels, N printed",
    12920: "LaTeX table + 薪資 scenario labels, N printed",
    12943: "LaTeX table + subject names in table and choices",
    12944: "LaTeX table + 月份/氣溫 labels",
    12939: "fraction display (decimal or \\frac) only; answers unchanged",
    12942: "linear map shown with \\frac coefficient only; answers unchanged",
    12945: "linear map shown with \\frac coefficient only; answers unchanged",
}
PACKAGE_FILES = ["__init__.py", "univariate_statistics_adapter.py", "univariate_statistics_chart.py", "univariate_statistics_domain.py"]
WORKSPACE = ROOT / "reports" / "domain_operation_workspaces" / PROPOSAL_ID / f"revision_{REVISION:04d}"
DOMAIN_KEY = B.DOMAIN_KEY


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scope() -> str:
    by_skill = {skill: sorted(cid for cid, spec in COMPONENTS.items() if SKILLS[spec[0]] == skill) for skill in SKILLS.values()}
    listed = "; ".join(f"{skill} ({len(ids)} components: {', '.join(map(str, ids))})" for skill, ids in by_skill.items())
    return (
        f"revision {REVISION}: 普高數學2 Unit 8 一維數據分析 — domain {DOMAIN_KEY} "
        f"({len(OP)} operations: {', '.join(sorted(OP))}); Skills {listed}; "
        f"all {len(COMPONENTS)} formal rows (ids 12912-12946); FIXED_ROWS={sorted(FIXED_ROWS)}. "
        "Population variance/sd (STDEV.P). "
        f"VISUAL_CAPABILITY_GAP {sorted(VISUAL_CAPABILITY_GAP)}. "
        f"Chart components {sorted(CHART_COMPONENTS)} (例題9/隨堂10) ship two generated bar-chart PNGs in visual_aids "
        "(runtime needs matplotlib and a CJK font; missing glyphs raise). "
        "Revision 3 only adds the bar charts; the other 33 components are byte-identical to revision 2. "
        "Revision 4 only changes the chart renderer (thread safety, landscape size) and the bundle schema; "
        "the data, answers and the other 33 components are identical to revision 3. "
        "This revision is not approved and is not published."
    )


def main() -> None:
    if REVISION < 4:
        raise SystemExit("revision_0001-0003 are kept as reviewed baselines and are never rebuilt")
    register_candidate_in_memory()
    from core.gencode.registered_operation_dispatch import dispatch_registered_operation

    package = WORKSPACE / "production_package"
    existing = WORKSPACE / "promotion_bundle.json"
    if existing.exists() and json.loads(existing.read_text(encoding="utf-8"))["review"]["status"] != "ready_for_human_review":
        raise SystemExit(f"{WORKSPACE.name} is already approved: never rebuilt, create the next revision instead")
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    package.mkdir(parents=True)
    for name in PACKAGE_FILES:
        shutil.copyfile(SOURCE / name, package / name)

    checkers: dict[str, set[str]] = {}
    types: dict[str, set[str]] = {}
    modes: dict[str, set[str]] = {}
    smoke: dict[str, list[dict]] = {}
    coverage = []
    for cid, (skill_key, op, source, sampler) in sorted(COMPONENTS.items()):
        variants = B.collect_variants(cid, op, source, sampler)
        smoke.setdefault(op, []).append({"seed": 0, "constraints": source, "textbook_example_id": cid})
        coverage.append({
            "textbook_example_id": cid,
            "skill_id": SKILLS[skill_key],
            "family": FAMILY[cid],
            "problem_type": op,
            "generator": f"src_{cid}",
            "domain_function": op,
            "variants": len(variants),
            "oracle": "dual_formula_or_expanded_list",
            "status": ("VISUAL_CAPABILITY_GAP" if cid in VISUAL_CAPABILITY_GAP
                       else "FIXED_CONCEPT" if cid in FIXED_CONCEPT else "VARIABLE"),
            "revision_2_change": REPAIRED.get(cid, "unchanged from revision 1"),
            "revision_3_change": CHART_CHANGE.get(cid, "unchanged from revision 2"),
            "revision_4_change": REVISION_4_CHANGE.get(cid, "unchanged from revision 3"),
        })
        for variant in variants[:3]:
            _m, payload = dispatch_registered_operation(DOMAIN_KEY, op, seed=0, constraints=dict(variant))
            contract = payload["answer_contract"]
            checkers.setdefault(op, set()).add(contract["checker_key"])
            checkers[op].update(part.get("checker") for part in contract.get("parts") or [] if part.get("checker"))
            types.setdefault(op, set()).add(contract["answer_type"])
            types[op].update(part.get("answer_type") for part in contract.get("parts") or [] if part.get("answer_type"))
            modes.setdefault(op, set()).add(payload["presentation_mode"])

    operations = {}
    for op in sorted(checkers):
        operations[op] = {
            "checker_keys": sorted(checkers[op]),
            "handler": "build_univariate_statistics_matrix",
            "payload_adapter": "univariate_statistics_adapter.adapt_univariate_statistics_matrix",
            "provided_capabilities": [op],
            "runtime_contract": "univariate_statistics_exact_v1",
            "supported_answer_types": sorted(types[op]),
            "supported_presentation_modes": sorted(modes[op]),
            "validator": f"validate_{op}_matrix",
        }

    bundle = {
        "schema": "reviewed_capability_bundle.v1",
        "proposal_id": PROPOSAL_ID,
        "proposal_revision": REVISION,
        "review": {
            "status": "ready_for_human_review",
            "approved_by": "",
            "approved_revision": None,
            "approval_scope": _scope(),
        },
        "domain_key": DOMAIN_KEY,
        "package_name": "univariate_statistics",
        "package_dir": "production_package",
        "files": {name: sha256(package / name) for name in PACKAGE_FILES},
        "domain_module": "univariate_statistics_domain",
        "entrypoint": "build_univariate_statistics_matrix",
        "capabilities": sorted(operations),
        "operations": operations,
        "skill_bindings": {
            SKILLS[key]: {"default_curriculum_profile": "general_high", "allowed_operations": sorted(ops)}
            for key, ops in sorted(SKILL_OPERATIONS.items())
        },
        "smoke_cases": {op: smoke[op] for op in sorted(operations)},
        "deferred_components": {str(cid): "VISUAL_CAPABILITY_GAP" for cid in sorted(VISUAL_CAPABILITY_GAP)},
        "coverage_rows": len(coverage),
        "supersedes": "revision_0003 (non-v1 bundle schema, chart renderer not thread-safe, charts too small at 430 px); "
                      "revision_0001-0003 are kept unchanged",
        "visual_assets": {
            str(cid): {"carrier": "visual_aids (2 x image/png)", "renderer": "univariate_statistics_chart.render_grade_charts",
                       "student_display": "scratchpad_layers multi_image grid (existing path, no front-end change)"}
            for cid in sorted(CHART_COMPONENTS)
        },
    }
    path = WORKSPACE / "promotion_bundle.json"
    path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    (WORKSPACE / "coverage_matrix.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"workspace": str(WORKSPACE), "components": len(coverage), "operations": len(operations),
                      "status": "ready_for_human_review", "bundle_sha256": sha256(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
