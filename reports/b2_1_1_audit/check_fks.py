import sys
sys.path.insert(0, '.')
import sqlite3
from config import Config

conn = sqlite3.connect(Config.db_path)
cur = conn.cursor()
cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
tables = []
for name, sql in cur.fetchall():
    if sql and 'textbook_example' in sql.lower() and name != 'textbook_examples':
        tables.append(name)
print('Tables referencing textbook_examples:', tables)
