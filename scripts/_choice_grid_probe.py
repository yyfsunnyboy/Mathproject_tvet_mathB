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

LAYOUT_JS = """
() => {
  const qc = document.getElementById('question-choices');
  if (!qc || qc.style.display === 'none') {
    return { hasChoices: false };
  }
  const opts = Array.from(qc.querySelectorAll('.choice-option'));
  const rects = opts.map((el, i) => {
    const b = el.getBoundingClientRect();
    return { i, top: b.top, left: b.left, w: b.width, h: b.height };
  });
  const isGrid = qc.classList.contains('choice-grid-2x2');
  const display = getComputedStyle(qc).display;
  let cols = 1;
  if (opts.length >= 2) {
    const sameRow = Math.abs(rects[0].top - rects[1].top) < 8;
    cols = sameRow ? 2 : 1;
  }
  const qBlock = document.querySelector('.practice-question-block');
  const canvas = document.querySelector('.canvas-wrap');
  return {
    hasChoices: true,
    count: opts.length,
    isGrid,
    display,
    cols,
    containerW: qc.getBoundingClientRect().width,
    questionBlockH: qBlock ? qBlock.getBoundingClientRect().height : null,
    canvasH: canvas ? canvas.getBoundingClientRect().height : null,
    rects,
  };
}
"""


def main() -> None:
    gen3896 = import_module(
        "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3896.generate"
    )
    gen3852 = import_module(
        "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3852.generate"
    )
    gen3885 = import_module(
        "agent_skills_v3.vh_數學B4_StatisticalChartReading.components.src_3885.generate"
    )

    four_short = gen3896.generate(seed=3896, component_id="src_3896")
    four_long = dict(four_short)
    four_long["choices"] = [
        {"key": "A", "label": "A", "text": "這是一個非常長的選項文字，用來測試兩欄排版時是否仍能自然換行而不裁切任何內容。"},
        {"key": "B", "label": "B", "text": "第二個同樣很長的選項，確認 B 與 A 同列且文字可換行。"},
        {"key": "C", "label": "C", "text": "第三個長選項，應與 D 同列。"},
        {"key": "D", "label": "D", "text": "第四個長選項，完成 2×2 測試。"},
    ]
    three_choice = dict(four_short)
    three_choice["choices"] = four_short["choices"][:3]
    three_choice["presentation_mode"] = "single_choice"
    three_choice["answer_shape"] = "single_choice"
    five_choice = dict(four_short)
    five_choice["choices"] = four_short["choices"] + [
        {"key": "E", "label": "E", "text": "第五選項"}
    ]
    multi = gen3852.generate(seed=3852, component_id="src_3852")
    chart4 = gen3885.generate(seed=3885, component_id="src_3885")

    scenarios = {
        "four_short": four_short,
        "four_long": four_long,
        "three_choice": three_choice,
        "five_choice": five_choice,
        "multi_part": multi,
        "chart_four": chart4,
    }

    app = create_app()
    app.config.update(TESTING=True, LOGIN_DISABLED=False)
    with app.app_context():
        user = User(username=f"cg_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    def run_server() -> None:
        app.run(host="127.0.0.1", port=5102, use_reloader=False, threaded=True)

    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(2.5)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
            client.get("/practice/vh_數學B4_LinearTransformationOfData")
            session_data = dict(sess)
        cookie_val = app.session_interface.get_signing_serializer(app).dumps(session_data)
        cookies = [{"name": app.config.get("SESSION_COOKIE_NAME", "session"), "value": cookie_val, "domain": "127.0.0.1", "path": "/"}]

    results = {}
    baseline_heights = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)

        for label, w, h in VIEWPORTS:
            page = context.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto("http://127.0.0.1:5102/practice/vh_數學B4_LinearTransformationOfData", wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(1200)
            page.evaluate("(p) => renderQuestion(p)", four_short)
            page.wait_for_timeout(600)
            layout = page.evaluate(LAYOUT_JS)
            results.setdefault("four_short", {})[label] = layout
            if label == "1920x1080":
                baseline_heights["four_short_1col_sim"] = layout
            page.close()

        for name, payload in scenarios.items():
            results[name] = {}
            for label, w, h in VIEWPORTS:
                page = context.new_page()
                page.set_viewport_size({"width": w, "height": h})
                page.goto("http://127.0.0.1:5102/practice/vh_數學B4_LinearTransformationOfData", wait_until="networkidle", timeout=90000)
                page.wait_for_timeout(1000)
                errs = []
                page.on("console", lambda msg: errs.append(msg.text) if msg.type == "error" else None)
                page.evaluate("(p) => renderQuestion(p)", payload)
                page.wait_for_timeout(700)
                layout = page.evaluate(LAYOUT_JS)
                layout["consoleErrors"] = errs
                results[name][label] = layout
                page.close()

        browser.close()

    out = Path(__file__).resolve().parents[1] / "probe_choice_grid.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
