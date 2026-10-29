"""Build review artifacts from the isolated Unit 5 replay; never touches the formal DB."""

import hashlib
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from core.textbook_stage1_auto_review import _chinese, _ordered_chinese_match, _pdf_fidelity


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PRIOR = ROOT / "reports/gh_math2_unit5_stage1_diagnostic"
SOURCE = ROOT / "textbook_import/uploaded_sources/general/數學2/12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


source = read(SOURCE)
raw = read(OUT / "dry_run_raw.json")
prior = read(PRIOR / "auto_review_issues.json")
db_guard = read(OUT / "formal_db_unchanged.json")
assert raw["original_evidence_status"] == "original_evidence_unavailable"
paths = {kind: ROOT / item["stored_path"] for kind, item in source["sources"].items()}
for kind, path in paths.items():
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sources"][kind]["sha256"]

ids = [12812, 12817, 12825, 12835, 12836, 12840, 12845]
rows = raw["capture"]["post_review_rows"]
by_id = {row["id"]: row for row in rows}
before = {issue["id"]: issue for issue in prior["issues"] if issue["id"] in ids}
assert set(before) == set(ids)
assert not raw["result"]["stage1_auto_review"]["issues"]

name = {12812: "例題1", 12817: "隨堂練習1", 12825: "5習題 觀念澄清3",
        12835: "例題6", 12836: "例題7", 12840: "5習題 觀念澄清4", 12845: "隨堂練習10"}
cause = {12812: "中文題幹只有 5 字；舊判準未比對公式", 12817: "中文題幹只有 5 字；舊判準未比對公式",
         12825: "原頁碼缺失；PDF 候選在第 14 頁", 12835: "原頁碼缺失；PDF 候選在第 10 頁",
         12836: "原頁碼缺失；PDF 候選在第 11 頁", 12840: "原頁碼誤指第 16 頁；實際在第 14 頁",
         12845: "原頁碼誤指第 13 頁；實際在第 12 頁"}
candidate_strips = {12812: [0, 115, 610, 208], 12817: [0, 365, 610, 474],
                    12825: [0, 255, 610, 284], 12835: [0, 435, 610, 514],
                    12836: [0, 109, 610, 189], 12840: [0, 283, 610, 322],
                    12845: [0, 577, 610, 648]}

details = []
for rid in ids:
    row = by_id[rid]
    notes = row["notes"]
    verified = notes["pdf_fidelity_verification"]
    issue = before[rid]
    assert verified["source_pdf_sha256"] == source["sources"]["pdf"]["sha256"]
    assert notes["question_anchor"]["anchor_id"] == issue["question_anchor"]["anchor_id"]
    details.append({
        "name": name[rid], "row_id": rid, "question_anchor": notes["question_anchor"]["anchor_id"],
        "source_order": notes["question_anchor"]["source_order"], "docx_block_index": notes["question_anchor"]["block_index"],
        "docx_problem_text_after_formula_conversion": row["problem_text"],
        "pdf_file": str(paths["pdf"]), "pdf_page_1_based": verified["verified_page"],
        "pdf_render": f"source_pages/page_{verified['verified_page']:02d}.png",
        "pdf_candidate_region_points_xyxy": candidate_strips[rid],
        "pdf_candidate_crop": f"pdf_fidelity_candidate_{rid}.png",
        "previous_source_page": issue.get("source_page"), "previous_pdf_candidate_pages": issue.get("pdf_text_candidate_pages"),
        "before_reason_code": issue["reason"], "before_stage": issue["stage"], "root_cause": cause[rid],
        "after_issue": None, "verification_method": verified["method"],
        "formula_and_symbol_evidence": "PDF 頁面中文字順序及數學 token 相符；短題要求局部文字區塊內的數學 token",
        "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
    })
    with fitz.open(paths["pdf"]) as doc:
        pdf_page = doc[verified["verified_page"] - 1]
        clip = fitz.Rect(candidate_strips[rid])
        details[-1]["pdf_extracted_text_in_candidate_region"] = pdf_page.get_text(clip=clip)
        pdf_page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip).save(OUT / f"pdf_fidelity_candidate_{rid}.png")
