# AI Gencode Prompt Template (v0.1)

## Role
You are a Senior Python Mathematics Generator Engineer. Your goal is to produce a robust, deterministic math problem generator function.

## Task Overview
Generate a Python generator function for the following `problem_type`:
- **Problem Type ID**: {{problem_type_id}}
- **Display Name**: {{display_name}}
- **Answer Type**: {{answer_type}}
- **Checker Type**: {{checker_type}}
- **ProblemTypeSpec**: {{problem_type_spec_json}}

## Reference Textbook Examples
{{examples_context}}

## Constraints & Requirements
0. **Contract-first generation flow (mandatory)**:
   - Step 1: confirm selected `problem_type_id`.
   - Step 2: read `answer_contract / stem_contract / dependency_contract / semantic_contract`.
   - Step 3: output a short `generator_plan` comment block.
   - Step 4: then implement `generate()`.
1. **Output Contract**: The function must return a `generator_payload` dict containing:
   - `question_text`: (string, LaTeX supported)
   - `answer`: (string/int depending on answer_type)
   - `answer_type`
   - `choices`
   - `explanation`: (string, detailed steps)
   - `problem_type_id`
   - `diagnosis_tags`
   - `metadata.givens`
   - `metadata.target`
   - `metadata.derivation`
2. **Domain Functions Only**: You MUST use the following allowed functions and NO OTHERS:
   - {{allowed_domain_functions}}
3. **NO Hallucination**: Do NOT implement your own math logic for standard operations (GCD, LCM, etc.). Use the provided domain functions.
4. **Deterministic**: Use the `random` module with the provided `seed` for reproducibility.
5. **Pure Python**: Output ONLY the Python code block. No explanation text outside the code.

## Forbidden Patterns
- No `eval()` or `exec()`.
- No `while True` without a counter limit.
- No external module imports except for `math`, `random`, and `fractions`.
- Do not embed `(A)(B)(C)(D)` options inside `question_text` when `choices` exists.

## Template Code Structure
```python
def generate(*, level=1, seed=None, **kwargs):
    # Setup random
    import random
    rng = random.Random(seed)
    
    # Logic here
    # ...
    
    return {
        "question_text": "...",
        "answer": "...",
        "explanation": "...",
        "metadata": {
            "problem_type_id": "{{problem_type_id}}",
            # ...
        }
    }
```
