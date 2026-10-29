"""Isolated Flask instance for the Unit 5 student-page check (NOT the formal 5000 / 5001 services).

* DB: a fresh copy of the rehearsal DB (formal DB copy + the new 37-row Unit 5 import with the staged verified region) in ./isolated/;
  two throw-away accounts are added to that copy only.
* Question images: served from the rehearsal sandbox uploads (the real uploads/ folder is not read for Unit 5 and never written).
* Fixed practice: a TEMP merge of the staged 進階題12 entry; the live configs/ files are not modified.

    python reports/gh_math2_unit5_visual_completion/isolated_server.py prepare
    python reports/gh_math2_unit5_visual_completion/isolated_server.py serve      # http://127.0.0.1:5057 , stop with Ctrl+C
"""
import hashlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXED = ROOT / "reports/gh_math2_unit5_fixed"
SANDBOX = FIXED / "sandbox"
ISO = HERE / "isolated"
DB = ISO / "unit5_preview.db"
CFG = ISO / "fixed_textbook_practice.merged.json"
PORT = 5057
USERS = {"u5preview_student": "student", "u5preview_admin": "admin"}
PASSWORD = "u5preview-only"


def prepare():
    from werkzeug.security import generate_password_hash

    ISO.mkdir(exist_ok=True)
    shutil.copyfile(SANDBOX / "unit5.db", DB)
    con = sqlite3.connect(DB)
    for name, role in USERS.items():
        con.execute("delete from users where username=?", (name,))
        con.execute("insert into users (username, password_hash, role, created_at) values (?,?,?,datetime('now'))",
                    (name, generate_password_hash(PASSWORD, method="pbkdf2:sha256"), role))
    con.commit()
    con.close()
    live = ROOT / "configs/fixed_textbook_practice.json"
    data = json.loads(live.read_text(encoding="utf-8"))
    data["entries"].update(json.loads((FIXED / "staged_fixed_entries.json").read_text(encoding="utf-8"))["entries"])
    CFG.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("prepared", DB, hashlib.sha256(DB.read_bytes()).hexdigest()[:16], "| merged entries:", len(data["entries"]))


def serve():
    assert DB.exists() and CFG.exists(), "run prepare first"
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{DB.as_posix()}"
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    from flask import abort, send_from_directory
    from werkzeug.security import safe_join

    from core import fixed_textbook_practice as F
    from core import question_image_assets as Q

    F.CONFIG_PATH = CFG
    F._cache.update(mtime=None, entries={})
    real_url = Q.question_asset_public_url
    Q.question_asset_public_url = lambda path, *, root_path=None: real_url(path, root_path=str(SANDBOX))

    from app import app

    assert app.config["SQLALCHEMY_DATABASE_URI"].endswith("isolated/unit5_preview.db"), app.config["SQLALCHEMY_DATABASE_URI"]
    base_dir = str(SANDBOX / "uploads" / "question_assets")

    def question_asset_file(filename):
        safe_path = safe_join(base_dir, filename)
        if not safe_path or not os.path.isfile(safe_path):
            abort(404)
        return send_from_directory(base_dir, filename)

    app.view_functions["question_asset_file"] = question_asset_file
    print(f"ISOLATED Unit 5 preview on http://127.0.0.1:{PORT} db={DB}", flush=True)
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    {"prepare": prepare, "serve": serve}[sys.argv[1]]()
