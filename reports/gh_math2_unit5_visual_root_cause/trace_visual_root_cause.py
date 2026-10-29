"""Read-only root-cause trace for Unit 5 進階題12 PDF visual (no DB writes, no core changes).

Runs the real detector functions in-process on the authoritative PDF and the rows captured by the
previous isolated dry-run, records every intermediate decision for page 16, and runs in-memory
counterfactuals.  Nothing here mounts an asset, writes notes, or touches the formal DB.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import fitz  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import core.textbook_pdf_visual as V  # noqa: E402
from core.textbook_pdf_visual_acceptance import bbox_iou, evaluate_visual_acceptance, search_band_bottom  # noqa: E402
from core.textbook_question_anchor import normalize_question_label  # noqa: E402

PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/e24c72f89309_單元05-組合.pdf"
PDF_SHA = "e24c72f893099354886c288daef25eab59cd315facc778f7ffa96d4e242ec166"
RAW = ROOT / "reports/gh_math2_unit5_stage1_repair/dry_run_raw.json"
FORMAL = ROOT / "instance/kumon_math.db"
TARGET_ANCHOR = "general_2_section_advanced_exercise_012_037"
TARGET_ID = 12834
PAGE = 16
TEACHER_BBOX = [420, 575, 540, 675]
REGIONS_CATALOG = ROOT / "configs/stage1_verified_visual_regions.json"
GENERAL_PDFS = sorted((ROOT / "textbook_import/uploaded_sources/general").rglob("*.pdf"))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def r(v, n=1):
    if v is None:
        return None
    return [round(float(x), n) for x in v] if isinstance(v, (list, tuple)) else round(float(v), n)


def iou(a, b):
    return round(bbox_iou(a, b), 3) if a and b else 0.0


def formal_db_fingerprint() -> dict:
    """Logical fingerprint through a read-only connection (WAL-safe, no copy, no write)."""
    with sqlite3.connect(f"file:{FORMAL.as_posix()}?mode=ro", uri=True) as con:
        rows = con.execute(
            "select id, source_chapter, source_description, notes from textbook_examples "
            "where source_curriculum='general' and source_volume='數學2' and source_chapter like '%組合%' order by id"
        ).fetchall()
        total = con.execute("select count(*) from textbook_examples").fetchone()[0]
        h = hashlib.sha256()
        for row in con.execute("select id, problem_text, notes, skill_id from textbook_examples order by id"):
            h.update(json.dumps(row, ensure_ascii=False, default=str).encode("utf-8"))
    unit5 = []
    for rid, chap, desc, notes in rows:
        try:
            n = json.loads(notes or "{}")
        except ValueError:
            n = {}
        assets = [a for a in (n.get("image_assets") or []) if isinstance(a, dict)]
        unit5.append({"id": rid, "chapter": chap, "label": str(desc or "").split(" [", 1)[0],
                      "image_assets": len(assets), "pdf_visual_status": n.get("pdf_visual_status")})
    return {"textbook_examples_total": total, "textbook_examples_content_sha256": h.hexdigest(), "unit5_rows": unit5}


def load_examples() -> list[SimpleNamespace]:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    titles = {row["id"]: row["title"] for row in raw["capture"]["visual_summary"]["rows"]}
    out = []
    for row in raw["capture"]["post_review_rows"]:
        notes = dict(row["notes"])
        for key in ("pdf_visual_enrichment", "pdf_visual_status", "image_assets"):
            notes.pop(key, None)
        out.append(SimpleNamespace(id=row["id"], source_description=titles.get(row["id"], row["label"]),
                                   problem_text=row["problem_text"], problem_type="", source_curriculum="general",
                                   source_volume="數學2", source_chapter="單元5 組合", source_section="5.組合",
                                   notes=json.dumps(notes, ensure_ascii=False), skill_id=row["skill_id"]))
    return out


def sorted_items(examples):
    items = [V._example_to_item(e) for e in examples]
    items.sort(key=lambda x: (int(x.get("source_order") or 10**9), int(x.get("id") or 0)))
    return items


def phrase_table(row, pages):
    page = pages[int(row["pdf_match"]["page"]) - 1]
    label = normalize_question_label(str(row.get("source_description") or ""))
    out = []
    for ph in V.extract_match_phrases(str(row.get("problem_text") or ""), label):
        on_page = ph in page["norm_text"]
        out.append({"phrase": ph, "len": len(ph), "on_matched_page": on_page,
                    "pages_with_phrase": V._phrase_page_frequency(pages, ph),
                    "y_on_matched_page": r(V.find_phrase_y(page, ph)) if on_page else None})
    return out


def earliest_hit_y(row, pages, floor_y):
    """Prototype: stem start = earliest on-page hit below the previous question's start (not the longest hit)."""
    ys = [t["y_on_matched_page"] for t in phrase_table(row, pages)
          if t["on_matched_page"] and t["y_on_matched_page"] is not None and t["y_on_matched_page"] > floor_y + 2]
    return min(ys) if ys else None


