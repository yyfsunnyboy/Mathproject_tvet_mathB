# -*- coding: utf-8 -*-
"""Bootstrap default prompt templates into database."""

from core.models.prompt_template import PromptTemplate
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from models import db


def bootstrap_prompt_templates() -> int:
    created_count = 0

    for prompt_key, template in DEFAULT_PROMPT_TEMPLATES.items():
        existing = (
            db.session.query(PromptTemplate)
            .filter(PromptTemplate.prompt_key == prompt_key)
            .first()
        )
        if existing:
            continue

        default_content = template["content"]
        record = PromptTemplate(
            prompt_key=prompt_key,
            title=template["title"],
            category=template["category"],
            description=template.get("description"),
            usage_context=template.get("usage_context", ""),
            used_in=template.get("used_in", ""),
            example_trigger=template.get("example_trigger", ""),
            content=default_content,
            default_content=default_content,
            required_variables=template.get("required_variables", ""),
            is_active=bool(template.get("is_active", True)),
        )
        db.session.add(record)
        created_count += 1

    if created_count > 0:
        db.session.commit()

    return created_count

