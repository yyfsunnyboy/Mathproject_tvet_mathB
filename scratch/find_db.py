import sqlite3
import os, sys, json
from pathlib import Path

os.chdir(r'e:\Python\Mathproject_tvet_mathB')
sys.path.insert(0, r'e:\Python\Mathproject_tvet_mathB')

db_paths = [
    r'e:\Python\Mathproject_tvet_mathB\math_system.db',
    r'e:\Python\Mathproject_tvet_mathB\instance\math_system.db',
]
conn = None
for db_path in db_paths:
    if Path(db_path).exists():
        conn = sqlite3.connect(db_path)
        print(f"Using DB: {db_path}")
        break

if conn is None:
    print("No DB found!")
    sys.exit(1)

tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("Tables:", tables)

if 'gencode_component_tracker' not in tables:
    print("gencode_component_tracker not found, trying instance db...")
    for db_path in db_paths:
        if 'instance' in db_path and Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            tables2 = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            print("Instance DB tables:", tables2)
