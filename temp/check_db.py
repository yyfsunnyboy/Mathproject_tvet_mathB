import sys
sys.path.insert(0, '.')
from app import app, db
from sqlalchemy import text

with app.app_context():
    rows = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    print("=== Tables ===")
    for r in rows:
        print(r[0])

    # Check textbook_examples columns
    try:
        cols = db.session.execute(text("PRAGMA table_info(textbook_examples)")).fetchall()
        print("\n=== textbook_examples columns ===")
        for c in cols:
            print(c[1], c[2])  # name, type
        
        # Sample row
        row = db.session.execute(text("SELECT * FROM textbook_examples LIMIT 1")).fetchone()
        if row:
            print("\n=== Sample row ===")
            print(dict(row._mapping))
        else:
            print("\nNo rows found")
    except Exception as e:
        print(f"Error: {e}")