def apply_earliest_start(matched, pages):
    changes = []
    prev = {}
    for row in matched:
        pm = row.get("pdf_match")
        if not pm or row.get("match_method") not in ("unique_phrase+order", "shared_phrase+order"):
            if pm:
                prev[int(pm["page"])] = float(pm["question_start_y"])
            continue
        page_no = int(pm["page"])
        floor_y = prev.get(page_no, -1.0)
        y_new = earliest_hit_y(row, pages, floor_y)
        y_old = float(pm["question_start_y"])
        if y_new is not None and y_new < y_old - 2:
            changes.append({"anchor_id": row.get("anchor_id"), "label": normalize_question_label(row.get("source_description") or ""),
                            "page": page_no, "longest_hit_y": r(y_old), "earliest_hit_y": r(y_new), "shift_pt": r(y_old - y_new)})
            pm["question_start_y"] = y_new
        prev[page_no] = float(pm["question_start_y"])
    return changes


def label_number(row):
    import re
    m = re.search(r"(\d+)\s*$", normalize_question_label(re.sub(r"\s*\[[^\]]*\]\s*$", "", str(row.get("source_description") or ""))))
    return m.group(1) if m else None


def marker_start_y(row, page, floor_y):
    """Prototype: nearest left-margin question-number marker above the longest hit and below the previous question."""
    num = label_number(row)
    pm = row["pdf_match"]
    y_hit = float(pm["question_start_y"])
    hit_line = [w for w in page["words"] if abs(float(w[1]) - y_hit) <= 3.0]
    text_left = min((float(w[0]) for w in hit_line), default=0.2 * page["width"])
    marks = [float(w[1]) for w in page["words"]
             if num and str(w[4]).strip() == num and float(w[2]) <= text_left - 4
             and float(w[0]) < 0.2 * page["width"] and floor_y + 2 < float(w[1]) <= y_hit + 2]
    return max(marks) if marks else None


def apply_marker_start(matched, pages):
    changes, prev = [], {}
    for row in matched:
        pm = row.get("pdf_match")
        if not pm:
            continue
        page_no = int(pm["page"])
        if row.get("match_method") in ("unique_phrase+order", "shared_phrase+order"):
            y_new = marker_start_y(row, pages[page_no - 1], prev.get(page_no, -1.0))
            y_old = float(pm["question_start_y"])
            if y_new is not None and y_new < y_old - 2:
                changes.append({"anchor_id": row.get("anchor_id"), "label": normalize_question_label(row.get("source_description") or ""),
                                "page": page_no, "longest_hit_y": r(y_old), "marker_y": r(y_new), "shift_pt": r(y_old - y_new)})
                pm["question_start_y"] = y_new
        prev[page_no] = float(pm["question_start_y"])
    return changes


def is_page_furniture(d, page, edge_pt=60.0):
    """Prototype: path leaving the page box, or a full-width band confined to the top/bottom margin."""
    bb = d["bbox"]
    pw, ph = float(page["width"]), float(page["height"])
    outside = bb[0] < -1 or bb[1] < -1 or bb[2] > pw + 1 or bb[3] > ph + 1
    full_width_band = (bb[2] - bb[0]) >= 0.9 * pw and (bb[1] >= ph - edge_pt or bb[3] <= edge_pt)
    return bool(d.get("blended") or outside or full_width_band)


def drop_furniture(pages):
    out = copy.deepcopy(pages)
    for p in out:
        p["drawings"] = [d for d in p["drawings"] if not is_page_furniture(d, p)]
        p["small_drawings"] = [d for d in p["small_drawings"] if not is_page_furniture(d, p)]
    return out


