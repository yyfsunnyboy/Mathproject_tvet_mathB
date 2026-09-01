# -*- coding: utf-8 -*-
"""Shared roster sync helpers (used by class-specific sync scripts)."""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from werkzeug.security import check_password_hash, generate_password_hash

from models import Class, ClassStudent, User, db, init_db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "instance" / "kumon_math.db"
BACKUP_DIR = PROJECT_ROOT / "instance" / "backups"
DEFAULT_PASSWORD = "1234"
PASSWORD_METHOD = "pbkdf2:sha256"

OfficialRoster = list[tuple[int, str, str]]


def validate_roster(roster: OfficialRoster, *, expected_count: int) -> None:
    if len(roster) != expected_count:
        raise ValueError(f"Roster length {len(roster)} != expected {expected_count}")

    seats: set[int] = set()
    usernames: set[str] = set()
    for seat_no, username, real_name in roster:
        if not isinstance(seat_no, int) or seat_no < 1:
            raise ValueError(f"Invalid seat_no: {seat_no!r} for {username}")
        if seat_no in seats:
            raise ValueError(f"Duplicate seat_no: {seat_no}")
        seats.add(seat_no)

        if not isinstance(username, str) or len(username) != 6 or not username.isdigit():
            raise ValueError(f"Invalid username (must be 6-digit string): {username!r}")
        if username in usernames:
            raise ValueError(f"Duplicate username: {username}")
        usernames.add(username)

        if not isinstance(real_name, str) or not real_name.strip():
            raise ValueError(f"Invalid real_name for {username}: {real_name!r}")

    if seats != set(range(1, expected_count + 1)):
        raise ValueError(f"seat_no must be 1..{expected_count}, got {sorted(seats)}")


def backup_db(suffix: str) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"kumon_math_before_{suffix}_{stamp}.db"
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


def class_member_count(class_name: str) -> int:
    cls = db.session.query(Class).filter_by(name=class_name).first()
    if not cls:
        return 0
    return db.session.query(ClassStudent).filter_by(class_id=cls.id).count()


def hash_password(raw: str) -> str:
    return generate_password_hash(raw, method=PASSWORD_METHOD)


def resolve_teacher_id_from_reference(reference_class_name: str) -> int:
    ref = db.session.query(Class).filter_by(name=reference_class_name).first()
    if not ref:
        raise RuntimeError(f"Reference class not found: {reference_class_name}")
    teacher = db.session.query(User).filter_by(id=ref.teacher_id).first()
    if not teacher:
        raise RuntimeError(f"teacher_id={ref.teacher_id} from {reference_class_name} not found")
    if teacher.role not in ("teacher", "admin"):
        raise RuntimeError(
            f"teacher_id={ref.teacher_id} ({teacher.username}) role={teacher.role!r} is not teacher/admin"
        )
    return int(ref.teacher_id)


def sync_class_roster(
    *,
    class_name: str,
    official_roster: OfficialRoster,
    expected_count: int,
    backup_suffix: str,
    dry_run: bool = False,
    create_if_missing: bool = True,
    reference_class_for_teacher: str | None = None,
    guard_classes: dict[str, int] | None = None,
    report_label: str | None = None,
) -> dict[str, Any]:
    validate_roster(official_roster, expected_count=expected_count)
    official_usernames = {username for _, username, _ in official_roster}
    label = report_label or class_name

    stats: dict[str, Any] = {
        "backup_path": None,
        "class_existed": False,
        "class_id": None,
        "teacher_id": None,
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

    cls = db.session.query(Class).filter_by(name=class_name).first()
    stats["class_existed"] = cls is not None

    if cls:
        stats["class_id"] = cls.id
        stats["teacher_id"] = cls.teacher_id
        before = current_members(cls.id)
    else:
        before = []

    stats["before_count"] = len(before)
    current_usernames = {u for u, _, _ in before}

    print(f"{label} CURRENT MEMBERS")
    for u, rn, seat in before:
        print(f"  {u} | seat={seat} | real_name={rn}")

    print("\nOFFICIAL MEMBERS")
    for seat, username, real_name in official_roster:
        print(f"  {seat} | {username} | {real_name}")

    extra = sorted(current_usernames - official_usernames)
    missing = sorted(official_usernames - current_usernames)

    print("\nEXTRA MEMBERS")
    for u in extra:
        print(f"  {u}")
    print("\nMISSING MEMBERS")
    for u in missing:
        print(f"  {u}")

    if dry_run:
        print("\n[DRY RUN] No changes applied.")
        return stats

    guard_before: dict[str, int] = {}
    if guard_classes:
        for gname, gcount in guard_classes.items():
            guard_before[gname] = class_member_count(gname)
            if guard_before[gname] != gcount:
                raise RuntimeError(
                    f"Guard pre-check failed: {gname} has {guard_before[gname]} members, expected {gcount}"
                )

    stats["backup_path"] = str(backup_db(backup_suffix))
    print(f"\nBackup: {stats['backup_path']}")

    pwd_hash = hash_password(DEFAULT_PASSWORD)

    try:
        if not cls:
            if not create_if_missing:
                raise RuntimeError(f"Class not found: {class_name}")
            if not reference_class_for_teacher:
                raise RuntimeError(f"Cannot create {class_name}: reference_class_for_teacher required")
            teacher_id = resolve_teacher_id_from_reference(reference_class_for_teacher)
            cls = Class(name=class_name, teacher_id=teacher_id)
            db.session.add(cls)
            db.session.flush()
            stats["class_id"] = cls.id
            stats["teacher_id"] = teacher_id
            print(f"\nCreated class {class_name!r} id={cls.id} teacher_id={teacher_id}")

        for seat_no, username, real_name in official_roster:
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
                if user.role != "student":
                    user.role = "student"
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

    stats["class_id"] = cls.id
    stats["teacher_id"] = cls.teacher_id
    after = current_members(cls.id)
    stats["after_count"] = len(after)

    if stats["after_count"] != expected_count:
        raise RuntimeError(f"Expected {expected_count} members after sync, got {stats['after_count']}")

    if guard_classes:
        for gname, gcount in guard_classes.items():
            now = class_member_count(gname)
            if now != gcount:
                raise RuntimeError(
                    f"Guard post-check failed: {gname} has {now} members, expected {gcount}"
                )

    for _seat_no, username, _real_name in official_roster:
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
