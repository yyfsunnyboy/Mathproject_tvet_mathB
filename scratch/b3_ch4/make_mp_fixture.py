"""Throwaway multipart presentation fixture for B3 Ch4 (served from /static by Flask)."""
import importlib.util
import json
import re
from pathlib import Path

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix

ROOT = Path.cwd()
first = {}
for eid, spec in sorted(SOURCE_SPECS.items()):
    if build_exponential_logarithmic_matrix(11, {"textbook_example_id": eid})["answer_type"] == "multi_part":
        first.setdefault(spec["op"], eid)

cases = []
for op, eid in sorted(first.items(), key=lambda kv: kv[1]):
    skill = SOURCE_SPECS[eid]["skill_id"]
    path = ROOT / "agent_skills_v3" / skill / "components" / f"src_{eid}" / "generate.py"
    spec = importlib.util.spec_from_file_location(f"fx_{eid}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    p = module.generate(seed=11, component_id=f"src_{eid}")
    cases.append({
        "eid": eid, "op": op, "skill": skill[-5:],
        "question_text": p["question_text"],
        "keys": list(p["correct_answer"]),
        "payload": {k: p[k] for k in ("answer_contract", "ui_contract", "stem_structure") if k in p},
    })

index = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
head = index.split("</head>", 1)[0]
styles = "\n".join(s for s in re.findall(r"<style[^>]*>(.*?)</style>", head, flags=re.S) if "{{" not in s and "{%" not in s)

html = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B3 Ch4 multipart fixture</title>
<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],macros:{dfrac:['{\\\\displaystyle\\\\frac{#1}{#2}}',2]}},svg:{fontCache:'global'}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>__STYLES__</style>
<link rel="stylesheet" href="/static/css/practice_answer_layout.css">
<link rel="stylesheet" href="/static/css/practice_math_typography.css">
<script src="/static/js/multipart_field_renderer.js"></script>
<style>.case{border:1px solid #ccc;margin:8px 0;padding:8px}.meta{color:#888;font-size:12px}.stem{white-space:pre-wrap}</style>
</head><body><div id="root"></div>
<script>
const CASES = __CASES__;
const root = document.getElementById('root');
CASES.forEach(function (c) {
  const box = document.createElement('div'); box.className = 'case'; box.dataset.eid = c.eid;
  const meta = document.createElement('div'); meta.className = 'meta'; meta.textContent = c.eid + ' ' + c.skill + ' ' + c.op;
  box.appendChild(meta);
  const q = document.createElement('div'); q.className = 'practice-question-block';
  const stem = document.createElement('div'); stem.className = 'stem practice-math-surface'; stem.textContent = c.question_text;
  q.appendChild(stem); box.appendChild(q);
  const a = document.createElement('div'); a.className = 'practice-answer-block';
  const sub = document.createElement('div'); sub.className = 'subquestions-container practice-math-surface';
  a.appendChild(sub); box.appendChild(a);
  window.MultipartFieldRenderer.render(sub, c.payload);
  sub.style.display = 'block';
  root.appendChild(box);
});
window.__mpProbe = function () {
  const cases = Array.from(document.querySelectorAll('.case')).map(function (box) {
    const c = CASES.find(function (x) { return String(x.eid) === box.dataset.eid; });
    const inputs = Array.from(box.querySelectorAll('.multi-part-input'));
    const labels = Array.from(box.querySelectorAll('.multi-part-row label')).map(function (l) { return l.textContent; });
    const lefts = inputs.map(function (i) { return Math.round(i.getBoundingClientRect().left); });
    const rights = inputs.map(function (i) { return Math.round(i.getBoundingClientRect().right); });
    const items = ((c.payload.stem_structure || {}).items || []).map(function (i) { return i.text; });
    return {
      eid: c.eid, op: c.op, skill: c.skill, arity: c.keys.length, controls: inputs.length,
      order_ok: JSON.stringify(inputs.map(function (i) { return i.dataset.fieldKey; })) === JSON.stringify(c.keys),
      labels: labels, leftSpread: Math.max.apply(null, lefts) - Math.min.apply(null, lefts),
      maxRight: Math.max.apply(null, rights),
      boxInLabel: labels.some(function (l) { return l.indexOf('□') >= 0 || l.indexOf('\\\\square') >= 0; }),
      stemInLabel: labels.some(function (l) { return items.some(function (t) { return l.length > 4 && t.indexOf(l) >= 0; }); }),
      overflow: box.scrollWidth > box.clientWidth + 1,
    };
  });
  return {width: window.innerWidth, docWidth: document.documentElement.scrollWidth,
    mathErrors: document.querySelectorAll('mjx-merror,[data-mjx-error],[data-mml-node=merror]').length, cases: cases};
};
</script></body></html>"""
out = ROOT / "static" / "_b3_ch4_multipart_fixture.html"
out.write_text(html.replace("__STYLES__", styles).replace("__CASES__", json.dumps(cases, ensure_ascii=False)), encoding="utf-8")
print(out, len(cases))
