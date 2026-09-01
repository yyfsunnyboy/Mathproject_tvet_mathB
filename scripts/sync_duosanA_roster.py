# -*- coding: utf-8 -*-
"""Sync 多三甲 official roster (31 students) into production DB."""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import Class, ClassStudent, User, db, init_db

DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
BACKUP_DIR = PROJECT_ROOT / "instance" / "backups"
CLASS_NAME = "多三甲"
DEFAULT_PASSWORD = "1234"
PASSWORD_METHOD = "pbkdf2:sha256"

OFFICIAL_ROSTER: list[tuple[int, str, str]] = [
    (1, "315001", "李家同"),
    (2, "315032", "黃聆瑄"),
    (3, "315003", "林育呈"),
    (4, "315033", "葉家妤"),
    (5, "315005", "張育瑞"),
    (6, "315006", "梁瑋國"),
    (7, "315007", "廖祐陞"),
    (8, "315008", "劉泓鋆"),
    (9, "315009", "潘李洲"),
    (10, "315034", "劉家瑜"),
    (11, "315011", "王于庭"),
    (12, "315012", "田歆"),
    (13, "315035", "蔡汶君"),
    (14, "315014", "吳孟諠"),
    (15, "315015", "宋子祺"),
    (16, "315016", "杜安蕎"),
    (17, "315017", "杜雅晴"),
    (18, "315036", "鄭恩如"),
    (19, "315019", "林宜葳"),
    (20, "315020", "林宸語"),
    (21, "315021", "涂軒慈"),
    (22, "315022", "高紫妍"),
    (23, "315023", "張念慈"),
    (24, "315024", "張芠喬"),
    (25, "315025", "張瑀津"),
    (26, "315026", "陳盈羽"),
    (27, "315027", "陳聖卉"),
    (28, "315028", "曾若瑄"),
    (29, "315029", "黃妤涵"),
    (30, "315030", "黃品嘉"),
    (31, "315031", "黃捷羽"),
]

OFFICIAL_USERNAMES = {username for _, username, _ in OFFICIAL_ROSTER}


def backup_db() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"kumon_math_before_duosanA_roster_sync_{stamp}.db"
    shutil.copy2(DB_PATH, dest)
    if not dest.exists() or dest.stat().st_size < 1000:
        raise RuntimeError(f"Backup failed or too small: {dest}")
    return dest


def ensure_schema(app) -> None:
    with app.app_context():
        init_db(db.engine)


def current_members(class_id: int) -> list[tuple[str, str | None, int | None]]:
    rows = (
        db.session.query(User.username, User.real_name, ClassStudent.seat_no)
        .join(ClassStudent, ClassStudent.student_id == User.id)
        .filter(ClassStudent.class_id == class_id)
        .order_by(User.username.asc())
        .all()
    )
    return [(r[0], r[1], r[2]) for r in rows]


def hash_password(raw: str) -> str:
    return generate_password_hash(raw, method=PASSWORD_METHOD)


def sync_roster(dry_run: bool = False) -> dict:
    stats = {
        "backup_path": None,
        "before_count": 0,
        "after_count": 0,
        "extra_removed": [],
        "membership_added": [],
        "users_created": [],
        "real_name_updated": 0,
        "password_reset": 0,
        "seat_no_updated": 0,
        "users_deleted": 0,
        "password_ok": 0,
    }

    app = create_app()
    ensure_schema(app)

    with app.app_context():
        cls = db.session.query(Class).filter_by(name=CLASS_NAME).first()
        if not cls:
            raise RuntimeError(f"Class not found: {CLASS_NAME}")

        before = current_members(cls.id)
        stats["before_count"] = len(before)
        current_usernames = {u for u, _, _ in before}

        print("MULTI-SAN-A CURRENT MEMBERS")
        for u, rn, seat in before:
            print(f"  {u} | seat={seat} | real_name={rn}")

        print("\nOFFICIAL MEMBERS")
        for seat, username, real_name in OFFICIAL_ROSTER:
            print(f"  {seat} | {username} | {real_name}")

        extra = sorted(current_usernames - OFFICIAL_USERNAMES)
        missing = sorted(OFFICIAL_USERNAMES - current_usernames)

        print("\nEXTRA MEMBERS")
        for u in extra:
            print(f"  {u}")
        print("\nMISSING MEMBERS")
        for u in missing:
            print(f"  {u}")

        if dry_run:
            print("\n[DRY RUN] No changes applied.")
            return stats

        stats["backup_path"] = str(backup_db())
        print(f"\nBackup: {stats['backup_path']}")

        pwd_hash = hash_password(DEFAULT_PASSWORD)

        try:
            for seat_no, username, real_name in OFFICIAL_ROSTER:
                user = db.session.query(User).filter_by(username=username).first()
                if not user:
                    user = User(
                        username=username,
                        password_hash=pwd_hash,
                        role="student",
                        real_name=real_name,
                    )
                    db.session.add(user)
                    db.session.flush()
                    stats["users_created"].append(username)
                    stats["password_reset"] += 1
                else:
                    if (user.real_name or "").strip() != real_name:
                        user.real_name = real_name
                        stats["real_name_updated"] += 1
                    user.password_hash = pwd_hash
                    stats["password_reset"] += 1

                membership = (
                    db.session.query(ClassStudent)
                    .filter_by(class_id=cls.id, student_id=user.id)
                    .first()
                )
                if not membership:
                    membership = ClassStudent(class_id=cls.id, student_id=user.id, seat_no=seat_no)
                    db.session.add(membership)
                    stats["membership_added"].append(username)
                    stats["seat_no_updated"] += 1
                elif membership.seat_no != seat_no:
                    membership.seat_no = seat_no
                    stats["seat_no_updated"] += 1

            for username in extra:
                user = db.session.query(User).filter_by(username=username).first()
                if not user:
                    continue
                membership = (
                    db.session.query(ClassStudent)
                    .filter_by(class_id=cls.id, student_id=user.id)
                    .first()
                )
                if membership:
                    db.session.delete(membership)
                    stats["extra_removed"].append(username)

            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        after = current_members(cls.id)
        stats["after_count"] = len(after)

        if stats["after_count"] != 31:
            raise RuntimeError(f"Expected 31 members after sync, got {stats['after_count']}")

        for seat_no, username, real_name in OFFICIAL_ROSTER:
            user = db.session.query(User).filter_by(username=username).first()
            if not user or not check_password_hash(user.password_hash, DEFAULT_PASSWORD):
                raise RuntimeError(f"Password verify failed for {username}")
            stats["password_ok"] += 1

        print("\n=== POST SYNC ROSTER ===")
        rows = (
            db.session.query(ClassStudent.seat_no, User.username, User.real_name)
            .join(User, User.id == ClassStudent.student_id)
            .filter(ClassStudent.class_id == cls.id)
            .order_by(ClassStudent.seat_no.asc())
            .all()
        )
        for seat, username, rn in rows:
            print(f"{seat:>2}  {username}  {rn}")

        return stats


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    result = sync_roster(dry_run=dry)
    print("\n=== SUMMARY ===")
    for k, v in result.items():
        print(f"{k}: {v}")
