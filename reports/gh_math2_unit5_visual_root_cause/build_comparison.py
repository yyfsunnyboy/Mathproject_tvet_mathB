"""Build candidate_regions.json, visual_comparison.png and visual_comparison.html from the read-only trace."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
trace = json.loads((OUT / "visual_pipeline_trace.json").read_text(encoding="utf-8"))
steps = {s["step"]: s for s in trace["steps"]}
cf = trace["counterfactuals_in_memory_only"]
PAGE_AREA = 609.4486083984375 * 793.7006225585938


def diagram_rank(bb, area, prefer_y, page_w=609.4486083984375):
    """Same formula as _pick_compact_diagram_bbox._diagram_score (a ranking score, not a confidence)."""
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    right_bonus = 2.0 if cx >= 0.45 * page_w else 1.0
    proximity = 1.0 / (1.0 + abs(cy - prefer_y) / 90.0)
    return round(right_bonus * proximity / (area / PAGE_AREA + 0.04), 3)


objs = {o["object"]: o for o in steps["4_candidate_filtering"]["objects"]}
footer, semi = objs["footer_band_path"], objs["semicircle_path"]
start_y = steps["2_anchor_to_pdf_page_and_y"]["result"]["question_start_y_used"]
acc = steps["7_acceptance_gate"]["result"]
proto = cf["CF_C_B_plus_prototype_ink_cluster_candidate"]

candidates = {
    "evidence_type": trace["evidence_type"],
    "original_evidence_status": "original_evidence_unavailable",
    "question_anchor": "general_2_section_advanced_exercise_012_037",
    "pdf_sha256": trace["pdf_sha256"], "page": 16,
    "confidence_model_note": "The pipeline has no numeric visual confidence. match_score (0.99) is text-to-page confidence only; "
                             "visual confidence is the categorical acceptance status (accepted / needs_review / rejected) from "
                             "evaluate_visual_acceptance. _diagram_score is a ranking score among candidates.",
    "question_region_used_by_pipeline": steps["3_question_region"]["result"]["question_bbox"],
    "candidates": [
        {"kind": "PIPELINE_CANDIDATE", "rank": 1, "object": "footer_band_path (page furniture)",
         "raw_bbox": footer["bbox"], "final_visual_bbox": steps["6_region_clip"]["result"]["visual_bbox"],
         "filters": {k: v for k, v in footer.items() if k not in ("object", "bbox")},
         "diagram_rank_score": diagram_rank(footer["bbox"], footer["area"], start_y),
         "match_score_text": 0.99, "acceptance_status": acc["visual_status"], "acceptance_reasons": acc["reasons"],
         "final_classification": "skipped_low_confidence", "asset": "NOT_GENERATED",
         "why_low": "Candidate is a 609x9pt blank strip of the footer band: vh<40 -> low_mapping_confidence; full-width aspect 67 -> overspan_multi_question."},
        {"kind": "NOT_A_PIPELINE_CANDIDATE", "object": "semicircle_path (real figure)",
         "raw_bbox": semi["bbox"], "filters": {k: v for k, v in semi.items() if k not in ("object", "bbox")},
         "excluded_because": ["does not intersect the question region (region top 670.2 > figure bottom 652.1)",
                              "even inside the region: h=39.7 < 40 (soft), area 3150 < 6000 (band search), area 3150 < 3500 (right-panel single path)"]},
        {"kind": "COUNTERFACTUAL_ONLY (not pipeline output, not verified)", "object": "prototype ink cluster",
         "bbox": proto["picked"]["bbox"] if proto["picked"] else None, "members": proto["picked"]["members"] if proto["picked"] else None,
         "contains_all_figure_ink": proto["contains_all_figure_ink"], "ink_paths_cut_by_crop": proto["ink_paths_cut_by_crop"],
         "inside_teacher_proposal": proto["inside_teacher_proposal"],
         "acceptance_with_current_gate": proto["acceptance_with_current_gate"], "reasons": proto["reasons"]},
        {"kind": "INVESTIGATOR_PROPOSAL_PENDING_TEACHER (previous round, not system output)",
         "bbox": [420, 575, 540, 675], "status": "pending_teacher_confirmation", "verified": False},
    ],
}
(OUT / "candidate_regions.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")


def font(size):
    for name in ("msjh.ttc", "msyh.ttc", "mingliu.ttc", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(img, w):
    return img.resize((w, int(img.height * w / img.width)))


def placeholder(w, h, text, color=(160, 0, 0)):
    im = Image.new("RGB", (w, h), (248, 248, 248))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, w - 3, h - 3], outline=color, width=3)
    d.multiline_text((16, h // 2 - 30), text, fill=color, font=font(24), spacing=6)
    return im


W = 1500
title_f, head_f, body_f = font(30), font(22), font(17)
page_overlay = fit(Image.open(OUT / "B_pipeline_candidate_overlay_page16.png"), 700)
src_page = Image.open(OUT / "A_source_pdf_page16.png")
z = src_page.width / 609.4486083984375
src_crop = fit(src_page.crop((int(80 * z), int(570 * z), int(560 * z), int(700 * z))), 740)
pipe_strip = fit(Image.open(OUT / "B_pipeline_candidate_crop_render.png"), 740)
proto_img = Image.open(OUT / "X_counterfactual_prototype_cluster_crop.png")

panels = [
    ("A. SOURCE_PDF_IMAGE — 第16頁題目位置（直接 render 權威 PDF，非教師截圖）", src_crop, (0, 90, 0)),
    ("B. PIPELINE_CANDIDATE — 唯一候選：頁尾帶 609×9pt 空白細條（依 Pipeline bbox 渲染）", pipe_strip, (200, 0, 0)),
    ("C. PIPELINE_GENERATED_ASSET", placeholder(740, 110, "NOT_GENERATED\nPipeline 在裁切前已 skip；無暫存或正式 PNG"), (200, 0, 0)),
    ("X. COUNTERFACTUAL_ONLY — 原型墨跡聚類（記憶體實驗，非 Pipeline 輸出、未核准）", proto_img, (120, 60, 160)),
    ("F. ISOLATED_RENDER_PREVIEW", placeholder(740, 90, "NOT_PERFORMED（本輪未授權隔離關聯）", (110, 110, 110)), (110, 110, 110)),
    ("PRODUCTION_DB_ASSET", placeholder(740, 90, "NONE（正式 DB Unit 5 28 列 image_assets=0）", (110, 110, 110)), (110, 110, 110)),
]
right_h = sum(40 + p[1].height + 20 for p in panels)
meta_lines = [
    "D/E. Metadata（新隔離唯讀追蹤；original_evidence_unavailable）",
    "anchor general_2_section_advanced_exercise_012_037",
    "page 16｜match unique_phrase+order 0.99（頁面正確）",
    f"question_start_y 用到 {start_y}（小題(2)），題號「12」實際在 y=586.9",
    f"question_region {steps['3_question_region']['result']['question_bbox']}",
    f"visual_bbox {steps['6_region_clip']['result']['visual_bbox']}",
    f"acceptance {acc['visual_status']} {acc['reasons']} → skipped_low_confidence",
    "visual_assets=[]｜pdf_visual_status=VISUAL_REQUIRED_MISSING｜Gate: required_figure_missing",
]
H = max(page_overlay.height + 60 + len(meta_lines) * 26 + 40, right_h) + 90
canvas = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(canvas)
d.text((20, 18), "Unit 5 進階題12 圖像對位調查 — 系統產物對照（不含教師截圖）", fill=(0, 0, 0), font=title_f)
canvas.paste(page_overlay, (20, 80))
d.text((20, 80 + page_overlay.height + 6), "疊圖：藍=Pipeline 題目區域；紅=Pipeline 候選；綠=真實圖形墨跡", fill=(60, 60, 60), font=body_f)
y = 80 + page_overlay.height + 40
for i, line in enumerate(meta_lines):
    d.text((20, y + i * 26), line, fill=(0, 0, 0) if i else (0, 0, 120), font=head_f if i == 0 else body_f)
x, y = 740, 80
for label, im, color in panels:
    d.text((x, y), label, fill=color, font=body_f)
    canvas.paste(im, (x, y + 30))
    y += 40 + im.height + 20
canvas.save(OUT / "visual_comparison.png")

rows = "".join(
    f"<tr><td>{html.escape(c['kind'])}</td><td>{html.escape(str(c.get('object', '')))}</td>"
    f"<td><code>{html.escape(json.dumps(c.get('final_visual_bbox') or c.get('bbox') or c.get('raw_bbox')))}</code></td>"
    f"<td>{html.escape(str(c.get('acceptance_status') or c.get('acceptance_with_current_gate') or c.get('status') or '—'))}</td></tr>"
    for c in candidates["candidates"])
page_html = f"""<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>Unit 5 進階題12 視覺對位調查</title>
<style>body{{font-family:system-ui,'Microsoft JhengHei';margin:24px;max-width:1200px}}section{{border:1px solid #ccc;padding:12px;margin:12px 0}}
h2{{font-size:18px}}.tag{{font-weight:bold;padding:2px 6px;border-radius:4px;color:#fff}}.src{{background:#2a7}}.cand{{background:#c22}}
.gen{{background:#c22}}.cf{{background:#749}}.na{{background:#777}}img{{max-width:100%;border:1px solid #ddd}}td,th{{border:1px solid #ccc;padding:4px 8px}}table{{border-collapse:collapse}}</style>
<h1>Unit 5「組合」進階題12 圖像對位調查</h1>
<p>證據性質：<b>new_isolated_readonly_trace</b>；原始任務證據：<b>original_evidence_unavailable</b>。本頁不含教師提供之截圖。</p>
<section><h2><span class="tag src">A. SOURCE_PDF_IMAGE</span> 原始 PDF 第16頁（由權威 PDF 直接 render）</h2><img src="A_source_pdf_page16.png"></section>
<section><h2><span class="tag cand">B. PIPELINE_CANDIDATE</span> 候選區域疊圖與裁切</h2><img src="B_pipeline_candidate_overlay_page16.png">
<p>Pipeline bbox 裁切（本調查以 <code>crop_pdf_bbox</code> 依該 bbox 渲染；Pipeline 本身未寫檔）：</p><img src="B_pipeline_candidate_crop_render.png"></section>
<section><h2><span class="tag gen">C. PIPELINE_GENERATED_ASSET</span></h2><p><b>NOT_GENERATED</b>：分類為 <code>skipped_low_confidence</code> 後於裁切前 <code>continue</code>，無暫存或正式 PNG。</p></section>
<section><h2>D. 候選與評分</h2><table><tr><th>類別</th><th>物件</th><th>bbox (pt)</th><th>狀態</th></tr>{rows}</table>
<p>{html.escape(candidates['confidence_model_note'])}</p></section>
<section><h2>E. Anchor 與 visual asset metadata</h2><pre>{html.escape(json.dumps(steps['2_anchor_to_pdf_page_and_y']['result'] | {'phrase_table': '見 visual_pipeline_trace.json'}, ensure_ascii=False, indent=2))}</pre>
<pre>visual_assets = []\npdf_visual_status = VISUAL_REQUIRED_MISSING\nStage 1 Gate blocker = required_figure_missing</pre></section>
<section><h2><span class="tag na">F. ISOLATED_RENDER_PREVIEW</span></h2><p><b>NOT_PERFORMED</b>：本輪未授權隔離關聯。</p></section>
<section><h2><span class="tag na">PRODUCTION_DB_ASSET</span></h2><p><b>NONE</b>：正式 DB Unit 5 現有 28 列，image_assets 合計 0；本調查前後內容指紋一致。</p></section>
<section><h2><span class="tag cf">COUNTERFACTUAL_ONLY</span> 原型墨跡聚類（記憶體內實驗，非 Pipeline 輸出、未核准）</h2><img src="X_counterfactual_prototype_cluster_crop.png">
<p>bbox {proto['picked']['bbox'] if proto['picked'] else None}；包含全部圖形墨跡={proto['contains_all_figure_ink']}；現行 Gate 判定 {proto['acceptance_with_current_gate']} {proto['reasons']}。</p></section>
</html>"""
(OUT / "visual_comparison.html").write_text(page_html, encoding="utf-8")
print("ok", canvas.size)
