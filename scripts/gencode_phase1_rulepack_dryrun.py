from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode import pipeline_orchestrator as po  # noqa: E402


def _build_summary(skill_id: str, pack: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    pt_cfg = {
        str(x.get("problem_type_id", "")).strip(): x
        for x in (pack.get("problem_types") or [])
        if isinstance(x, dict) and str(x.get("problem_type_id", "")).strip()
    }
    counts: dict[str, int] = {}
    for row in entries:
        pt = str(row.get("problem_type_id", "")).strip()
        if not pt:
            continue
        counts[pt] = counts.get(pt, 0) + 1
    problem_types = []
    for pt, matched in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        cfg = pt_cfg.get(pt, {})
        problem_types.append(
            {
                "problem_type_id": pt,
                "matched": matched,
                "checker": str(cfg.get("checker", "")).strip(),
                "equivalence": str(cfg.get("equivalence", "")).strip(),
                "runtime_candidate": bool(cfg.get("runtime_candidate", False)),
                "requires_human_action": bool(cfg.get("requires_human_action", False)),
                "is_default_problem_type": bool(cfg.get("is_default_problem_type", False) or pt.endswith("_default")),
            }
        )
    requires_human_action = any(bool(x.get("requires_human_action")) for x in problem_types)
    return {
        "skill_id": skill_id,
        "classifier_source": "rule_pack",
        "ai_bootstrap_used": False,
        "rule_pack_found": True,
        "source_example_count": len(entries),
        "problem_types": problem_types,
        "requires_human_action": requires_human_action,
        "source_classifications": [
            {
                "example_id": row.get("example_id"),
                "title": row.get("title"),
                "problem_type_id": row.get("problem_type_id"),
                "runtime_category": row.get("runtime_category"),
                "manual_review_reason": row.get("manual_review_reason"),
            }
            for row in entries
        ],
        "default_problem_type_used": bool(pack.get("source_policy", {}).get("default_problem_type_used", False)),
        "single_primary_problem_type": bool(pack.get("source_policy", {}).get("single_primary_problem_type", False)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Local Phase1 rule_pack dry-run (no AI, no DB write, no phase2/3)")
    ap.add_argument("--skill-id", required=True, help="skill_id to dry-run")
    ap.add_argument("--json", action="store_true", dest="as_json", help="print JSON output")
    ap.add_argument("--write-report", action="store_true", help="write dry-run report json under reports/gencode_closed_loop")
    args = ap.parse_args()

    skill_id = str(args.skill_id or "").strip()
    if not skill_id:
        print("error: --skill-id is required", file=sys.stderr)
        return 1

    # 1) Load rule pack only (no AI)
    try:
        pack = po._load_registered_classifier_rulepack(skill_id)  # type: ignore[attr-defined]
    except Exception as ex:
        print(f"yaml parse error: {ex}", file=sys.stderr)
        return 3
    if not pack:
        out = {
            "skill_id": skill_id,
            "classifier_source": "none",
            "rule_pack_found": False,
            "ai_bootstrap_used": False,
        }
        if args.as_json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
            print(f"skill_id: {skill_id}")
            print("classifier_source: none")
            print("rule_pack_found: false")
            print("ai_bootstrap_used: false")
        return 2

    # 2) Load source examples (read-only DB)
    examples = po._load_examples(skill_id)  # type: ignore[attr-defined]
    if not examples:
        print("source examples missing", file=sys.stderr)
        return 4

    # 3) Classify with rule pack only
    entries = po._classify_examples_with_rulepack(skill_id=skill_id, examples=examples, pack=pack)  # type: ignore[attr-defined]
    summary = _build_summary(skill_id, pack, entries)

    if args.write_report:
        report_path = PROJECT_ROOT / "reports" / "gencode_closed_loop" / f"{skill_id}_phase1_rulepack_dryrun.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary["report_path"] = str(report_path)

    if args.as_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"skill_id: {summary['skill_id']}")
        print(f"classifier_source: {summary['classifier_source']}")
        print(f"ai_bootstrap_used: {str(summary['ai_bootstrap_used']).lower()}")
        print(f"rule_pack_found: {str(summary['rule_pack_found']).lower()}")
        print("problem_types:")
        for pt in summary["problem_types"]:
            print(
                f"- {pt['problem_type_id']} matched={pt['matched']} checker={pt['checker']} equivalence={pt['equivalence']}"
            )
        print(f"requires_human_action: {str(summary['requires_human_action']).lower()}")
        print(f"default_problem_type_used: {str(summary['default_problem_type_used']).lower()}")
        print(f"single_primary_problem_type: {str(summary['single_primary_problem_type']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

