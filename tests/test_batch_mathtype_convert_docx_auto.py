from argparse import Namespace
from pathlib import Path

import scripts.batch_mathtype_convert_docx as mod


class DummyDoc:
    def __init__(self):
        self.saved = False

    def SaveAs2(self, path, **_kwargs):
        self.saved = True
        Path(path).write_text("saved", encoding="utf-8")


def _args(**overrides):
    base = dict(
        input_folder="in",
        output_folder="out",
        pattern="*.docx",
        interactive=False,
        batch=False,
        dry_run=False,
        limit=None,
        overwrite=False,
        continue_on_fail=False,
        report=None,
        discover_mathtype=False,
        auto=True,
        semi_auto=False,
        macro_name=None,
        command_onaction=None,
        command_caption=None,
        allow_ui_automation=False,
    )
    base.update(overrides)
    return Namespace(**base)


def test_macro_strategy_success_converted(tmp_path: Path, monkeypatch):
    doc = DummyDoc()
    out = tmp_path / "o.docx"
    monkeypatch.setattr(mod, "try_macro_strategy", lambda *_: (True, "macro:X"))
    monkeypatch.setattr(mod, "try_commandbar_strategy", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "try_ui_automation_fallback", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "count_latex_signals_docx", lambda *_: 5)
    seq = iter(["", "$x$ $y$"])
    monkeypatch.setattr(mod, "get_doc_text", lambda *_: next(seq))

    status, _reason, _cmd, _b, _c, _s, _strategy = mod.perform_auto_conversion(
        app=object(), doc=doc, args=_args(), output_path=out, diagnostics={"macro_attempts": [], "commandbar_attempts": [], "errors": [], "ui_automation_steps": []}
    )
    assert status == "converted"
    assert doc.saved is True


def test_commandbar_strategy_success_converted(tmp_path: Path, monkeypatch):
    doc = DummyDoc()
    out = tmp_path / "o.docx"
    monkeypatch.setattr(mod, "try_macro_strategy", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "try_commandbar_strategy", lambda *_: (True, "control:C"))
    monkeypatch.setattr(mod, "try_ui_automation_fallback", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "count_latex_signals_docx", lambda *_: 3)
    seq = iter(["a", "a $b$"])
    monkeypatch.setattr(mod, "get_doc_text", lambda *_: next(seq))

    status, *_rest = mod.perform_auto_conversion(
        app=object(), doc=doc, args=_args(), output_path=out, diagnostics={"macro_attempts": [], "commandbar_attempts": [], "errors": [], "ui_automation_steps": []}
    )
    assert status == "converted"


def test_no_latex_signal_no_save(tmp_path: Path, monkeypatch):
    doc = DummyDoc()
    out = tmp_path / "o.docx"
    monkeypatch.setattr(mod, "try_macro_strategy", lambda *_: (True, "macro:X"))
    monkeypatch.setattr(mod, "count_latex_signals_docx", lambda *_: 0)
    seq = iter(["abc", "abc"])
    monkeypatch.setattr(mod, "get_doc_text", lambda *_: next(seq))

    status, *_rest = mod.perform_auto_conversion(
        app=object(), doc=doc, args=_args(), output_path=out, diagnostics={"macro_attempts": [], "commandbar_attempts": [], "errors": [], "ui_automation_steps": []}
    )
    assert status == "failed_no_latex_signal_after_convert"
    assert doc.saved is False


def test_ui_fallback_not_allowed(monkeypatch):
    diagnostics = {"macro_attempts": [], "commandbar_attempts": [], "errors": [], "ui_automation_steps": []}
    doc = DummyDoc()
    monkeypatch.setattr(mod, "try_macro_strategy", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "try_commandbar_strategy", lambda *_: (False, ""))
    status, reason, *_rest = mod.perform_auto_conversion(
        app=object(),
        doc=doc,
        args=_args(allow_ui_automation=False),
        output_path=Path("x.docx"),
        diagnostics=diagnostics,
    )
    # by default strategies fail with object app
    assert status in ("failed_ui_automation_not_allowed", "failed_no_latex_signal_after_convert", "failed_no_auto_command")


def test_a_b_fail_without_ui_returns_not_allowed(tmp_path: Path, monkeypatch):
    doc = DummyDoc()
    monkeypatch.setattr(mod, "try_macro_strategy", lambda *_: (False, ""))
    monkeypatch.setattr(mod, "try_commandbar_strategy", lambda *_: (False, ""))
    status, reason, *_rest = mod.perform_auto_conversion(
        app=object(),
        doc=doc,
        args=_args(allow_ui_automation=False),
        output_path=tmp_path / "o.docx",
        diagnostics={"macro_attempts": [], "commandbar_attempts": [], "errors": [], "ui_automation_steps": []},
    )
    assert status == "failed_ui_automation_not_allowed"
    assert "without_ui_automation" in reason


def test_output_exists_without_overwrite_skipped(tmp_path: Path):
    input_file = tmp_path / "a.docx"
    input_file.write_text("x", encoding="utf-8")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "a_Latex.docx").write_text("x", encoding="utf-8")
    r = mod.classify_file(input_file, out_dir, overwrite=False)
    assert r.status == "skipped_existing_output"
