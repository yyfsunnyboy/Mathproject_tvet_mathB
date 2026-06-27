# -*- coding: utf-8 -*-
"""One-off Playwright probe for /practice viewport layout (not part of CI)."""
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
    ("1600x900", 1600, 900),
    ("1536x864", 1536, 864),
    ("1366x768", 1366, 768),
    ("1280x800", 1280, 800),
    ("1024x1366", 1024, 1366),
    ("800x1280", 800, 1280),
]

MOCK_SCENARIOS = {
    "choice": """
        () => {
          document.getElementById('question-text').innerHTML =
            '下列哪一種抽樣方法屬於機率抽樣？';
          const choices = document.getElementById('question-choices');
          choices.innerHTML = `
            <div class="choice-list">
              <button type="button" class="choice-option"><span class="choice-label">(A)</span><span class="choice-text">便利抽樣</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(B)</span><span class="choice-text">簡單隨機抽樣</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(C)</span><span class="choice-text">立意抽樣</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(D)</span><span class="choice-text">滾雪球抽樣</span></button>
            </div>`;
          const media = document.getElementById('question-media-container');
          media.innerHTML = '';
          media.style.display = 'none';
          if (typeof updateAppViewportMetrics === 'function') updateAppViewportMetrics();
          if (typeof scheduleResizeCanvas === 'function') scheduleResizeCanvas();
        }
    """,
    "chart": """
        () => {
          document.getElementById('question-text').innerHTML =
            '依下圖累積次數折線圖，回答第 3 組資料以上共有幾人？';
          const media = document.getElementById('question-media-container');
          media.style.display = 'block';
          media.innerHTML = `<svg viewBox="0 0 640 360" width="640" height="360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="chart">
            <rect x="0" y="0" width="640" height="360" fill="#fff"/>
            <line x1="60" y1="30" x2="60" y2="300" stroke="#333"/>
            <line x1="60" y1="300" x2="600" y2="300" stroke="#333"/>
            <text x="320" y="24" text-anchor="middle" font-size="16">累積次數折線圖</text>
            <polyline fill="none" stroke="#3498db" stroke-width="3"
              points="100,260 180,220 260,170 340,120 420,80 500,50"/>
            <text x="100" y="320" text-anchor="middle" font-size="12">1</text>
            <text x="180" y="320" text-anchor="middle" font-size="12">2</text>
            <text x="260" y="320" text-anchor="middle" font-size="12">3</text>
            <text x="340" y="320" text-anchor="middle" font-size="12">4</text>
            <text x="420" y="320" text-anchor="middle" font-size="12">5</text>
            <text x="500" y="320" text-anchor="middle" font-size="12">6</text>
          </svg>`;
          document.getElementById('question-choices').innerHTML = `
            <div class="choice-list">
              <button type="button" class="choice-option"><span class="choice-label">(A)</span><span class="choice-text">12</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(B)</span><span class="choice-text">18</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(C)</span><span class="choice-text">24</span></button>
              <button type="button" class="choice-option"><span class="choice-label">(D)</span><span class="choice-text">30</span></button>
            </div>`;
          if (typeof updateAppViewportMetrics === 'function') updateAppViewportMetrics();
          if (typeof scheduleResizeCanvas === 'function') scheduleResizeCanvas();
        }
    """,
    "long": """
        () => {
          const rows = Array.from({length: 18}, (_, i) =>
            `<tr><td>${i+1}</td><td>${60+i*3}</td><td>${70+i*2}</td><td>${80+i}</td><td>${90-i}</td></tr>`).join('');
          document.getElementById('question-text').innerHTML =
            '下表為某班 18 位學生四次段考成績。請依資料回答：\\n(1) 全距為多少？\\n(2) 哪一位學生成績變化最大？\\n(3) 若只取前 10 位學生，平均約為多少？';
          const media = document.getElementById('question-media-container');
          media.style.display = 'block';
          media.innerHTML = `<div class="math-table-scroll-wrap"><table class="math-table-readonly"><thead><tr><th>學生</th><th>第一次</th><th>第二次</th><th>第三次</th><th>第四次</th></tr></thead><tbody>${rows}</tbody></table></div>`;
          document.getElementById('question-choices').innerHTML = '';
          if (typeof updateAppViewportMetrics === 'function') updateAppViewportMetrics();
          if (typeof scheduleResizeCanvas === 'function') scheduleResizeCanvas();
        }
    """,
}


