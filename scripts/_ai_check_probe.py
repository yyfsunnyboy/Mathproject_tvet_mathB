# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import threading
import time
import uuid
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from models import User, db
from playwright.sync_api import sync_playwright

VIEWPORTS = [
    ("1920x1080", 1920, 1080),
    ("1366x768", 1366, 768),
    ("1024x1366", 1024, 1366),
    ("800x1280", 800, 1280),
]

CHECK_JS = """
() => {
  const btn = document.getElementById('analyze-handwriting-button');
  const drawBtn = document.getElementById('draw-diagram-button');
  const actions = document.querySelector('.canvas-actions');
  const primary = document.querySelector('.scratchpad-tools-primary');
  const rect = (el) => el ? el.getBoundingClientRect() : null;
  const visible = (el) => {
    if (!el || el.hidden) return false;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') return false;
    const b = el.getBoundingClientRect();
    return b.width > 0 && b.height > 0;
  };
  return {
    aiVisible: visible(btn),
    aiHiddenAttr: btn ? btn.hidden : null,
    drawDiagramExists: !!drawBtn,
    canvasActionsVisible: visible(actions),
    canvasActionsRight: actions && primary ? actions.getBoundingClientRect().left >= primary.getBoundingClientRect().left : null,
    toolbarOverflowX: primary ? getComputedStyle(primary).overflowX : null,
    scratchpadVisible: visible(document.getElementById('scratchpad-container')),
  };
}
"""


def main() -> None:
    scenarios = {
        "chart_reading": import_module(
            "agent_skills_v3.vh_數學B4_StatisticalChartReading.components.src_3885.generate"
        ).generate(seed=3885, component_id="src_3885"),
        "histogram": import_module(
            "agent_skills_v3.vh_數學B4_HistogramsAndFrequencyPolygons.components.src_3829.generate"
        ).generate(seed=3829, component_id="src_3829"),
        "plain_choice": import_module(
            "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3896.generate"
        ).generate(seed=3896, component_id="src_3896"),
        "ai_false": import_module(
            "agent_skills_v3.vh_數學B4_HistogramsAndFrequencyPolygons.components.src_3829.generate"
        ).generate(seed=3829, component_id="src_3829"),
        "multi_part": import_module(
            "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3852.generate"
        ).generate(seed=3852, component_id="src_3852"),
    }
    scenarios["ai_true"] = dict(scenarios["plain_choice"])
    ui = dict((scenarios["ai_true"].get("ui_contract") or {}))
    ui.update({"ai_check_required": True})
    scenarios["ai_true"]["ui_contract"] = ui
    ac = dict(scenarios["ai_true"].get("answer_contract") or {})
    ac_ui = dict(ac.get("ui_contract") or {})
    ac_ui.update({"ai_check_required": True})
    ac["ui_contract"] = ac_ui
    scenarios["ai_true"]["answer_contract"] = ac

    app = create_app()
    app.config.update(TESTING=True, LOGIN_DISABLED=False)
    with app.app_context():
        user = User(username=f"ai_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    threading.Thread(
        target=lambda: app.run(host="127.0.0.1", port=5103, use_reloader=False, threaded=True),
        daemon=True,
    ).start()
    time.sleep(2.5)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
            client.get("/practice/vh_數學B4_StatisticalChartReading")
            session_data = dict(sess)
        cookie_val = app.session_interface.get_signing_serializer(app).dumps(session_data)
        cookies = [{"name": app.config.get("SESSION_COOKIE_NAME", "session"), "value": cookie_val, "domain": "127.0.0.1", "path": "/"}]

    results = {}
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)

        for sname, payload in scenarios.items():
            payload = dict(payload)
            payload["skill_id"] = "vh_數學B4_StatisticalChartReading"
            results[sname] = {}
            for label, w, h in VIEWPORTS:
                page = context.new_page()
                page.set_viewport_size({"width": w, "height": h})
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                page.goto("http://127.0.0.1:5103/practice/vh_數學B4_StatisticalChartReading", wait_until="networkidle", timeout=90000)
                page.wait_for_timeout(800)
                page.evaluate("(p) => { applyCurrentQuestion(p); renderQuestion(p); applyDrawingUiContract(); }", payload)
                page.wait_for_timeout(400)
                results[sname][label] = page.evaluate(CHECK_JS)
                page.close()

        browser.close()

    expected = {
        "chart_reading": True,
        "histogram": False,
        "plain_choice": True,
        "ai_false": False,
        "ai_true": True,
        "multi_part": True,
    }
    out = {"results": results, "consoleErrors": errors, "pass": {}, "fail": []}
    for sname, vp_map in results.items():
        exp = expected.get(sname)
        for label, data in vp_map.items():
            ok = (
                data.get("drawDiagramExists") is False
                and data.get("canvasActionsRight") is True
                and data.get("toolbarOverflowX") == "auto"
                and (data.get("aiVisible") is True) == exp
            )
            key = f"{sname}@{label}"
            out["pass"][key] = ok
            if not ok:
                out["fail"].append({"case": key, "expectedAiVisible": exp, "data": data})
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
