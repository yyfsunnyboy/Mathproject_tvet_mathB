import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from core.gencode.pipeline_orchestrator import _load_examples
import sqlite3

skill_id = "vh_數學B1_LinearFunction"
print(f"Calling _load_examples with skill_id: {skill_id!r}")
try:
    res = _load_examples(skill_id)
    print(f"Result count: {len(res)}")
except Exception as e:
    print(f"Error calling _load_examples: {e}")

# Let's inspect raw query inside _load_examples
db_path = root / "instance" / "kumon_math.db"
con = sqlite3.connect(str(db_path))
con.row_factory = sqlite3.Row
rows = con.execute("SELECT * FROM textbook_examples WHERE skill_id=? ORDER BY rowid", (skill_id,)).fetchall()
print(f"Raw query rows count: {len(rows)}")
for r in rows[:2]:
    print(dict(r))
con.close()
