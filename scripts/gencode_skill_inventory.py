import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

TARGET_SKILL = "vh_數學B1_AbsoluteValue"


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


def _example_text(ex: dict[str, Any]) -> str:
    parts = []
    for k in ("problem_text", "problem", "question", "stem", "content", "title"):
        val = ex.get(k)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
    return " ".join(parts)


def _is_expr_eval(t: str) -> bool:
    return ("|a|" in t and "|b|" in t) or ("|a-b|" in t) or ("|x-y|" in t)


def _is_equation(t: str) -> bool:
    return "|x|=" in t or ("方程" in t and "|x|" in t)


def _is_choice_def(t: str) -> bool:
    return ("下列何者" in t or "選擇" in t) and ("絕對值" in t or "|a|" in t)


def _is_compare(t: str) -> bool:
    return "比較" in t or "大小" in t or "最大" in t or "最小" in t or "排序" in t


def _is_numeric(t: str) -> bool:
    return ("求" in t and "值" in t and "|" in t) or ("|-" in t)


def _infer_subskills(examples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        "absolute_value_numeric_evaluation",
        "absolute_value_distance_from_zero",
        "absolute_value_expression_evaluation",
        "absolute_value_compare_or_order",
        "absolute_value_equation_basic",
        "absolute_value_simplification_by_sign",
        "absolute_value_definition_choice",
    ]
    out = []
    for sid in candidates:
        ids = []
        for ex in examples:
            t = _example_text(ex)
            ok = False
            if sid == "absolute_value_numeric_evaluation":
                ok = _is_numeric(t)
            elif sid == "absolute_value_distance_from_zero":
                ok = "距離" in t and ("原點" in t or "0" in t)
            elif sid == "absolute_value_expression_evaluation":
                ok = _is_expr_eval(t)
            elif sid == "absolute_value_compare_or_order":
                ok = _is_compare(t)
            elif sid == "absolute_value_equation_basic":
                ok = _is_equation(t)
            elif sid == "absolute_value_simplification_by_sign":
                ok = ("化簡" in t and "|x|" in t and ("x<0" in t or "x>0" in t))
            elif sid == "absolute_value_definition_choice":
                ok = _is_choice_def(t)
            if ok:
                ids.append(ex.get("id"))
        observed = len(ids) > 0
        runtime = "not_observed"
        if observed:
            if sid in {"absolute_value_compare_or_order", "absolute_value_definition_choice"}:
                runtime = "deterministic_choice"
            elif sid == "absolute_value_simplification_by_sign":
                runtime = "manual_review"
            else:
                runtime = "deterministic_numeric"
        out.append(
            {
                "subskill_id": sid,
                "observed": observed,
                "supporting_example_ids": ids,
                "suggested_problem_types": [sid] if observed else [],
                "runtime_category": runtime,
                "prerequisite_subskills": ["absolute_value_numeric_evaluation"] if sid != "absolute_value_numeric_evaluation" else [],
                "diagnosis_tags": ["absolute_value"],
            }
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--db-path", default="instance/kumon_math.db")
    args = p.parse_args()
    if args.skill_id != TARGET_SKILL:
        raise RuntimeError("此版本僅支援 vh_數學B1_AbsoluteValue")

    root = Path(__file__).resolve().parents[1]
    con = sqlite3.connect(str(root / args.db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    meta = [dict(r) for r in cur.execute(
        """
        SELECT sc.skill_id, sc.curriculum, sc.volume, sc.chapter, sc.section, si.skill_ch_name, si.category
        FROM skill_curriculum sc
        LEFT JOIN skills_info si ON si.skill_id=sc.skill_id
        WHERE sc.skill_id=?
        """,
        (args.skill_id,),
    ).fetchall()]
    te_cols = [r[1] for r in cur.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    order_key = "id" if "id" in te_cols else "rowid"
    examples = [dict(r) for r in cur.execute(f"SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY {order_key}", (args.skill_id,)).fetchall()]
    con.close()

    if len(examples) == 0:
        raise RuntimeError("textbook_examples count is 0; cannot build inventory")

    subskills = _infer_subskills(examples)
    pts = []
    for s in subskills:
        if not s["observed"]:
            continue
        sid = s["subskill_id"]
        if sid == "absolute_value_simplification_by_sign":
            continue
        ans = "integer"
        chk = "integer_checker"
        runtime = "deterministic_numeric"
        if sid in {"absolute_value_compare_or_order", "absolute_value_definition_choice"}:
            ans = "choice"
            chk = "choice_checker"
            runtime = "deterministic_choice"
        if sid == "absolute_value_equation_basic":
            ans = "text"
            chk = "exact_string_checker"
            runtime = "deterministic_expression"
        pts.append(
            {
                "problem_type_id": sid,
                "skill_id": args.skill_id,
                "subskill_id": sid,
                "display_name": sid.replace("_", " "),
                "runtime_category": runtime,
                "answer_type": ans,
                "checker_type": chk,
                "examples_refs": s["supporting_example_ids"],
                "prerequisite_subskills": s["prerequisite_subskills"],
                "diagnosis_tags": s["diagnosis_tags"],
                "difficulty_policy": "easy_only_v1",
                "output_contract": {"required_keys": ["problem_type_id", "skill_id", "subskill_id", "question_text", "answer", "answer_type", "checker_type", "solution_steps", "metadata"]},
                "status": "draft",
            }
        )

    base = root / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value"
    base.mkdir(parents=True, exist_ok=True)
    slug = "absolute_value"
    (base / f"subskills_{slug}.yaml").write_text(_yaml_like({"skill_id": args.skill_id, "subskills": subskills}) + "\n", encoding="utf-8")
    (base / f"problem_types_{slug}.yaml").write_text(_yaml_like({"items": pts}) + "\n", encoding="utf-8")
    examples_map = [{"id": e.get("id"), "skill_id": e.get("skill_id"), "problem_text_preview": _example_text(e)[:200]} for e in examples]
    (base / f"examples_map_{slug}.yaml").write_text(_yaml_like({"examples": examples_map}) + "\n", encoding="utf-8")
    prereq = [{"subskill_id": s["subskill_id"], "prerequisite_subskills": s["prerequisite_subskills"]} for s in subskills]
    (base / f"prerequisites_{slug}.yaml").write_text(_yaml_like({"items": prereq}) + "\n", encoding="utf-8")

    rpt = root / "reports" / "gencode_closed_loop" / f"{args.skill_id}_inventory_report.md"
    rpt.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Inventory Report: {args.skill_id}",
        "",
        f"- examples_count: {len(examples)}",
        "- subskills:",
        *[f"  - {s['subskill_id']}: {'observed' if s['observed'] else 'not_observed'}" for s in subskills],
        "",
        "- problem_types:",
        *[f"  - {pt['problem_type_id']}" for pt in pts],
    ]
    rpt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"success": True, "examples_count": len(examples), "report": str(rpt)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
