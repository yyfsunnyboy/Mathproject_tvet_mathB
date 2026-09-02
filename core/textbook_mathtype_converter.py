# -*- coding: utf-8 -*-
"""
Deterministic MathType / EQ → LaTeX DOCX converter for V3.

Responsibility:
  original MathType DOCX → compatibility *_Latex.docx

Does NOT:
  - call Word / MathType / COM / OCR / Gemini
  - slice questions or write DB
"""

from __future__ import annotations

import io
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree

from core.mtef import equation_native_to_latex, mtef_bytes_to_latex
from core.textbook_importer_v3_docx import (
    NS,
    REL_NS,
    W_NS,
    _load_relationship_maps,
    _local_name,
    _resolve_relationship_target,
    find_reference_docx_in_storage,
    parse_docx_structure,
)

try:
    import olefile
except ImportError:  # pragma: no cover
    olefile = None

MATH_FAIL_PREFIX = "[MATH_PARSE_FAILED_"
EQ_FAIL_PREFIX = "[EQ_PARSE_FAILED_"


def wrap_latex_for_v2(latex: str) -> str:
    """
    Match existing converted_docx / V2 extractor expectations.

    Prefer \\(...\\); also accept $...$ readers via the same content.
    """
    text = (latex or "").strip()
    if not text:
        return ""
    if text.startswith("$") and text.endswith("$") and text.count("$") >= 2:
        text = text[1:-1].strip()
    if text.startswith(r"\(") and text.endswith(r"\)"):
        inner = text[2:-2].strip()
        return rf"\({inner}\)" if inner else ""
    if text.startswith(r"\[") and text.endswith(r"\]"):
        inner = text[2:-2].strip()
        return rf"\[{inner}\]" if inner else ""
    # Collapse excessive internal spaces from MTEF renderer.
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    return rf"\({text}\)"


def convert_eq_instruction_to_latex(instruction: str) -> tuple[str, str | None]:
    """
    Convert common Word EQ field instructions to LaTeX.

    Supports a practical subset used by vocational textbooks:
      EQ \\f(a,b)  → fraction
      EQ \\r(...)  → root
      EQ \\s\\up(...) / \\s\\do(...) → super/subscript-ish
    """
    raw = (instruction or "").strip()
    if not raw:
        return "", "empty_eq_instruction"
    body = re.sub(r"^\s*EQ\s*", "", raw, flags=re.IGNORECASE).strip()
    if not body:
        return "", "empty_eq_body"

    def _split_args(argstr: str) -> list[str]:
        parts: list[str] = []
        depth = 0
        buf: list[str] = []
        for ch in argstr:
            if ch == "," and depth == 0:
                parts.append("".join(buf).strip())
                buf = []
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(0, depth - 1)
            buf.append(ch)
        parts.append("".join(buf).strip())
        return [p for p in parts if p != ""]

    def _convert_piece(expr: str) -> str:
        expr = expr.strip()
        if not expr:
            return ""
        # Nested EQ-like snippets without leading EQ.
        m_frac = re.match(r"^\\f\((.*)\)\s*$", expr, flags=re.DOTALL)
        if m_frac:
            args = _split_args(m_frac.group(1))
            if len(args) >= 2:
                return r"\frac{%s}{%s}" % (_convert_piece(args[0]), _convert_piece(args[1]))
        m_root = re.match(r"^\\r(?:\((.*)\))?\s*$", expr, flags=re.DOTALL)
        if m_root:
            args = _split_args(m_root.group(1) or "")
            if len(args) == 1:
                return r"\sqrt{%s}" % _convert_piece(args[0])
            if len(args) >= 2:
                return r"\sqrt[%s]{%s}" % (_convert_piece(args[0]), _convert_piece(args[1]))
        m_sup = re.match(r"^\\s\\up\((.*)\)\s*$", expr, flags=re.DOTALL | re.IGNORECASE)
        if m_sup:
            return "^{%s}" % _convert_piece(m_sup.group(1))
        m_sub = re.match(r"^\\s\\do\((.*)\)\s*$", expr, flags=re.DOTALL | re.IGNORECASE)
        if m_sub:
            return "_{%s}" % _convert_piece(m_sub.group(1))
        # Plain text / numbers / operators
        return expr

    try:
        latex = _convert_piece(body)
        if not latex:
            return "", "eq_unhandled"
        return latex, None
    except Exception as exc:  # pragma: no cover - defensive
        return "", f"eq_convert_error:{exc}"


