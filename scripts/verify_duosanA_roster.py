# -*- coding: utf-8 -*-
"""Post-sync verification for 多三甲 roster."""
import sys
from pathlib import Path

from werkzeug.security import check_password_hash

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import Class, ClassStudent, User, db
from core.teacher_analysis_service import get_class_students_stats, parse_time_range

OFFICIAL = [
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

app = create_app()
with app.app_context():
    cls = Class.query.filter_by(name="多三甲").first()
    cnt = ClassStudent.query.filter_by(class_id=cls.id).count()
    print("COUNT:", cnt)

    rows = (
        db.session.query(ClassStudent.seat_no, User.username, User.real_name)
        .join(User, User.id == ClassStudent.student_id)
        .filter(ClassStudent.class_id == cls.id)
        .order_by(ClassStudent.seat_no.asc())
        .all()
    )
    ok_roster = rows == [(s, u, n) for s, u, n in OFFICIAL]
    print("ROSTER_MATCH:", ok_roster)
    for r in rows:
        print(r)

    samples = ["315001", "315032", "315003", "315031"]
    for u in samples:
        user = User.query.filter_by(username=u).first()
        print(f"login {u}:", check_password_hash(user.password_hash, "1234"))

    ok_count = sum(
        1
        for _, username, _ in OFFICIAL
        if check_password_hash(User.query.filter_by(username=username).first().password_hash, "1234")
    )
    print("password_ok:", f"{ok_count}/31")

    stats_rows = get_class_students_stats(cls, parse_time_range("all"))
    print("teacher_analysis_rows:", len(stats_rows))
    for row in stats_rows[:3]:
        print("  ", row["seat_no"], row["display_name"], row["student"].username)
    print("  ...")
    last = stats_rows[-1]
    print("  ", last["seat_no"], last["display_name"], last["student"].username)

    extra_in_class = (
        db.session.query(User.username)
        .join(ClassStudent, ClassStudent.student_id == User.id)
        .filter(ClassStudent.class_id == cls.id)
        .filter(User.username.like("__restore_stub_%"))
        .all()
    )
    print("stubs_in_class:", extra_in_class)
