import sys
sys.path.insert(0, '.')
import sqlite3
from config import Config

conn = sqlite3.connect(Config.db_path)
cur = conn.cursor()
cur.execute("SELECT * FROM gencode_component_tracker WHERE textbook_example_id >= 11587 AND textbook_example_id <= 11605")
rows = cur.fetchall()
print('gencode rows for B2 1-1:', len(rows))
