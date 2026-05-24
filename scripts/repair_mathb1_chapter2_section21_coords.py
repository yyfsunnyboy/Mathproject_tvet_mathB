# -*- coding: utf-8 -*-
"""
修正 2-1 斜率 formal skill 被誤寫入第 1 章的 SkillCurriculum / TextbookExample。
僅處理 section 2-1 斜率 與指定 skill_id，不影響第 1 章資料。
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

TARGET_SKILL_IDS = (
    "vh_數學B1_SlopeOfALine",
    "vh_數學B1_PropertiesOfParallelLines",
    "vh_數學B1_PropertiesOfPerpendicularLines",
)

SECTION_PREFIX = "2-1 "


def main() -> int:
    from app import create_app
    from models import SkillCurriculum, SkillInfo, TextbookExample, db

    app = create_app()
    with app.app_context():
        outline = (
            SkillCurriculum.query.filter(
                SkillCurriculum.curriculum == "vocational",
                SkillCurriculum.volume == "數學B1",
                SkillCurriculum.section.startswith(SECTION_PREFIX),
                SkillCurriculum.skill_id.startswith("outline_"),
            )
            .order_by(SkillCurriculum.id.asc())
            .first()
        )
        if outline is None:
            print("ERROR: no outline row for 2-1 section")
            return 1

        correct_chapter = str(outline.chapter or "").strip()
        correct_section = str(outline.section or "").strip()
        print(f"outline chapter={correct_chapter!r} section={correct_section!r}")

        cur_fixed = 0
        for sid in TARGET_SKILL_IDS:
            rows = SkillCurriculum.query.filter_by(skill_id=sid).all()
            for row in rows:
                sec = str(row.section or "")
                if not sec.startswith("2-1"):
                    continue
                if str(row.chapter or "") != correct_chapter:
                    print(f"SkillCurriculum fix {sid}: chapter {row.chapter!r} -> {correct_chapter!r}")
                    row.chapter = correct_chapter
                    cur_fixed += 1
                if row.section != correct_section and correct_section.startswith("2-1"):
                    row.section = correct_section

        info_fixed = 0
        for sid in TARGET_SKILL_IDS:
            info = SkillInfo.query.get(sid)
            if info is None:
                continue
            if str(info.category or "") != correct_section:
                print(f"SkillInfo fix {sid}: category -> {correct_section!r}")
                info.category = correct_section
                info_fixed += 1

        wrong_ch = "1 坐標系與函數圖形"
        ex_fixed = 0
        ex_reverted = 0
        # 還原誤改：非目標 skill、章名曾為「2 機率」等 B2 資料
        for ex in TextbookExample.query.filter(
            TextbookExample.source_section.like("2-1 %"),
            TextbookExample.source_chapter == correct_chapter,
        ).all():
            sid = str(ex.skill_id or "")
            if sid in TARGET_SKILL_IDS:
                continue
            if "數學B1" not in str(ex.source_volume or "") and ex.source_volume:
                if ex.source_chapter == correct_chapter:
                    ex.source_chapter = "2 機率"
                    ex_reverted += 1
                    print(f"TextbookExample revert {ex.id} -> 2 機率 (B2)")

        for ex in TextbookExample.query.filter(
            TextbookExample.skill_id.in_(TARGET_SKILL_IDS)
        ).all():
            sec = str(ex.source_section or "")
            if not sec.startswith("2-1"):
                continue
            changed = False
            if ex.source_chapter == wrong_ch:
                print(
                    f"TextbookExample {ex.id} chapter {ex.source_chapter!r} -> {correct_chapter!r}"
                )
                ex.source_chapter = correct_chapter
                changed = True
            if correct_section and ex.source_section != correct_section:
                ex.source_section = correct_section
                changed = True
            if changed:
                ex_fixed += 1

        db.session.commit()
        print(
            f"done curriculum_rows={cur_fixed} skill_info={info_fixed} "
            f"textbook_examples={ex_fixed} reverted={ex_reverted}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
