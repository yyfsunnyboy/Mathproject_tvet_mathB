"""Teacher preview for 普高數學2 Unit 5 習題進階題12 (fixed graded entry + reviewed crop): teacher_preview.html / teacher_preview.png.

Shows, side by side, the ORIGINAL PDF region (rendered from the authoritative PDF, page 16) and the ISOLATED_RENDER_PREVIEW asset (the PNG the
isolated Stage 1 rehearsal produced from the staged verified region), the stem exactly as stored, both parts with the student-facing input,
the reference answers / solution (teacher view only) and the provenance.  Read-only: nothing outside this folder is written.
"""
import base64
import hashlib
import html
import io
import json
import sqlite3
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/e24c72f89309_單元05-組合.pdf"
staged = json.loads((HERE / "staged_fixed_entries.json").read_text(encoding="utf-8"))
rid, entry = next(iter(staged["entries"].items()))
rehearsal = json.loads((HERE / "rehearsal_result.json").read_text(encoding="utf-8"))
prov = entry["provenance"]

assert hashlib.sha256(PDF.read_bytes()).hexdigest() == prov["pdf_sha256"]
con = sqlite3.connect(f"file:{(HERE / 'sandbox' / 'unit5.db').as_posix()}?mode=ro", uri=True)
text, notes = con.execute("select problem_text, notes from textbook_examples where id=?", (int(rid),)).fetchone()
con.close()
asset = json.loads(notes)["image_assets"][0]
asset_png = HERE / "sandbox" / asset["path"]
assert hashlib.sha256(asset_png.read_bytes()).hexdigest() == asset["sha256"]

doc = fitz.open(PDF)
page = doc[prov["pdf_page"] - 1]
x0, y0, x1, y1 = prov["figure_bbox"]
context_png = page.get_pixmap(dpi=200, clip=fitz.Rect(70, 560, 545, 700)).tobytes("png")
z = 200 / 72
ctx = Image.open(io.BytesIO(context_png)).convert("RGB")
ImageDraw.Draw(ctx).rectangle([(x0 - 70) * z, (y0 - 560) * z, (x1 - 70) * z, (y1 - 560) * z], outline=(0, 140, 0), width=4)
ctx_buf = io.BytesIO()
ctx.save(ctx_buf, "PNG")
context_png = ctx_buf.getvalue()


