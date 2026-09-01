# -*- coding: utf-8 -*-
"""Post-sync verification for 資一乙 roster."""
from __future__ import annotations

import sys
from pathlib import Path

from werkzeug.security import check_password_hash

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from core.teacher_analysis_service import get_accessible_classes, get_class_students_stats, parse_time_range
from models import Class, ClassStudent, User, db
from scripts.roster_sync_lib import class_member_count

OFFICIAL = [
    (1, "511031", "林千玄"),
    (2, "511032", "林庚德"),
    (3, "511033", "紀宥任"),
    (4, "511034", "陳世邦"),
    (5, "511035", "游楊浩恩"),
    (6, "511036", "黃麒澔"),
    (7, "511037", "廖品綸"),
    (8, "511038", "賴昶易"),
    (9, "511040", "温睿洋"),
    (10, "511039", "王恩敏"),
    (11, "511041", "江品萱"),
    (12, "511042", "吳岱錡"),
    (13, "511043", "呂沛潔"),
    (14, "511044", "汪佩伶"),
    (15, "511045", "張佳怡"),
    (16, "511046", "陳莃"),
    (17, "511047", "黃敏綺"),
    (18, "511048", "董鈺瑄"),
    (19, "511050", "賴家宇"),
]

app = create_app()
with app.app_context():
    duosan_cnt = class_member_count("多三甲")
    print("多三甲 COUNT:", duosan_cnt)

    cls = Class.query.filter_by(name="資一乙").first()
    cnt = ClassStudent.query.filter_by(class_id=cls.id).count()
    print("資一乙 COUNT:", cnt)
    print("class_id:", cls.id, "teacher_id:", cls.teacher_id)

    rows = (
        db.session.query(ClassStudent.seat_no, User.username, User.real_name)
        .join(User, User.id == ClassStudent.student_id)
        .filter(ClassStudent.class_id == cls.id)
        .order_by(ClassStudent.seat_no.asc())
        .all()
    )
    print("ROSTER_MATCH:", rows == [(s, u, n) for s, u, n in OFFICIAL])

    ok_count = sum(
        1
        for _, username, _ in OFFICIAL
        if check_password_hash(User.query.filter_by(username=username).first().password_hash, "1234")
    )
    print("password_ok:", f"{ok_count}/19")

    admin = User.query.filter_by(username="admin").first()
    classes = get_accessible_classes(admin)
    print("admin classes:", [c.name for c in classes])

    stats_rows = get_class_students_stats(cls, parse_time_range("all"))
    print("teacher_analysis_rows:", len(stats_rows))
    for row in stats_rows[:2]:
        print(" ", row["seat_no"], row["display_name"], row["student"].username)
    last = stats_rows[-1]
    print(" ", last["seat_no"], last["display_name"], last["student"].username)
