# -*- coding: utf-8 -*-
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DB = ROOT / "instance" / "kumon_math.db"
RESULT = ROOT / "reports" / "b2_2_1_scoped_import_formal_result.json"


def sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    print("DB files:")
    for p in [DB, Path(str(DB) + "-wal"), Path(str(DB) + "-shm")]:
        print(" ", p.name, "exists=", p.is_file(), "sha=", sha(p), "size=", p.stat().st_size if p.is_file() else None)

    # Force checkpoint via Python sqlite
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA wal_checkpoint(FULL)")
    except Exception as e:
        print("checkpoint err", e)
    conn.close()

    print("After checkpoint main sha:", sha(DB))
    print("Before sha from report:", result["before"]["sha256"])

    conn = sqlite3.connect(DB)
    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("textbook_examples", "skills_info", "skill_curriculum")
    }
    print("COUNTS", counts)

    rows = conn.execute(
        """
        SELECT id, problem_type, source_description, skill_id, source_section, source_chapter,
               substr(problem_text,1,60), notes
        FROM textbook_examples
        WHERE source_curriculum='vocational' AND source_volume='數學B2'
          AND (source_section LIKE '%2-1%' OR source_section LIKE '%正弦定理%')
        ORDER BY id
        """
    ).fetchall()
    print("SECTION_ROWS", len(rows))
    for r in rows:
        desc = r[2] or ""
        m = re.search(r"source_type=([^\s|\]]+)", desc)
        st = m.group(1) if m else r[1]
        title = desc.split(" [", 1)[0]
        notes = r[7] or ""
        print(json.dumps({
            "id": r[0],
            "problem_type": r[1],
            "inferred_source_type": st,
            "label": title,
            "skill_id": r[3],
            "section": r[4],
            "chapter": r[5],
            "problem_start": r[6],
            "notes_len": len(notes),
            "has_visual": "visual" in notes.lower() if notes else False,
        }, ensure_ascii=False))

    # new skills
    skills = conn.execute(
        """
        SELECT si.skill_id, si.skill_ch_name, si.skill_en_name, sc.section, sc.paragraph
        FROM skills_info si
        LEFT JOIN skill_curriculum sc ON sc.skill_id = si.skill_id
        WHERE si.skill_id LIKE 'vh_數學B2_SubSection_2_1_%'
        ORDER BY si.skill_id
        """
    ).fetchall()
    print("NEW_SKILLS")
    for s in skills:
        print(s)

    # student tables unchanged?
    for t in ("adaptive_learning_logs", "practice_attempts", "student_mastery", "class_students"):
        try:
            n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"TABLE {t}: {n}")
        except Exception as e:
            print(f"TABLE {t}: skip ({e})")
    conn.close()


if __name__ == "__main__":
    main()