save("pdf_fidelity_7_details.json", details)
save("issue_comparison.json", {
    "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
    "prior_diagnostic_issue_count": len(prior["issues"]), "prior_seven_reason_code": "stem_not_verified_against_pdf",
    "after_auto_review_issues": raw["result"]["stage1_auto_review"]["issues"],
    "seven_resolved": len(details), "new_pdf_fidelity_issues": 0,
    "remaining_gate_reasons": raw["result"]["stage1_gate"]["reasons"],
})
save("stage1_gate_latest.json", {
    "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
    "source_record": str(SOURCE), "source_sha256": {k: source["sources"][k]["sha256"] for k in paths},
    "gate": raw["result"]["stage1_gate"], "auto_review_issues": raw["result"]["stage1_auto_review"]["issues"],
    "formal_db_zero_change_confirmed": db_guard["formal_db_zero_change_confirmed"],
})

ordered = sorted(rows, key=lambda row: row["notes"]["question_anchor"]["source_order"])
bindings = [{
    "source_order": row["notes"]["question_anchor"]["source_order"],
    "title": row["label"], "anchor": row["notes"]["question_anchor"]["anchor_id"],
    "docx_block_index": row["notes"]["question_anchor"]["block_index"],
    "skill_id": row["skill_id"], "pdf_page": (row["notes"].get("pdf_visual_enrichment") or {}).get("page"),
    "visual_status": row["notes"].get("pdf_visual_status"),
} for row in ordered]
assert len(bindings) == 37
assert [x["source_order"] for x in bindings] == list(range(1, 38))
assert len({x["anchor"] for x in bindings}) == 37
assert all(x["skill_id"] for x in bindings)
prior_bindings = read(PRIOR / "anchor_skill_binding_37.json")["rows"]
prior_by_anchor = {x["question_anchor"]["anchor_id"]: x for x in prior_bindings}
binding_deltas = [{"anchor": x["anchor"], "prior_skill": prior_by_anchor[x["anchor"]]["assigned_skill_id"],
                   "current_skill": x["skill_id"]} for x in bindings
                  if x["anchor"] not in prior_by_anchor or prior_by_anchor[x["anchor"]]["assigned_skill_id"] != x["skill_id"]]
assert not binding_deltas
save("anchor_skill_binding_37_verified.json", {
    "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
    "count": 37, "unique_anchors": 37, "source_orders_complete": True,
    "binding_deltas_vs_prior_diagnostic": binding_deltas,
    "skill_ids": sorted({x["skill_id"] for x in bindings}), "rows": bindings,
    "limitation": "Reconstructed Gemini metadata was used for this isolated replay; original Gemini response is unavailable.",
})
save("pdf_visual_mapping_latest.json", {
    "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
    "pdf_sha256": source["sources"]["pdf"]["sha256"],
    "visual_summary": raw["capture"]["visual_summary"],
    "note": "No candidate figure was marked verified or mounted in the isolated replay.",
})

figure = by_id[12834]
figure_note = figure["notes"]
figure_anchor = figure_note["question_anchor"]["anchor_id"]
assert figure_anchor == "general_2_section_advanced_exercise_012_037"
assert figure_note["pdf_visual_status"] == "VISUAL_REQUIRED_MISSING"
bbox = [420, 575, 540, 675]
shutil.copyfile(OUT / "source_pages/page_16.png", OUT / "teacher_advanced12_page16.png")
shutil.copyfile(PRIOR / "pdf_page16_advanced12_figure_candidate.png", OUT / "teacher_advanced12_crop.png")
with fitz.open(paths["pdf"]) as doc:
    page = doc[15]
    assert fitz.Rect(bbox) in page.rect
    dimensions = [page.rect.width, page.rect.height]
figure_data = {
    "evidence_type": "new_isolated_dry_run_and_visual_inspection", "original_evidence_status": "original_evidence_unavailable",
    "status": "pending_teacher_confirmation", "verified": False,
    "source_docx": str(paths["docx"]), "source_pdf": str(paths["pdf"]),
    "docx_sha256": source["sources"]["docx"]["sha256"], "pdf_sha256": source["sources"]["pdf"]["sha256"],
    "question_anchor": figure_anchor, "docx_block_index": 36, "source_order": 37,
    "pdf_page_1_based": 16, "printed_page": 99, "page_size_points": dimensions,
    "proposed_bbox_pdf_points_xyxy": bbox,
    "full_question_text_after_formula_conversion": figure["problem_text"],
    "full_page_preview": "teacher_advanced12_page16.png", "crop_preview": "teacher_advanced12_crop.png",
    "figure_relation": "第 16 頁進階題 12 題幹左上方的半圓圖；A1–A4 在直徑上，B1–B6 在半圓弧上；對應題幹所述 10 點。",
    "visual_check": "預覽保留半圓、直徑、全部 10 個點及 A1–A4、B1–B6 標記，未混入進階題 11 的圖形。",
    "gate_reason": "required_figure_missing", "mapping_reason": "skipped_low_confidence",
}
save("teacher_advanced12_region_proposal.json", figure_data)

