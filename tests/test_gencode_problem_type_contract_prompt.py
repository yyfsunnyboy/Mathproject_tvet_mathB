from __future__ import annotations

from core.gencode.problem_type_spec import build_generator_code_prompt


def test_generator_code_prompt_requires_complete_stems_and_unit_soul_tokens():
    prompt = build_generator_code_prompt(
        {
            "problem_type_id": "single_choice_linear_function",
            "display_name": "linear function choice",
        }
    )

    assert "5. STEM COMPLETENESS & SOUL TOKENS:" in prompt
    assert "fully cohesive, human-readable textbook problem" in prompt
    assert "truncated stubs or generic placeholders" in prompt
    assert "choice-based or fallback problem types" in prompt
    assert "passing coordinates, full contextual application stories" in prompt
    assert "'線型函數', 'f(x)', '通過'" in prompt
    assert "complete and verbose mathematical scenario" in prompt
    assert "EVERY random branch, scenario conditional, or fallback string assignment" in prompt
    assert "Truncating text in ANY code path is strictly prohibited" in prompt
    assert "EVERY generated seed MUST be robust and naturally exceed 30 characters" in prompt
    assert prompt.index("4. MULTI-TEMPLATE PRINCIPLE:") < prompt.index(
        "5. STEM COMPLETENESS & SOUL TOKENS:"
    )
