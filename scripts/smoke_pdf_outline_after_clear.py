from app import app
from models import db, SkillInfo, SkillCurriculum
from core.textbook_processor_v2 import _sync_skill_curriculum_outline_v2


def main():
    parsed = {
        "curriculum": "vocational",
        "volume": "數學B1",
        "grade": 10,
        "chapters": [
            {
                "chapter_title": "1 坐標系與函數圖形",
                "sections": [
                    {"section_code": "1-1", "section_title": "1-1 數線與絕對值"},
                    {"section_code": "1-2", "section_title": "1-2 平面坐標系與線型函數"},
                ],
            }
        ],
    }
    curriculum_info = {"curriculum": "vocational", "volume": "數學B1", "grade": 10}

    expected_skill = "outline_vocational_數學B1_11"

    with app.app_context():
        # Simulate post-clear state for target outlines.
        SkillCurriculum.query.filter(SkillCurriculum.skill_id.like("outline_vocational_數學B1_%")).delete(synchronize_session=False)
        SkillInfo.query.filter(SkillInfo.skill_id.like("outline_vocational_數學B1_%")).delete(synchronize_session=False)
        db.session.commit()

        # Must not raise IntegrityError
        stats = _sync_skill_curriculum_outline_v2(parsed, curriculum_info, queue=None)
        print({"sync_stats": stats})

        assert db.session.get(SkillInfo, expected_skill) is not None, "missing SkillInfo placeholder"
        assert (
            SkillCurriculum.query.filter_by(
                skill_id=expected_skill,
                curriculum="vocational",
                volume="數學B1",
                grade=10,
            ).first()
            is not None
        ), "missing SkillCurriculum row"
        print({"ok": True, "expected_skill": expected_skill})


if __name__ == "__main__":
    main()
