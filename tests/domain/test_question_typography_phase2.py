"""Phase 2 typography contracts for confirmed mixed shared generators."""

from __future__ import annotations

import hashlib
import importlib
import json
import re

import pytest


CASES = {
    "vh_數學B1_AbsoluteValue": ["src_4398", "src_4399", "src_4408", "src_4412"],
    "vh_數學B1_LinearFunction": ["src_4516"],
    "vh_數學B1_PolynomialFactoring": ["src_4675", "src_4685", "src_4701"],
    "vh_數學B1_PropertiesOfParallelLines": ["src_4602"],
    "vh_數學B1_RationalEquation": ["src_4690"],
    "vh_數學B1_SlopeOfALine": ["src_4522", "src_4590"],
}
SEEDS = (0, 1, 7, 23, 41)
INLINE_MATH_RE = re.compile(r"\$[^$]+\$|\\\(.*?\\\)", re.DOTALL)


def _payload(skill: str, component: str, seed: int) -> dict:
    module = importlib.import_module(f"agent_skills_v3.{skill}")
    return module.generate(seed=seed, component_id=component)


@pytest.mark.parametrize(
    ("skill", "component"),
    [(skill, component) for skill, components in CASES.items() for component in components],
)
@pytest.mark.parametrize("seed", SEEDS)
def test_confirmed_mixed_stems_keep_math_atoms_inline(
    skill: str,
    component: str,
    seed: int,
) -> None:
    question = str(_payload(skill, component, seed)["question_text"])
    assert question.count("$") % 2 == 0
    assert question.count(r"\(") == question.count(r"\)")
    assert "$$" not in question
    assert r"\[" not in question
    assert r"\]" not in question

    plain_text = INLINE_MATH_RE.sub("", question)
    assert not re.search(r"[A-Za-z]", plain_text), question


def test_phase2_answer_and_checker_digest_is_unchanged() -> None:
    rows = []
    for skill, components in CASES.items():
        for component in components:
            for seed in SEEDS:
                payload = _payload(skill, component, seed)
                rows.append(
                    {
                        "skill": skill,
                        "component": component,
                        "seed": seed,
                        "answer": payload.get("answer"),
                        "correct_answer": payload.get("correct_answer"),
                        "answer_type": payload.get("answer_type"),
                        "checker": payload.get("checker"),
                        "checker_key": payload.get("checker_key"),
                        "checker_type": payload.get("checker_type"),
                        "answer_contract": payload.get("answer_contract"),
                        "choices": payload.get("choices"),
                    }
                )
    digest = hashlib.sha256(
        json.dumps(
            rows,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    assert digest == "70839b68d2637161dbef50b7753a8f50edea01a34ef05e78e4b67aff62058d1a"
