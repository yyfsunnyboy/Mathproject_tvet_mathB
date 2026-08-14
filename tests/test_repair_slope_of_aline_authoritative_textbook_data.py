import json
import sqlite3

from scripts.repair_slope_of_aline_authoritative_textbook_data import (
    AUTHORITATIVE_PATCHES,
    TARGET_IDS,
    TARGET_SKILL_ID,
    apply_patch,
)


def _make_db(path):
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            skill_id TEXT,
            source_description TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            notes TEXT,
            source_volume TEXT,
            source_section TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO textbook_examples
        (id, skill_id, source_description, problem_text, correct_answer, detailed_solution, notes)
        VALUES
        (4519, ?, '例題 [source_type=textbook_example]', '舊4519', 'old', 'old', '{"keep":true}'),
        (4520, ?, '例題 [source_type=textbook_example]', '舊4520', 'old', 'old', '{}'),
        (4533, ?, '例題 [source_type=textbook_example]', '舊4533', 'old', 'old', '{}'),
        (4534, ?, '例題 [source_type=textbook_example]', '舊4534', 'old', 'old', '{}'),
        (4601, ?, '例題 [source_type=textbook_example]', '舊4601', 'old', 'old', '{}'),
        (9999, 'vh_數學B1_OtherSkill', '其他', '不變', 'x', 'y', '{}')
        """,
        (TARGET_SKILL_ID, TARGET_SKILL_ID, TARGET_SKILL_ID, TARGET_SKILL_ID, TARGET_SKILL_ID),
    )
    conn.commit()
    return conn


def test_dry_run_does_not_write(tmp_path):
    db = tmp_path / "repair.sqlite"
    conn = _make_db(db)
    report = apply_patch(conn, write=False)
    assert report["updated_records"] == len(TARGET_IDS)
    assert report["skipped_records"] == 0
    row = conn.execute("SELECT problem_text FROM textbook_examples WHERE id=4519").fetchone()
    assert row["problem_text"] == "舊4519"
    conn.close()


def test_write_updates_only_scoped_fields(tmp_path):
    db = tmp_path / "repair.sqlite"
    conn = _make_db(db)
    report = apply_patch(conn, write=True, repaired_at="20260814T000000Z")
    assert report["updated_records"] == len(TARGET_IDS)
    assert report["updated_ids"] == list(TARGET_IDS)

    row4519 = conn.execute(
        "SELECT problem_text, correct_answer, detailed_solution, notes FROM textbook_examples WHERE id=4519"
    ).fetchone()
    assert row4519["problem_text"] == AUTHORITATIVE_PATCHES[4519]["problem_text"]
    assert row4519["correct_answer"] == AUTHORITATIVE_PATCHES[4519]["correct_answer"]
    assert row4519["detailed_solution"] == AUTHORITATIVE_PATCHES[4519]["detailed_solution"]
    notes = json.loads(row4519["notes"])
    assert notes["keep"] is True
    assert notes["formal_data_repair"]["skill_id"] == TARGET_SKILL_ID

    other = conn.execute("SELECT problem_text FROM textbook_examples WHERE id=9999").fetchone()
    assert other["problem_text"] == "不變"
    conn.close()


def test_idempotent_second_run_skips(tmp_path):
    db = tmp_path / "repair.sqlite"
    conn = _make_db(db)
    first = apply_patch(conn, write=True, repaired_at="20260814T000000Z")
    assert first["updated_records"] == len(TARGET_IDS)
    second = apply_patch(conn, write=True, repaired_at="20260814T000001Z")
    assert second["updated_records"] == 0
    assert second["skipped_records"] == len(TARGET_IDS)
    conn.close()


def test_rejects_skill_mismatch(tmp_path):
    db = tmp_path / "repair.sqlite"
    conn = _make_db(db)
    conn.execute(
        "UPDATE textbook_examples SET skill_id=? WHERE id=?",
        ("vh_數學B1_WrongSkill", 4519),
    )
    conn.commit()
    report = apply_patch(conn, write=True, repaired_at="20260814T000000Z")
    assert report["rejected_records"] == 1
    assert report["updated_records"] == len(TARGET_IDS) - 1
    row = conn.execute("SELECT problem_text FROM textbook_examples WHERE id=4519").fetchone()
    assert row["problem_text"] == "舊4519"
    conn.close()
