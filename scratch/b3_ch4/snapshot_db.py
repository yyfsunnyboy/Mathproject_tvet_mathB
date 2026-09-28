import os
import sqlite3
import sys

src = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
dest_path = sys.argv[1]
if os.path.exists(dest_path):
    os.remove(dest_path)
dest = sqlite3.connect(dest_path)
src.backup(dest)
dest.execute("PRAGMA journal_mode=DELETE")
print(dest.execute("SELECT COUNT(*) FROM textbook_examples WHERE id BETWEEN 12127 AND 12272").fetchone())
dest.close()
src.close()
