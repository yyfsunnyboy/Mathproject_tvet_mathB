from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import app
from models import TextbookExample, User, db


OUT = Path(__file__).resolve().parent
TARGET_ASSETS = {11557: 1, 11567: 1, 11558: 1, 11559: 1, 11561: 2}
CHECK_IDS = [11556, 11566, 11557, 11567, 11558, 11568, 11559, 11569, 11560,
             11570, 11561, 11571, 11562, 11572, 11563, 11573, 11564, 11586,
             11565, 11574, 11585, 11575, 11576, 11577, 11578, 11579, 11580,
             11581, 11582, 11583, 11584]


def main():
    with app.app_context():
        admin = User.query.filter(User.role == "admin").order_by(User.id).first()
        if admin is None:
            admin = User.query.order_by(User.id).first()
        if admin is None:
            raise RuntimeError("No user available for authenticated runtime check")
        rows = {row.id: row for row in TextbookExample.query.filter(TextbookExample.id.in_(CHECK_IDS)).all()}
        if set(rows) != set(CHECK_IDS):
            raise RuntimeError("B2 1-2 runtime rows missing")

        client = app.test_client()
        with client.session_transaction() as session:
            session["_user_id"] = str(admin.id)
            session["_fresh"] = True
            session["current_curriculum"] = "vocational"

        admin_response = client.get(
            "/examples",
            query_string={
                "f_curriculum": "vocational",
                "f_grade": "10",
                "f_volume": "數學B2",
                "f_chapter": "第1章 三角函數",
                "f_section": "1-2 銳角三角函數",
            },
        )
        admin_html = admin_response.get_data(as_text=True)
        rendered_ids = [
            int(value)
            for value in re.findall(r"<td>\s*(\d+)\s*</td>", admin_html)
            if int(value) in rows
        ]
        # Each row's first table cell appears once; ignore any unrelated numeric cells.
        rendered_ids = list(dict.fromkeys(rendered_ids))
        admin_ok = (
            admin_response.status_code == 200
            and rendered_ids == CHECK_IDS
            and "MATH_PARSE_FAILED" not in admin_html
        )

        student_checks = []
        for example_id in [11557, 11567, 11558, 11559, 11561, 11586]:
            row = rows[example_id]
            response = client.get(
                "/get_next_question",
                query_string={
                    "skill": row.skill_id,
                    "textbook_example_id": example_id,
                },
            )
            payload = response.get_json(silent=True) or {}
            assets = payload.get("image_assets") or []
            expected_assets = TARGET_ASSETS.get(example_id, 0)
            asset_http = []
            for asset in assets:
                url = asset.get("url") or asset.get("display_url") or asset.get("display_path")
                if url and not str(url).startswith("/"):
                    url = "/" + str(url).lstrip("/")
                asset_response = client.get(url) if url else None
                asset_http.append(bool(asset_response and asset_response.status_code == 200))
            ok = (
                response.status_code == 200
                and payload.get("textbook_example_id") == example_id
                and "MATH_PARSE_FAILED" not in str(payload.get("question_text") or "")
                and len(assets) == expected_assets
                and all(asset_http)
            )
            student_checks.append(
                {
                    "id": example_id,
                    "status": response.status_code,
                    "assets": len(assets),
                    "asset_http": asset_http,
                    "ok": ok,
                }
            )

        result = {
            "admin_status": admin_response.status_code,
            "admin_rendered_ids": rendered_ids,
            "admin_11586_position": rendered_ids.index(11586) + 1 if 11586 in rendered_ids else None,
            "admin_ok": admin_ok,
            "student_checks": student_checks,
            "runtime_page_check": admin_ok and all(item["ok"] for item in student_checks),
        }
        (OUT / "runtime_page_verification.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if not result["runtime_page_check"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
