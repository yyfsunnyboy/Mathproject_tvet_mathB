from flask import abort, render_template
from flask_login import current_user, login_required

from core.routes import core_bp
from core.skill_card_mastery import build_skill_card_mastery
from core.vocational_mock_exam_scope import build_mock_exam_scope
from core.vocational_student_home import is_vocational_student


@core_bp.route("/vocational/mock-exam/<exam_id>")
@login_required
def vocational_mock_exam(exam_id: str):
    can_preview = bool(current_user.is_admin or current_user.role == "teacher")
    if not is_vocational_student(current_user) and not can_preview:
        abort(403)
    scope = build_mock_exam_scope(exam_id)
    if scope is None:
        abort(404)
    skills = [
        skill
        for volume in scope["volumes"]
        for unit in volume["units"]
        for skill in unit["skills"]
    ]
    mastery = build_skill_card_mastery(
        student_id=current_user.id,
        skill_ids=[skill["skill_id"] for skill in skills],
    )
    for skill in skills:
        skill.update(mastery[skill["skill_id"]])
    return render_template("vocational_mock_exam_scope.html", **scope)
