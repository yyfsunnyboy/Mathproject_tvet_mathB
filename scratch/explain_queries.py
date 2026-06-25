import sqlite3
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
db_path = PROJECT_ROOT / "instance" / "kumon_math.db"

def main():
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    
    print("====== 1. Main SQL Query Explain ======")
    main_sql = """
    EXPLAIN QUERY PLAN
    SELECT DISTINCT s.skill_id, s.skill_ch_name, c.display_order
    FROM skills_info s
    JOIN skill_curriculum c ON s.skill_id = c.skill_id
    ORDER BY c.display_order ASC, s.skill_id ASC
    """
    for row in conn.execute(main_sql).fetchall():
        print(dict(row))
        
    print("\n====== 2. tracker query by skill_id Explain ======")
    tracker_sql = """
    EXPLAIN QUERY PLAN
    SELECT textbook_example_id, component_id, gencode_status, gencode_error_log, induced_spec_payload
    FROM gencode_component_tracker
    WHERE skill_id = ?
    ORDER BY textbook_example_id ASC
    """
    for row in conn.execute(tracker_sql, ("vh_數學B1_PointSlopeForm",)).fetchall():
        print(dict(row))
        
    print("\n====== 3. textbook_examples query Explain ======")
    examples_sql = """
    EXPLAIN QUERY PLAN
    SELECT id
    FROM textbook_examples
    WHERE skill_id = ?
    ORDER BY id ASC
    """
    for row in conn.execute(examples_sql, ("vh_數學B1_PointSlopeForm",)).fetchall():
        print(dict(row))
        
    conn.close()

if __name__ == '__main__':
    main()
