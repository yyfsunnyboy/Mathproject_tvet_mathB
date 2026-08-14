# -*- coding: utf-8 -*-
"""Browser E2E acceptance for scratchpad question-background layers."""

from __future__ import annotations

import json
import threading
import time
import uuid
from urllib.parse import quote

import pytest

from app import create_app
from models import User, db

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright

PORT = 5105
BASE = f"http://127.0.0.1:{PORT}"

MEASURE_LAYOUT_JS = """
async ({ skillId, componentId }) => {
  const fetchUrl = `/get_next_question?skill=${encodeURIComponent(skillId)}&component_id=${encodeURIComponent(componentId)}&level=1`;
  const resp = await fetch(fetchUrl);
  const data = await resp.json();
  if (data.error) throw new Error(data.error);
  if (typeof scheduleResizeCanvas === 'function') scheduleResizeCanvas();
  else if (typeof resizeCanvas === 'function') resizeCanvas();
  if (typeof resetScratchpadForNextQuestion === 'function') resetScratchpadForNextQuestion();
  if (typeof undoStack !== 'undefined') { undoStack = []; redoStack = []; }
  if (typeof applyQuestionScratchpadBackground === 'function') {
    await applyQuestionScratchpadBackground(data);
  }
  const bg = document.getElementById('drawing-background-canvas');
  const ink = document.getElementById('handwriting-canvas');
  const layer = window.ScratchpadBackgroundLayer;
  const runtime = window.VisualSpecRuntime;
  const cw = bg.clientWidth || bg.width;
  const ch = bg.clientHeight || bg.height;
  const region = layer.computeQuestionBackgroundRegion(cw, ch);
  const ctx = bg.getContext('2d');
  const bounds = layer.getLastRenderBounds() || layer.measureBackgroundContentBounds(ctx, cw, ch);
  const renderMeta = layer.getLastRenderMeta && layer.getLastRenderMeta();
  const validation = bounds ? layer.validateQuadrantBounds(bounds, cw, ch, region.edgePadding, region) : null;
  const sample = (canvas, x, y) => {
    const scaleX = canvas.width / (canvas.clientWidth || canvas.width || 1);
    const scaleY = canvas.height / (canvas.clientHeight || canvas.height || 1);
    const px = Math.max(0, Math.min(canvas.width - 1, Math.floor(x * scaleX)));
    const py = Math.max(0, Math.min(canvas.height - 1, Math.floor(y * scaleY)));
    const d = canvas.getContext('2d').getImageData(px, py, 1, 1).data;
    return { r: d[0], g: d[1], b: d[2], a: d[3] };
  };
  const isNonWhite = (px) => px && (px.r < 248 || px.g < 248 || px.b < 248) && px.a > 0;
  const lowerRight = sample(bg, cw * 0.75, ch * 0.75);
  const upperLeft = sample(bg, region.x + 8, region.y + 8);
  const gridInfo = runtime && runtime.isMultiFigureSpec && runtime.isMultiFigureSpec(data.visual_spec)
    ? runtime.computeMultiFigureGrid(
        runtime.buildMultiFigurePanels(data.visual_spec).length,
        region.width,
        region.height,
        region.edgePadding
      )
    : null;
  return {
    skillId,
    componentId,
    renderable: runtime ? runtime.isVisualSpecRenderable(data.visual_spec) : false,
    hasBg: layer.hasQuestionBackground(),
    bounds,
    region,
    renderMeta,
    scaleMode: renderMeta ? renderMeta.scaleMode : null,
    validation,
    validationChecks: validation,
    lowerRightWhite: !isNonWhite(lowerRight),
    upperLeftNonWhite: isNonWhite(upperLeft),
    multiFigure: runtime ? runtime.isMultiFigureSpec(data.visual_spec) : false,
    panelCount: runtime && runtime.buildMultiFigurePanels ? runtime.buildMultiFigurePanels(data.visual_spec || {}).length : 0,
    gridCols: gridInfo ? gridInfo.cols : null,
    gridRows: gridInfo ? gridInfo.rows : null,
    qmcHidden: (() => {
      const qmc = document.getElementById('question-media-container');
      return !qmc || qmc.style.display === 'none' || qmc.hidden;
    })(),
    inkMatchesBgSize: (ink.clientWidth || ink.width) === cw && (ink.clientHeight || ink.height) === ch,
    canvasWidth: cw,
    canvasHeight: ch,
  };
}
"""

