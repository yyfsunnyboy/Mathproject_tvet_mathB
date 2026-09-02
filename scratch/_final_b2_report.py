# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.textbook_mathtype_converter import (
    convert_reference_b2_1_1,
    pick_representative_formulas,
)


def phase1_like(path: Path) -> list[str]:
    doc = Document(str(path))
    lines: list[str] = []
    for block in doc.element.body.iterchildren():
        if block.tag.endswith("}p"):
            t = Paragraph(block, doc).text.strip()
            if t:
                lines.append(t)
        elif block.tag.endswith("}tbl"):
            tbl = Table(block, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        t = para.text.strip()
                        if t:
                            lines.append(t)
    return lines


def main() -> None:
    report = convert_reference_b2_1_1()
    reps = pick_representative_formulas(report, 10)
    all_ok = [f for f in report["formulas"] if f["status"] == "ok"]
    seen = {r["formula_index"] for r in reps}
    for cat, pat in [("sqrt", r"\\sqrt"), ("trig", r"\\(?:sin|cos|tan)")]:
        for f in all_ok:
            if f["formula_index"] in seen:
                continue
            if re.search(pat, f.get("latex") or ""):
                reps.append(
                    {
                        "formula_index": f["formula_index"],
                        "category": cat,
                        "latex": f["latex"],
                        "location": f.get("location"),
                    }
                )
                seen.add(f["formula_index"])
                break

    lines = phase1_like(Path(report["output"]))
    inline_count = sum(ln.count(r"\(") for ln in lines)
    failed = [f for f in report["formulas"] if f["status"] != "ok"]
    out = {
        "mathtype_ole": report["mathtype_ole"],
        "equation_native_ok": report["equation_native_ok"],
        "converted_ok": report["converted_ok"],
        "converted_failed": report["converted_failed"],
        "failed_reasons": [
            {
                "formula_index": f["formula_index"],
                "error": f.get("error"),
                "embedding_path": f.get("embedding_path"),
            }
            for f in failed
        ],
        "eq_fields": report["eq_fields"],
        "eq_converted_ok": report["eq_converted_ok"],
        "output": report["output"],
        "original_unchanged": report["original_unchanged"],
        "phase1_lines": len(lines),
        "phase1_inline_latex_markers": inline_count,
        "phase1_opened_ok": True,
        "representatives": [
            {
                "formula_index": r["formula_index"],
                "category": r.get("category"),
                "latex": r.get("latex"),
                "location": r.get("location"),
            }
            for r in reps
        ],
        "phase1_sample_lines": [ln for ln in lines if r"\(" in ln][:12],
    }
    Path("scratch/b2_1_1_convert_report.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({k: out[k] for k in out if k not in {"representatives", "phase1_sample_lines"}}, ensure_ascii=False, indent=2))
    print("---REPS---")
    for r in out["representatives"]:
        loc = r.get("location") or {}
        print(
            f"#{r['formula_index']} [{r.get('category')}] "
            f"p={loc.get('paragraph_index')} table={loc.get('table_index')} "
            f"cell=({loc.get('row')},{loc.get('col')}) => {r['latex']}"
        )


if __name__ == "__main__":
    main()
