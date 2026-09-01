"""Read-only smoke: production DB integrity + /db_maintenance 200."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from models import User

db_path = Path("instance/kumon_math.db")
conn = sqlite3.connect(db_path)
print("integrity_check", conn.execute("PRAGMA integrity_check").fetchone()[0])
print("fk_check_rows", len(conn.execute("PRAGMA foreign_key_check").fetchall()))
row = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='practice_attempts'"
).fetchone()
print("practice_attempts exists", row is not None)
print("practice_attempts count", conn.execute("SELECT COUNT(*) FROM practice_attempts").fetchone()[0])
cols = [r[1] for r in conn.execute("PRAGMA table_info(class_students)")]
print("class_students has seat_no", "seat_no" in cols)
conn.close()

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username="admin").first()
    client = app.test_client()
    with client.session_transaction() as s:
        s["_user_id"] = str(admin.id)
        s["_fresh"] = True
    r = client.get("/db_maintenance")
    print("GET /db_maintenance", r.status_code)