def _layout_js() -> str:
    return """
    () => {
      const r = (sel) => {
        const el = document.querySelector(sel);
        if (!el) return null;
        const b = el.getBoundingClientRect();
        const st = getComputedStyle(el);
        return {
          top: b.top, bottom: b.bottom, height: b.height, width: b.width,
          overflowY: st.overflowY, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight,
        };
      };
      const bodyScroll = document.documentElement.scrollHeight > window.innerHeight + 2;
      const bodyOverflowX = document.documentElement.scrollWidth > window.innerWidth + 2;
      const inView = (b) => b && b.top >= 0 && b.bottom <= window.innerHeight + 1;
      const keys = {
        answerInput: r('#answer-input'),
        submitBtn: r('#submit-button'),
        toolbar: r('#scratchpad-controls'),
        canvasWrap: r('.canvas-wrap'),
        chatInput: r('#chat-input'),
        chatSend: r('#chat-send-button'),
        staticPrompts: r('#static-prompts'),
      };
      const visible = Object.fromEntries(
        Object.entries(keys).map(([k, b]) => [k, inView(b)])
      );
      const media = document.querySelector('#question-media-container');
      const qBlock = r('.practice-question-block');
      const qScrollable = qBlock && qBlock.scrollHeight > qBlock.clientHeight + 2;
      const chatHist = r('#chat-history');
      return {
        innerWidth: window.innerWidth,
        innerHeight: window.innerHeight,
        bodyScroll,
        bodyOverflowX,
        navbarH: document.querySelector('.student-navbar')?.getBoundingClientRect().height || 0,
        container: r('.container'),
        questionBlock: qBlock,
        questionScrollable: qScrollable,
        questionMediaEmpty: !media?.innerHTML?.trim(),
        chatHistory: chatHist,
        visible,
        allKeyVisible: Object.values(visible).every(Boolean),
        gridRows: getComputedStyle(document.querySelector('.practice-area') || document.body).gridTemplateRows || '',
        practiceDisplay: getComputedStyle(document.querySelector('.practice-area') || document.body).display,
      };
    }
    """


def main() -> None:
    app = create_app()
    app.config.update(TESTING=True, LOGIN_DISABLED=False)

    with app.app_context():
        user = User(
            username=f"layout_probe_{uuid.uuid4().hex[:8]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    def run_server() -> None:
        app.run(host="127.0.0.1", port=5099, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2.5)

    results = {"viewports": {}, "questionTypes": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_user_id"] = str(user_id)
                sess["_fresh"] = True
            client.get("/practice/vh_數學B4_StatisticalChartReading")
            with client.session_transaction() as sess:
                session_data = dict(sess)
            serializer = app.session_interface.get_signing_serializer(app)
            cookie_value = serializer.dumps(session_data)
            cookies = [
                {
                    "name": app.config.get("SESSION_COOKIE_NAME", "session"),
                    "value": cookie_value,
                    "domain": "127.0.0.1",
                    "path": "/",
                }
            ]
        context.add_cookies(cookies)

        for label, w, h in VIEWPORTS:
            page = context.new_page()
            page.set_viewport_size({"width": w, "height": h})
            page.goto(
                "http://127.0.0.1:5099/practice/vh_數學B4_StatisticalChartReading",
                wait_until="networkidle",
                timeout=60000,
            )
            page.wait_for_timeout(1200)
            page.evaluate(MOCK_SCENARIOS["choice"])
            page.wait_for_timeout(400)
            data = page.evaluate(_layout_js())
            desktop = w >= 900
            results["viewports"][label] = {
                **data,
                "desktop": desktop,
                "bodyScrollOk": (not desktop) or (not data["bodyScroll"]),
            }
            page.close()

        for kind, script in MOCK_SCENARIOS.items():
            page = context.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(
                "http://127.0.0.1:5099/practice/vh_數學B4_StatisticalChartReading",
                wait_until="networkidle",
                timeout=60000,
            )
            page.wait_for_timeout(1000)
            page.evaluate(script)
            page.wait_for_timeout(500)
            data = page.evaluate(_layout_js())
            mediaOverflowX = page.evaluate("""
              () => {
                const m = document.querySelector('#question-media-container');
                if (!m) return false;
                return m.scrollWidth > m.clientWidth + 2;
              }
            """)
            results["questionTypes"][kind] = {
                **data,
                "mediaOverflowXOnly": mediaOverflowX,
                "bodyScrollOk": not data["bodyScroll"],
            }
            page.close()

        browser.close()

    out_path = Path(__file__).resolve().parents[1] / "probe_layout_result.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