def prototype_ink_clusters(page, gap=6.0):
    """Prototype: connected components of figure ink (paths + glyph/dot paths), furniture excluded."""
    objs = []
    for d in list(page["drawings"]) + list(page["small_drawings"]):
        if is_page_furniture(d, page):
            continue
        bb = [float(v) for v in d["bbox"]]
        # Panels, frames and rules (example boxes, section bars) are layout, not figure ink.
        if bb[2] - bb[0] >= 0.5 * page["width"] or bb[3] - bb[1] > 0.5 * page["height"]:
            continue
        objs.append(bb)
    prose = [[float(v) for v in w[:4]] for w in page["words"] if len(str(w[4]).strip()) >= 2]
    clusters, used = [], [False] * len(objs)
    for i in range(len(objs)):
        if used[i]:
            continue
        used[i] = True
        members, box, changed = [objs[i]], list(objs[i]), True
        while changed:
            changed = False
            for j in range(len(objs)):
                if not used[j] and V._bbox_gap(box, objs[j]) <= gap:
                    used[j] = True
                    members.append(objs[j])
                    box = V.union_bbox([box, objs[j]])
                    changed = True
        if len(members) < 2 and V._box_area(box) < 2500:
            continue
        clusters.append({"bbox": r(box), "members": len(members), "w": r(box[2] - box[0]), "h": r(box[3] - box[1]),
                         "area": r(V._box_area(box), 0),
                         "prose_words_inside": sum(1 for p in prose if V.intersect_area(box, p) > 0.3 * max(V._box_area(p), 1.0))})
    return clusters


def object_filters(d, qb, page):
    """Same predicates as classify_and_detect_visuals (core/textbook_pdf_visual.py L820-L950)."""
    bb, area = d["bbox"], float(d["area"])
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    pw, ph = float(page["width"]), float(page["height"])
    inter = V.intersect_area(qb, bb)
    hit = inter > 0 and 2500 <= area <= 0.55 * pw * ph
    return {
        "bbox": r(bb), "w": r(w), "h": r(h), "area": r(area, 0), "blended": d.get("blended"),
        "intersects_question_region": inter > 0,
        "extends_outside_page": bb[0] < -1 or bb[1] < -1 or bb[2] > pw + 1 or bb[3] > ph + 1,
        "draw_hit[intersects,2500<=area<=0.55page]": hit,
        "significant[area>=15000,w>=100,h>=70]": hit and area >= 15000 and w >= 100 and h >= 70,
        "soft_strong_cue[area>=2500,w>=40,h>=40]": hit and w >= 40 and h >= 40,
        "band_search[area>=6000,w>=60,h>=50]": area >= 6000 and w >= 60 and h >= 50,
        "right_panel_fallback[area>=1800,x0>=0.42W,w>=25,h>=25]": area >= 1800 and bb[0] >= 0.42 * pw and w >= 25 and h >= 25,
        "right_panel_single_min_area[>=3500]": area >= 3500,
        "page_furniture_by_prototype_rule": is_page_furniture(d, page),
    }


def detect(pages, examples, *, earliest_start=False, marker_start=False):
    matched = V.match_questions_to_pdf(sorted_items(examples), pages)
    changes = apply_earliest_start(matched, pages) if earliest_start else []
    if marker_start:
        changes = apply_marker_start(matched, pages)
    matched = V.classify_and_detect_visuals(V.assign_question_regions(matched, pages), pages, assemble_visual_groups=True)
    return matched, changes


def summarize(row):
    return {"question_bbox": r(row["regions"][0]["bbox"]) if row.get("regions") else None,
            "visual_bbox": r(row.get("visual_bbox")), "visual_classification": row.get("visual_classification"),
            "visual_status": row.get("visual_status"), "visual_reason": row.get("visual_reason"),
            "should_mount": row.get("should_mount")}


def accept(row, bbox, page):
    qb = row["regions"][0]["bbox"]
    return evaluate_visual_acceptance(
        problem_text=row["problem_text"], visual_bbox=bbox, question_bbox=qb, next_question_y=row.get("next_question_y"),
        page_words=page["words"], match_score=row["match_score"], strong_cue=V._text_has_strong_figure_cue(row["problem_text"]),
        page_height=page["height"], question_start_y=row["pdf_match"]["question_start_y"], page=page)


