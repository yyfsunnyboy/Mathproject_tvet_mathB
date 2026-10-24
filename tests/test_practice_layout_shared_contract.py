"""Shared practice-page layout contract (stem reading order, answer strip, option choices, figure panels).

These are source-level guards for fixes that were verified in a real browser (390 px phone, 1180x820 iPad, desktop):
the behaviour itself is DOM / MathJax work, so the tests pin the mechanisms that must not silently disappear.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
RENDERER = (ROOT / "static" / "js" / "multipart_field_renderer.js").read_text(encoding="utf-8")
ANSWER_CSS = (ROOT / "static" / "css" / "practice_answer_layout.css").read_text(encoding="utf-8")
VISUAL = (ROOT / "static" / "js" / "visual_spec.js").read_text(encoding="utf-8")


def test_part_canvas_ink_layer_does_not_hide_the_grid_layer():
    # the page-wide `canvas { background: #fff }` rule made the transparent ink canvas opaque and hid the grid / axes
    assert "background:transparent" in RENDERER.replace(" ", "")
    assert "width:100%;height:100%" in RENDERER.replace(" ", "")


def test_independent_canvases_share_one_strip_on_their_own_line():
    assert "multi-part-canvas-strip" in RENDERER and "appendPartField" in RENDERER
    assert ".multi-part-canvas-strip" in ANSWER_CSS and "flex: 1 1 100%" in ANSWER_CSS


def test_raw_tex_part_labels_are_typeset_not_shown_as_source():
    assert "mathSafeLabel" in RENDERER and "label.textContent = mathSafeLabel(prompt)" in RENDERER
    assert "mathSafeLabel," in RENDERER  # exported


def test_stem_text_keeps_reading_order_when_it_wraps():
    assert "function glueStemText" in INDEX and "function keepMarkersWithMath" in INDEX
    assert INDEX.count("glueStemText(") >= 4  # definition + legacy stem + structured prompt + structured body
    assert "keepMarkersWithMath(element)" in INDEX
    assert "\\\\text{" in INDEX  # closing punctuation moves inside the formula


def test_short_options_sit_in_one_row_and_the_header_chips_do_not_split():
    assert "choice-compact" in INDEX and "#question-choices.choice-list.choice-compact" in INDEX
    assert INDEX.count("white-space: nowrap !important;") >= 2


def test_multi_figure_panels_can_carry_curves_and_a_fixed_range():
    assert "fig.curves" in VISUAL and "fixed_range" in VISUAL and "curvesAreDrawable(panelSpec.curves)" in VISUAL


def test_wrapped_subquestion_run_becomes_a_left_aligned_block_under_the_prompt():
    # an inline-block run that needs several lines is baseline-aligned to its last line: it rose above the prompt and
    # sat on the right.  After layout such a run is switched to a block (prompt first, then (1)...(n), left aligned).
    assert "function settleMultipartItems" in INDEX and "settleMultipartItems(element)" in INDEX
    assert ".multipart-stem-items.question-multipart-items-multiline" in INDEX
