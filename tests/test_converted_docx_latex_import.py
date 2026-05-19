from pathlib import Path

from docx import Document

from app import app
from core import textbook_processor as processor


class _Q:
    def __init__(self):
        self.items = []

    def put(self, msg):
        self.items.append(str(msg))


def test_extract_converted_docx_latex_keeps_inline_absolute_value(tmp_path: Path):
    p = tmp_path / "converted.docx"
    d = Document()
    d.add_paragraph("數線上，若 $|x|=7$，試求 $x$ 之值。")
    d.save(str(p))
    content, _meta = processor.extract_converted_latex_docx(str(p))
    assert "$|x|=7$" in content[1]


def test_extract_converted_docx_latex_keeps_table_ge(tmp_path: Path):
    p = tmp_path / "converted_table.docx"
    d = Document()
    t = d.add_table(rows=1, cols=1)
    t.cell(0, 0).text = "試求下列不等式之解：(1) $|x|<3$ (2) $|x|\\ge 4$"
    d.save(str(p))
    content, _meta = processor.extract_converted_latex_docx(str(p))
    assert "\\ge" in content[1]


def test_extract_converted_docx_latex_keeps_frac(tmp_path: Path):
    p = tmp_path / "converted_frac.docx"
    d = Document()
    d.add_paragraph("$-\\frac{4}{3}$")
    d.save(str(p))
    content, _meta = processor.extract_converted_latex_docx(str(p))
    assert "\\frac{4}{3}" in content[1]


def test_converted_mode_skips_assets_ocr_pix2tex(tmp_path: Path):
    p = tmp_path / "converted_mode.docx"
    d = Document()
    d.add_paragraph("數線上，若 $|x|=7$，試求 $x$ 之值。")
    d.save(str(p))
    q = _Q()
    with app.app_context():
        out = processor.extract_content_from_file(
            str(p),
            q,
            import_policy={"docx_formula_source_mode": "converted_docx_latex"},
        )
        ctx = processor._DOCX_IMPORT_CONTEXT
    assert "$|x|=7$" in out[1]
    assert "[FORMULA_IMAGE_" not in out[1]
    assert ctx.get("formula_assets_extraction_skipped") is True
    assert ctx.get("ocr_skipped") is True
    assert ctx.get("pix2tex_skipped") is True


def test_prompt_contains_converted_docx_latex_rules():
    src = Path("core/textbook_processor.py").read_text(encoding="utf-8")
    assert "converted_docx_latex 規則（必須遵守）" in src
    assert "不可改寫為 [FORMULA_IMAGE_N]" in src
