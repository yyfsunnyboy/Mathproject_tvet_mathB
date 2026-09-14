from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from app import create_app
from core.backup.backup_validator import build_and_validate_export
from core.data_importer import FULL_CONFIRM_TOKEN, import_excel_to_db
from core.models.prompt_template import PromptTemplate
from core.prompts.bootstrap_templates import bootstrap_prompt_templates
from core.prompts.default_templates import DEFAULT_PROMPT_TEMPLATES
from core.prompts.registry import get_prompt_with_source
from models import db


@pytest.fixture()
def prompt_app(tmp_path):
    import config as config_module

    db_path = tmp_path / "prompt-backup.db"
    previous_uri = config_module.Config.SQLALCHEMY_DATABASE_URI
    config_module.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(db_path).replace("\\", "/")
    try:
        app = create_app()
        app.config.update(TESTING=True)
        with app.app_context():
            yield app, tmp_path
    finally:
        config_module.Config.SQLALCHEMY_DATABASE_URI = previous_uri


def _snapshot():
    columns = [
        "id",
        "prompt_key",
        "title",
        "category",
        "description",
        "content",
        "default_content",
        "required_variables",
        "usage_context",
        "used_in",
        "example_trigger",
        "is_active",
    ]
    rows = PromptTemplate.query.order_by(PromptTemplate.prompt_key).all()
    return {
        row.prompt_key: {column: getattr(row, column) for column in columns}
        for row in rows
    }


def test_full_backup_restore_round_trips_prompt_templates(prompt_app):
    _app, tmp_path = prompt_app
    PromptTemplate.query.delete()
    prompts = [
        PromptTemplate(
            prompt_key="roundtrip_tutor",
            title="Tutor",
            category="tutor",
            description="first prompt",
            content="runtime content A {question}",
            default_content="default content A {question}",
            required_variables="question",
            usage_context="practice",
            used_in="test",
            example_trigger="ask",
            is_active=True,
        ),
        PromptTemplate(
            prompt_key="roundtrip_handwriting",
            title="Handwriting",
            category="vision",
            description="second prompt",
            content="runtime content B {image}",
            default_content="default content B {image}",
            required_variables="image",
            usage_context="whiteboard",
            used_in="test",
            example_trigger="submit",
            is_active=False,
        ),
    ]
    db.session.add_all(prompts)
    db.session.commit()
    expected = _snapshot()

    frame = pd.read_sql_table("prompt_templates", db.engine)
    payload, summary = build_and_validate_export(
        mode="full",
        engine=db.engine,
        frames={"prompt_templates": frame},
        expected_tables=["prompt_templates"],
        source_counts={"prompt_templates": len(frame)},
        source_database_name=Path(str(db.engine.url.database)).name,
    )
    assert summary["table_count"] == 1
    assert summary["total_rows"] == 2
    backup_path = tmp_path / "prompt-full-backup.xlsx"
    backup_path.write_bytes(payload)

    PromptTemplate.query.filter_by(prompt_key="roundtrip_tutor").update(
        {"content": "corrupted", "default_content": "corrupted", "is_active": False}
    )
    PromptTemplate.query.filter_by(prompt_key="roundtrip_handwriting").delete()
    db.session.commit()

    ok, message = import_excel_to_db(
        str(backup_path), mode="full", confirm_full_clear=FULL_CONFIRM_TOKEN
    )
    assert ok is True, message
    assert _snapshot() == expected


def test_bundled_defaults_seed_only_when_prompt_table_is_empty(prompt_app):
    PromptTemplate.query.delete()
    db.session.commit()

    assert bootstrap_prompt_templates() == len(DEFAULT_PROMPT_TEMPLATES)
    assert PromptTemplate.query.count() == len(DEFAULT_PROMPT_TEMPLATES)

    row = PromptTemplate.query.filter_by(prompt_key="chat_tutor_prompt").one()
    row.content = "admin-owned runtime override"
    db.session.commit()

    assert bootstrap_prompt_templates() == 0
    assert PromptTemplate.query.filter_by(prompt_key="chat_tutor_prompt").one().content == "admin-owned runtime override"


def test_runtime_prefers_db_and_uses_bundled_default_only_when_missing(prompt_app):
    row = PromptTemplate.query.filter_by(prompt_key="chat_tutor_prompt").one()
    row.content = "db is authoritative"
    db.session.commit()

    content, source = get_prompt_with_source("chat_tutor_prompt", "chat_ai_prompt")
    assert (content, source) == ("db is authoritative", "db_prompt_template")

    db.session.delete(row)
    db.session.commit()
    content, source = get_prompt_with_source("chat_tutor_prompt", "chat_ai_prompt")
    assert content == DEFAULT_PROMPT_TEMPLATES["chat_tutor_prompt"]["content"]
    assert source == "default_template"
