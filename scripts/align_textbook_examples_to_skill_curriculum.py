#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
將 textbook_examples 的 source_chapter / source_section 強制對齊 skill_curriculum 標準座標。

用途：清除匯入殘留（如「1-4習題 基礎題7 [...]」）並與多層次選單大綱字串一致。

用法：
  python scripts/align_textbook_examples_to_skill_curriculum.py --dry-run
  python scripts/align_textbook_examples_to_skill_curriculum.py --apply
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from core.textbook_processor import extract_section_code_from_title  # noqa: E402
from models import SkillCurriculum, TextbookExample, db  # noqa: E402

_GARBAGE_SECTION_RE = re.compile(r"習題|基礎題|進階題|自我評量\s*題|\[\.\.\.\]|\[source_type=", re.I)


def _is_official_skill_id(skill_id: str) -> bool:
    sid = str(skill_id or "").strip()
    return sid.startswith("vh_") and not sid.startswith("outline_")


def _section_sort_key(row: SkillCurriculum) -> tuple:
    sec = str(getattr(row, "section", "") or "")
    garbage = 1 if _GARBAGE_SECTION_RE.search(sec) else 0
    return (
        garbage,
        len(sec),
        int(getattr(row, "display_order", 0) or 0),
        int(getattr(row, "id", 0) or 0),
    )


def _pick_standard_meta(
    rows: list[SkillCurriculum],
    *,
    hint_section: str = "",
) -> SkillCurriculum | None:
    """自同一 skill_id 的多筆大綱中選一筆標準錨點。"""
    official = [r for r in rows if _is_official_skill_id(str(getattr(r, "skill_id", "") or ""))]
    if not official:
        return None

    code = extract_section_code_from_title(hint_section)
    if code:
        scoped = [
            r
            for r in official
            if str(getattr(r, "section", "") or "") == code
            or str(getattr(r, "section", "") or "").startswith(f"{code} ")
        ]
        if scoped:
            return sorted(scoped, key=_section_sort_key)[0]

    clean = [r for r in official if not _GARBAGE_SECTION_RE.search(str(getattr(r, "section", "") or ""))]
    pool = clean or official
    return sorted(pool, key=_section_sort_key)[0]


def _build_curriculum_indexes(
    *,
    curriculum: str,
    volume: str,
    grade: int,
) -> tuple[dict[str, list[SkillCurriculum]], dict[str, list[SkillCurriculum]]]:
    rows = (
        SkillCurriculum.query.filter_by(
            curriculum=curriculum,
            volume=volume,
            grade=grade,
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .all()
    )
    by_skill: dict[str, list[SkillCurriculum]] = defaultdict(list)
    by_section_code: dict[str, list[SkillCurriculum]] = defaultdict(list)
    for row in rows:
        sid = str(getattr(row, "skill_id", "") or "").strip()
        if sid:
            by_skill[sid].append(row)
        code = extract_section_code_from_title(str(getattr(row, "section", "") or ""))
        if code:
            by_section_code[code].append(row)
    return by_skill, by_section_code


def _resolve_standard_meta(
    *,
    skill_id: str,
    hint_section: str,
    by_skill: dict[str, list[SkillCurriculum]],
    by_section_code: dict[str, list[SkillCurriculum]],
) -> SkillCurriculum | None:
    sid = str(skill_id or "").strip()
    if sid:
        hit = _pick_standard_meta(by_skill.get(sid) or [], hint_section=hint_section)
        if hit is not None:
            return hit
    code = extract_section_code_from_title(hint_section)
    if code:
        return _pick_standard_meta(by_section_code.get(code) or [], hint_section=hint_section)
    return None


def align_textbook_examples(
    *,
    curriculum: str = "vocational",
    volume: str = "數學B1",
    grade: int = 10,
    dry_run: bool = True,
    limit: int | None = None,
) -> dict[str, int]:
    by_skill, by_section_code = _build_curriculum_indexes(
        curriculum=curriculum, volume=volume, grade=grade
    )

    # 遍歷全表；僅在 skill_id 能對到指定冊別大綱時才覆寫章節座標
    q = TextbookExample.query.order_by(TextbookExample.id.asc())
    if limit is not None and limit > 0:
        q = q.limit(limit)

    stats = {
        "scanned": 0,
        "updated": 0,
        "already_aligned": 0,
        "no_skill_id": 0,
        "no_curriculum_meta": 0,
        "unchanged_fields": 0,
    }
    samples: list[str] = []

    for ex in q.all():
        stats["scanned"] += 1
        sid = str(getattr(ex, "skill_id", "") or "").strip()
        if not sid:
            stats["no_skill_id"] += 1
            continue

        hint_section = str(getattr(ex, "source_section", "") or "")
        standard = _resolve_standard_meta(
            skill_id=sid,
            hint_section=hint_section,
            by_skill=by_skill,
            by_section_code=by_section_code,
        )
        if standard is None:
            stats["no_curriculum_meta"] += 1
            if len(samples) < 20:
                samples.append(
                    f"id={ex.id} skill_id={sid!r} "
                    f"chapter={ex.source_chapter!r} section={ex.source_section!r} -> NO_META"
                )
            continue

        target_chapter = str(getattr(standard, "chapter", "") or "").strip()
        target_section = str(getattr(standard, "section", "") or "").strip()
        if not target_chapter or not target_section:
            stats["no_curriculum_meta"] += 1
            continue

        cur_ch = str(getattr(ex, "source_chapter", "") or "").strip()
        cur_sec = str(getattr(ex, "source_section", "") or "").strip()

        if cur_ch == target_chapter and cur_sec == target_section:
            stats["already_aligned"] += 1
            continue

        stats["updated"] += 1
        if len(samples) < 30:
            samples.append(
                f"id={ex.id} skill_id={sid}\n"
                f"  chapter: {cur_ch!r} -> {target_chapter!r}\n"
                f"  section: {cur_sec!r} -> {target_section!r}"
            )

        if not dry_run:
            ex.source_chapter = target_chapter
            ex.source_section = target_section
            ex.source_curriculum = curriculum
            ex.source_volume = volume
            if str(getattr(ex, "skill_id", "") or "") != str(getattr(standard, "skill_id", "") or ""):
                ex.skill_id = str(getattr(standard, "skill_id", "") or "").strip()

    if not dry_run and stats["updated"] > 0:
        db.session.commit()
    elif dry_run:
        db.session.rollback()

    print(f"--- align textbook_examples ({'DRY RUN' if dry_run else 'APPLIED'}) ---")
    print(f"scope: curriculum={curriculum!r} volume={volume!r} grade={grade}")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    if samples:
        print("\nSample changes:")
        for line in samples:
            print(line)
            print()

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Align textbook_examples chapter/section to skill_curriculum (Math B1)."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="寫入資料庫並 commit（預設僅 dry-run）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="僅預覽變更，不寫入（預設行為，可省略）",
    )
    parser.add_argument("--curriculum", default="vocational")
    parser.add_argument("--volume", default="數學B1")
    parser.add_argument("--grade", type=int, default=10)
    parser.add_argument("--limit", type=int, default=0, help="僅處理前 N 筆（除錯用，0=全部）")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        dry_run = not args.apply
        align_textbook_examples(
            curriculum=str(args.curriculum).strip(),
            volume=str(args.volume).strip(),
            grade=int(args.grade),
            dry_run=dry_run,
            limit=args.limit if args.limit > 0 else None,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
