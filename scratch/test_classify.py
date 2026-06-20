import sys
import sqlite3
from pathlib import Path

# Configure stdout to use UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.gencode.services.v3_example_semantic_classifier import (
    TextbookExampleSource,
    _deterministic_classify,
    calculate_source_hash,
)

PROJECT_ROOT = Path("E:/Python/Mathproject_tvet_mathB")
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

ids = [4565, 4566, 4567, 4572, 4573, 4574, 4581, 4582, 4585, 4592, 4593, 4594, 4595, 4596, 4597, 4598, 4599]
placeholders = ",".join("?" for _ in ids)
cursor.execute(f"SELECT * FROM textbook_examples WHERE id IN ({placeholders})", ids)
rows = cursor.fetchall()

print(f"Total rows fetched: {len(rows)}")
for row in rows:
    row_id = row["id"]
    q_text = row["problem_text"] or ""
    ans_text = row["correct_answer"] or ""
    sol_text = row["detailed_solution"] or ""
    s_hash = calculate_source_hash(q_text, ans_text, sol_text)
    
    src = TextbookExampleSource(
        skill_id="vh_數學B1_GeneralFormOfLinearEquation",
        textbook_example_id=row_id,
        question_text=q_text,
        answer=ans_text,
        choices=[],
        explanation=sol_text,
        source_label=row["source_description"],
        source_type=row["problem_type"],
        presentation_mode="short_answer",
        question_type=row["problem_type"],
        source_hash=s_hash,
    )
    
    res = _deterministic_classify(src)
    if res:
        print(f"ID {row_id} -> {res['problem_type_id']}")
    else:
        print(f"ID {row_id} -> FAILED TO CLASSIFY! Text: {repr(q_text)}")

conn.close()
