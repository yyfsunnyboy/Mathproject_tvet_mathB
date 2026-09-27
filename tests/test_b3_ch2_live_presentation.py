"""Live presentation contract for B3 Chapter 2.

Counts interactive controls from the shared renderer contract and the DOM
audit artifact. Payload parts are not treated as rendered inputs.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOM_JSON = ROOT / "scratch" / "b3_ch2_live_dom_counts.json"


def _generate(source_id: int, seed: int = 3):
    matches = list((ROOT / "agent_skills_v3").glob(f"**/src_{source_id}/generate.py"))
    spec = importlib.util.spec_from_file_location(f"live_{source_id}", matches[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate(level=1, seed=seed)


def _labels(payload):
    parts = (payload.get("answer_contract") or {}).get("parts") or []
    return [str(part.get("display_label") or "") for part in parts]


def test_tent_two_controls_use_semantic_labels():
    payload = _generate(11977)
    labels = _labels(payload)
    assert len(labels) == 2
    assert "帳篷數" in labels[0]
    assert "學生數" in labels[1]
    assert all("未知數" not in label for label in labels)
    assert "第一個數量" not in payload["question_text"]


def test_four_linear_equations_do_not_repeat_as_labels():
    payload = _generate(11987)
    labels = _labels(payload)
    assert labels == ["(1) 第1題", "(2) 第2題", "(3) 第3題", "(4) 第4題"]
    assert all("=" not in label for label in labels)
    assert "+ (-" not in payload["question_text"]


def test_two_inequalities_have_short_labels():
    payload = _generate(11979)
    labels = _labels(payload)
    assert len(labels) == 2
    assert all("=" not in label and ">" not in label and "<" not in label for label in labels)


def test_factor_identity_mcq_has_operator_and_single_math_wrap():
    payload = _generate(12024)
    text = payload["question_text"]
    assert r"\(" not in "".join(choice["text"] for choice in payload["choices"])
    assert all(choice["text"].count("$") == 2 for choice in payload["choices"])
    assert len(payload["choices"]) == 4
    assert "x^{2}" in text or "x^2" in text
    assert "x^{2} " not in text.replace("x^{2} +", "").replace("x^{2} -", "")
    compact = text.replace(" ", "")
    assert "x^{2}+" in compact or "x^{2}-" in compact


def test_quadratic_roots_labels_are_smaller_and_larger():
    payload = _generate(11997)
    labels = _labels(payload)
    assert "較小根" in labels[0]
    assert "較大根" in labels[1]
    assert all("=0" not in label for label in labels)


def test_root_count_has_three_short_labels():
    payload = _generate(12003)
    labels = _labels(payload)
    assert [label.split()[-1] for label in labels] == ["第1式", "第2式", "第3式"]
    assert all("=" not in label for label in labels)


def test_delimited_choice_is_not_double_wrapped():
    from core.gencode.domain_matrix_adapter import _format_latex_display_answer

    rendered = _format_latex_display_answer(r"\(-3\)")
    assert r"\(" not in rendered
    assert r"\)" not in rendered
    assert rendered.strip("$") == "-3"


def test_dom_gate_matches_expected_controls():
    if not DOM_JSON.exists():
        pytest.skip("DOM audit artifact is produced by the browser gate")
    counts = {int(row["source_id"]): row for row in json.loads(DOM_JSON.read_text(encoding="utf-8"))}
    expected = {
        11977: (2, 0),
        11987: (4, 0),
        11979: (2, 0),
        12024: (0, 4),
        11997: (2, 0),
        12003: (3, 0),
    }
    for source_id, (inputs, choices) in expected.items():
        row = counts[source_id]
        assert row["visible_input_element_count"] == inputs
        assert row["choice_button_count"] == choices
        assert row["choice_text_has_raw_delimiter"] is False
    assert len(counts) == 68
    for row in counts.values():
        visible = row["visible_input_element_count"] + row["choice_button_count"]
        assert visible >= 1
        assert row["choice_text_has_raw_delimiter"] is False
