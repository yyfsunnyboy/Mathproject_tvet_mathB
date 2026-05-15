from core.routes.admin import _derive_formula_status


def test_formula_status_image_placeholder_no_asset():
    status, label, _ = _derive_formula_status(
        formula_assets_count=0,
        has_formula_image_placeholder=True,
        has_formula_missing_placeholder=False,
        needs_formula_review=True,
    )
    assert status == "image_placeholder_no_asset"
    assert "未找到對應資產" in label


def test_formula_status_missing_no_asset():
    status, label, _ = _derive_formula_status(
        formula_assets_count=0,
        has_formula_image_placeholder=False,
        has_formula_missing_placeholder=True,
        needs_formula_review=True,
    )
    assert status == "missing_no_asset"
    assert "公式缺失" in label


def test_formula_status_asset_attached():
    status, _, _ = _derive_formula_status(
        formula_assets_count=1,
        has_formula_image_placeholder=True,
        has_formula_missing_placeholder=False,
        needs_formula_review=True,
    )
    assert status == "asset_attached"


def test_formula_status_asset_attached_but_text_missing():
    status, _, _ = _derive_formula_status(
        formula_assets_count=2,
        has_formula_image_placeholder=False,
        has_formula_missing_placeholder=True,
        needs_formula_review=True,
    )
    assert status == "asset_attached_but_text_missing"


def test_formula_status_ok_without_placeholder_and_no_formula_review():
    status, _, _ = _derive_formula_status(
        formula_assets_count=0,
        has_formula_image_placeholder=False,
        has_formula_missing_placeholder=False,
        needs_formula_review=False,
    )
    assert status == "ok"
