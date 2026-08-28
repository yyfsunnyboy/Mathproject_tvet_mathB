# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import Config

con = sqlite3.connect(Config.db_path)
con.row_factory = sqlite3.Row
print("=== distinct curriculum chapters ===")
for r in con.execute(
    "SELECT DISTINCT volume, chapter FROM skill_curriculum WHERE skill_id LIKE '%B1%' ORDER BY 1,2"
):
    print(dict(r))
print("=== curriculum rows with chapter like 3 ===")
for r in con.execute(
    """
    SELECT skill_id, volume, chapter, section, display_order
    FROM skill_curriculum
    WHERE skill_id LIKE '%B1%'
    ORDER BY volume, chapter, section, display_order, skill_id
    """
):
    print(dict(r))
print("=== example source chapters ===")
for r in con.execute(
    """
    SELECT DISTINCT source_volume, source_chapter, COUNT(*) AS n
    FROM textbook_examples
    WHERE skill_id LIKE '%B1%'
    GROUP BY source_volume, source_chapter
    ORDER BY 1,2
    """
):
    print(dict(r))