CLEAR_INK_JS = """
async () => {
  const bg = document.getElementById('drawing-background-canvas');
  const ink = document.getElementById('handwriting-canvas');
  const layer = window.ScratchpadBackgroundLayer;
  const bgBefore = bg.toDataURL();
  const ictx = ink.getContext('2d');
  ictx.strokeStyle = '#111827';
  ictx.lineWidth = 4;
  ictx.beginPath();
  ictx.moveTo(30, 30);
  ictx.lineTo(220, 180);
  ictx.stroke();
  const inkDirty = ink.toDataURL();
  const cw = ink.clientWidth || ink.width;
  const ch = ink.clientHeight || ink.height;
  layer.clearInkLayer(ictx, cw, ch);
  return {
    hasBg: layer.hasQuestionBackground(),
    bgUnchanged: bg.toDataURL() === bgBefore,
    inkCleared: ink.toDataURL() !== inkDirty,
  };
}
"""

RESIZE_JS = """
async () => {
  if (typeof scheduleResizeCanvas === 'function') scheduleResizeCanvas();
  else if (typeof resizeCanvas === 'function') resizeCanvas();
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const layer = window.ScratchpadBackgroundLayer;
  const bg = document.getElementById('drawing-background-canvas');
  const cw = bg.clientWidth || bg.width;
  const ch = bg.clientHeight || bg.height;
  const ctx = bg.getContext('2d');
  const bounds = layer.getLastRenderBounds() || layer.measureBackgroundContentBounds(ctx, cw, ch);
  const region = layer.computeQuestionBackgroundRegion(cw, ch);
  const validation = bounds ? layer.validateQuadrantBounds(bounds, cw, ch, region.edgePadding, region) : null;
  return {
    hasBg: layer.hasQuestionBackground(),
    bgWidth: bg ? bg.width : 0,
    bgHeight: bg ? bg.height : 0,
    bounds,
    validation,
  };
}
"""


def _assert_quadrant_layout(result: dict) -> None:
    assert result["hasBg"] is True
    assert result["bounds"] is not None
    assert result["validation"] is not None
    if not result["validation"]["ok"]:
        failed = {k: v for k, v in result["validation"].items() if k != "ok" and v is False}
        pytest.fail(f"quadrant validation failed: {failed}, bounds={result.get('bounds')}, region={result.get('region')}")
    assert result["lowerRightWhite"] is True
    assert result["inkMatchesBgSize"] is True
    pad = result["region"]["edgePadding"]
    bounds = result["bounds"]
    region = result["region"]
    cw = result["canvasWidth"]
    ch = result["canvasHeight"]
    assert bounds["minX"] >= region["x"] - 2
    assert bounds["minY"] >= region["y"] - 2
    assert bounds["width"] <= region["quadrantWidth"] + 1
    assert bounds["height"] <= region["quadrantHeight"] + 1
    assert bounds["maxX"] <= region["x"] + region["width"] + 2
    assert bounds["maxY"] <= region["y"] + region["height"] + 2


@pytest.fixture(scope="module")
def browser_env():
    app = create_app()
    app.config.update(TESTING=True, LOGIN_DISABLED=False)

    with app.app_context():
        user = User(username=f"scratch_e2e_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    def run_server() -> None:
        app.run(host="127.0.0.1", port=PORT, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2.5)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
            client.get("/practice/vh_數學B1_SlopeOfALine")
            session_data = dict(sess)
        cookie_val = app.session_interface.get_signing_serializer(app).dumps(session_data)
        cookies = [{
            "name": app.config.get("SESSION_COOKIE_NAME", "session"),
            "value": cookie_val,
            "domain": "127.0.0.1",
            "path": "/",
        }]

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)
        yield {"browser": browser, "context": context}
        browser.close()


def _open_practice_page(page, skill_id: str) -> None:
    page.goto(f"{BASE}/practice/{quote(skill_id)}", wait_until="networkidle")
    page.wait_for_function("window.VisualSpecRuntime && window.ScratchpadBackgroundLayer")
    page.wait_for_selector("#drawing-background-canvas")
    page.wait_for_selector("#handwriting-canvas")


