import sqlite3

conn = sqlite3.connect('instance/kumon_math.db')
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT skill_id FROM textbook_examples")
for row in cursor.fetchall():
    print(row[0])
conn.close()
