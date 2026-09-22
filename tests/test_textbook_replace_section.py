"""Replace-section safety tests use a simulated session, never the project DB."""

from __future__ import annotations

import sqlite3
from types import SimpleNamespace

import pytest
from flask import Flask

import core.textbook_importer_v3_pipeline as pipeline
import core.textbook_processor_v2 as processor
import models


INFO = {
    "curriculum": "vocational", "grade": 10, "volume": "數學B2",
    "chapter": "第2章 三角函數的應用", "section": "2-1 正弦定理與餘弦定理",
    "source_scope": "section_textbook",
}


def test_replace_scope_requires_exact_grade_and_section():
    coords = pipeline._replace_section_coords(INFO)
    assert coords == {
        "source_curriculum": "vocational", "source_volume": "數學B2",
        "source_chapter": INFO["chapter"], "source_section": INFO["section"],
    }
    for changed in ({"grade": 11}, {"section": ""}, {"source_scope": "chapter_self_assessment"}):
        with pytest.raises(pipeline.V3PipelineError):
            pipeline._replace_section_coords({**INFO, **changed})


def test_replace_requires_verified_backup_before_delete():
    for backup_info in ({"created": False}, {"created": True, "backup_path": "missing-backup.db"}):
        with pytest.raises(pipeline.V3PipelineError) as exc:
            pipeline._require_verified_replace_backup(backup_info)
        assert exc.value.error_code == "db_backup_failed"


def test_replace_backup_includes_committed_wal_rows(tmp_path):
    db_dir = tmp_path / "instance"
    db_dir.mkdir()
    db_path = db_dir / "kumon_math.db"
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY)")
        connection.execute("INSERT INTO sample (id) VALUES (1)")
        connection.commit()
        backup = pipeline.ensure_db_backup(project_root=tmp_path, label="replace_test", online=True)
        pipeline._require_verified_replace_backup(backup)
        with sqlite3.connect(backup["backup_path"]) as saved:
            assert saved.execute("SELECT id FROM sample").fetchall() == [(1,)]
    finally:
        connection.close()


@pytest.mark.parametrize("failure", ["formula", "parser"])
def test_replace_preflight_failure_keeps_existing_rows(monkeypatch, tmp_path, failure):
    import core.textbook_importer_v3_scope as scope

    source = tmp_path / "2-1-source.docx"
    source.write_bytes(b"source")
    old_rows = [1, 2]
    monkeypatch.setattr(pipeline, "parse_docx_summary", lambda *args, **kwargs: {"summary": {}})

    def fake_convert(_source, output):
        output.write_bytes(b"converted")
        return {"mathtype_ole": 1, "converted_ok": 1, "converted_failed": 0}

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    monkeypatch.setattr(pipeline, "build_curriculum_info_for_v3_import", lambda **kwargs: dict(INFO))
    monkeypatch.setattr(scope, "analyze_scoped_conversion", lambda *args: {
        "counts": {"required_formula_failed": 1 if failure == "formula" else 0},
        "unresolved": [], "failures": ["formula"] if failure == "formula" else [],
        "target_count": 1, "would_write_count": 1,
    })
    monkeypatch.setattr(processor, "phase1_extract_docx_lines", lambda *args, **kwargs: ["2-1 source"])
    monkeypatch.setattr(processor, "_resolve_import_source_metadata", lambda **kwargs: {
        "curriculum_info": dict(INFO), "source_scope": "section_textbook",
    })
    monkeypatch.setattr(pipeline, "audit_v3_skill_extraction", lambda *args: {
        "curriculum_binding": "FAIL", "curriculum_info": dict(INFO),
    })
    monkeypatch.setattr(pipeline, "_replace_section_transaction", lambda **kwargs: pytest.fail("delete reached"))
    monkeypatch.setattr(pipeline, "ensure_db_backup", lambda **kwargs: pytest.fail("backup reached"))
    result = pipeline.run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", target_source_types={"textbook_example"},
        import_mode="replace_section", app=Flask("replace_preflight_test"),
    )
    assert result["ok"] is False
    assert old_rows == [1, 2]


