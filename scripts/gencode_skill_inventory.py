import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.classifiers import get_classifier_for_skill
from core.gencode.classifiers.base import (
    REQUIRED_EXAMPLE_FIELDS,
    DETERMINISTIC_RUNTIME_CATEGORIES,
    ClassifierContext,
)


def _yaml_like(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        out = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                out.append(f"{pad}{k}:")
                out.append(_yaml_like(v, indent + 2))
            else:
                out.append(f"{pad}{k}: {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(out)
    if isinstance(data, list):
        out = []
        for v in data:
            if isinstance(v, (dict, list)):
                out.append(f"{pad}-")
                out.append(_yaml_like(v, indent + 2))
            else:
                out.append(f"{pad}- {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(out)
    return f"{pad}{json.dumps(data, ensure_ascii=False)}"


def _load_examples(root: Path, db_path: str, skill_id: str) -> list[dict[str, Any]]:
    con = sqlite3.connect(str(root / db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    te_cols = [r[1] for r in cur.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    order_key = "id" if "id" in te_cols else "rowid"
    rows = [
        dict(r)
        for r in cur.execute(
            f"SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY {order_key}",
            (skill_id,),
        ).fetchall()
    ]
    con.close()
    return rows


def _validate_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for e in entries:
        row = dict(e)
        for f in REQUIRED_EXAMPLE_FIELDS:
            if f not in row:
                row[f] = "" if f not in {"semantic_risk_flags"} else []
        if not isinstance(row.get("semantic_risk_flags"), list):
            row["semantic_risk_flags"] = []
        out.append(row)
    return out


def _build_subskills(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_sub: dict[str, list[int]] = defaultdict(list)
    runtime_by_sub: dict[str, str] = {}
    for e in entries:
        sid = str(e.get("subskill_id", "")).strip()
        if not sid:
            continue
        exid = e.get("example_id")
        if isinstance(exid, int):
            by_sub[sid].append(exid)
        runtime_by_sub[sid] = str(e.get("runtime_category", "not_observed"))
    out = []
    for sid in sorted(by_sub.keys()):
        refs = sorted(set(by_sub[sid]))
        prereq = [] if sid == "absolute_value_numeric_evaluation" else ["absolute_value_numeric_evaluation"]
        if sid == "absolute_value_distance_between_two_points":
            prereq = ["number_line_basic_position", "absolute_value_numeric_evaluation"]
        out.append(
            {
                "subskill_id": sid,
                "observed": len(refs) > 0,
                "supporting_example_ids": refs,
                "suggested_problem_types": [sid] if refs else [],
                "runtime_category": runtime_by_sub.get(sid, "not_observed"),
                "prerequisite_subskills": prereq,
                "diagnosis_tags": ["absolute_value"],
            }
        )
    return out


def _problem_type_spec(entries: list[dict[str, Any]], skill_id: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in entries:
        pt = str(e.get("problem_type_id", "")).strip()
        if not pt or pt == "unknown":
            continue
        groups[pt].append(e)

    answer_checker = {
        "deterministic_numeric": ("integer", "integer_checker"),
        "deterministic_expression": ("text", "exact_string_checker"),
        "deterministic_choice": ("choice", "choice_checker"),
    }

    out = []
    for pt in sorted(groups.keys()):
        items = groups[pt]
        runtime = str(items[0].get("runtime_category", "manual_review"))
        ans, chk = answer_checker.get(runtime, ("text", "exact_string_checker"))
        refs = sorted({int(x.get("example_id")) for x in items if isinstance(x.get("example_id"), int)})
        prereq = []
        if pt == "absolute_value_distance_between_two_points":
            prereq = ["number_line_basic_position", "absolute_value_numeric_evaluation"]
        elif pt != "absolute_value_numeric_evaluation":
            prereq = ["absolute_value_numeric_evaluation"]
        out.append(
            {
                "problem_type_id": pt,
                "skill_id": skill_id,
                "subskill_id": pt,
                "display_name": pt.replace("_", " "),
                "runtime_category": runtime,
                "answer_type": ans,
                "checker_type": chk,
                "examples_refs": refs,
                "prerequisite_subskills": prereq,
                "diagnosis_tags": ["absolute_value"],
                "difficulty_policy": "easy_only_v1",
                "output_contract": {
                    "required_keys": [
                        "problem_type_id",
                        "skill_id",
                        "subskill_id",
                        "question_text",
                        "answer",
                        "answer_type",
                        "checker_type",
                        "solution_steps",
                        "metadata",
                    ]
                },
                "status": "draft",
            }
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--db-path", default="instance/kumon_math.db")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[1]
    examples = _load_examples(root, args.db_path, args.skill_id)
    if len(examples) == 0:
        raise RuntimeError("textbook_examples count is 0; cannot build inventory")

    classifier = get_classifier_for_skill(args.skill_id)
    ctx = ClassifierContext(project_root=root, skill_id=args.skill_id)
    result = classifier.classify_examples(examples, ctx)
    entries = _validate_entries(result.examples_map_entries)

    if len(entries) != len(examples):
        raise RuntimeError("classifier output count mismatch with textbook_examples")

    package_dir = result.package_dir
    package_dir.mkdir(parents=True, exist_ok=True)
    slug = "absolute_value"

    subskills = _build_subskills(entries)
    pts = _problem_type_spec(entries, args.skill_id)
    prereq = [{"subskill_id": s["subskill_id"], "prerequisite_subskills": s.get("prerequisite_subskills", [])} for s in subskills]

    (package_dir / f"subskills_{slug}.yaml").write_text(_yaml_like({"skill_id": args.skill_id, "subskills": subskills}) + "\n", encoding="utf-8")
    (package_dir / f"problem_types_{slug}.yaml").write_text(_yaml_like({"items": pts}) + "\n", encoding="utf-8")
    (package_dir / f"examples_map_{slug}.yaml").write_text(_yaml_like({"examples": entries}) + "\n", encoding="utf-8")
    (package_dir / f"prerequisites_{slug}.yaml").write_text(_yaml_like({"items": prereq}) + "\n", encoding="utf-8")

    rpt = root / "reports" / "gencode_closed_loop" / f"{args.skill_id}_inventory_report.md"
    rpt.parent.mkdir(parents=True, exist_ok=True)
    observed_det = sorted({
        str(e.get("problem_type_id"))
        for e in entries
        if str(e.get("runtime_category")) in DETERMINISTIC_RUNTIME_CATEGORIES and str(e.get("problem_type_id")) not in {"", "unknown"}
    })
    lines = [
        f"# Inventory Report: {args.skill_id}",
        "",
        f"- examples_count: {len(examples)}",
        f"- examples_map_count: {len(entries)}",
        f"- observed_deterministic_problem_types: {observed_det}",
        f"- package_dir: {package_dir}",
    ]
    rpt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"success": True, "examples_count": len(examples), "report": str(rpt), "package_dir": str(package_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