def extract_equation_native(ole_bytes: bytes) -> tuple[bytes | None, str | None]:
    if olefile is None:
        return None, "olefile_missing"
    try:
        ole = olefile.OleFileIO(io.BytesIO(ole_bytes))
    except Exception as exc:
        return None, f"ole_open_failed:{exc}"
    try:
        for entry in ole.listdir():
            if entry[-1] == "Equation Native":
                return ole.openstream(entry).read(), None
        return None, "equation_native_missing"
    finally:
        try:
            ole.close()
        except Exception:
            pass


def _make_latex_run(latex_text: str) -> etree._Element:
    run = etree.Element(f"{{{W_NS}}}r")
    text = etree.SubElement(run, f"{{{W_NS}}}t")
    text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text.text = latex_text
    return run


def _replace_element_with_run(element: etree._Element, latex_text: str) -> None:
    """Replace an OLE object or similar node with a LaTeX text run in-place."""
    parent = element.getparent()
    if parent is None:
        return
    run = _make_latex_run(latex_text)
    # If parent is already w:r, replace object child with w:t; else replace element with run.
    if _local_name(parent.tag) == "r":
        # Remove non-property children and append text.
        for child in list(parent):
            if _local_name(child.tag) not in {"rPr"}:
                parent.remove(child)
        parent.append(run.find(f"{{{W_NS}}}t"))
    else:
        index = list(parent).index(element)
        parent.remove(element)
        parent.insert(index, run)


def _collect_eq_field_run_groups(paragraph: etree._Element) -> list[dict[str, Any]]:
    """Return EQ field run spans: begin..end inclusive run elements."""
    runs = [el for el in paragraph.iter(f"{{{W_NS}}}r")]
    groups: list[dict[str, Any]] = []
    in_field = False
    after_sep = False
    instr: list[str] = []
    result: list[str] = []
    start_idx: int | None = None
    end_idx: int | None = None

    for idx, run in enumerate(runs):
        for fld in run.findall(f"{{{W_NS}}}fldChar"):
            fld_type = fld.get(f"{{{W_NS}}}fldCharType")
            if fld_type == "begin":
                in_field = True
                after_sep = False
                instr = []
                result = []
                start_idx = idx
                end_idx = None
            elif fld_type == "separate" and in_field:
                after_sep = True
            elif fld_type == "end" and in_field:
                end_idx = idx
                instruction = "".join(instr).strip()
                if re.match(r"^\s*EQ\b", instruction, flags=re.IGNORECASE):
                    groups.append(
                        {
                            "start": start_idx,
                            "end": end_idx,
                            "runs": runs[start_idx : end_idx + 1],
                            "instruction": instruction,
                            "display_text": "".join(result).strip(),
                        }
                    )
                in_field = False
                after_sep = False
        if in_field:
            for node in run.findall(f"{{{W_NS}}}instrText"):
                if node.text:
                    instr.append(node.text)
            if after_sep:
                for node in run.findall(f"{{{W_NS}}}t"):
                    if node.text:
                        result.append(node.text)
    return groups


