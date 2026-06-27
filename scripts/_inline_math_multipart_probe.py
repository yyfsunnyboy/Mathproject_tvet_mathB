# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import threading
import time
import uuid
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

INLINE_CHECK_JS = """
async () => {
  const waitTypeset = () => new Promise((resolve) => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([document.getElementById('question-text')])
        .then(resolve).catch(resolve);
    } else {
      setTimeout(resolve, 800);
    }
  });
  await waitTypeset();
  await new Promise(r => setTimeout(r, 300));
  const qt = document.getElementById('question-text');
  const containers = qt ? Array.from(qt.querySelectorAll('mjx-container:not([display="true"])')) : [];
  const blockish = containers.filter((el) => {
    const st = getComputedStyle(el);
    return st.display === 'block' || st.width === '100%';
  });
  const centeredSvg = qt ? Array.from(qt.querySelectorAll('mjx-container svg')).filter((svg) => {
    const st = getComputedStyle(svg);
    return st.display === 'block' && (st.marginLeft === 'auto' || st.marginRight === 'auto');
  }) : [];
  const lineBreakCount = qt ? (qt.innerHTML.match(/<br\\s*\\/?>/gi) || []).length : 0;
  return {
    mjxInlineCount: containers.length,
    mjxBlockishCount: blockish.length,
    centeredSvgCount: centeredSvg.length,
    brCount: lineBreakCount,
    inlineOk: containers.length > 0 && blockish.length === 0 && centeredSvg.length === 0,
  };
}
"""

MULTIPART_CHECK_JS = """
() => {
  const groups = Array.from(document.querySelectorAll('.multi-part-group'));
  const rows = groups.map((g) => {
    const label = g.querySelector('.multi-part-group-label');
    const fields = g.querySelector('.multi-part-inline-fields');
    if (!label || !fields) return { ok: false, reason: 'missing-parts' };
    const lb = label.getBoundingClientRect();
    const fb = fields.getBoundingClientRect();
    const sameRow = Math.abs(lb.top - fb.top) < 14 && lb.bottom <= fb.bottom + 4;
    const labelAlone = lb.bottom - lb.top > 0 && fb.top > lb.bottom + 2;
    return {
      ok: sameRow && !labelAlone,
      labelTop: lb.top,
      fieldsTop: fb.top,
      labelBottom: lb.bottom,
      fieldsBottom: fb.bottom,
    };
  });
  return {
    groupCount: groups.length,
    rowsOk: rows.every(r => r.ok),
    rows,
  };
}
"""


def main() -> None:
    app = create_app()
    app.config.update(TESTING=True, LOGIN_DISABLED=False)
    with app.app_context():
        user = User(username=f"probe_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    def run_server() -> None:
        app.run(host="127.0.0.1", port=5101, use_reloader=False, threaded=True)

    threading.Thread(target=run_server, daemon=True).start()
    time.sleep(2.5)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
        client.get("/practice/vh_數學B4_LinearTransformationOfData")
        with client.session_transaction() as sess:
            session_data = dict(sess)
        cookie_val = app.session_interface.get_signing_serializer(app).dumps(session_data)
        cookies = [{"name": app.config.get("SESSION_COOKIE_NAME", "session"), "value": cookie_val, "domain": "127.0.0.1", "path": "/"}]

    from importlib import import_module

    gen3896 = import_module(
        "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3896.generate"
    )
    gen3852 = import_module(
        "agent_skills_v3.vh_數學B4_LinearTransformationOfData.components.src_3852.generate"
    )
    payload_choice = gen3896.generate(seed=3896, component_id="src_3896")
    payload_multi = gen3852.generate(seed=3852, component_id="src_3852")

    results = {"inlineChoice": {}, "multiPart": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)

        for label, w, h in VIEWPORTS:
            page = context.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(
                "http://127.0.0.1:5101/practice/vh_數學B4_LinearTransformationOfData",
                wait_until="networkidle",
                timeout=90000,
            )
            page.wait_for_timeout(1500)
            page.evaluate(
                """(payload) => {
                  if (typeof renderQuestion === 'function') renderQuestion(payload);
                }""",
                payload_choice,
            )
            inline = page.evaluate(INLINE_CHECK_JS)
            results["inlineChoice"][label] = inline
            page.close()

        for label, w, h in VIEWPORTS:
            page = context.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(
                "http://127.0.0.1:5101/practice/vh_數學B4_LinearTransformationOfData",
                wait_until="networkidle",
                timeout=90000,
            )
            page.wait_for_timeout(1500)
            page.evaluate(
                """(payload) => {
                  if (typeof renderQuestion === 'function') renderQuestion(payload);
                }""",
                payload_multi,
            )
            page.wait_for_timeout(500)
            mp = page.evaluate(MULTIPART_CHECK_JS)
            bodyScroll = page.evaluate(
                "() => window.innerWidth >= 900 && document.documentElement.scrollHeight > window.innerHeight + 2"
            )
            mp["bodyScrollDesktop"] = bodyScroll
            results["multiPart"][label] = mp
            page.close()

        browser.close()

    out = Path(__file__).resolve().parents[1] / "probe_math_multipart.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
