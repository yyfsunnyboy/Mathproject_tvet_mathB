"""Merge scan + manual PDF page review + isolated HTTP/browser result into the Unit 5 visual inventory."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
scan = json.loads((HERE / "scan_raw.json").read_text(encoding="utf-8"))
http = json.loads((HERE / "isolated_http_result.json").read_text(encoding="utf-8"))["summary"]

FIGURE_ANCHOR = "general_2_section_advanced_exercise_012_037"

# Manual review of every rendered page (pages/page_XX.png) against the PDF.
PAGE_NOTES = {
    "general_2_section_example_001_001": "p3 版面有裝飾插圖，題幹未引用，不影響作答",
    "general_2_section_example_002_003": "p3 版面有裝飾插圖（手球），題幹未引用",
    "general_2_section_in_class_practice_003_006": "p5 版面有裝飾插圖，題幹未引用",
    "general_2_section_example_005_009": "p7–8 袋中取球示意圖位於「解」內，屬解說，不屬題幹",
    "general_2_section_example_007_014": "p11 版面有裝飾插圖，題幹未引用",
    "general_2_section_example_010_020": "p13 版面有裝飾插圖，題幹未引用",
    FIGURE_ANCHOR: "p16 半圓上 A1–A4、B1–B6 共 10 點；第(1)小題須依圖判讀共線點，缺圖無法作答",
}

rows = []
for r in scan["isolated_rows"]:
    needs = r["anchor"] == FIGURE_ANCHOR
    title = r["title"].split(" [")[0]
    note = PAGE_NOTES.get(r["anchor"], "")
    rows.append({
        "id": r["id"],
        "title": title,
        "anchor": r["anchor"],
        "skill_id": r["skill_id"],
        "pdf_page": r["pdf_page"],
        "stem_cues": r["cues"],
        "pdf_has_figure_in_stem": needs,
        "page_decoration_only": bool(note) and not needs,
        "figure_required_to_answer": needs,
        "formal_db_has_image": False,
        "formal_db_row": 1440 if needs else None,
        "isolated_image_assets": r["image_assets"],
        "student_page_display": "顯示半圓圖（真實學生頁）" if needs else "無圖（正確）",
        "action": "固定圖片資產（verified region，待教師確認裁切）＋固定題庫 graded multi_part" if needs else "無需處理",
        "note": note,
    })

assert sum(r["isolated_image_assets"] for r in rows) == 1
assert http["figure_required"] == http["rows_with_images"] == [12834] and not http["problems"]

out = {
    "pdf_sha256": scan["pdf_sha256"],
    "docx_sha256": scan["docx_sha256"],
    "rows_total": len(rows),
    "figure_required": [r["id"] for r in rows if r["figure_required_to_answer"]],
    "decoration_only": [r["id"] for r in rows if r["page_decoration_only"]],
    "formal_legacy_rows": scan["formal_rows"],
    "docx_non_ole_pictures": scan["docx_pictures"],
    "docx_ole_formula_objects": scan["docx_ole_objects"],
    "rows": rows,
}
(HERE / "unit5_visual_inventory.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

yn = lambda b: "有" if b else "無"
lines = [
    "# 普高數學2 Unit 5 圖片盤點表（37 題）",
    "",
    f"- PDF SHA-256：`{scan['pdf_sha256']}`",
    f"- DOCX SHA-256：`{scan['docx_sha256']}`",
    "- 「原始PDF有圖」只計題幹作答所需的圖；版面裝飾插圖與「解」內示意圖列於備註。",
    "- 「正式DB有圖」以正式 DB 現況為準：正式 DB 只有舊版 28 題（1413–1440），全部沒有圖片資產。",
    "- 「學生端顯示」以隔離 SQLite 複本＋真實學生練習頁驗證。",
    "",
    "| ID | 題目 | 頁 | 原始PDF有圖 | 正式DB有圖 | 學生端顯示 | 處理方式 | 備註 |",
    "|---|---|---|---|---|---|---|---|",
]
for r in sorted(rows, key=lambda x: x["anchor"].rsplit("_", 1)[-1]):
    lines.append(
        f"| {r['id']} | {r['title']} | {r['pdf_page']} | {yn(r['pdf_has_figure_in_stem'])} | "
        f"{'無（舊列 1440 缺圖）' if r['figure_required_to_answer'] else '無（不需要）'} | "
        f"{r['student_page_display']} | {r['action']} | {r['note']} |"
    )
lines += [
    "",
    "## 正式 DB 舊版 28 題對照",
    "",
    "| ID | Skill | 標題 | 題幹提示詞 | 圖片資產 |",
    "|---|---|---|---|---|",
]
for f in scan["formal_rows"]:
    lines.append(f"| {f['id']} | {f['skill_id']} | {f['title']} | {'、'.join(f['cues']) or '—'} | {f['image_assets']} |")
(HERE / "unit5_visual_inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("rows", len(rows), "figure_required", out["figure_required"], "decoration_only", out["decoration_only"])
