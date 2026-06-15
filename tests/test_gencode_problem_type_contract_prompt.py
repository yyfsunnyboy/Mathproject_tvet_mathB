from __future__ import annotations

from core.gencode.problem_type_spec import build_generator_code_prompt


def test_generator_code_prompt_requires_complete_stems_and_semantic_contract_tokens():
    prompt = build_generator_code_prompt(
        {
            "problem_type_id": "single_choice_linear_function",
            "display_name": "linear function choice",
        }
    )

    assert "5. STEM COMPLETENESS & REQUIRED CONCEPT TOKENS:" in prompt
    assert "fully cohesive, human-readable textbook problem" in prompt
    assert "truncated stubs or generic placeholders" in prompt
    assert "choice-based or fallback problem types" in prompt
    assert "semantic_contract.required_concepts" in prompt
    assert "provided source examples" in prompt
    assert "EVERY random branch, scenario conditional, or fallback string assignment" in prompt
    assert "Truncating text in ANY code path is strictly prohibited" in prompt
    assert "EVERY generated seed MUST be robust and naturally exceed 30 characters" in prompt
    assert prompt.index("4. MULTI-TEMPLATE PRINCIPLE:") < prompt.index(
        "5. STEM COMPLETENESS & REQUIRED CONCEPT TOKENS:"
    )

    # Constraint 6 assertions
    assert "6. SLOT REGISTRATION DEFENSE & LATEX WRAPPING FOR TEXT_SHORT:" in prompt
    assert "registered 'text_short' slot" in prompt
    assert "strictly forbidden from inventing unregistered slot names" in prompt
    assert "standard LaTeX dollar delimiters $...$" in prompt
    assert "double escaped (e.g., {{...}})" in prompt
    assert "degradation to runtime_ready_with_warning" in prompt
    assert prompt.index("5. STEM COMPLETENESS & REQUIRED CONCEPT TOKENS:") < prompt.index(
        "6. SLOT REGISTRATION DEFENSE & LATEX WRAPPING FOR TEXT_SHORT:"
    )
