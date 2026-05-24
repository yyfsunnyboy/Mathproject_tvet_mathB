# -*- coding: utf-8 -*-
import os
import re
import sqlite3
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def find_b1_self_assessment_docx() -> str | None:
    gdrive = r"E:\Google Drive"
    if not os.path.isdir(gdrive):
        return None
    account_dirs = [os.path.join(gdrive, n) for n in os.listdir(gdrive)]
    hits: list[str] = []
    for acc in account_dirs:
        if not os.path.isdir(acc):
            continue
        for dirpath, dirnames, filenames in os.walk(acc):
            if dirpath.count(os.sep) - acc.count(os.sep) > 8:
                dirnames[:] = []
                continue
            for fn in filenames:
                if not fn.lower().endswith(".docx"):
                    continue
                path = os.path.join(dirpath, fn)
                try:
                    with zipfile.ZipFile(path) as z:
                        xml = z.read("word/document.xml").decode("utf-8", "ignore")
                except Exception:
                    continue
                if (
                    "自我評量" in xml
                    and "1-1" in xml
                    and "1-2" in xml
                    and "1-3" in xml
                    and "1-4" in xml
                ):
                    hits.append(path)
    if not hits:
        return None
    for p in hits:
        if os.path.basename(p) == "第一章 自我評量-課本_Latex.docx":
            return p
    for p in hits:
        bn = os.path.basename(p)
        if "自我評量" in bn and "B1" in bn:
            return p
    for p in hits:
        if "自我評量" in os.path.basename(p):
            return p
    return hits[0]


def query_db():
    db = os.path.join(ROOT, "instance", "kumon_math.db")
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    out = []
    out.append("=== Q1-20 FROM DB (ids 4336-4355) ===")
    cur.execute(
        """
        SELECT te.id, te.skill_id, si.skill_ch_name, te.source_section, te.source_description
        FROM textbook_examples te
        LEFT JOIN skills_info si ON si.skill_id = te.skill_id
        WHERE te.id BETWEEN 4336 AND 4355
        ORDER BY te.id
        """
    )
    for r in cur.fetchall():
        m = re.search(r"題\s*(\d+)", r["source_description"] or "")
        q = m.group(1) if m else "?"
        sec = (r["source_section"] or "").split(" ", 1)[0]
        out.append(
            f"Q{int(q):>2} section_code={sec:<4} skill_id={r['skill_id']} skill_ch_name={r['skill_ch_name']}"
        )
    out.append("\n=== FALLBACK SKILL CHECK ===")
    for pat in ["SelfAssessment", "MixedExercise", "Unknown", "Concept_", "SubSection_"]:
        cur.execute(
            "SELECT skill_id FROM skills_info WHERE skill_id LIKE ? ORDER BY skill_id",
            (f"%{pat}%",),
        )
        rows = [x[0] for x in cur.fetchall()]
        out.append(f"{pat}: count={len(rows)}")
        for sid in rows:
            out.append(f"  {sid}")
    cur.execute("SELECT COUNT(*) FROM skills_info")
    out.append(f"\nskills_info total={cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM skill_curriculum")
    out.append(f"skill_curriculum total={cur.fetchone()[0]}")
    conn.close()
    return "\n".join(out)


def main():
    path = os.path.join(ROOT, "scratch", "acceptance_report.txt")
    lines = []
    src = find_b1_self_assessment_docx()
    lines.append(f"DOCX_FOUND={src!r}")
    lines.append("")
    lines.append(query_db())
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("written", path)
    if src:
        print("FOUND", src)


if __name__ == "__main__":
    main()
