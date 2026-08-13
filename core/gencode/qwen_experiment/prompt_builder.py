# -*- coding: utf-8 -*-
"""Prompt builders for isolated Qwen Gencode experiment."""

from __future__ import annotations

import json
from typing import Any

from core.gencode.qwen_experiment.constants import PROMPT_VERSION


def build_generation_prompt(
    context: dict[str, Any],
    *,
    seed: int,
    prompt_mode: str = "full",
) -> str:
    domain = context.get("domain") if isinstance(context.get("domain"), dict) else {}
    compact = str(prompt_mode or "full").strip().lower() == "compact"
    sections = [
        f"PROMPT_VERSION={PROMPT_VERSION}",
        "You are generating ONE V3 component generate.py for an isolated experiment.",
        "Output ONLY Python source for generate.py (optionally include get_hint in the same file).",
        "Do not modify any other project files. Do not invent production writes.",
        "",
        "## Source example (reference only; do NOT copy fixed stem/answer)",
        f"skill_id: {context.get('skill_id')}",
        f"source_id / component_id: {context.get('component_id')}",
        f"textbook_example_id: {context.get('textbook_example_id')}",
        f"problem_text:\n{context.get('problem_text')}",
        f"correct_answer:\n{context.get('correct_answer')}",
        f"detailed_solution:\n{context.get('detailed_solution')}",
        "",
        "## Seed requirement",
        f"Primary experiment seed={seed}. generate(seed=...) MUST produce legal varied questions.",
        "Forbidden: copy original stem verbatim as only output, fixed constant answer, placeholders.",
        "",
        "## Required generate.py interface / payload schema",
        str(context.get("generate_interface_spec") or ""),
    ]
    if not compact:
        sections.extend(
            [
                "",
                "## Domain reuse (prefer existing capabilities)",
                json.dumps(
                    {
                        "fixed_domain_key": domain.get("fixed_domain_key"),
                        "domain_module": domain.get("domain_module"),
                        "entrypoint": domain.get("entrypoint"),
                        "allowed_operations": domain.get("allowed_operations"),
                        "registry_revision": domain.get("registry_revision"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                "Prefer calling existing domain APIs. If capability is insufficient, you may propose",
                "a candidate capability note in a top-level comment CANDIDATE_CAPABILITY: ...",
                "but must NOT write into core/ or production registries.",
                "",
                "## Allowed checkers",
                ", ".join(context.get("allowed_checkers") or []),
                "",
                "## Answer schema keys",
                ", ".join(context.get("answer_schema_keys") or []),
                "",
                "## One-example one-component rule",
                "This job produces exactly one component directory for this textbook example.",
                "",
                "## Output format",
                "Return a single ```python code fence containing generate.py only.",
            ]
        )
    else:
        sections.append(
            "Return a single ```python code fence with def generate(...). Reuse domain APIs when possible."
        )
    return "\n".join(sections).strip() + "\n"


def build_repair_prompt(
    *,
    previous_code: str,
    validation_errors: dict[str, Any],
    context: dict[str, Any],
    seed: int,
    round_idx: int,
) -> str:
    # Structured errors only — never include hidden oracle / secret test answers.
    safe_errors = {
        "passed": bool(validation_errors.get("passed")),
        "failure_layer": validation_errors.get("failure_layer"),
        "blockers": list(validation_errors.get("blockers") or []),
        "warnings": list(validation_errors.get("warnings") or []),
        "checks": validation_errors.get("checks") if isinstance(validation_errors.get("checks"), dict) else {},
    }
    # Strip any accidental answer fields if present.
    for key in ("hidden_answers", "oracle", "expected_answers", "seed_payloads"):
        safe_errors.pop(key, None)
    checks = safe_errors.get("checks")
    if isinstance(checks, dict):
        checks = {
            k: v
            for k, v in checks.items()
            if k
            not in {
                "sample_payloads",
                "correct_answers",
                "payloads",
            }
        }
        safe_errors["checks"] = checks

    domain = context.get("domain") if isinstance(context.get("domain"), dict) else {}
    return "\n".join(
        [
            f"PROMPT_VERSION={PROMPT_VERSION}",
            f"Repair round={round_idx}. Fix the previous generate.py to satisfy validators.",
            "Return ONLY a corrected ```python code fence.",
            "Do not ask questions. Do not explain outside the code fence.",
            "",
            f"skill_id={context.get('skill_id')} component_id={context.get('component_id')} seed={seed}",
            "",
            "## Previous code",
            "```python",
            previous_code,
            "```",
            "",
            "## Structured validator errors (no hidden answers)",
            json.dumps(safe_errors, ensure_ascii=False, indent=2),
            "",
            "## Necessary contract reminders",
            str(context.get("generate_interface_spec") or ""),
            "",
            "## Domain API summary",
            json.dumps(
                {
                    "fixed_domain_key": domain.get("fixed_domain_key"),
                    "domain_module": domain.get("domain_module"),
                    "entrypoint": domain.get("entrypoint"),
                    "allowed_operations": domain.get("allowed_operations"),
                },
                ensure_ascii=False,
                indent=2,
            ),
            "",
            "Allowed checkers: " + ", ".join(context.get("allowed_checkers") or []),
        ]
    ).strip() + "\n"
