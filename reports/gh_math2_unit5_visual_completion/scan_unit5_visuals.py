"""Read-only figure inventory of 普高數學2 Unit 5 (37 questions): stem cues, pipeline classification, DOCX pictures and PDF figure objects.

Inputs (all read-only): the authoritative DOCX / PDF (SHA-256 checked), the isolated rehearsal DB (37 rows of the new import) and the formal DB.
Outputs: scan_raw.json and pages/page_XX.png (each PDF page rendered with every non-text drawing / raster object outlined, for manual review).
"""
import hashlib
import json
import re
import sqlite3
import sys
import zipfile
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "textbook_import/uploaded_sources/general/數學2"
PDF = SRC / "e24c72f89309_單元05-組合.pdf"
DOCX = SRC / "ae362631e1be_單元05-組合.docx"
PDF_SHA = "e24c72f893099354886c288daef25eab59cd315facc778f7ffa96d4e242ec166"
DOCX_SHA = "ae362631e1be7030b8ac800c2553f9c067e8081c44e886e76cd0cbf0d4328fad"
ISOLATED = ROOT / "reports/gh_math2_unit5_fixed/sandbox/unit5.db"
FORMAL = ROOT / "instance/kumon_math.db"
CUES = ("如圖", "右圖", "下圖", "左圖", "上圖", "附圖", "圖中", "圖形", "下表", "右表", "表中", "如表")

assert hashlib.sha256(PDF.read_bytes()).hexdigest() == PDF_SHA
assert hashlib.sha256(DOCX.read_bytes()).hexdigest() == DOCX_SHA
out = {"pdf_sha256": PDF_SHA, "docx_sha256": DOCX_SHA}

# --- rows of the new import (isolated) -------------------------------------------------------------------------------------------
con = sqlite3.connect(f"file:{ISOLATED.as_posix()}?mode=ro", uri=True)
rows = []
for rid, skill, title, text, answer, notes in con.execute(
        "select id, skill_id, source_description, problem_text, correct_answer, notes from textbook_examples "
        "where source_curriculum='general' and source_chapter='單元5 組合' order by id"):
    n = json.loads(notes or "{}")
    a = n.get("question_anchor") or {}
    e = n.get("pdf_visual_enrichment") or {}
    rows.append({"id": rid, "skill_id": skill, "title": title, "anchor": a.get("anchor_id"), "source_order": a.get("source_order"),
                 "block_index": a.get("block_index"), "cues": [c for c in CUES if c in text], "stem_head": text[:90].replace("\n", " "),
                 "pdf_page": e.get("page"), "pipeline_status": n.get("pdf_visual_status"), "pipeline_classification": e.get("classification"),
                 "pipeline_reason": e.get("visual_reason"), "needs_image": n.get("needs_image"),
                 "image_dependency_reason": n.get("image_dependency_reason"), "image_assets": len(n.get("image_assets") or []),
                 "answer_present": bool(str(answer or "").strip())})
con.close()
out["isolated_rows"] = rows

# --- formal DB (legacy Unit 5 import) --------------------------------------------------------------------------------------------
con = sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True)
formal = []
for rid, skill, title, text, notes in con.execute(
        "select id, skill_id, source_description, problem_text, notes from textbook_examples "
        "where source_curriculum='general' and source_volume='數學2' and source_chapter='單元5 組合' order by id"):
    n = json.loads(notes or "{}")
    formal.append({"id": rid, "skill_id": skill, "title": title, "cues": [c for c in CUES if c in (text or "")],
                   "anchor": (n.get("question_anchor") or {}).get("anchor_id"), "image_assets": len(n.get("image_assets") or []),
                   "stem_head": (text or "")[:60].replace("\n", " ")})
con.close()
out["formal_rows"] = formal

# --- DOCX pictures (exclude OLE equation previews inside <w:object>) -----------------------------------------------------------
xml = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf-8")
body = re.sub(r"<w:object\b.*?</w:object>", "<OLE/>", xml, flags=re.S)
paras = re.findall(r"<w:p\b.*?</w:p>", body, flags=re.S)
docx_pics = []
for i, p in enumerate(paras):
    pics = len(re.findall(r"<w:drawing\b", p)) + len(re.findall(r"<v:imagedata\b", p))
    if pics:
        ctx = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", "".join(paras[max(0, i - 3):i + 1])))
        docx_pics.append({"paragraph": i, "pictures": pics, "context_text": ctx[-120:]})
out["docx_pictures"] = docx_pics
out["docx_ole_objects"] = len(re.findall(r"<w:object\b", xml))

# --- PDF figure objects ------------------------------------------------------------------------------------------------------------
doc = fitz.open(PDF)
(HERE / "pages").mkdir(exist_ok=True)
pages = []
for pno, page in enumerate(doc, start=1):
    W, H = page.rect.width, page.rect.height
    objs = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.width > 0.6 * W or r.y0 < 40 or r.y1 > H - 40:
            continue  # full-width boxes / rules, header and footer bands
        if r.width < 4 and r.height < 4:
            continue
        objs.append(("path", [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)]))
    for img in page.get_images(full=True):
        for r in page.get_image_rects(img[0]):
            if r.y0 < 40 or r.y1 > H - 40:
                continue
            objs.append(("raster", [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)]))
    pix = page.get_pixmap(dpi=110)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    z = 110 / 72
    dr = ImageDraw.Draw(im)
    for kind, (x0, y0, x1, y1) in objs:
        dr.rectangle([x0 * z, y0 * z, x1 * z, y1 * z], outline=(255, 0, 0) if kind == "raster" else (0, 120, 255), width=1)
    im.save(HERE / "pages" / f"page_{pno:02d}.png")
    pages.append({"page": pno, "raster_objects": [o[1] for o in objs if o[0] == "raster"], "path_objects": len([o for o in objs if o[0] == "path"]),
                  "text_head": page.get_text()[:80].replace("\n", " ")})
out["pdf_pages"] = pages
(HERE / "scan_raw.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

print("isolated rows", len(rows), "| formal rows", len(formal), "| docx pictures", len(docx_pics), "| OLE", out["docx_ole_objects"], "| pdf pages", len(pages))
for r in rows:
    print(r["id"], r["source_order"], r["title"], r["skill_id"], "p", r["pdf_page"], r["pipeline_status"], r["cues"], r["image_assets"], "|", r["stem_head"][:50])
for p in docx_pics:
    print("DOCX pic", p)
for p in pages:
    print("PDF page", p["page"], "raster", len(p["raster_objects"]), "paths", p["path_objects"], "|", p["text_head"][:50])
for f in formal:
    if f["cues"]:
        print("FORMAL cue", f)
