import sqlite3

db_path = "instance/kumon_math.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get distinct skill_ids
cursor.execute("SELECT DISTINCT skill_id FROM textbook_examples WHERE skill_id LIKE '%LinearFunction%';")
print("Distinct skill_ids:", cursor.fetchall())

cursor.execute("SELECT id, correct_answer, problem_text FROM textbook_examples WHERE skill_id LIKE '%LinearFunction%';")
rows = cursor.fetchall()
print(f"Found {len(rows)} examples:")
for row in rows[:5]:
    print(f"ID: {row[0]}, Answer: {row[1]}, Text: {row[2][:60]}...")
