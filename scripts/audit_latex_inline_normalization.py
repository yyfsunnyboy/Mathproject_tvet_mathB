# -*- coding: utf-8 -*-
"""Audit/apply converted_docx_latex inline LaTeX normalization on textbook_examples."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from core.math_formula_normalizer import normalize_converted_docx_latex_text


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--volume")
    p.add_argument("--section")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("--report")
    return p.parse_args()


def _build_where(args: argparse.Namespace) -> tuple[str, list[str]]:
    clauses = []
    params: list[str] = []
    if args.volume:
        clauses.append("source_volume = ?")
        params.append(args.volume)
    if args.section:
        clauses.append("source_section = ?")
        params.append(args.section)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def _decision(text_before: str, norm: dict) -> str:
    text_after = str(norm.get("text", "") or "")
    changes = norm.get("changes", []) or []
    if not changes or text_before == text_after:
        return "no_change"
    if norm.get("needs_review"):
        return "review_only"
    min_conf = min(float(c.get("confidence", 0.0)) for c in changes)
    return "auto_fix" if min_conf >= 0.9 else "review_only"


def _write_report(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# LaTeX Inline Normalization Audit",
        "",
        "| id | title/source_description | skill_id | decision | changes |",
        "|---:|---|---|---|---:|",
    ]
    for r in rows:
        title = (r["source_description"] or "").replace("\n", " ")
        lines.append(f"| {r['id']} | {title} | {r['skill_id']} | {r['decision']} | {len(r['changes'])} |")
        lines.append("")
        lines.append("**before**")
        lines.append("")
        lines.append(f"```text\n{r['before']}\n```")
        lines.append("")
        lines.append("**after**")
        lines.append("")
        lines.append(f"```text\n{r['after']}\n```")
        lines.append("")
        lines.append("**changes**")
        lines.append("")
        lines.append("```json")
        lines.append(str(r["changes"]))
        lines.append("```")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = _parse_args()
    if not args.dry_run and not args.write:
        raise SystemExit("Specify either --dry-run or --write.")
    if args.dry_run and args.write:
        raise SystemExit("Use only one mode: --dry-run or --write.")

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where, params = _build_where(args)
    query = (
        "SELECT id, source_description, skill_id, problem_text "
        f"FROM textbook_examples {where} ORDER BY id"
    )
    rows = [dict(r) for r in cur.execute(query, params).fetchall()]

    audited: list[dict] = []
    apply_count = 0
    for r in rows:
        before = str(r.get("problem_text", "") or "")
        norm = normalize_converted_docx_latex_text(before)
        after = str(norm.get("text", "") or "")
        changes = norm.get("changes", []) or []
        decision = _decision(before, norm)
        audited.append(
            {
                "id": r["id"],
                "source_description": r.get("source_description", ""),
                "skill_id": r.get("skill_id", ""),
                "before": before,
                "after": after,
                "changes": changes,
                "decision": decision,
            }
        )

        if args.write and decision == "auto_fix":
            cur.execute("UPDATE textbook_examples SET problem_text = ? WHERE id = ?", (after, r["id"]))
            apply_count += 1

    if args.write:
        conn.commit()
    conn.close()

    if args.report:
        _write_report(Path(args.report), audited)

    print(f"rows={len(audited)} write={bool(args.write)} updated={apply_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