def convert_docx_mathtype_to_latex_docx(
    source_docx: str | Path,
    output_docx: str | Path | None = None,
) -> dict[str, Any]:
    """
    Copy source DOCX and replace MathType OLE + EQ fields with LaTeX text runs.

    Returns conversion report dict.
    """
    source_path = Path(source_docx)
    if not source_path.is_file():
        raise FileNotFoundError(str(source_path))

    source_bytes = source_path.read_bytes()
    if output_docx is None:
        output_path = source_path.with_name(f"{source_path.stem}_Latex.docx")
    else:
        output_path = Path(output_docx)

    # Never mutate the original file.
    if output_path.resolve() == source_path.resolve():
        raise ValueError("output path must differ from source path")

    parsed = parse_docx_structure(source_bytes, filename=source_path.name, include_blocks=True)
    formula_reports: list[dict[str, Any]] = []
    eq_reports: list[dict[str, Any]] = []

    # Map relationship id / embedding path → latex text for replacement.
    latex_by_rel: dict[str, str] = {}
    latex_by_embed: dict[str, str] = {}

    with zipfile.ZipFile(io.BytesIO(source_bytes), "r") as zf:
        for ole in parsed.get("mathtype_oles") or []:
            formula_index = int(ole.get("formula_index") or 0)
            rel_id = ole.get("relationship_id")
            embed_path = ole.get("embedding_path")
            report: dict[str, Any] = {
                "formula_index": formula_index,
                "relationship_id": rel_id,
                "embedding_path": embed_path,
                "location": ole.get("location"),
                "equation_native_found": False,
                "mtef_version": None,
                "latex": None,
                "status": "failed",
                "error": None,
            }
            try:
                if not embed_path:
                    raise ValueError("missing_embedding_path")
                ole_bytes = zf.read(embed_path)
                native, native_err = extract_equation_native(ole_bytes)
                if native is None:
                    raise ValueError(native_err or "equation_native_missing")
                report["equation_native_found"] = True
                latex, meta = equation_native_to_latex(native)
                report["mtef_version"] = meta.get("mtef_version")
                if not latex or not meta.get("valid"):
                    # Fallback: full OLE parse
                    latex2, meta2 = mtef_bytes_to_latex(ole_bytes)
                    if latex2 and meta2.get("valid"):
                        latex, meta = latex2, meta2
                        report["mtef_version"] = meta.get("mtef_version")
                    else:
                        raise ValueError(meta.get("error") or meta2.get("error") or "mtef_convert_failed")
                wrapped = wrap_latex_for_v2(latex)
                if not wrapped:
                    raise ValueError(meta.get("error") or "empty_latex")
                report["latex"] = wrapped
                report["status"] = "ok"
                report["mtef_summary"] = {
                    "inline": meta.get("inline"),
                    "raw_latex": latex,
                }
                if rel_id:
                    latex_by_rel[str(rel_id)] = wrapped
                if embed_path:
                    latex_by_embed[str(embed_path).replace("\\", "/")] = wrapped
            except Exception as exc:
                placeholder = f"{MATH_FAIL_PREFIX}{formula_index}]"
                report["error"] = str(exc)
                report["latex"] = placeholder
                report["status"] = "failed"
                if rel_id:
                    latex_by_rel[str(rel_id)] = placeholder
                if embed_path:
                    latex_by_embed[str(embed_path).replace("\\", "/")] = placeholder
            formula_reports.append(report)

        # EQ fields from structure parse.
        for eq in parsed.get("eq_fields") or []:
            field_index = int(eq.get("field_index") or 0)
            instruction = eq.get("instruction") or ""
            latex, err = convert_eq_instruction_to_latex(instruction)
            report = {
                "field_index": field_index,
                "instruction": instruction,
                "location": eq.get("location"),
                "latex": None,
                "status": "failed",
                "error": err,
            }
            if latex and not err:
                wrapped = wrap_latex_for_v2(latex)
                report["latex"] = wrapped
                report["status"] = "ok"
                report["error"] = None
            else:
                report["latex"] = f"{EQ_FAIL_PREFIX}{field_index}]"
                report["status"] = "failed"
            eq_reports.append(report)

        # Rewrite document.xml
        document_xml = zf.read("word/document.xml")
        root = etree.fromstring(document_xml)
        rel_maps = _load_relationship_maps(zf)

        # Replace MathType OLE objects.
        for ole_elem in root.xpath(".//o:OLEObject", namespaces=NS):
            prog_id = str(ole_elem.get("ProgID") or "").strip()
            if prog_id != "Equation.DSMT4":
                continue
            rel_id = ole_elem.get(f"{{{REL_NS}}}id")
            embed_path, _ = _resolve_relationship_target("word/document.xml", rel_id or "", rel_maps)
            latex_text = None
            if rel_id and str(rel_id) in latex_by_rel:
                latex_text = latex_by_rel[str(rel_id)]
            elif embed_path and embed_path.replace("\\", "/") in latex_by_embed:
                latex_text = latex_by_embed[embed_path.replace("\\", "/")]
            if not latex_text:
                continue
            # Replace nearest w:object ancestor when present.
            target = ole_elem
            parent = ole_elem.getparent()
            while parent is not None and _local_name(parent.tag) not in {"object", "r", "p"}:
                parent = parent.getparent()
            if parent is not None and _local_name(parent.tag) == "object":
                target = parent
            _replace_element_with_run(target, latex_text)

        # Replace EQ fields.
        eq_by_instruction_order = [e for e in eq_reports]
        eq_cursor = 0
        for paragraph in root.xpath(".//w:p", namespaces=NS):
            groups = _collect_eq_field_run_groups(paragraph)
            # Replace from the end so indexes stay valid.
            for group in reversed(groups):
                # Match next unused eq report with same instruction when possible.
                matched = None
                for candidate in eq_by_instruction_order:
                    if candidate.get("_used"):
                        continue
                    if candidate.get("instruction") == group["instruction"]:
                        matched = candidate
                        break
                if matched is None and eq_cursor < len(eq_by_instruction_order):
                    matched = eq_by_instruction_order[eq_cursor]
                if matched is None:
                    continue
                matched["_used"] = True
                eq_cursor += 1
                latex_text = matched.get("latex") or f"{EQ_FAIL_PREFIX}{matched.get('field_index')}]"
                runs = group["runs"]
                if not runs:
                    continue
                first = runs[0]
                parent = first.getparent()
                if parent is None:
                    continue
                insert_at = list(parent).index(first)
                for run in runs:
                    if run.getparent() is parent:
                        parent.remove(run)
                parent.insert(insert_at, _make_latex_run(latex_text))

        new_document_xml = etree.tostring(
            root,
            xml_declaration=True,
            encoding="UTF-8",
            standalone=True,
        )

        # Write output zip (copy all parts, overwrite document.xml).
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as out_zf:
            for item in zf.infolist():
                data = zf.read(item.filename)
                if item.filename.replace("\\", "/") == "word/document.xml":
                    data = new_document_xml
                out_zf.writestr(item, data)

    ok_count = sum(1 for f in formula_reports if f["status"] == "ok")
    fail_count = sum(1 for f in formula_reports if f["status"] != "ok")
    native_ok = sum(1 for f in formula_reports if f.get("equation_native_found"))
    eq_ok = sum(1 for e in eq_reports if e["status"] == "ok")

    # Verify original unchanged.
    after_bytes = source_path.read_bytes()
    original_unchanged = after_bytes == source_bytes

    report = {
        "source": str(source_path),
        "output": str(output_path),
        "original_unchanged": original_unchanged,
        "mathtype_ole": len(formula_reports),
        "equation_native_ok": native_ok,
        "converted_ok": ok_count,
        "converted_failed": fail_count,
        "eq_fields": len(eq_reports),
        "eq_converted_ok": eq_ok,
        "formulas": formula_reports,
        "eq_field_results": [{k: v for k, v in e.items() if k != "_used"} for e in eq_reports],
        "summary": parsed.get("summary") or {},
    }
    return report


