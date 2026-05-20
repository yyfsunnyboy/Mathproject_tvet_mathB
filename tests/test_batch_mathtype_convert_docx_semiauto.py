from argparse import Namespace
from pathlib import Path

import scripts.batch_mathtype_convert_docx as mod


def _args(tmp_path: Path, **kwargs):
    base = dict(
        input_folder=str(tmp_path / "in"),
        output_folder=str(tmp_path / "out"),
        pattern="*.docx",
        interactive=False,
        batch=True,
        semi_auto=False,
        dry_run=False,
        limit=None,
        overwrite=False,
        report=None,
        macro_name=None,
    )
    base.update(kwargs)
    return Namespace(**base)


def test_output_folder_warning_token():
    assert mod.detect_output_folder_warning("H:/x/第 一冊_latex") == "第 一冊"


def test_pywin32_missing_status_is_failed_pywin32_missing(tmp_path: Path, monkeypatch):
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out"
    (inf / "original.docx").write_text("x", encoding="utf-8")

    monkeypatch.setattr(mod, "parse_args", lambda: _args(tmp_path))
    monkeypatch.setattr(mod, "check_pywin32_available", lambda: False)

    captured = {}

    def fake_write_report(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(mod, "write_report", fake_write_report)
    monkeypatch.setattr(mod, "count_latex_signals", lambda *_: 1)

    rc = mod.main()
    assert rc == 0


def test_semi_auto_does_not_call_auto_macro(tmp_path: Path, monkeypatch):
    inf = tmp_path / "in"
    inf.mkdir()
    outf = tmp_path / "out"
    (inf / "original.docx").write_text("x", encoding="utf-8")

    monkeypatch.setattr(mod, "parse_args", lambda: _args(tmp_path, semi_auto=True))
    monkeypatch.setattr(mod, "check_pywin32_available", lambda: True)

    called = {"auto": 0, "semi": 0}

    def fake_auto(*_args, **_kwargs):
        called["auto"] += 1
        return "failed_no_macro", "no_mathtype_convert_macro_found", {}

    def fake_semi(*_args, **_kwargs):
        called["semi"] += 1
        out = Path(_args[1])
        out.write_text("x", encoding="utf-8")
        return "converted", "ok", {}

    monkeypatch.setattr(mod, "try_convert_one_via_word", fake_auto)
    monkeypatch.setattr(mod, "try_convert_one_via_word_semi_auto", fake_semi)
    monkeypatch.setattr(mod, "count_latex_signals", lambda *_: 2)

    rc = mod.main()
    assert rc == 0
    assert called["semi"] == 1
    assert called["auto"] == 0
