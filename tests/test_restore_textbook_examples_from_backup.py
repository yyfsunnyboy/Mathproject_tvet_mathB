import sqlite3

import pandas as pd

from scripts.restore_textbook_examples_from_backup import restore_section


def _make_db(path):
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE textbook_examples (
            id INTEGER PRIMARY KEY,
            source_volume TEXT,
            source_section TEXT,
            source_description TEXT,
            problem_text TEXT,
            correct_answer TEXT,
            detailed_solution TEXT,
            notes TEXT
        )
        """
    )
    rows = [
        (1, "數學B1", "1-1 數線與絕對值", "例題1 [dedupe=aaa]", "[FORMULA_IMAGE_1]=7", "", "略", '{"formula_assets":[1]}'),
        (2, "數學B1", "1-1 數線與絕對值", "例題2 [dedupe=bbb]", "試求 \\(|x|<3\\)", "x", "完整解析", '{"keep":true}'),
    ]
    conn.executemany(
        """
        INSERT INTO textbook_examples
        (id, source_volume, source_section, source_description, problem_text, correct_answer, detailed_solution, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    conn.close()


def _make_xlsx(path):
    df = pd.DataFrame(
        [
            {
                "source_volume": "數學B1",
                "source_section": "1-1 數線與絕對值",
                "source_description": "例題1 [dedupe=aaa]",
                "problem_text": "例題1：\\(|x|=7\\)",
                "correct_answer": "\\(x=\\pm 7\\)",
                "detailed_solution": "由絕對值定義可得。",
                "notes": '{"old":true}',
            },
            {
                "source_volume": "數學B1",
                "source_section": "1-1 數線與絕對值",
                "source_description": "例題2 [dedupe=bbb]",
                "problem_text": "[FORMULA_IMAGE_1]<3",
                "correct_answer": "",
                "detailed_solution": "略",
                "notes": '{"old":true}',
            },
        ]
    )
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, sheet_name="textbook_examples", index=False)


def test_restore_dry_run_does_not_write_and_preserves_notes(tmp_path):
    db = tmp_path / "test.db"
    xlsx = tmp_path / "backup.xlsx"
    report = tmp_path / "report.md"
    _make_db(db)
    _make_xlsx(xlsx)

    stats = restore_section(
        xlsx=xlsx,
        db_path=db,
        volume="數學B1",
        section="1-1 數線與絕對值",
        write=False,
        report=report,
    )

    assert stats["matched_records"] == 2
    assert stats["backup_better_records"] == 1
    conn = sqlite3.connect(str(db))
    row = conn.execute("SELECT problem_text, notes FROM textbook_examples WHERE id=1").fetchone()
    conn.close()
    assert row[0] == "[FORMULA_IMAGE_1]=7"
    assert row[1] == '{"formula_assets":[1]}'


def test_restore_write_updates_only_better_text_and_keeps_notes(tmp_path):
    db = tmp_path / "test.db"
    xlsx = tmp_path / "backup.xlsx"
    report = tmp_path / "report.md"
    _make_db(db)
    _make_xlsx(xlsx)

    stats = restore_section(
        xlsx=xlsx,
        db_path=db,
        volume="數學B1",
        section="1-1 數線與絕對值",
        write=True,
        report=report,
    )

    assert stats["updated_records"] == 1
    conn = sqlite3.connect(str(db))
    row1 = conn.execute("SELECT problem_text, correct_answer, detailed_solution, notes FROM textbook_examples WHERE id=1").fetchone()
    row2 = conn.execute("SELECT problem_text, correct_answer, detailed_solution, notes FROM textbook_examples WHERE id=2").fetchone()
    conn.close()
    assert row1[0] == "例題1：\\(|x|=7\\)"
    assert row1[1] == "\\(x=\\pm 7\\)"
    assert row1[2] == "由絕對值定義可得。"
    assert row1[3] == '{"formula_assets":[1]}'
    assert row2[0] == "試求 \\(|x|<3\\)"
    assert row2[3] == '{"keep":true}'