def font(size):
    for name in ("msjh.ttc", "msyh.ttc", "mingliu.ttc", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert PDF.is_file() and sha(PDF) == PDF_SHA, "authoritative PDF hash mismatch"
    db_before = formal_db_fingerprint()
    with fitz.open(str(PDF)) as doc:
        pages = V.build_page_index(doc)
    examples = load_examples()

    # Baseline: exact pipeline call order of enrich_textbook_examples_with_pdf_visuals (L1514-L1516).
    base, _ = detect(pages, examples)
    row = next(m for m in base if m.get("anchor_id") == TARGET_ANCHOR)
    page = pages[PAGE - 1]
    qb = row["regions"][0]["bbox"]
    next_q_y = row.get("next_question_y")
    group_limit = [qb[0], qb[1], qb[2], search_band_bottom(qb, page_height=page["height"], next_question_y=next_q_y)]
    recorded = json.loads(RAW.read_text(encoding="utf-8"))
    rec_row = next(x for x in recorded["capture"]["visual_summary"]["rows"] if x["id"] == TARGET_ID)
    reproduced = r(row.get("visual_bbox"), 4) == r(rec_row["visual_bbox"], 4) and row["visual_reason"] == rec_row["visual_reason"]

    phrases = phrase_table(row, pages)
    label_word = next((w for w in page["words"] if str(w[4]).strip() == "12" and float(w[0]) < 110), None)
    semicircle = next(d for d in page["drawings"] if abs(d["bbox"][0] - 435.9) < 1 and abs(d["bbox"][1] - 599.2) < 1)
    footer = next(d for d in page["drawings"] if d["bbox"][0] < -100 and d["bbox"][1] > 700)
    figure_ink = [d for d in page["small_drawings"] if V._bbox_inside([420, 580, 530, 660], d["bbox"])]
    ink_union = V.union_bbox([semicircle["bbox"]] + [d["bbox"] for d in figure_ink])
    objects = [{"object": "semicircle_path", **object_filters(semicircle, qb, page)},
               {"object": "footer_band_path", **object_filters(footer, qb, page)}]
    acc_actual = accept(row, row["visual_bbox"], page)

    # Counterfactuals (in-memory only), applied cumulatively.
    _, earliest_changes = detect(pages, examples, earliest_start=True)
    cf_a_rows, cf_a_changes = detect(pages, examples, marker_start=True)
    cf_a = next(m for m in cf_a_rows if m.get("anchor_id") == TARGET_ANCHOR)
    pages_nf = drop_furniture(pages)
    cf_f_rows, _ = detect(pages_nf, examples)
    cf_f = next(m for m in cf_f_rows if m.get("anchor_id") == TARGET_ANCHOR)
    cf_b_rows, _ = detect(pages_nf, examples, marker_start=True)
    cf_b = next(m for m in cf_b_rows if m.get("anchor_id") == TARGET_ANCHOR)
    cf_b_qb = cf_b["regions"][0]["bbox"]
    cf_b_limit = [cf_b_qb[0], cf_b_qb[1], cf_b_qb[2],
                  search_band_bottom(cf_b_qb, page_height=page["height"], next_question_y=cf_b.get("next_question_y"))]
    clusters = [c for c in prototype_ink_clusters(pages_nf[PAGE - 1]) if V.intersect_area(c["bbox"], cf_b_limit) > 0]
    proto = max((c for c in clusters if c["prose_words_inside"] == 0), key=lambda c: c["area"], default=None)
    acc_proto = accept(cf_b, proto["bbox"] if proto else None, pages_nf[PAGE - 1])
    semi_group = V.assemble_visual_group_bbox(list(semicircle["bbox"]), pages_nf[PAGE - 1], limit_bbox=cf_b_limit)
    acc_semi = accept(cf_b, semi_group, pages_nf[PAGE - 1])

    def side_effects(rows):
        before = {m["anchor_id"]: summarize(m) for m in base}
        diff = []
        for m in rows:
            s = summarize(m)
            b = before[m["anchor_id"]]
            if (s["visual_classification"], s["should_mount"], s["visual_status"]) != (b["visual_classification"], b["should_mount"], b["visual_status"]):
                diff.append({"anchor_id": m["anchor_id"], "before": b, "after": s})
        return {"rows_changed": len(diff), "rows_newly_mounted": sum(1 for d in diff if d["after"]["should_mount"]), "changes": diff}

    # Unit 5 systemic: how often the longest hit is not the stem start.
    shift_rows = [c for c in cf_a_changes if c["shift_pt"] >= 20]
    earliest_verdicts = {
        "general_2_section_example_001_001": "WRONG: y=185.6 is exposition text above 例1 (shared C(n,k) tokens)",
        "general_2_section_exercise_001_022": "BORDERLINE: y=177.0 is the shared 觀念澄清 instruction line",
        "general_2_section_exercise_005_030": "WRONG: y=164.1 is inside 基礎題4 (shared phrase 共有多少種分配方法)",
        "general_2_section_advanced_exercise_012_037": "CORRECT: y=587.5 is the first stem line",
    }
    for c in earliest_changes:
        c["manual_check"] = earliest_verdicts.get(c["anchor_id"], "unchecked")

    def ink_cut_by_crop(pg, bb):
        """Ink paths that straddle the crop edge (a cut figure), furniture/panels excluded."""
        cut = 0
        for d in list(pg["drawings"]) + list(pg["small_drawings"]):
            b = d["bbox"]
            if is_page_furniture(d, pg) or b[2] - b[0] >= 0.5 * pg["width"]:
                continue
            inter = V.intersect_area(bb, b)
            if 0 < inter < 0.98 * max(V._box_area(b), 1e-6):
                cut += 1
        return cut

    # Images -----------------------------------------------------------------------------------------
    with fitz.open(str(PDF)) as doc:
        pg = doc.load_page(PAGE - 1)
        z = 150 / 72.0
        pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save(OUT / "A_source_pdf_page16.png")
    ann = img.copy()
    dr = ImageDraw.Draw(ann)
    f = font(17)
    pw, ph = page["width"], page["height"]

    def box(bb, color, width, label=None, dy=-22):
        x0, y0, x1, y1 = max(0, bb[0]), max(0, bb[1]), min(pw, bb[2]), min(ph, bb[3])
        dr.rectangle([x0 * z, y0 * z, x1 * z, y1 * z], outline=color, width=width)
        if label:
            dr.text((x0 * z + 4, max(0, y0 * z + dy)), label, fill=color, font=f)

    box(qb, (30, 90, 220), 3, "Pipeline question_region (start_y=678.2 = 小題(2))", dy=4)
    box(footer["bbox"], (230, 120, 0), 3, "footer band path (only candidate)", dy=-22)
    box(row["visual_bbox"], (220, 0, 0), 5)
    box(ink_union, (0, 150, 0), 3, "real figure ink (NOT in region)", dy=-22)
    dr.line([0, 587.5 * z, pw * z, 587.5 * z], fill=(0, 150, 0), width=1)
    dr.text((8, 587.5 * z - 20), "stem start y=587.5", fill=(0, 150, 0), font=f)
    dr.text((8, 745.7 * z + 2), "PIPELINE_CANDIDATE visual_bbox [0,736.6,609.4,745.7]", fill=(220, 0, 0), font=f)
    ann.save(OUT / "B_pipeline_candidate_overlay_page16.png")
    V.crop_pdf_bbox(PDF, PAGE, row["visual_bbox"], OUT / "B_pipeline_candidate_crop_render.png", dpi=200)
    if proto:
        V.crop_pdf_bbox(PDF, PAGE, proto["bbox"], OUT / "X_counterfactual_prototype_cluster_crop.png", dpi=200)

    # Systemic scan across all general PDFs and the 6 manually verified regions (Units 3/4) -----------
    systemic_pdfs = []
    for pdf_path in GENERAL_PDFS:
        with fitz.open(str(pdf_path)) as d2:
            pidx = V.build_page_index(d2)
        n = 0
        for p in pidx:
            if any(not d.get("blended") and is_page_furniture(d, p) and d["bbox"][1] < p["height"] - 36.0
                   and 2500 <= d["area"] <= 0.55 * p["width"] * p["height"]
                   and (d["bbox"][2] - d["bbox"][0]) >= 40 and (d["bbox"][3] - d["bbox"][1]) >= 40 for d in p["drawings"]):
                n += 1
        systemic_pdfs.append({"pdf": pdf_path.relative_to(ROOT).as_posix(), "pages": len(pidx),
                              "pages_where_footer_furniture_enters_last_question_region_and_passes_soft_filter": n})

    manual_regions = []
    catalog = json.loads(REGIONS_CATALOG.read_text(encoding="utf-8"))
    pdf_by_sha = {sha(p): p for p in GENERAL_PDFS}
    for src in catalog.get("sources", []):
        pdf_path = pdf_by_sha.get(src.get("pdf_sha256"))
        if not pdf_path:
            continue
        with fitz.open(str(pdf_path)) as d2:
            pidx = V.build_page_index(d2)
        for label, specs in (src.get("regions") or {}).items():
            for spec in specs:
                p = pidx[int(spec["page"]) - 1]
                vb = [float(v) for v in spec["bbox"]]
                inside = [d for d in p["drawings"] if not d.get("blended") and V.intersect_area(vb, d["bbox"]) > 0.5 * max(d["area"], 1)]
                largest = max(inside, key=lambda d: d["area"], default=None)
                lw = (largest["bbox"][2] - largest["bbox"][0]) if largest else 0
                lh = (largest["bbox"][3] - largest["bbox"][1]) if largest else 0
                cands = [c for c in prototype_ink_clusters(p) if V.intersect_area(c["bbox"], vb) > 0 and c["prose_words_inside"] == 0]
                best = max(cands, key=lambda c: iou(c["bbox"], vb), default=None)
                manual_regions.append({
                    "chapter": src.get("chapter"), "label": label, "page": spec["page"], "verified_bbox": vb,
                    "verified_size_pt": r([vb[2] - vb[0], vb[3] - vb[1]]), "paths_ge_80pt2_inside": len(inside),
                    "small_ink_paths_inside": sum(1 for d in p["small_drawings"] if V._bbox_inside(vb, d["bbox"], tol=2)),
                    "largest_single_path": {"bbox": r(largest["bbox"]), "w": r(lw), "h": r(lh), "area": r(largest["area"], 0)} if largest else None,
                    "largest_path_passes_soft[area>=2500,w>=40,h>=40]": bool(largest and largest["area"] >= 2500 and lw >= 40 and lh >= 40),
                    "largest_path_passes_band[area>=6000,w>=60,h>=50]": bool(largest and largest["area"] >= 6000 and lw >= 60 and lh >= 50),
                    "prototype_best_cluster": best, "prototype_iou_with_verified": iou(best["bbox"], vb) if best else 0.0,
                    "prototype_tiny_sliver_rule_would_flag": bool(best and best["w"] * best["h"] < 9000 and best["w"] < 140),
                })

    db_after = formal_db_fingerprint()
    hits = [t for t in phrases if t["on_matched_page"]]
    longest = max(hits, key=lambda t: t["len"]) if hits else None

    trace = {
        "evidence_type": "new_isolated_readonly_trace",
        "original_evidence_status": "original_evidence_unavailable",
        "note": "Re-runs the real detector functions on the authoritative PDF with rows captured by the previous isolated dry-run "
                "(reports/gh_math2_unit5_stage1_repair/dry_run_raw.json). Not the original task's evidence. No DB/asset/notes writes.",
        "source_pdf": PDF.relative_to(ROOT).as_posix(), "pdf_sha256": PDF_SHA,
        "reproduces_recorded_pipeline_result": reproduced,
        "recorded": {"visual_bbox": rec_row["visual_bbox"], "visual_reason": rec_row["visual_reason"], "status": rec_row["status"]},
        "steps": [
            {"step": "1_pdf_page_index", "function": "core/textbook_pdf_visual.py::build_page_index",
             "result": {"page": PAGE, "size_pt": r([pw, ph]), "drawings_ge_80pt2": len(page["drawings"]),
                        "small_drawings_lt_80pt2": len(page["small_drawings"]), "embedded_images": len(page["images"]),
                        "figure": {"semicircle_single_path": r(semicircle["bbox"]), "dots_and_label_glyph_paths": len(figure_ink),
                                   "full_figure_ink_union": r(ink_union)},
                        "note": "Figure is vector-only: one 79x39.7pt path for arc+diameter; 10 dots and the A1-A4/B1-B6 labels are outlined glyph paths (<80pt2) in small_drawings, not text-layer words."}},
            {"step": "2_anchor_to_pdf_page_and_y", "function": "match_questions_to_pdf L362-L409 + find_phrase_y",
             "result": {"anchor_id": TARGET_ANCHOR, "source_order": row.get("source_order"), "page": row["pdf_match"]["page"],
                        "page_verdict": "CORRECT (page 16)", "match_method": row["match_method"], "match_score": row["match_score"],
                        "question_start_y_used": r(row["pdf_match"]["question_start_y"]),
                        "chosen_phrase(longest hit)": longest, "phrase_table": phrases,
                        "question_number_glyph_12_y": r(float(label_word[1])) if label_word else None,
                        "earliest_hit_y": r(min(t["y_on_matched_page"] for t in hits)) if hits else None,
                        "text_layer_first_sentence": "如圖AAAA1234為半圓直徑上的4個點BBB126f為半圓周上的6個點",
                        "docx_first_sentence_normalized": "如圖A1A2A3A4為半圓直徑上的4個點B1B2ldot...",
                        "y_verdict": "WRONG: y is taken from the LONGEST hit, which is sub-question (2) at y=678.2. First-sentence phrases miss because the PDF text layer emits base letters then subscripts (AAAA1234) and maps the ellipsis to 'f', while DOCX normalizes to A1A2A3A4 / ldot."}},
            {"step": "3_question_region", "function": "assign_question_regions (y0-8 .. next question or page_height-36)",
             "result": {"question_bbox": r(qb), "next_question_y": next_q_y,
                        "verdict": "Region top 670.2 is below the figure (y 588-652): the figure is excluded before detection starts. Last on page, so bottom=757.7 reaches into the footer band (top 736.6)."}},
            {"step": "4_candidate_filtering", "function": "classify_and_detect_visuals L806-L895", "objects": objects,
             "verdict": "Semicircle does not intersect the region at all. Footer band (non-blended, leaves the page box) intersects and passes the strong-cue soft filter; it becomes the sole candidate."},
            {"step": "5_pick_and_assemble", "function": "_pick_compact_diagram_bbox -> assemble_visual_group_bbox",
             "result": {"graph_draws_primary": "empty (footer w=1235.9 > 0.85W)", "graph_draws_fallback": "[footer_band]",
                        "assembled_bbox": r(V.assemble_visual_group_bbox(list(footer["bbox"]), page, limit_bbox=group_limit)),
                        "group_limit": r(group_limit)}},
            {"step": "6_region_clip", "function": "classify_and_detect_visuals L1077-L1113",
             "result": {"visual_bbox": r(row["visual_bbox"], 2),
                        "size_pt": r([row["visual_bbox"][2] - row["visual_bbox"][0], row["visual_bbox"][3] - row["visual_bbox"][1]]),
                        "verdict": "Footer clipped to a 609x9pt strip: no figure ink."}},
            {"step": "7_acceptance_gate", "function": "core/textbook_pdf_visual_acceptance.py::evaluate_visual_acceptance",
             "result": {"visual_status": acc_actual["visual_status"], "reasons": acc_actual["visual_review_reasons"],
                        "verdict": "Gate correctly refused the wrong strip (vh<40; aspect 67 full-width). The 'low confidence' is about the shape of a wrong candidate, not the 0.99 text match."}},
            {"step": "8_classification", "function": "classify_and_detect_visuals L1150-L1166",
             "result": {"visual_classification": row["visual_classification"], "should_mount": row["should_mount"], "visual_reason": row["visual_reason"]}},
            {"step": "9_crop_and_asset", "function": "enrich_textbook_examples_with_pdf_visuals L1590-L1594",
             "result": {"crop_pdf_bbox_called": False, "temp_or_final_png": "NOT_GENERATED", "image_assets": [],
                        "verdict": "classification=skipped_low_confidence -> `continue` before cropping; the pipeline never produced any image for this row."}},
            {"step": "10_visual_status", "function": "core/textbook_processor.py::classify_general_high_visual_status L637-L654",
             "result": {"pdf_visual_status": "VISUAL_REQUIRED_MISSING", "why": "no image_assets and strong cue 如圖 in DOCX stem"}},
            {"step": "11_stage1_gate", "function": "core/textbook_stage1_gate.py L110-L115",
             "result": {"blocker": "required_figure_missing", "verdict": "Gate is correct given the upstream miss."}},
        ],
        "counterfactuals_in_memory_only": {
            "CF_F_drop_page_furniture_only": {**summarize(cf_f), "side_effects_all_37": side_effects(cf_f_rows)},
            "REJECTED_ALT_earliest_hit_stem_start": {"start_y_changes_all_37": earliest_changes,
                                                     "verdict": "Unsafe: 2 of 4 shifts land in another block (例1, 基礎題5)."},
            "CF_A_question_number_marker_start_only": {**summarize(cf_a), "start_y_changes_all_37": cf_a_changes,
                                                       "side_effects_all_37": side_effects(cf_a_rows)},
            "CF_B_marker_start_plus_drop_furniture": {**summarize(cf_b), "side_effects_all_37": side_effects(cf_b_rows)},
            "CF_C_B_plus_prototype_ink_cluster_candidate": {
                "clusters_in_question_band": clusters, "picked": proto,
                "acceptance_with_current_gate": acc_proto["visual_status"], "reasons": acc_proto["visual_review_reasons"],
                "ink_paths_cut_by_crop": ink_cut_by_crop(pages_nf[PAGE - 1], proto["bbox"]) if proto else None,
                "iou_with_teacher_proposal": iou(proto["bbox"], TEACHER_BBOX) if proto else 0.0,
                "inside_teacher_proposal": bool(proto and V._bbox_inside(TEACHER_BBOX, proto["bbox"])),
                "contains_all_figure_ink": bool(proto and V._bbox_inside(proto["bbox"], ink_union, tol=0.6))},
            "CF_C2_B_plus_real_assembler_seeded_with_semicircle": {
                "assembled_bbox": r(semi_group), "acceptance_with_current_gate": acc_semi["visual_status"],
                "reasons": acc_semi["visual_review_reasons"],
                "ink_paths_cut_by_crop": ink_cut_by_crop(pages_nf[PAGE - 1], semi_group),
                "contains_all_figure_ink": V._bbox_inside(semi_group, ink_union, tol=0.6),
                "why_incomplete": "glyph pass is single-shot with 6pt gap from the pre-glyph group; B6 subscript sits 6.7pt from the arc"},
        },
        "systemic_scan": {
            "unit5_rows_where_longest_hit_is_ge_20pt_below_earliest_hit": shift_rows,
            "general_pdfs_footer_furniture": systemic_pdfs,
            "manually_verified_regions_units_3_4": manual_regions},
        "artifacts": {
            "SOURCE_PDF_IMAGE": "A_source_pdf_page16.png",
            "PIPELINE_CANDIDATE": ["B_pipeline_candidate_overlay_page16.png", "B_pipeline_candidate_crop_render.png (rendered by this investigation from the pipeline bbox; the pipeline itself wrote no file)"],
            "PIPELINE_GENERATED_ASSET": "NOT_GENERATED",
            "ISOLATED_RENDER_PREVIEW": "NOT_PERFORMED (no isolated association authorized this round)",
            "PRODUCTION_DB_ASSET": "NONE",
            "COUNTERFACTUAL_ONLY_NOT_PIPELINE_OUTPUT": ["X_counterfactual_prototype_cluster_crop.png"],
        },
        "formal_db": {"before": db_before, "after": db_after,
                      "zero_change": db_before["textbook_examples_content_sha256"] == db_after["textbook_examples_content_sha256"]},
    }
    (OUT / "visual_pipeline_trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    cf = trace["counterfactuals_in_memory_only"]
    print(json.dumps({
        "reproduced": reproduced, "actual": acc_actual["visual_review_reasons"],
        "CF_F": {k: cf["CF_F_drop_page_furniture_only"][k] for k in ("visual_bbox", "visual_reason")},
        "CF_A": {k: cf["CF_A_question_number_marker_start_only"][k] for k in ("question_bbox", "visual_bbox", "visual_reason")},
        "CF_A_changes": cf_a_changes, "CF_A_side": cf["CF_A_question_number_marker_start_only"]["side_effects_all_37"]["rows_changed"],
        "CF_B": {k: cf["CF_B_marker_start_plus_drop_furniture"][k] for k in ("question_bbox", "visual_bbox", "visual_reason")},
        "CF_B_side": cf["CF_B_marker_start_plus_drop_furniture"]["side_effects_all_37"]["rows_changed"],
        "CF_C": {k: cf["CF_C_B_plus_prototype_ink_cluster_candidate"][k] for k in ("picked", "acceptance_with_current_gate", "reasons", "ink_paths_cut_by_crop", "inside_teacher_proposal", "contains_all_figure_ink")},
        "CF_C2": cf["CF_C2_B_plus_real_assembler_seeded_with_semicircle"],
        "shift_rows": shift_rows,
        "manual": [(m["chapter"], m["label"], m["verified_size_pt"], m["largest_single_path"], m["largest_path_passes_soft[area>=2500,w>=40,h>=40]"], m["prototype_iou_with_verified"], m["prototype_tiny_sliver_rule_would_flag"]) for m in manual_regions],
        "footer": [(s["pdf"].rsplit("/", 1)[-1], s["pages"], s["pages_where_footer_furniture_enters_last_question_region_and_passes_soft_filter"]) for s in systemic_pdfs],
        "db_zero": trace["formal_db"]["zero_change"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