def test_replace_dry_run_reports_scope_without_db_changes(monkeypatch, tmp_path):
    import core.textbook_importer_v3_scope as scope
    import core.textbook_formal_concept as formal_concept

    source = tmp_path / "2-1-source.docx"
    source.write_bytes(b"source")
    session = SimpleNamespace(rollback=lambda: None)
    monkeypatch.setattr(models, "db", SimpleNamespace(session=session))
    monkeypatch.setattr(pipeline, "parse_docx_summary", lambda *args, **kwargs: {"summary": {}})

    def fake_convert(_source, output):
        output.write_bytes(b"converted")
        return {"mathtype_ole": 1, "converted_ok": 1, "converted_failed": 0}

    monkeypatch.setattr(pipeline, "convert_docx_mathtype_to_latex_docx", fake_convert)
    info = dict(INFO, structural_skill_candidates=[{"skill_id": "skill"}])
    monkeypatch.setattr(pipeline, "build_curriculum_info_for_v3_import", lambda **kwargs: dict(info))
    monkeypatch.setattr(scope, "analyze_scoped_conversion", lambda *args: {
        "counts": {"required_formula_failed": 0, "required_formula_success": 1},
        "unresolved": [], "failures": [], "target_count": 1, "would_write_count": 1,
        "target_source_type_counts": {"textbook_example": 1},
    })
    monkeypatch.setattr(processor, "phase1_extract_docx_lines", lambda *args, **kwargs: ["2-1 source"])
    monkeypatch.setattr(processor, "_resolve_import_source_metadata", lambda **kwargs: {
        "curriculum_info": dict(info), "source_scope": "section_textbook",
    })
    monkeypatch.setattr(pipeline, "audit_v3_skill_extraction", lambda *args: {
        "curriculum_binding": "PASS", "curriculum_info": dict(info), "skill_candidates": [],
    })
    monkeypatch.setattr(pipeline, "_fill_chapter_section_from_outline_or_lines", lambda info, lines: info)
    monkeypatch.setattr(processor, "_lookup_outline_section_curriculum_row", lambda *args: SimpleNamespace(
        skill_id="outline", chapter=INFO["chapter"], section=INFO["section"],
    ))

    def fake_phase2(*args, **kwargs):
        assert kwargs["read_only"] is True
        processor._DOCX_BLOCK_META = {"例1": {"source_type": "textbook_example", "anchor": "例1"}}
        return {"例1": "題目內容足夠長度"}

    monkeypatch.setattr(processor, "phase2_deterministic_block_slice", fake_phase2)
    monkeypatch.setattr(formal_concept, "get_section_formal_skill_candidates", lambda **kwargs: [])
    monkeypatch.setattr(processor, "phase3_ai_metadata_alignment", lambda *args: {
        "chapters": [{"sections": [{"concepts": [{"examples": [{"title": "例1"}], "practice_questions": []}]}]}],
    })
    monkeypatch.setattr(pipeline, "_attach_anchor_notes_to_phase3", lambda *args: ([], {"collision_count": 0}))
    monkeypatch.setattr(pipeline, "_replace_section_existing_rows", lambda info: (
        pipeline._replace_section_coords(info), [SimpleNamespace(id=42)],
    ))
    monkeypatch.setattr(pipeline, "ensure_db_backup", lambda **kwargs: pytest.fail("backup reached"))
    monkeypatch.setattr(pipeline, "_replace_section_transaction", lambda **kwargs: pytest.fail("delete reached"))
    result = pipeline.run_v3_pair_pipeline(
        project_root=tmp_path, docx_path=source, pdf_path=None,
        curriculum="vocational", volume="數學B2", target_source_types={"textbook_example"},
        import_mode="replace_section", allow_phase4=False, app=Flask("replace_dry_run_test"),
    )
    assert result["ok"] is True, result.get("error")
    preview = result["metrics"]["replace_preview"]
    assert preview["would_delete"] == [42]
    assert preview["would_insert"] == 1
    assert preview["formula_status"]["required_formula_success"] == 1
    assert preview["db_actual_changes"] == 0


@pytest.mark.parametrize("fail_insert", [False, True])
def test_replace_transaction_scope_and_rollback(monkeypatch, fail_insert):
    rows = [
        SimpleNamespace(id=1, source_curriculum="vocational", source_volume="數學B2",
                        source_chapter=INFO["chapter"], source_section=INFO["section"]),
        SimpleNamespace(id=2, source_curriculum="vocational", source_volume="數學B2",
                        source_chapter=INFO["chapter"], source_section="2-2 三角測量"),
        SimpleNamespace(id=3, source_curriculum="vocational", source_volume="數學B1",
                        source_chapter=INFO["chapter"], source_section=INFO["section"]),
    ]
    original_ids = [row.id for row in rows]
    events = []

    class FakeQuery:
        def __init__(self, criteria=None):
            self.criteria = criteria or {}

        def filter_by(self, **criteria):
            return FakeQuery(criteria)

        def all(self):
            return [row for row in rows if all(getattr(row, key) == value for key, value in self.criteria.items())]

        def delete(self, **kwargs):
            victims = self.all()
            events.append(("delete", [row.id for row in victims]))
            rows[:] = [row for row in rows if row not in victims]
            return len(victims)

    class FakeSession:
        def query(self, model):
            return FakeQuery()

        def connection(self):
            return SimpleNamespace(exec_driver_sql=lambda *args: SimpleNamespace(scalar_one=lambda: 0))

        def commit(self):
            events.append(("commit", None))

        def rollback(self):
            events.append(("rollback", None))
            rows[:] = initial_rows[:]

    initial_rows = rows[:]
    fake_model = SimpleNamespace(query=FakeQuery())
    monkeypatch.setattr(models, "TextbookExample", fake_model)
    monkeypatch.setattr(models, "db", SimpleNamespace(session=FakeSession()))

    def fake_phase4(*args, **kwargs):
        assert kwargs["commit"] is False
        assert [row.id for row in rows] == [2, 3]
        events.append(("insert", None))
        rows.append(SimpleNamespace(id=4, **pipeline._replace_section_coords(INFO)))
        if fail_insert:
            raise RuntimeError("insert failed")
        return {"inserted": 1, "updated": 0}

    monkeypatch.setattr(processor, "phase4_absolute_hydrate_and_save", fake_phase4)
    if fail_insert:
        with pytest.raises(RuntimeError, match="insert failed"):
            pipeline._replace_section_transaction(
                curriculum_info=INFO, phase3_parsed={}, question_blocks={"例1": "problem"},
                target_source_types={"textbook_example"}, task_queue=None,
            )
        assert [row.id for row in rows] == original_ids
        assert events == [("delete", [1]), ("insert", None), ("rollback", None)]
    else:
        stats, deleted_ids, coords = pipeline._replace_section_transaction(
            curriculum_info=INFO, phase3_parsed={}, question_blocks={"例1": "problem"},
            target_source_types={"textbook_example"}, task_queue=None,
        )
        assert stats["inserted"] == 1 and deleted_ids == [1]
        assert coords["source_section"] == INFO["section"]
        assert [row.id for row in rows] == [2, 3, 4]
        assert events == [("delete", [1]), ("insert", None), ("commit", None)]
