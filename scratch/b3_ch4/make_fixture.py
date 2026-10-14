"""Write a throwaway presentation fixture for B3 Ch4 (served from /static by Flask)."""
import importlib.util
import json
from pathlib import Path

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS

ROOT = Path.cwd()
seen = {}
for eid, spec in sorted(SOURCE_SPECS.items()):
    seen.setdefault((spec["op"], spec["presentation"]), eid)

cases = []
for (op, pres), eid in sorted(seen.items()):
    skill = SOURCE_SPECS[eid]["skill_id"]
    path = ROOT / "agent_skills_v3" / skill / "components" / f"src_{eid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"fx_{eid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.generate(seed=11, component_id=f"src_{eid}")
    stem = payload.get("stem_structure") or (payload.get("domain_matrix") or {}).get("stem_structure")
    cases.append({
        "eid": eid, "op": op, "presentation": pres,
        "question_text": payload.get("question_text"),
        "stem": stem,
        "choices": [{"label": c.get("label"), "text": c.get("text")} for c in payload.get("choices") or []],
        "parts": [p.get("display_label") or p.get("label") for p in (payload.get("answer_contract") or {}).get("parts") or []],
        "visual_spec": payload.get("visual_spec") if (payload.get("visual_spec") or {}).get("kind") not in (None, "none") else None,
    })

html = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B3 Ch4 presentation fixture</title>
<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],macros:{dfrac:['{\\\\displaystyle\\\\frac{#1}{#2}}',2]}},svg:{fontCache:'global'}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<script src="/static/js/visual_spec.js?v=exp-log-curves-1"></script>
<style>body{font-family:sans-serif;margin:8px;max-width:960px}.case{border:1px solid #ccc;margin:8px 0;padding:8px;overflow:hidden}
.stem{white-space:pre-wrap;line-height:1.7}.choices button{display:block;margin:4px 0;padding:6px 10px;text-align:left;max-width:100%}
canvas{border:1px solid #eee;max-width:100%}.meta{color:#888;font-size:12px}</style></head><body>
<h3>B3 Ch4 fixture</h3><div id="root"></div>
<script>
const CASES = __CASES__;
const root = document.getElementById('root');
CASES.forEach(function (c) {
  const box = document.createElement('div'); box.className = 'case'; box.dataset.eid = c.eid;
  const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = c.eid + ' ' + c.op + ' [' + c.presentation + ']';
  box.appendChild(meta);
  const stem = document.createElement('div'); stem.className = 'stem';
  stem.textContent = c.question_text;
  box.appendChild(stem);
  if (c.choices.length) {
    const wrap = document.createElement('div'); wrap.className = 'choices';
    c.choices.forEach(function (ch) { const b = document.createElement('button'); b.innerHTML = '(' + ch.label + ') ' + ch.text; wrap.appendChild(b); });
    box.appendChild(wrap);
  }
  if (c.visual_spec) {
    const cv = document.createElement('canvas'); const w = Math.min(420, window.innerWidth - 40); cv.width = w; cv.height = Math.round(w * 0.75);
    box.appendChild(cv);
    const ok = window.VisualSpecRuntime.renderToContext(cv.getContext('2d'), c.visual_spec, cv.width, cv.height, {padding: 16, visualOpacity: 1, backgroundFill: '#ffffff'});
    cv.dataset.ok = String(ok);
  }
  root.appendChild(box);
});
window.__fixtureProbe = function () {
  const errors = document.querySelectorAll('mjx-merror, [data-mjx-error]').length;
  const rawTex = [];
  document.querySelectorAll('.stem, .choices button').forEach(function (el) {
    const clone = el.cloneNode(true); clone.querySelectorAll('mjx-container').forEach(function (m) { m.remove(); });
    if (/\\\\[A-Za-z]|\\^\\{|\\\\\\(|\\$/.test(clone.textContent)) rawTex.push(el.closest('.case').dataset.eid + ':' + clone.textContent.slice(0, 60));
  });
  const overflow = [];
  document.querySelectorAll('.case').forEach(function (el) { if (el.scrollWidth > el.clientWidth + 2) overflow.push(el.dataset.eid); });
  const canvases = Array.from(document.querySelectorAll('canvas')).map(function (cv) {
    const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data; let ink = 0;
    for (let i = 0; i < d.length; i += 16) { if (d[i] < 200 || d[i + 1] < 200 || d[i + 2] < 200) ink++; }
    return {eid: cv.closest('.case').dataset.eid, ok: cv.dataset.ok, ink: ink};
  });
  return {cases: CASES.length, mathjax: document.querySelectorAll('mjx-container').length, errors: errors, rawTex: rawTex, overflow: overflow, canvases: canvases, width: window.innerWidth};
};
</script></body></html>"""
out = ROOT / "static" / "_b3_ch4_presentation_fixture.html"
out.write_text(html.replace("__CASES__", json.dumps(cases, ensure_ascii=False)), encoding="utf-8")
print(out, len(cases))
