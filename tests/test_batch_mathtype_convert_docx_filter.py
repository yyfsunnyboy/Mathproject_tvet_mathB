from pathlib import Path

from scripts.batch_mathtype_convert_docx import FileResult, ScanResult, classify_file, write_report


def test_filter_include_docx(tmp_path: Path):
    input_file = tmp_path / "第一章 1-1 數線與絕對值-課本.docx"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "candidate"


def test_filter_skip_pdf(tmp_path: Path):
    input_file = tmp_path / "第一章 1-1 數線與絕對值-課本.pdf"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_pdf"


def test_filter_skip_already_latex_upper(tmp_path: Path):
    input_file = tmp_path / "第一章 1-1 數線與絕對值-課本_Latex.docx"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_already_latex"


def test_filter_skip_already_latex_lower(tmp_path: Path):
    input_file = tmp_path / "第一章 1-2 平面坐標與典型函數-課本_latex.docx"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_already_latex"


def test_filter_skip_word_temp(tmp_path: Path):
    input_file = tmp_path / "~$第一章 1-3 二次函數-課本.docx"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_word_temp"


def test_filter_skip_existing_output(tmp_path: Path):
    input_file = tmp_path / "第一章 1-3 二次函數-課本.docx"
    input_file.write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    existing = out / "第一章 1-3 二次函數-課本_Latex.docx"
    existing.write_text("x", encoding="utf-8")

    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_existing_output"


def test_filter_skip_existing_latex_sibling_upper(tmp_path: Path):
    input_file = tmp_path / "original.docx"
    input_file.write_text("x", encoding="utf-8")
    (tmp_path / "original_Latex.docx").write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_existing_latex_sibling"
    assert result.reason == "input_folder_already_has_latex_version"


def test_filter_skip_existing_latex_sibling_lower(tmp_path: Path):
    input_file = tmp_path / "original.docx"
    input_file.write_text("x", encoding="utf-8")
    (tmp_path / "original_latex.docx").write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_existing_latex_sibling"


def test_filter_skip_existing_latex_sibling_no_underscore(tmp_path: Path):
    input_file = tmp_path / "original.docx"
    input_file.write_text("x", encoding="utf-8")
    (tmp_path / "originalLatex.docx").write_text("x", encoding="utf-8")
    out = tmp_path / "out"
    out.mkdir()
    result = classify_file(input_file, out, overwrite=False)
    assert result.status == "skipped_existing_latex_sibling"


def test_report_writer_uses_utf8_sig(tmp_path: Path):
    report = tmp_path / "report.md"
    scan_results = [ScanResult("a.docx", tmp_path / "a.docx", "skipped_existing_latex_sibling", "r")]
    file_results = [
        FileResult(
            index=1,
            filename="a.docx",
            status="skipped_existing_latex_sibling",
            reason="input_folder_already_has_latex_version",
            strategy_used="",
            command_used="",
            output_path="",
            latex_signal_count_before=0,
            latex_signal_count_current=0,
            latex_signal_count_saved=0,
        )
    ]
    write_report(
        report_path=report,
        mode="dry-run",
        scan_results=scan_results,
        file_results=file_results,
        diagnostics={},
        auto=False,
        allow_ui_automation=False,
        selected_file="",
    )
    raw = report.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
