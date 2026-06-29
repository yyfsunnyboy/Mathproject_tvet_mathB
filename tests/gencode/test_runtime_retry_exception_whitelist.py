from __future__ import annotations

import pytest

import core.gencode.runtime_skill_wrapper as runtime
from core.exceptions import RetryableSamplingError


def _payload() -> dict:
    return {
        "problem_type_id": "audit_pt",
        "question_text": "question",
        "answer": "answer",
        "correct_answer": "answer",
        "choices": [],
        "metadata": {"givens": {}},
    }


def _prepare(monkeypatch, generator, *, semantic_errors=None):
    spec = {"problem_type_id": "audit_pt", "answer_contract": {}}
    monkeypatch.setattr(
        runtime,
        "load_problem_type_spec",
        lambda skill_id, problem_type_id, prefer="auto": dict(spec),
    )
    monkeypatch.setattr(runtime, "generate_from_problem_type_spec", generator)
    monkeypatch.setattr(
        runtime,
        "validate_generator_payload",
        semantic_errors or (lambda payload, problem_type_spec=None: []),
    )
    monkeypatch.setattr(
        runtime,
        "validate_generated_question_format",
        lambda payload, **kwargs: [],
    )


def _generate(*, seed=10, max_attempts=3):
    return runtime.generate_for_skill(
        "audit_skill",
        [{"problem_type_id": "audit_pt", "max_attempts": max_attempts}],
        seed=seed,
    )


def test_retryable_sampling_error_retries_deterministically(monkeypatch):
    seeds = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        if len(seeds) < 3:
            raise RetryableSamplingError(f"collision-{seed}")
        return _payload()

    _prepare(monkeypatch, generator)
    assert _generate(seed=10)["problem_type_id"] == "audit_pt"
    assert seeds == [10, 11, 12]


def test_zero_division_error_is_immediate_fail_fast(monkeypatch):
    seeds = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        raise ZeroDivisionError("generator bug")

    _prepare(monkeypatch, generator)
    with pytest.raises(ZeroDivisionError, match="generator bug"):
        _generate(seed=20)
    assert seeds == [20]


def test_zero_division_bug_is_not_sampling_exhausted(monkeypatch):
    def generator(skill_id, spec, seed=None):
        raise ZeroDivisionError("unexpected denominator")

    _prepare(monkeypatch, generator)
    with pytest.raises(ZeroDivisionError) as exc_info:
        _generate(seed=30)
    assert "SAMPLING_EXHAUSTED" not in str(exc_info.value)


def test_explicit_sampling_collision_can_recover_on_next_seed(monkeypatch):
    seeds = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        if seed == 40:
            raise RetryableSamplingError("sampled denominator is zero")
        return _payload()

    _prepare(monkeypatch, generator)
    assert _generate(seed=40)["problem_type_id"] == "audit_pt"
    assert seeds == [40, 41]


def test_explicit_sampling_collision_exhaustion(monkeypatch):
    seeds = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        raise RetryableSamplingError(f"sampled denominator is zero:{seed}")

    _prepare(monkeypatch, generator)
    with pytest.raises(RuntimeError) as exc_info:
        _generate(seed=50, max_attempts=2)
    message = str(exc_info.value)
    assert "SAMPLING_EXHAUSTED" in message
    assert "attempts=2" in message
    assert "sampled denominator is zero:51" in message
    assert seeds == [50, 51]


def test_choices_duplicate_behavior_is_unchanged(monkeypatch):
    seeds = []
    validations = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        return _payload()

    def semantic_errors(payload, problem_type_spec=None):
        validations.append(payload)
        return ["choices_duplicate"] if len(validations) == 1 else []

    _prepare(monkeypatch, generator, semantic_errors=semantic_errors)
    assert _generate(seed=60)["problem_type_id"] == "audit_pt"
    assert seeds == [60, 61]


@pytest.mark.parametrize(
    "error",
    [ValueError("ordinary value error"), RuntimeError("unknown runtime error")],
)
def test_other_errors_remain_fail_fast(monkeypatch, error):
    seeds = []

    def generator(skill_id, spec, seed=None):
        seeds.append(seed)
        raise error

    _prepare(monkeypatch, generator)
    with pytest.raises(type(error), match=str(error)):
        _generate(seed=70)
    assert seeds == [70]
