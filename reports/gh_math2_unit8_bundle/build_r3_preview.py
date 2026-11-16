"""revision_0003 browser preview for 例題9／隨堂練習10 (generated bar charts).

Each page shows the stem (MathJax) and a scratchpad-sized canvas painted by the student page's own
``static/js/scratchpad_layers.js`` from the student-filtered payload, so what is captured is the shipped display path.
Writes only ``reports/gh_math2_unit8_bundle/revision_0003_preview/``.
"""

from __future__ import annotations

import html
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports" / "gh_math2_unit8_bundle" / "revision_0003_preview"
DRYRUN = ROOT / "tmp" / "gh_math2_unit8_sandbox_dryrun_r3" / "gh_VarianceAndStandardDeviation" / "components"
SAMPLES = [(12926, 0, 960, 600), (12926, 5, 960, 600), (12926, 12, 960, 600), (12930, 0, 960, 600), (12930, 7, 960, 600), (12930, 3, 430, 760)]

PAGE = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>LOADING</title>
<style>body{{font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif;margin:16px;color:#1f2937}}
.q{{font-size:17px;line-height:1.7;white-space:pre-wrap;border:1px solid #d1d5db;padding:10px 14px;border-radius:6px;max-width:{w}px}}
canvas{{border:1px solid #9ca3af;margin-top:10px;background:#fff}} .meta{{font-size:13px;color:#4b5563;margin-top:6px}}</style>
<script>window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>
<script src="{layers}"></script></head><body>
<div class="meta">{caption}</div><div class="q">{stem}</div>
<canvas id="pad" width="{w}" height="{h}"></canvas><div class="meta" id="meta"></div>
<script>
const payload = {payload};
function norm(v) {{ v = String(v || '').trim(); if (!v) return '';
  if (v.startsWith('data:image/') || v.startsWith('/') || v.startsWith('http')) return v; return 'data:image/png;base64,' + v; }}
(async () => {{
  const layer = window.ScratchpadBackgroundLayer;
  const info = layer.shouldRenderBackgroundForPayload(payload, null);
  const srcs = (info.rawImages || [info.rawImage]).map(norm).filter(Boolean);
  const imgs = await layer.loadImageBackgrounds(srcs);
  const pad = document.getElementById('pad');
  const ok = layer.setImagesBackground(imgs, srcs, pad.getContext('2d'), pad.width, pad.height);
  const meta = layer.getLastRenderMeta() || {{}};
  document.getElementById('meta').textContent = `scratchpad_layers: kind=${{info.kind}} images=${{srcs.length}} drawn=${{ok}} scaleMode=${{meta.scaleMode}} natural=${{imgs.map(i => i.naturalWidth + 'x' + i.naturalHeight).join(', ')}}`;
  if (window.MathJax && MathJax.typesetPromise) await MathJax.typesetPromise();
  document.title = 'DONE';
}})();
</script></body></html>"""


def _load(cid: int):
    spec = importlib.util.spec_from_file_location(f"p{cid}", DRYRUN / f"src_{cid}" / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> list[Path]:
    from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory
    from core.practice_student_payload import student_question_payload

    register_candidate_in_memory()
    OUT.mkdir(parents=True, exist_ok=True)
    layers = (ROOT / "static" / "js" / "scratchpad_layers.js").as_uri()
    pages = []
    for cid, seed, w, h in SAMPLES:
        full = _load(cid).generate(seed=seed)
        student = student_question_payload(full)
        assert len(student.get("visual_aids") or []) == 2, "student payload lost the charts"
        assert "correct_answer" not in student and "chart_data" not in student
        g = full["math_core"]["givens"]
        caption = (f"src_{cid} seed {seed} dataset={g['dataset']} canvas {w}x{h} | 審核用參考答案（學生端不送出）："
                   f"{full['display_answer']} | {'；'.join(full['explanation_steps'])}")
        page = OUT / f"src_{cid}_seed{seed}_{w}x{h}.html"
        page.write_text(PAGE.format(w=w, h=h, layers=layers, caption=html.escape(caption), stem=html.escape(full["question_text"]),
                                    payload=json.dumps(student, ensure_ascii=False)), encoding="utf-8")
        pages.append(page)
    return pages


if __name__ == "__main__":
    for p in main():
        print(p)
