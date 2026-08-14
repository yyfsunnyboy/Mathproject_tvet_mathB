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

APPLY_QUESTION_JS = """
async ({ skillId, componentId }) => {
  const fetchUrl = `/get_next_question?skill=${encodeURIComponent(skillId)}&component_id=${encodeURIComponent(componentId)}&level=1`;
  const resp = await fetch(fetchUrl);
  const data = await resp.json();
  if (data.error) {
    throw new Error(data.error);
  }
  if (typeof scheduleResizeCanvas === 'function') {
    scheduleResizeCanvas();
  } else if (typeof resizeCanvas === 'function') {
    resizeCanvas();
  }
  if (typeof resetScratchpadForNextQuestion === 'function') {
    resetScratchpadForNextQuestion();
  }
  if (typeof undoStack !== 'undefined') {
    undoStack = [];
    redoStack = [];
  }
  if (typeof applyQuestionScratchpadBackground === 'function') {
    await applyQuestionScratchpadBackground(data);
  }
  if (typeof saveState === 'function') {
    saveState();
  }
  const bg = document.getElementById('drawing-background-canvas');
  const ink = document.getElementById('handwriting-canvas');
  const runtime = window.VisualSpecRuntime;
  const layer = window.ScratchpadBackgroundLayer;
  const bgCtx = bg ? bg.getContext('2d') : null;
  const sample = (canvas, x, y) => {
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    const px = Math.max(0, Math.min(canvas.width - 1, Math.floor(x)));
    const py = Math.max(0, Math.min(canvas.height - 1, Math.floor(y)));
    const d = ctx.getImageData(px, py, 1, 1).data;
    return { r: d[0], g: d[1], b: d[2], a: d[3] };
  };
  const isNonWhite = (px) => px && (px.r < 248 || px.g < 248 || px.b < 248) && px.a > 0;
  const gridInfo = runtime && runtime.isMultiFigureSpec && runtime.isMultiFigureSpec(data.visual_spec)
    ? runtime.computeMultiFigureGrid(
        runtime.buildMultiFigurePanels(data.visual_spec).length,
        bg.clientWidth || bg.width,
        bg.clientHeight || bg.height,
        16
      )
    : null;
  const panelSamples = (gridInfo && gridInfo.cells || []).map((cell) => {
    const x = (cell.x + cell.width / 2) * (bg.width / (bg.clientWidth || bg.width || 1));
    const y = (cell.y + cell.height / 2) * (bg.height / (bg.clientHeight || bg.height || 1));
    return isNonWhite(sample(bg, x, y));
  });
  return {
    skillId,
    componentId,
    renderable: runtime ? runtime.isVisualSpecRenderable(data.visual_spec) : false,
    hasBg: layer ? layer.hasQuestionBackground() : false,
    multiFigure: runtime ? runtime.isMultiFigureSpec(data.visual_spec) : false,
    panelCount: runtime && runtime.buildMultiFigurePanels ? runtime.buildMultiFigurePanels(data.visual_spec || {}).length : 0,
    gridCols: gridInfo ? gridInfo.cols : null,
    gridRows: gridInfo ? gridInfo.rows : null,
    panelSamples,
    centerNonWhite: isNonWhite(sample(bg, bg.width / 2, bg.height / 2)),
    qmcHidden: (() => {
      const qmc = document.getElementById('question-media-container');
      return !qmc || qmc.style.display === 'none' || qmc.hidden;
    })(),
    visualKind: (data.visual_spec && data.visual_spec.kind) || '',
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
  if (typeof scheduleResizeCanvas === 'function') {
    scheduleResizeCanvas();
  } else if (typeof resizeCanvas === 'function') {
    resizeCanvas();
  }
  await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const layer = window.ScratchpadBackgroundLayer;
  const bg = document.getElementById('drawing-background-canvas');
  return {
    hasBg: layer.hasQuestionBackground(),
    bgWidth: bg ? bg.width : 0,
    bgHeight: bg ? bg.height : 0,
  };
}
"""


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
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4536"},
    )
    assert result["renderable"] is True
    assert result["hasBg"] is True
    assert result["centerNonWhite"] is True

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
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    assert desktop["renderable"] is True
    assert desktop["multiFigure"] is True
    assert desktop["panelCount"] == 6
    assert desktop["gridCols"] == 3
    assert desktop["gridRows"] == 2
    assert desktop["hasBg"] is True
    assert desktop["visualKind"] == "coordinate_plane_multi_figure"
    page.close()

    mobile = context.new_page()
    mobile.set_viewport_size({"width": 390, "height": 844})
    _open_practice_page(mobile, "vh_數學B1_SlopeOfALine")
    phone = mobile.evaluate(
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    assert phone["gridCols"] == 2
    assert phone["gridRows"] == 3
    assert phone["panelCount"] == 6
    mobile.close()


def test_4526_keeps_blank_scratchpad_without_fake_axes(browser_env) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, "vh_數學B1_PropertiesOfPerpendicularLines")
    result = page.evaluate(
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4526"},
    )
    assert result["renderable"] is False
    assert result["hasBg"] is False
    assert result["centerNonWhite"] is False
    page.close()


def test_next_question_replaces_background_and_clears_ink(browser_env) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, "vh_數學B1_PropertiesOfPerpendicularLines")

    first = page.evaluate(
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_PropertiesOfPerpendicularLines", "componentId": "src_4536"},
    )
    assert first["hasBg"] is True
    page.evaluate(CLEAR_INK_JS)

    second = page.evaluate(
        APPLY_QUESTION_JS,
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
        APPLY_QUESTION_JS,
        {"skillId": "vh_數學B1_SlopeOfALine", "componentId": "src_4520"},
    )
    page.set_viewport_size({"width": 1024, "height": 768})
    resized = page.evaluate(RESIZE_JS)
    assert resized["hasBg"] is True
    assert resized["bgWidth"] > 0
    assert resized["bgHeight"] > 0
    page.close()


@pytest.mark.parametrize(
    ("skill_id", "component_id", "expect_bg", "require_pixels"),
    [
        ("vh_數學B1_LinearFunction", "src_4424", True, True),
        ("vh_數學B4_StatisticalChartReading", "src_3884", True, True),
        ("vh_數學B4_HistogramsAndFrequencyPolygons", "src_3826", True, False),
        ("vh_數學B4_NormalDistributionAndEmpiricalRule", "src_3859", True, False),
        ("vh_數學B1_LinearFunction", "src_4433", False, False),
    ],
)
def test_production_visual_kinds_render_background(
    browser_env, skill_id, component_id, expect_bg, require_pixels
) -> None:
    context = browser_env["context"]
    page = context.new_page()
    page.set_viewport_size({"width": 1366, "height": 900})
    _open_practice_page(page, skill_id)
    result = page.evaluate(
        APPLY_QUESTION_JS,
        {"skillId": skill_id, "componentId": component_id},
    )
    assert result["hasBg"] is expect_bg
    if expect_bg and require_pixels:
        assert result["centerNonWhite"] is True
    if expect_bg:
        assert result["qmcHidden"] is True
    page.close()
