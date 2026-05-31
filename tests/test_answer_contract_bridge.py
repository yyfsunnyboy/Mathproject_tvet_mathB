from __future__ import annotations

from core.gencode.answer_contract_bridge import legacy_fields_from_answer_contract


def test_short_answer_bridge():
    legacy = legacy_fields_from_answer_contract(
        {"answer_type": "short_answer", "answer_equivalence": "exact_text"}
    )
    assert legacy["checker_key"] == "text_checker"
    assert legacy["equivalence_type"] == "exact_string"
    assert legacy["answer_shape"]


def test_single_choice_bridge():
    legacy = legacy_fields_from_answer_contract(
        {
            "answer_type": "single_choice",
            "answer_equivalence": "choice_label",
            "choices_required": True,
        }
    )
    assert legacy["checker_key"] == "choice_label_checker"
    assert legacy["equivalence_type"] == "choice_label"
