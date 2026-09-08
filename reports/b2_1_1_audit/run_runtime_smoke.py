import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from flask_login import login_user
from app import create_app
from models import db, User, TextbookExample

app = create_app()

targets = [
    ("例1", 11606, "vh_數學B2_AngleMeasurementAndConversion"),
    ("隨堂練習1", 11607, "vh_數學B2_AngleMeasurementAndConversion"),
    ("基礎題1", 11616, "vh_數學B2_AngleMeasurementAndConversion"),
    ("基礎題2", 11617, "vh_數學B2_AngleMeasurementAndConversion"),
    ("基礎題3", 11618, "vh_數學B2_AngleMeasurementAndConversion"),
    ("SDG", 11610, "vh_數學B2_ArcLengthAndAreaOfSector"),
    ("例2(扇形圖)", 11608, "vh_數學B2_ArcLengthAndAreaOfSector"),
    ("基礎題5(扇形圖)", 11620, "vh_數學B2_ArcLengthAndAreaOfSector"),
]

results = {}

with app.app_context():
    user = db.session.get(User, 2)
    client = app.test_client()

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True

    for name, te_id, skill_id in targets:
        url = f"/get_next_question?skill={skill_id}&textbook_example_id={te_id}"
        resp = client.get(url)
        status = resp.status_code
        data = resp.get_json() if status == 200 else {}
        
        te = db.session.get(TextbookExample, te_id)
        
        has_mpf = "MATH_PARSE_FAILED" in (te.problem_text or "") or "MATH_PARSE_FAILED" in (te.detailed_solution or "")
        
        # Check image assets
        image_assets = data.get("image_assets") or []
        broken_assets = []
        for img in image_assets:
            p = ROOT / img["path"] if not Path(img["path"]).is_absolute() else Path(img["path"])
            if not p.is_file():
                broken_assets.append(f"file_not_found: {img['path']}")
            # Also test the static route
            route_sub = img["path"].replace("uploads/question_assets/", "")
            route_url = f"/uploads/question_assets/{route_sub}"
            img_resp = client.get(route_url)
            if img_resp.status_code != 200:
                broken_assets.append(f"http_{img_resp.status_code}: {route_url}")

        q_text = data.get("question_text") or data.get("new_question_text") or ""
        results[name] = {
            "te_id": te_id,
            "skill_id": skill_id,
            "status_code": status,
            "has_mpf": has_mpf,
            "question_text": q_text,
            "detailed_solution": te.detailed_solution,
            "source_description": te.source_description,
            "has_image": bool(image_assets),
            "image_count": len(image_assets),
            "image_assets": image_assets,
            "broken_assets": broken_assets,
            "pass": status == 200 and not has_mpf and len(broken_assets) == 0,
        }
        print(f"[{name}] status={status}, mpf={has_mpf}, imgs={len(image_assets)}, broken={len(broken_assets)}")

(ROOT / "reports/b2_1_1_audit/runtime_smoke_results.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Runtime smoke finished, results saved!")
