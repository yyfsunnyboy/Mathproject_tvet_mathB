"""Opt-in backfill decisions use the Phase 4 structural identity lookup."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from flask import Flask

import core.textbook_processor_v2 as processor


class _Session:
    def __init__(self):
        self.added = []
        self.commits = 0

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.commits += 1


@pytest.mark.parametrize(
    ("existing", "insert_missing_only", "inserted", "updated", "existing_skipped"),
    [
        (True, False, 0, 1, 0),
        (True, True, 0, 0, 1),
        (False, False, 1, 0, 0),
        (False, True, 1, 0, 0),
    ],
)
def test_phase4_opt_in_backfill(monkeypatch, existing, insert_missing_only, inserted, updated, existing_skipped):
    session = _Session()
    old = SimpleNamespace(id=42, skill_id="existing_skill", problem_text="original", notes=None)
    lookups = []
    monkeypatch.setattr(processor, "db", SimpleNamespace(session=session))
    monkeypatch.setattr(processor, "_DOCX_BLOCK_META", {
        "例1": {
            "source_type": "textbook_example", "anchor": "例1",
            "problem_text": "題目內容足夠長度，供測試使用",
        }
    })
    monkeypatch.setattr(
        processor.ImportAuthorityResolver, "resolve_phase4_item_authority",
        lambda **kwargs: SimpleNamespace(section_code="2-1"),
    )
    monkeypatch.setattr(
        processor, "_phase4_resolve_mathb_formal_binding",
        lambda **kwargs: ("concept", "new_skill", SimpleNamespace()),
    )
    monkeypatch.setattr(
        processor, "validate_existing_skill_binding_for_import",
        lambda *args, **kwargs: (True, ""),
    )
    monkeypatch.setattr(processor, "_curriculum_authority_coords", lambda row: {
        "curriculum": "vocational", "volume": "數學B2",
        "chapter_title": "第2章", "section_title": "2-1 測試", "skill_id": "new_skill",
    })
    monkeypatch.setattr(processor, "_coords_from_curriculum_row", lambda row, info: {"grade": 10})
    monkeypatch.setattr(processor, "_phase4_propagate_curriculum_authority", lambda row, authority, **kwargs: (None, False))

    def find_existing(**kwargs):
        lookups.append(kwargs)
        return old if existing else None

    monkeypatch.setattr(processor, "_find_existing_by_structural_title", find_existing)
    monkeypatch.setattr(processor, "_find_existing_by_structural_title_any_skill", lambda **kwargs: None)
    parsed = {"chapters": [{"chapter_title": "第2章", "sections": [{
        "section_title": "2-1 測試", "section_code": "2-1",
        "concepts": [{"concept_name": "concept", "examples": [{"title": "例1"}], "practice_questions": []}],
    }]}]}
    stats = processor.phase4_absolute_hydrate_and_save(
        parsed, {"例1": "題目內容足夠長度，供測試使用"},
        {"curriculum": "vocational", "volume": "數學B2", "grade": 10, "source_scope": "section_textbook"},
        None, insert_missing_only=insert_missing_only,
    )
    assert lookups and lookups[0]["title"] == "例1"
    assert (stats["inserted"], stats["updated"], stats["existing_skipped"]) == (
        inserted, updated, existing_skipped
    )
    assert len(session.added) == inserted
    assert session.commits == 1
    if existing and insert_missing_only:
        assert old.problem_text == "original"
        assert stats["backfill_decisions"] == [{
            "source_type": "textbook_example", "source_label": "例1",
            "existing_db_id": 42, "skill_id": "existing_skill",
            "decision": "EXISTING_SKIP",
        }]
    elif existing:
        assert old.problem_text != "original"
    elif insert_missing_only:
        assert stats["backfill_decisions"][0]["decision"] == "NEW_INSERT"
        assert stats["backfill_decisions"][0]["existing_db_id"] is None
    else:
        assert stats["backfill_decisions"] == []


def test_scoped_backfill_dry_run_stops_before_db_write(monkeypatch, tmp_path):
    import core.textbook_importer_v3_pipeline as pipeline
    import core.textbook_importer_v3_scope as scope

    source = tmp_path / "2-1-source.docx"
    source.write_bytes(b"test source")
    monkeypatch.setattr(pipeline, "parse_docx_summary", lambda *args, **kwargs: {"summary": {}})

    def fake_convert(_source, output):
        output.write_bytes(b"converted")
        return {"mathtype_ole": 0, "converted_ok": 0, "converted_failed": 0}

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    monkeypatch.setattr(pipeline, "build_curriculum_info_for_v3_import", lambda **kwargs: {
        "curriculum": "vocational", "volume": "數學B2", "source_scope": "section_textbook",
    })
    monkeypatch.setattr(scope, "analyze_scoped_conversion", lambda *args: {
        "counts": {"required_formula_failed": 0}, "unresolved": [],
        "failures": [], "would_write_count": 1,
    })
    monkeypatch.setattr(pipeline, "ensure_db_backup", lambda **kwargs: pytest.fail("DB write reached"))
    monkeypatch.setattr(processor, "phase4_absolute_hydrate_and_save", lambda *args, **kwargs: pytest.fail("Phase 4 reached"))
    result = pipeline.run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", allow_phase4=False,
        target_source_types={"textbook_example", "advanced_exercise"},
        insert_missing_only=True, app=Flask("backfill_dry_run_test"),
    )
    assert result["ok"] is True
    assert result["would_write"] == 1
    assert "db_write" not in result["metrics"]
