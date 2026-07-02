#!/usr/bin/env python3
"""Route-level smoke for V3 runtime dispatch (no sympy required for non-symbolic)."""

from __future__ import annotations

import sys
import uuid
from urllib.parse import quote

from app import create_app
from models import User, db

SKILL_DISTANCE = "vh_數學B1_DistanceBetweenTwoPointsInPlane"
SKILL_DIVISION = "vh_數學B1_DivisionPointCoordinates"
COMPONENT_DIVISION_SHORT = "src_4420"
COMPONENT_DIVISION_CHOICE = "src_4512"


def _client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        user = User(
            username=f"smoke_{uuid.uuid4().hex[:8]}",
            password_hash="test-hash",
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    return client


def _check(label: str, resp) -> None:
    data = resp.get_json() or {}
    print(f"[{label}] status={resp.status_code}")
    if resp.status_code != 200:
        print(f"  ERROR: {data}")
        sys.exit(1)
    if data.get("error"):
        print(f"  ERROR: {data['error']}")
        sys.exit(1)
    if "No module named 'sympy'" in str(data):
        print("  ERROR: sympy import leaked into non-symbolic route")
        sys.exit(1)
    print(
        f"  component_id={data.get('component_id')} "
        f"presentation_mode={data.get('presentation_mode')} "
        f"problem_type_id={data.get('problem_type_id')}"
    )


def main() -> None:
    client = _client()
    _check(
        "short-answer component",
        client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}"
            f"&component_id={COMPONENT_DIVISION_SHORT}&gen_seed=41&level=1"
        ),
    )
    _check(
        "single-choice component",
        client.get(
            f"/get_next_question?skill={quote(SKILL_DIVISION)}"
            f"&component_id={COMPONENT_DIVISION_CHOICE}&gen_seed=43&level=1"
        ),
    )
    _check(
        "unspecified component",
        client.get(
            f"/get_next_question?skill={quote(SKILL_DISTANCE)}&gen_seed=47&level=1"
        ),
    )
    print("ALL SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()
