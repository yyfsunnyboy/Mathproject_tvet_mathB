from __future__ import annotations

import pytest

from core.gencode.choice_contract_validator import validate_vocational_multiple_choice
from core.gencode.single_choice_contract import build_single_choice_contract
from core.gencode.vocational_choice_contract import normalize_legacy_vocational_choices
from core.gencode.answer_payload import refresh_runtime_question_session


def _legacy(answer, **extra):
    payload = {
        "skill_id": "vh_數學B2_SubSection_2_1_2",
        "presentation_mode": "single_choice",
        "answer_type": "choice",
        "choices": [
            {"label": label, "text": text}
            for label, text in zip("ABCDEF", ("500", "1800", "400", "700", "1100", "800"))
        ],
        "answer": answer,
        "correct_answer": answer,
    }
    payload.update(extra)
    return payload


@pytest.mark.parametrize("answer,semantic", [("A", "500"), ("F", "800"), (5, "800"), (800, "800"), ({"value": "800"}, "800")])
def test_legacy_six_choices_preserve_correct_semantic_answer(answer, semantic):
    repaired = normalize_legacy_vocational_choices(_legacy(answer, answer_index=5))
    assert not validate_vocational_multiple_choice(repaired)
    assert [c["label"] for c in repaired["choices"]] == list("ABCD")
    assert repaired["choices"][repaired["answer_index"]]["value"] == semantic
    assert repaired["choices"][ord(repaired["correct_answer"]) - 65]["value"] == semantic


def test_builder_generates_three_distinct_distractors_for_vocational():
    for seed in range(20):
        result = build_single_choice_contract("800", ["500", "1800", "400", "700", "1100"], seed=seed, curriculum_profile="vocational_high_b")
        assert len(result["choices"]) == 4
        assert len({c["value"] for c in result["choices"]}) == 4
        assert result["choices"][ord(result["correct_answer"]) - 65]["value"] == "800"


def test_non_vocational_and_non_choice_payloads_are_unchanged():
    other = _legacy("F", skill_id="jh_數學1上_FourArithmeticOperationsOfIntegers")
    assert normalize_legacy_vocational_choices(other) is other
    text = {"skill_id": "vh_數學B2_SubSection_2_1_2", "answer_type": "text", "choices": []}
    assert normalize_legacy_vocational_choices(text) is text


def test_generator_validator_rejects_five_choices():
    assert "vocational_choice_count" in validate_vocational_multiple_choice(_legacy("F"))


def test_session_normalization_remaps_checker_answer_after_shuffle():
    from core.routes.practice import _choice_value_to_label

    for seed in range(20):
        payload = _legacy("F", seed=seed)
        repaired = refresh_runtime_question_session(payload, skill_id=payload["skill_id"])
        assert len(repaired["choices"]) == 4
        assert _choice_value_to_label("800", repaired["choices"]) == repaired["correct_answer"]
        assert _choice_value_to_label(repaired["answer"], repaired["choices"]) == repaired["correct_answer"]