@pytest.mark.parametrize(
    ("page_kind", "path"),
    [
        ("practice", "/practice/vh_數學B1_PropertiesOfPerpendicularLines"),
        ("adaptive", "/adaptive_practice?skill_id=vh_數學B1_PropertiesOfPerpendicularLines"),
    ],
)
def test_4536_background_survives_clear_across_pages(browser_env, page_kind, path) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    page.goto(f"{BASE}{path}", wait_until="networkidle")
    page.wait_for_function("window.VisualSpecRuntime && window.ScratchpadBackgroundLayer")

    result = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4536"},
    )
    assert result["renderable"] is True
    assert result["scaleMode"] == "cartesian_equal_units"
    _assert_quadrant_layout(result)

    cleared = page.evaluate(CLEAR_INK_JS)
    assert cleared["hasBg"] is True
    assert cleared["bgUnchanged"] is True
    assert cleared["inkCleared"] is True
    page.close()


def test_4520_renders_six_panel_grid_desktop_and_mobile(browser_env) -> None:
    context = browser_env["context"]

    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, "vh_數學B1_SlopeOfALine")
    desktop = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    assert desktop["renderable"] is True
    assert desktop["multiFigure"] is True
    assert desktop["panelCount"] == 6
    assert desktop["gridCols"] == 3
    assert desktop["gridRows"] == 2
    assert desktop["scaleMode"] == "cartesian_equal_units"
    _assert_quadrant_layout(desktop)
    page.close()

    mobile = context.new_page()
    mobile.set_viewport_size({"width": 390, "height": 844})
    _open_practice_page(mobile, "vh_數學B1_SlopeOfALine")
    phone = mobile.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    assert phone["gridCols"] == 2
    assert phone["gridRows"] == 3
    assert phone["panelCount"] == 6
    _assert_quadrant_layout(phone)
    mobile.close()


def test_4526_keeps_blank_scratchpad_without_fake_axes(browser_env) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, "vh_數學B1_PropertiesOfPerpendicularLines")
    result = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4526"},
    )
    assert result["renderable"] is False
    assert result["hasBg"] is False
    assert result["bounds"] is None
    page.close()


def test_next_question_replaces_background_and_clears_ink(browser_env) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, "vh_數學B1_PropertiesOfPerpendicularLines")

    first = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4536"},
    )
    _assert_quadrant_layout(first)
    page.evaluate(CLEAR_INK_JS)

    second = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4526"},
    )
    assert second["hasBg"] is False
    assert second["renderable"] is False
    page.close()


def test_resize_keeps_background_and_panel_layout(browser_env) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 800})
    _open_practice_page(page, "vh_數學B1_SlopeOfALine")
    page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    page.set_viewport_size({"width": 1024, "height": 768})
    resized = page.evaluate(RESIZE_JS)
    assert resized["hasBg"] is True
    assert resized["bgWidth"] > 0
    assert resized["bgHeight"] > 0
    assert resized["validation"] is not None
    assert resized["validation"]["ok"] is True
    page.close()


@pytest.mark.parametrize(
    ("skill_id", "component_id", "expect_bg", "require_quadrant", "expected_scale_mode"),
    [
        ("vh_數學B1_LinearFunction", "src_4424", True, True, "cartesian_equal_units"),
        ("vh_數學B4_StatisticalChartReading", "src_3884", True, True, "chart_independent_axes"),
        ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3826", True, True, "image_contain"),
        ("vh_數學B4_NormalDistributionAndEmpiricalRule", "src_3859", True, True, "image_contain"),
        ("vh_數學B1_LinearFunction", "src_4433", False, False, None),
    ],
)
@pytest.mark.parametrize("viewport", [(1366, 900), (390, 844)])
def test_production_visual_kinds_quadrant_layout(
    browser_env, skill_id, component_id, expect_bg, require_quadrant, expected_scale_mode, viewport
) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": viewport[0], "height": viewport[1]})
    _open_practice_page(page, skill_id)
    result = page.evaluate(
        MEASURE_LAYOUT_JS,
        {"skillId": skill_id, "componentId": component_id},
    )
    assert result["hasBg"] is expect_bg
    if expected_scale_mode:
        assert result["scaleMode"] == expected_scale_mode
    if expect_bg:
        assert result["qmcHidden"] is True
        if require_quadrant:
            _assert_quadrant_layout(result)
    page.close()
