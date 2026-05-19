import json
import sqlite3

from scripts.apply_canonical_problem_text_patch import apply_patch


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
    conn.execute(
        """
        INSERT INTO textbook_examples
        (id, source_volume, source_section, source_description, problem_text, correct_answer, detailed_solution, notes)
        VALUES
        (1,'數學B1','1-1 數線與絕對值','例1 [source_type=textbook_example]','舊題幹 [FORMULA_IMAGE_1]','ans1','sol1','{"formula_assets":[{"placeholder_token":"[FORMULA_IMAGE_1]"}],"needs_formula_review":true}'),
        (2,'數學B1','1-1 數線與絕對值','隨堂練習 1 [source_type=in_class_practice]','舊題幹2 [FORMULA_MISSING]','ans2','sol2','{}'),
        (3,'數學B1','1-1 數線與絕對值','其他題目','不變','ans3','sol3','{}')
        """
    )
    conn.commit()
    return conn


def test_patch_dry_run_and_write(tmp_path):
    db = tmp_path / "patch.sqlite"
    conn = _make_db(db)
    report = apply_patch(conn, write=False)
    assert report["matched_records"] == 2
    assert report["updated_records"] == 2
    row = conn.execute("SELECT problem_text FROM textbook_examples WHERE id=1").fetchone()[0]
    assert "[FORMULA_IMAGE_1]" in row
    conn.close()

    conn2 = sqlite3.connect(str(db))
    report2 = apply_patch(conn2, write=True)
    assert report2["updated_records"] == 2
    r1 = conn2.execute(
        "SELECT problem_text, correct_answer, detailed_solution, notes FROM textbook_examples WHERE id=1"
    ).fetchone()
    assert "$\\left| x \\right|=7$" in r1[0]
    assert r1[1] == "ans1"
    assert r1[2] == "sol1"
    notes1 = json.loads(r1[3])
    assert notes1.get("needs_formula_review") is False
    assert notes1.get("formula_missing") is False
    assert notes1.get("review_required") is False
    assert notes1.get("formula_assets")
    conn2.close()
