from __future__ import annotations

from types import ModuleType

from core.legacy_generator_adapter import invoke_legacy_generator


def test_invoke_legacy_generator_passes_only_level() -> None:
    calls = []
    mod = ModuleType("skills.jh_legacy")

    def generate(level=1):
        calls.append({"level": level})
        return {"question_text": "legacy question", "answer": "1"}

    mod.generate = generate

    payload = invoke_legacy_generator(mod, skill_id="jh_legacy", level=3)

    assert calls == [{"level": 3}]
    assert payload["question_text"] == "legacy question"
    assert payload["new_question_text"] == "legacy question"
    assert payload["answer"] == "1"
    assert payload["correct_answer"] == "1"
    assert payload["choices"] == []
    assert payload["answer_type"] == "text"
    assert payload["generator_mode"] == "legacy"
    assert payload["route_source"] == "legacy_skill"


def test_invoke_legacy_generator_does_not_swallow_generator_type_error() -> None:
    mod = ModuleType("skills.jh_legacy")

    def generate(level=1):
        raise TypeError("internal generator bug")

    mod.generate = generate

    try:
        invoke_legacy_generator(mod, skill_id="jh_legacy", level=1)
    except TypeError as exc:
        assert str(exc) == "internal generator bug"
    else:
        raise AssertionError("expected TypeError to propagate")