def convert_reference_b2_1_1(project_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
    source = find_reference_docx_in_storage(root)
    if source is None:
        raise FileNotFoundError(
            "Reference DOCX not found under textbook_import/source/vocational/math_B2/"
        )
    return convert_docx_mathtype_to_latex_docx(source)


def pick_representative_formulas(report: dict[str, Any], limit: int = 10) -> list[dict[str, Any]]:
    """Pick diverse successful formulas for human review."""
    formulas = [f for f in report.get("formulas") or [] if f.get("status") == "ok" and f.get("latex")]
    categories = {
        "degree": re.compile(r"circ|°"),
        "pi": re.compile(r"\\pi"),
        "theta": re.compile(r"\\theta"),
        "fraction": re.compile(r"\\frac"),
        "overline": re.compile(r"\\overline"),
        "paren": re.compile(r"\\left|\\right|\("),
        "superscript": re.compile(r"\^"),
        "subscript": re.compile(r"_\{"),
        "sqrt": re.compile(r"\\sqrt"),
        "trig": re.compile(r"\\(?:sin|cos|tan)"),
        "simple": re.compile(r"."),
    }
    picked: list[dict[str, Any]] = []
    used: set[int] = set()
    for name, pattern in categories.items():
        for f in formulas:
            idx = f["formula_index"]
            if idx in used:
                continue
            if pattern.search(f.get("latex") or ""):
                item = dict(f)
                item["category"] = name
                picked.append(item)
                used.add(idx)
                break
        if len(picked) >= limit:
            break
    return picked[:limit]
