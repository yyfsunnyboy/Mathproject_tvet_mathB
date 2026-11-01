"""Static display preview for 普高數學2 Unit 7 (no Flask, no DB write).

Renders seed 0 and seed 3 of every sandbox component with the practice page's own stem functions
(``renderStructuredStem`` / ``setQuestionDisplayText`` and their helpers, copied verbatim from templates/index.html at
build time) and the page's MathJax 3 configuration. Writes tmp/gh_math2_unit7_isolated/display_preview.html.
After typesetting, ``#status`` holds a JSON summary: MathJax errors, rendered formulas and sub-question rows per card.
"""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.mathematical_expectation import build_sandbox as B  # noqa: E402
from agent_domains_candidate.mathematical_expectation.mathematical_expectation_specs import COMPONENTS, SKILLS  # noqa: E402
from agent_domains_candidate.mathematical_expectation.sandbox_harness import register_candidate_in_memory  # noqa: E402

OUT = ROOT / "tmp" / "gh_math2_unit7_isolated" / "display_preview.html"
SEEDS = (0, 3)


def _frontend_js() -> str:
    source = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    start = source.index("        function resolveStemStructure(payload)")
    end = source.index("        function showMissingQuestionTextError(")
    return source[start:end]


def _generate(cid: int, seed: int) -> dict:
    path = B.DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"preview_{cid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate(seed=seed)


def _fields(payload: dict) -> str:
    contract = payload["answer_contract"]
    parts = contract.get("parts") or [{**contract, "label": "答案", "expected_answer": payload["correct_answer"]}]
    out = []
    for part in parts:
        if part.get("answer_type") == "single_choice" or part.get("choices"):
            options = " / ".join(f"{c['label']}. {c['value']}" for c in part["choices"])
            out.append(f"<li>{html.escape(str(part.get('group_label') or part.get('label') or ''))} 選擇：{html.escape(options)}</li>")
        else:
            out.append(f"<li>{html.escape(str(part.get('group_label') or part.get('label') or ''))} 輸入框</li>")
    return "<ul class='fields'>" + "".join(out) + "</ul>"


def main() -> None:
    register_candidate_in_memory()
    cards = []
    for cid in sorted(COMPONENTS):
        for seed in SEEDS:
            payload = _generate(cid, seed)
            data = {k: payload.get(k) for k in ("question_text", "stem_structure", "metadata")}
            cards.append(
                f"<section class='card' data-cid='{cid}' data-seed='{seed}'><h3>src_{cid} seed {seed}"
                f" — {html.escape(payload['domain_operation'])}</h3>"
                f"<div class='question-text'></div>{_fields(payload)}"
                f"<p class='answer'>標準答案：{html.escape(str(payload['display_answer']))}</p>"
                f"<script type='application/json' class='payload'>{json.dumps(data, ensure_ascii=False).replace('</', '<' + chr(92) + '/')}</script>"
                "</section>"
            )
    page = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><title>Unit 7 display preview</title>
<script>
window.MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']], macros: {{ dfrac: ['{{\\\\displaystyle\\\\frac{{#1}}{{#2}}}}', 2] }} }},
  svg: {{ fontCache: 'global' }}, startup: {{ typeset: false }} }};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
body {{ font-family: "Microsoft JhengHei", sans-serif; margin: 16px; max-width: 980px; }}
.card {{ border: 1px solid #ccc; border-radius: 8px; padding: 10px 14px; margin: 10px 0; }}
.card h3 {{ font-size: 13px; color: #666; margin: 0 0 6px; }}
.question-text {{ font-size: 1.15em; line-height: 1.85; white-space: pre-wrap; overflow-wrap: anywhere; }}
.multipart-stem-item {{ display: inline; white-space: normal; }}
.fields {{ font-size: 13px; color: #245; margin: 6px 0; }}
.answer {{ font-size: 12px; color: #999; margin: 0; }}
</style></head><body>
<pre id="status">pending</pre>
{''.join(cards)}
<script>
{_frontend_js()}
async function run() {{
  const report = [];
  for (const card of document.querySelectorAll('.card')) {{
    const payload = JSON.parse(card.querySelector('.payload').textContent);
    const el = card.querySelector('.question-text');
    if (!renderStructuredStem(el, payload)) setQuestionDisplayText(el, payload.question_text);
    report.push(card);
  }}
  await MathJax.startup.promise;
  await MathJax.typesetPromise();
  document.querySelectorAll('.card').forEach((card) => {{ keepMarkersWithMath(card); settleMultipartItems(card); }});
  const rows = report.map((card) => ({{
    cid: card.dataset.cid, seed: card.dataset.seed,
    errors: card.querySelectorAll('mjx-merror, [data-mjx-error]').length,
    formulas: card.querySelectorAll('mjx-container').length,
    items: card.querySelectorAll('.multipart-stem-item').length,
    raw_dollar: /\\$/.test(card.querySelector('.question-text').textContent),
  }}));
  document.getElementById('status').textContent = JSON.stringify({{
    cards: rows.length, errors: rows.reduce((s, r) => s + r.errors, 0),
    raw_dollar_cards: rows.filter((r) => r.raw_dollar).map((r) => r.cid + '/' + r.seed),
    multipart_items: Object.fromEntries(rows.filter((r) => r.items).map((r) => [r.cid + '/' + r.seed, r.items])),
  }});
}}
window.addEventListener('load', () => run().catch((err) => {{ document.getElementById('status').textContent = 'ERROR ' + err; }}));
</script></body></html>"""
    OUT.write_text(page, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
