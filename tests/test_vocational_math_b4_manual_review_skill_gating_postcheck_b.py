from __future__ import annotations

from pathlib import Path

from app import create_app


MANUAL_REVIEW_SKILLS = [
    "vh_數學B4_TreeDiagramCounting",
    "vh_數學B4_PascalTriangle",
]


def _client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _text(response) -> str:
    return response.get_data(as_text=True)


def test_tree_diagram_counting_practice_page_is_friendly_unavailable() -> None:
    client = _client()
    response = client.get("/practice/vh_數學B4_TreeDiagramCounting")

    assert response.status_code == 200
    body = _text(response)
    assert "暫緩" in body or "尚未開放" in body
    assert "AI" in body or "手寫" in body or "教師審閱" in body
    assert "disabled" in body or "data-manual-review-unavailable" in body
    assert "生成題目失敗" not in body
    assert "No module named" not in body


def test_pascal_triangle_practice_page_is_friendly_unavailable() -> None:
    client = _client()
    response = client.get("/practice/vh_數學B4_PascalTriangle")

    assert response.status_code == 200
    body = _text(response)
    assert "暫緩" in body or "尚未開放" in body
    assert "AI" in body or "手寫" in body or "教師審閱" in body
    assert "disabled" in body or "data-manual-review-unavailable" in body
    assert "生成題目失敗" not in body
    assert "No module named" not in body


def test_deterministic_skill_practice_page_is_not_marked_unavailable() -> None:
    client = _client()
    response = client.get("/practice/vh_數學B4_CombinationDefinition")

    assert response.status_code == 200
    body = _text(response)
    assert "此題型目前屬於 AI 手寫判分 / 教師審閱候選題型" not in body
    assert "data-manual-review-unavailable" not in body


def test_manual_review_skill_wrappers_are_not_added() -> None:
    assert not Path("skills/vh_數學B4_TreeDiagramCounting.py").exists()
    assert not Path("skills/vh_數學B4_PascalTriangle.py").exists()