def b64(data: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(data).decode()


def font(size):
    for name in ("msjh.ttc", "msyh.ttc", "mingliu.ttc", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


parts = entry["answer_contract"]["parts"]
choices = "　".join(f"{c['label']}{c['value']}" for c in parts[0]["choices"])
checks = [
    ("Stage 1 Gate（隔離重新評估）", f"{rehearsal['gate']['status']}，{rehearsal['gate']['rows']} 題，blocked {len(rehearsal['gate']['blocked'])}"),
    ("其餘 36 題", "內容／Skill／anchor／圖片狀態零差異" if not any(rehearsal["other_36_rows"].values()) else json.dumps(rehearsal["other_36_rows"], ensure_ascii=False)),
    ("正式 DB", "零變更" if rehearsal["formal_db_zero_change"] else "有變更！"),
    ("live 設定檔", "未修改" if rehearsal["live_config_unchanged"] else "被修改！"),
]
html_doc = f"""<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>Unit 5 進階題12 固定題預覽（待教師確認）</title>
<script>window.MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)'],['$','$']]}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<style>body{{font-family:"Microsoft JhengHei",sans-serif;max-width:1100px;margin:24px auto;line-height:1.7}}
.box{{border:1px solid #ccc;border-radius:8px;padding:14px 18px;margin:14px 0}} .warn{{background:#fff7e0;border-color:#e0b000}}
.row{{display:flex;gap:18px;align-items:flex-start}} .row>div{{flex:1}} img{{max-width:100%;border:1px solid #999}}
.tag{{display:inline-block;font-size:12px;padding:1px 8px;border-radius:10px;background:#eee;margin-left:6px}}
table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:4px 10px;text-align:left}} pre{{white-space:pre-wrap}}</style>
<h1>普高數學第二冊 單元5「組合」習題進階題12 — 固定題預覽（待教師確認）</h1>
<div class="box warn">請確認：①右側系統裁切圖與左側原始 PDF 一致（半圓、A<sub>1</sub>～A<sub>4</sub>、B<sub>1</sub>～B<sub>6</sub> 標籤完整，無多餘內容）；
②題幹與兩小題正確；③答案與解析正確。確認後才會寫入 verified region 與固定題庫（需另行授權）。</div>
<div class="row">
 <div class="box"><b>原始 PDF 第 {prov['pdf_page']} 頁</b><span class="tag">SOURCE_PDF_IMAGE</span><br>
  <img src="{b64(context_png)}"><br><small>綠框＝待核准裁切範圍 bbox {prov['figure_bbox']}（PDF pt）</small></div>
 <div class="box"><b>系統裁切圖（學生端將顯示）</b><span class="tag">ISOLATED_RENDER_PREVIEW</span><br>
  <img src="{b64(asset_png.read_bytes())}" style="max-width:340px"><br>
  <small>由隔離 Stage 1 重建產生；{asset['width']}×{asset['height']} px @ {asset['dpi']} dpi；SHA-256 {asset['sha256'][:16]}…；
  visual_status={asset['visual_status']}；match_method={asset['match_method']}</small></div>
</div>
<div class="box"><b>學生看到的題目</b>（Stage 1 題幹原文，未改寫）<pre>{html.escape(text)}</pre>
作答欄位：<b>{parts[0]['label']}</b> 文字輸入（可填 ③、3 或 40）　<b>{parts[1]['label']}</b> 文字輸入（整數）<br>
<small>送出前前端不會收到任何答案或解析（已由隔離測試驗證）。選項：{html.escape(choices)}</small></div>
<div class="box"><b>參考答案與解析（教師檢閱，學生作答後才顯示）</b>
<p>(1) {entry['answer']['part_1']}（{40} 條）　(2) {entry['answer']['part_2']} 個</p>
<ol>{''.join(f'<li>{html.escape(s)}</li>' for s in entry['reference_solution'])}</ol>
<small>獨立驗算：由 PDF 向量圖取得 10 個點座標，列舉全部 45 組點對與 120 組三點，共線三點組只有 A 點的 4 組 → 直線 {entry['oracle']['lines']} 條、三角形 {entry['oracle']['triangles']} 個，與公式一致。</small></div>
<div class="box"><b>來源與綁定</b><table>
<tr><th>curriculum / 冊 / 單元</th><td>{prov['curriculum']} / {prov['volume']} / {prov['chapter']}</td></tr>
<tr><th>skill_id</th><td>{entry['skill_id']}</td></tr><tr><th>question_anchor</th><td>{entry['question_anchor']}</td></tr>
<tr><th>PDF SHA-256</th><td>{prov['pdf_sha256']}</td></tr>
<tr><th>題幹 SHA-256 綁定</th><td>{entry['problem_text_sha256']}（題幹若變動，固定題自動失效）</td></tr>
<tr><th>模式</th><td>固定題庫 graded（非 Generator）；row id {rid} 為隔離演練編號，正式匯入後依 anchor 重新綁定</td></tr></table></div>
<div class="box"><b>隔離驗證</b><table>{''.join(f'<tr><th>{k}</th><td>{v}</td></tr>' for k, v in checks)}</table></div>
</html>"""
(HERE / "teacher_preview.html").write_text(html_doc, encoding="utf-8")

W = 1400
title_f, head_f, body_f = font(30), font(22), font(19)
src = Image.open(io.BytesIO(context_png)).convert("RGB")
src = src.resize((820, int(src.height * 820 / src.width)))
crop = Image.open(asset_png).convert("RGB")
crop = crop.resize((440, int(crop.height * 440 / crop.width)))
stem_lines = text.replace("\\(", "").replace("\\)", "").replace("_{ ", "").replace(" }", "").replace("\\ldots", "…").split("\n")
sol = [f"(1) 答案 {entry['answer']['part_1']}：C(10,2) - C(4,2) + 1 = 45 - 6 + 1 = 40 條直線",
       f"(2) 答案 {entry['answer']['part_2']}：C(10,3) - C(4,3) = 120 - 4 = 116 個三角形",
       "獨立驗算：PDF 向量點座標列舉 45 組點對／120 組三點，只有 A1～A4 共線"]
meta = [f"skill_id {entry['skill_id']}　anchor {entry['question_anchor']}",
        f"PDF {prov['pdf_sha256'][:16]}… 第 {prov['pdf_page']} 頁　bbox {prov['figure_bbox']}",
        *(f"{k}：{v}" for k, v in checks)]
H = 90 + max(src.height, crop.height) + 60 + 34 * (len(stem_lines) + len(sol) + len(meta)) + 120
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
d.text((30, 24), "Unit 5 習題進階題12 — 固定題預覽（待教師確認）", fill="black", font=title_f)
d.text((30, 72), "原始 PDF 第16頁（綠框＝待核准裁切範圍）", fill=(0, 110, 0), font=head_f)
d.text((890, 72), "系統裁切圖（隔離產生，學生端顯示）", fill=(0, 70, 160), font=head_f)
im.paste(src, (30, 104))
im.paste(crop, (890, 104))
d.rectangle([889, 103, 890 + crop.width, 104 + crop.height], outline=(0, 70, 160), width=2)
y = 104 + max(src.height, crop.height) + 24
for heading, lines, color in (("學生看到的題目（題幹原文）", stem_lines, "black"), ("參考答案與解析（教師檢閱）", sol, (150, 0, 0)),
                              ("來源與隔離驗證", meta, (60, 60, 60))):
    d.text((30, y), heading, fill=(0, 0, 0), font=head_f)
    y += 32
    for line in lines:
        d.text((50, y), line, fill=color, font=body_f)
        y += 30
    y += 10
im.crop((0, 0, W, y + 10)).save(HERE / "teacher_preview.png")
print("teacher_preview.html / teacher_preview.png written")
