# -*- coding: utf-8 -*-
"""Student practice display of TextbookExample.notes.image_assets."""

import json
import os

import pytest

from core.question_image_assets import (
    extract_raw_image_assets_from_notes,
    list_student_image_assets_from_notes,
    parse_notes_dict,
    question_asset_public_url,
)


def test_parse_notes_null_and_empty():
    assert parse_notes_dict(None) == {}
    assert parse_notes_dict("") == {}
    assert parse_notes_dict("   ") == {}
    assert parse_notes_dict("{not json") == {}
    assert parse_notes_dict([]) == {}


def test_notes_without_image_assets_yields_empty():
    assert extract_raw_image_assets_from_notes(None) == []
    assert extract_raw_image_assets_from_notes('{"question_anchor":"x"}') == []
    assert extract_raw_image_assets_from_notes('{"image_assets":[]}') == []
    assert list_student_image_assets_from_notes(None) == []
    assert list_student_image_assets_from_notes('{"image_assets":[]}') == []


def test_single_image_asset_renders_url(tmp_path):
    rel = "uploads/question_assets/test_student/fig1.png"
    abs_path = tmp_path / "uploads" / "question_assets" / "test_student" / "fig1.png"
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    notes = json.dumps(
        {
            "image_assets": [
                {
                    "path": rel,
                    "display_path": rel,
                    "source_page": 3,
                    "bbox": [1, 2, 3, 4],
                }
            ]
        },
        ensure_ascii=False,
    )
    assets = list_student_image_assets_from_notes(notes, root_path=str(tmp_path))
    assert len(assets) == 1
    assert assets[0]["url"] == "/" + rel
    assert question_asset_public_url(rel, root_path=str(tmp_path)) == "/" + rel


def test_multiple_image_assets_preserve_order(tmp_path):
    paths = []
    for i in (1, 2, 3):
        rel = f"uploads/question_assets/test_student/fig{i}.png"
        abs_path = tmp_path / "uploads" / "question_assets" / "test_student" / f"fig{i}.png"
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_bytes(b"\x89PNG\r\n\x1a\n")
        paths.append(rel)
    notes = json.dumps(
        {"image_assets": [{"path": p, "display_path": p} for p in paths]},
        ensure_ascii=False,
    )
    assets = list_student_image_assets_from_notes(notes, root_path=str(tmp_path))
    assert [a["url"] for a in assets] == ["/" + p for p in paths]


def test_invalid_missing_asset_skipped(tmp_path):
    good = "uploads/question_assets/test_student/ok.png"
    bad = "uploads/question_assets/test_student/missing.png"
    abs_path = tmp_path / "uploads" / "question_assets" / "test_student" / "ok.png"
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\x89PNG\r\n\x1a\n")
    notes = json.dumps(
        {
            "image_assets": [
                {"path": bad, "display_path": bad},
                {"path": good, "display_path": good},
                {"path": "C:/Windows/not_allowed.png"},
            ]
        }
    )
    assets = list_student_image_assets_from_notes(notes, root_path=str(tmp_path))
    assert len(assets) == 1
    assert assets[0]["url"] == "/" + good


@pytest.fixture
def app_client():
    from app import create_app
    from models import User, db
    from werkzeug.security import generate_password_hash

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        user = User.query.filter_by(username="pytest_student_img").first()
        if user is None:
            user = User(
                username="pytest_student_img",
                password_hash=generate_password_hash("test"),
                role="student",
            )
            db.session.add(user)
            db.session.commit()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True
        yield app, client


def test_b2_image_asset_urls_http_200(app_client):
    app, client = app_client
    paths = [
        "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/textbook_exercise_1-1習題_基礎題5_vocation_fig1.png",
        "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題9_vocation_fig1.png",
        "uploads/question_assets/vocational/longteng/數學B2/ch01_三角函數/sec_1-1_角度的基本性質/advanced_exercise_1-1習題_進階題10_vocation_fig1.png",
    ]
    with app.app_context():
        for rel in paths:
            abs_path = os.path.join(app.root_path, rel.replace("/", os.sep))
            if not os.path.isfile(abs_path):
                pytest.skip(f"asset missing on disk: {rel}")
            url = "/" + rel
            resp = client.get(url)
            assert resp.status_code == 200, url
            ctype = (resp.headers.get("Content-Type") or "").lower()
            assert "image/png" in ctype, (url, ctype)


def test_get_next_question_returns_image_assets_for_te(app_client):
    app, client = app_client
    cases = [
        (11560, "基礎題"),
        (11564, "進階題"),
        (11565, "進階題"),
    ]
    skill = "vh_數學B2_ArcLengthAndSectorArea"
    with app.app_context():
        from models import TextbookExample

        for te_id, _hint in cases:
            te = TextbookExample.query.get(te_id)
            if te is None:
                pytest.skip(f"TE {te_id} missing")
            resp = client.get(
                f"/get_next_question?skill={skill}&textbook_example_id={te_id}"
            )
            assert resp.status_code == 200, resp.get_data(as_text=True)[:300]
            data = resp.get_json()
            assert data.get("textbook_example_id") == te_id
            assert data.get("question_text") or data.get("new_question_text")
            assets = data.get("image_assets") or []
            assert len(assets) >= 1, te_id
            assert assets[0]["url"].startswith("/uploads/question_assets/")
            img = client.get(assets[0]["url"])
            assert img.status_code == 200
            assert "image/png" in (img.headers.get("Content-Type") or "").lower()


def test_get_next_question_no_image_for_text_only_te(app_client):
    app, client = app_client
    skill = "vh_數學B2_AngleMeasurementAndConversion"
    te_id = 11566  # 例1 — text/formula only under AI_REFERENCE policy
    with app.app_context():
        from models import TextbookExample
        from core.textbook_pdf_visual import parse_notes_dict

        te = TextbookExample.query.get(te_id)
        if te is None:
            pytest.skip("例1 TE missing")
        notes = parse_notes_dict(te.notes)
        assets = notes.get("image_assets") or []
        if assets:
            pytest.skip("例1 unexpectedly has image_assets")
        resp = client.get(f"/get_next_question?skill={skill}&textbook_example_id={te_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get("textbook_example_id") == te_id
        assert data.get("image_assets") == []


def test_attach_student_image_assets_null_notes_no_crash(app_client):
    app, _client = app_client
    with app.app_context():
        from core.routes.practice import _attach_student_image_assets

        out = _attach_student_image_assets({"question_text": "x", "notes": None})
        assert out["image_assets"] == []
        out2 = _attach_student_image_assets({"question_text": "x", "notes": "not-json"})
        assert out2["image_assets"] == []
        out3 = _attach_student_image_assets({"question_text": "x", "notes": '{"image_assets":[]}'})
        assert out3["image_assets"] == []
