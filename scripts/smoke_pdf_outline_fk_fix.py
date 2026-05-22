from app import app
from models import db, SkillInfo, SkillCurriculum
from core.textbook_processor_v2 import _sync_skill_curriculum_outline_v2


def main():
    curriculum_info = {
        "curriculum": "vocational",
        "volume": "數學B1",
        "grade": 10,
    }
    parsed = {
        "curriculum": "vocational",
        "volume": "數學B1",
        "grade": 10,
        "chapters": [
            {
                "chapter_title": "第1章 直線方程式",
                "sections": [
                    {"section_code": "1-1", "section_title": "1-1 數線與絕對值"},
                    {"section_code": "1-2", "section_title": "1-2 區間表示法"},
                    {"section_code": "1-3", "section_title": "1-3 一次不等式"},
                    {"section_code": "1-4", "section_title": "1-4 一次不等式應用"},
                ],
            }
        ],
    }
    expected_ids = [
        "outline_vocational_數學B1_11",
        "outline_vocational_數學B1_12",
        "outline_vocational_數學B1_13",
        "outline_vocational_數學B1_14",
    ]

    with app.app_context():
        # Optional cleanup for deterministic smoke run.
        SkillCurriculum.query.filter(SkillCurriculum.skill_id.in_(expected_ids)).delete(synchronize_session=False)
        SkillInfo.query.filter(SkillInfo.skill_id.in_(expected_ids)).delete(synchronize_session=False)
        db.session.commit()

        stats = _sync_skill_curriculum_outline_v2(parsed, curriculum_info, queue=None)
        print({"sync_stats": stats})

        missing_skill_info = [sid for sid in expected_ids if db.session.get(SkillInfo, sid) is None]
        missing_curriculum = [
            sid
            for sid in expected_ids
            if SkillCurriculum.query.filter_by(
                skill_id=sid, curriculum="vocational", volume="數學B1", grade=10
            ).first()
            is None
        ]
        print({"missing_skill_info": missing_skill_info, "missing_curriculum": missing_curriculum})
        assert not missing_skill_info, f"missing skills_info rows: {missing_skill_info}"
        assert not missing_curriculum, f"missing skill_curriculum rows: {missing_curriculum}"


if __name__ == "__main__":
    main()
