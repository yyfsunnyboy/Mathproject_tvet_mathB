#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""One-time repair for Math B4 chapter-2 self-assessment records.

Uses Flask app context + SQLAlchemy models only.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from sqlalchemy import or_


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # pylint: disable=wrong-import-position
from models import db, SkillInfo, TextbookExample  # pylint: disable=wrong-import-position
from core.textbook_processor import normalize_probability_event_notation  # pylint: disable=wrong-import-position


def preview(text: str, n: int = 120) -> str:
    s = str(text or "").replace("\n", "\\n")
    return s[:n] + ("..." if len(s) > n else "")


def has_risk_to_keep_review(problem_text: str, notes: str, source_description: str) -> bool:
    text = str(problem_text or "")
    note = str(notes or "")
    desc = str(source_description or "")
    if any(k in text for k in ("[FORMULA_MISSING]", "[WORD_EQUATION_UNPARSED]")):
        return True
    if "formula_missing" in note and "true" in note.lower():
        return True
    if "needs_formula_review" in note and "true" in note.lower():
        return True
    if "block_boundary_error" in note and "true" in note.lower():
        return True
    if "image_warning" in note or "missing_docx_image_asset" in note:
        return True
    if "missing_docx_image_asset" in desc:
        return True
    return False


def clear_needs_review_flag(source_description: str, keep: bool) -> str:
    sd = str(source_description or "")
    if keep or "needs_review=true" not in sd:
        return sd
    sd = sd.replace(" | needs_review=true", "")
    sd = sd.replace("needs_review=true | ", "")
    sd = sd.replace("needs_review=true", "")
    sd = re.sub(r"\[\s*\|\s*", "[", sd)
    sd = re.sub(r"\s*\|\s*\]", "]", sd)
    sd = re.sub(r"\[\s*\]", "", sd)
    sd = re.sub(r"\s{2,}", " ", sd).strip()
    return sd


def _skill_exists(skill_id: str) -> bool:
    return SkillInfo.query.get(skill_id) is not None


def infer_skill_id(problem_text: str) -> str:
    text = str(problem_text or "")
    if re.search(r"條件機率|P\s*\(\s*[A-Za-z]\s*\|\s*[A-Za-z]\s*\)|已知.{0,20}發生|在.{0,20}條件下", text):
        return "vh_數學B4_ConditionalProbability"
    if re.search(r"獨立事件|相互獨立|命中率|連續命中", text):
        return "vh_數學B4_IndependentEvents"
    if re.search(r"期望值|期望|獲利|公平|平均獲利|期望獲利", text):
        target = "vh_數學B4_ApplicationsOfExpectation"
        if _skill_exists(target):
            return target
        return "vh_數學B4_MathematicalExpectation"
    if re.search(r"P\s*\(\s*[A-Za-z](?:'|\\prime)?(?:\s*(?:\\cup|\\cap|\||-)\s*[A-Za-z](?:'|\\prime)?)?\s*\)|機率", text):
        return "vh_數學B4_ProbabilityProperties"
    if re.search(r"樣本空間|樣本點|事件|餘事件|互斥|和事件|積事件", text):
        return "vh_數學B4_SampleSpaceAndEvents"
    if re.search(r"集合|子集|子集合|A\s*\\subset\s*B|A\s*\\cap\s*B|A\s*\\cup\s*B|空集合|宇集|元素", text):
        return "vh_數學B4_BasicConceptsOfSets"
    return ""


def _inline_ranges(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in re.finditer(r"\\\((.*?)\\\)", text)]


def _inside_ranges(idx: int, ranges: list[tuple[int, int]]) -> bool:
    return any(s <= idx < e for s, e in ranges)


def normalize_set_notation_inline_math(text: str) -> tuple[str, bool]:
    out = str(text or "")
    changed = False
    pattern = re.compile(r"\b([A-Za-z])\s*(\\subset|\\cap|\\cup)\s*([A-Za-z])\b")

    def repl(match: re.Match) -> str:
        nonlocal changed, out
        ranges = _inline_ranges(out)
        if _inside_ranges(match.start(), ranges):
            return match.group(0)
        changed = True
        return rf"\({match.group(1)} {match.group(2)} {match.group(3)}\)"

    out = pattern.sub(repl, out)
    return out, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    do_apply = bool(args.apply)
    if not args.apply and not args.dry_run:
        args.dry_run = True

    app = create_app()
    with app.app_context():
        print(f"SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")

        rows = (
            TextbookExample.query.filter(
                TextbookExample.source_curriculum == "vocational",
                TextbookExample.source_volume == "數學B4",
                or_(
                    TextbookExample.source_chapter.contains("2"),
                    TextbookExample.source_chapter.contains("機率"),
                ),
                or_(
                    TextbookExample.source_description.contains("self_assessment"),
                    TextbookExample.source_description.contains("自我評量"),
                ),
            )
            .order_by(TextbookExample.id.asc())
            .all()
        )

        scanned_count = len(rows)
        updated_count = 0
        skill_changed_count = 0
        review_cleared_count = 0
        latex_fixed_count = 0
        previews = []

        for row in rows:
            old_skill_id = str(row.skill_id or "")
            old_desc = str(row.source_description or "")
            old_text = str(row.problem_text or "")
            notes = str(row.notes or "")

            new_skill_id = old_skill_id
            if new_skill_id == "vh_數學B4_ProbabilityOperations":
                new_skill_id = "vh_數學B4_ProbabilityProperties"

            mapped_skill = infer_skill_id(old_text)
            if mapped_skill and _skill_exists(mapped_skill):
                new_skill_id = mapped_skill

            prob_fixed, prob_meta = normalize_probability_event_notation(old_text)
            set_fixed, set_changed = normalize_set_notation_inline_math(prob_fixed)
            new_text = set_fixed

            keep_review = has_risk_to_keep_review(new_text, notes, old_desc)
            new_desc = clear_needs_review_flag(old_desc, keep=keep_review)

            row_changed = (new_skill_id != old_skill_id) or (new_desc != old_desc) or (new_text != old_text)
            if not row_changed:
                continue

            updated_count += 1
            if new_skill_id != old_skill_id:
                skill_changed_count += 1
            if old_desc != new_desc and "needs_review=true" in old_desc and "needs_review=true" not in new_desc:
                review_cleared_count += 1
            if prob_meta.get("changed") or set_changed:
                latex_fixed_count += 1

            if len(previews) < 30:
                previews.append(
                    {
                        "id": row.id,
                        "source_description": old_desc,
                        "old_skill_id": old_skill_id,
                        "new_skill_id": new_skill_id,
                        "old_problem_text": old_text,
                        "new_problem_text": new_text,
                    }
                )

            row.skill_id = new_skill_id
            row.source_description = new_desc
            row.problem_text = new_text

        if do_apply:
            db.session.commit()
        else:
            db.session.rollback()

        print(f"scanned_count={scanned_count}")
        print(f"updated_count={updated_count}")
        print(f"skill_changed_count={skill_changed_count}")
        print(f"review_cleared_count={review_cleared_count}")
        print(f"latex_fixed_count={latex_fixed_count}")
        print("\npreview_first_30:")
        for p in previews:
            print(f"- id={p['id']}")
            print(f"  source_description={preview(p['source_description'])}")
            print(f"  old_skill_id={p['old_skill_id']}")
            print(f"  new_skill_id={p['new_skill_id']}")
            print(f"  old_problem_text={preview(p['old_problem_text'])}")
            print(f"  new_problem_text={preview(p['new_problem_text'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

