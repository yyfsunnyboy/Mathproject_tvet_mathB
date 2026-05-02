#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mark math B4 3-2 image-dependent chart questions without re-import."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from sqlalchemy import and_, or_


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # pylint: disable=wrong-import-position
from models import TextbookExample, db  # pylint: disable=wrong-import-position


TARGET_SKILLS = {
    "vh_數學B4_FrequencyDistributionTableConstruction",
    "vh_數學B4_HistogramsAndFrequencyPolygons",
    "vh_數學B4_CumulativeFrequencyTablesAndGraphs",
    "vh_數學B4_StatisticalChartReading",
}

IMAGE_DEP_PAT = re.compile(
    r"如右|如下|下圖|右圖|圖中|直方圖如右|折線圖如右|長條圖|圓形圖|"
    r"累積次數分配折線圖如右|以上累積次數分配折線圖如右|以下累積次數分配折線圖如下"
)


def parse_meta(raw: str) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {"raw": raw}
    except Exception:
        return {"raw": raw}


def dump_meta(meta: dict) -> str:
    return json.dumps(meta, ensure_ascii=False)


def append_unique_log(meta: dict, msg: str) -> None:
    logs = meta.get("repair_log", [])
    if not isinstance(logs, list):
        logs = [str(logs)]
    if msg not in logs:
        logs.append(msg)
    meta["repair_log"] = logs


def has_nonempty_image_assets(meta: dict) -> bool:
    assets = meta.get("image_assets", [])
    return isinstance(assets, list) and len(assets) > 0


def ensure_needs_review_in_source_description(source_description: str) -> str:
    s = str(source_description or "")
    if "needs_review=true" in s:
        return s
    if "]" in s and "[" in s:
        return s.replace("]", " | needs_review=true]", 1)
    return f"{s} [needs_review=true]"


def preview(text: str, n: int = 120) -> str:
    t = str(text or "").replace("\n", "\\n")
    return t[:n] + ("..." if len(t) > n else "")


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
        rows = (
            TextbookExample.query.filter(
                TextbookExample.source_curriculum == "vocational",
                TextbookExample.source_volume == "數學B4",
                or_(
                    and_(
                        or_(
                            TextbookExample.source_chapter.contains("3"),
                            TextbookExample.source_chapter.contains("統計"),
                        ),
                        or_(
                            TextbookExample.source_section.contains("3-2"),
                            TextbookExample.source_section.contains("統計資料整理"),
                        ),
                    ),
                    TextbookExample.skill_id.in_(TARGET_SKILLS),
                ),
            )
            .order_by(TextbookExample.id.asc())
            .all()
        )

        scanned_count = len(rows)
        image_dependent_count = 0
        missing_image_marked_count = 0
        has_image_asset_count = 0
        previews = []

        for row in rows:
            problem_text = str(row.problem_text or "")
            if not IMAGE_DEP_PAT.search(problem_text):
                continue
            image_dependent_count += 1

            old_meta = parse_meta(row.notes)
            new_meta = dict(old_meta)
            old_desc = str(row.source_description or "")
            new_desc = old_desc

            if has_nonempty_image_assets(old_meta):
                has_image_asset_count += 1
                new_meta["has_image"] = True
                new_meta["needs_image_review"] = False
            else:
                missing_image_marked_count += 1
                new_meta["has_image"] = True
                new_meta["needs_image_review"] = True
                new_meta["missing_docx_image_asset"] = True
                new_meta["needs_review"] = True
                append_unique_log(new_meta, "marked image-dependent chart question without image asset")
                new_desc = ensure_needs_review_in_source_description(new_desc)
                if "（圖片待補）" not in problem_text:
                    row.problem_text = problem_text + "（圖片待補）"

            row.notes = dump_meta(new_meta)
            row.source_description = new_desc

            if len(previews) < 30:
                previews.append(
                    {
                        "id": row.id,
                        "source_description": row.source_description,
                        "skill_id": row.skill_id,
                        "problem_text": row.problem_text,
                        "old_metadata": old_meta,
                        "new_metadata": new_meta,
                    }
                )

        if do_apply:
            db.session.commit()
        else:
            db.session.rollback()

        print(f"scanned_count={scanned_count}")
        print(f"image_dependent_count={image_dependent_count}")
        print(f"missing_image_marked_count={missing_image_marked_count}")
        print(f"has_image_asset_count={has_image_asset_count}")
        print("\npreview_first_30:")
        for p in previews:
            print(f"- id={p['id']}")
            print(f"  source_description={preview(p['source_description'])}")
            print(f"  skill_id={p['skill_id']}")
            print(f"  problem_text={preview(p['problem_text'])}")
            print(f"  old_metadata={preview(json.dumps(p['old_metadata'], ensure_ascii=False), 200)}")
            print(f"  new_metadata={preview(json.dumps(p['new_metadata'], ensure_ascii=False), 200)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

