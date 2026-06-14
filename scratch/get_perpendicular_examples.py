import sqlite3

conn = sqlite3.connect('instance/kumon_math.db')
cursor = conn.cursor()
cursor.execute("SELECT id, problem_text, correct_answer FROM textbook_examples WHERE skill_id='vh_數學B1_PropertiesOfPerpendicularLines'")
for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"Text: {row[1]}")
    print(f"Answer: {row[2]}")
    print("-" * 50)
conn.close()