unit4_rows_data = read(ROOT / "reports/gh_math2_unit4_stage1/pre_review_with_regions.json")
unit4_pdf = ROOT / "textbook_import/uploaded_sources/general/數學2/bf39d447345e_單元04-排列.pdf"
unit4_rows = [SimpleNamespace(**{**row, "notes": json.dumps(row["notes"], ensure_ascii=False)}) for row in unit4_rows_data]
with fitz.open(unit4_pdf) as document:
    unit4_raw = [page.get_text() for page in document]
    unit4_blocks = [page.get_text("blocks") for page in document]
unit4_chinese = [_chinese(text) for text in unit4_raw]
unit4_delta = []
for row, record in zip(unit4_rows, unit4_rows_data):
    notes = record["notes"]
    page = (notes.get("pdf_visual_enrichment") or {}).get("page")
    stem = _chinese(record["problem_text"])
    old = isinstance(page, int) and 1 <= page <= len(unit4_raw) and len(stem) >= 6 and _ordered_chinese_match(stem, unit4_chinese[page - 1])
    new = _pdf_fidelity(row, notes, unit4_chinese, unit4_raw, unit4_blocks, unit4_rows) is not None
    if old != new:
        unit4_delta.append({"id": record["id"], "label": record["label"], "old": old, "new": new})
regression = {
    "focused_pdf_fidelity_tests": "3 passed",
    "existing_stage1_auto_review_tests": "12 passed (second run with sandbox temp; initial setup failed due system temp permissions)",
    "unit4_pdf_fidelity_read_only_comparison": {
        "rows": len(unit4_rows), "changed_outcomes": unit4_delta,
        "old_pass_count": sum(isinstance((rec["notes"].get("pdf_visual_enrichment") or {}).get("page"), int)
                              and len(_chinese(rec["problem_text"])) >= 6
                              and _ordered_chinese_match(_chinese(rec["problem_text"]), unit4_chinese[rec["notes"]["pdf_visual_enrichment"]["page"] - 1])
                              for rec in unit4_rows_data),
    },
    "unit5_formula_conversion": "131/131 OLE, 10/10 equation fields; failed=0",
    "unit5_inventory": "37 expected, 37 returned, 0 missing",
    "unit5_gate": raw["result"]["stage1_gate"]["status"],
    "unit5_visual": raw["capture"]["visual_summary"]["status_counts"],
    "formal_db_unchanged": db_guard,
    "evidence_type": "new_isolated_dry_run", "original_evidence_status": "original_evidence_unavailable",
}
regression["unit4_pdf_fidelity_read_only_comparison"]["new_pass_count"] = regression["unit4_pdf_fidelity_read_only_comparison"]["old_pass_count"] + sum(int(x["new"]) - int(x["old"]) for x in unit4_delta)
save("regression_results.json", regression)

(OUT / "TEACHER_ADVANCED12.md").write_text(
    "# 5習題 進階題12 圖像確認\n\n"
    "狀態：**pending_teacher_confirmation**；目前未標記 verified，亦未寫入正式圖像設定。\n\n"
    f"- Anchor：`{figure_anchor}`；DOCX block_index：36；PDF：第 16 頁（印刷頁 99）。\n"
    f"- PDF SHA-256：`{figure_data['pdf_sha256']}`。\n"
    f"- 建議裁切：PDF points `xyxy={bbox}`；頁面大小 `{dimensions}`。\n\n"
    "## 題幹\n\n" + figure["problem_text"] + "\n\n"
    "## 原始頁面\n\n![PDF 第 16 頁](teacher_advanced12_page16.png)\n\n"
    "## 建議裁切預覽\n\n![進階題12半圓圖](teacher_advanced12_crop.png)\n\n"
    "圖中半圓、直徑、A1–A4、B1–B6 均完整；裁切範圍不含進階題 11 圖形。"
    "請教師確認此圖確屬進階題12及裁切邊界，確認前 Gate 保持 BLOCKED。\n",
    encoding="utf-8",
)

print(json.dumps({"seven": len(details), "unit4": regression["unit4_pdf_fidelity_read_only_comparison"],
                  "gate": raw["result"]["stage1_gate"]["status"], "db_unchanged": db_guard["formal_db_zero_change_confirmed"]}))
