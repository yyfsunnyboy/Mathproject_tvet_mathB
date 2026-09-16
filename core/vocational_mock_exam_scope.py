from __future__ import annotations

from collections import OrderedDict
from typing import Any

from models import SkillCurriculum, SkillInfo, db


VOCATIONAL_CURRICULUM = "vocational"

# Scope policy only. Skill links are resolved from the canonical SkillInfo and
# SkillCurriculum rows so inactive/missing skills can never become bad links.
MOCK_EXAM_SCOPE: dict[str, dict[str, Any]] = {
    "exam_1": {
        "label": "第一次模擬考",
        "volumes": OrderedDict(
            [
                ("數學B1", ("1 坐標系與函數圖形", "2 直線方程式", "3 式的運算")),
                ("數學B3", ("第2章 方程式與不等式",)),
            ]
        ),
    },
    "exam_2": {
        "label": "第二次模擬考",
        "volumes": OrderedDict(
            [
                ("數學B1", ("1 坐標系與函數圖形", "2 直線方程式", "3 式的運算")),
                ("數學B2", ("第1章 三角函數", "第3章 向 量", "第4章 圓與直線")),
                ("數學B3", ("第2章 方程式與不等式",)),
                ("數學B4", ("第2章 三角函數的應用",)),
            ]
        ),
    },
    "exam_5": {
        "label": "第五次模擬考",
        # None means every existing chapter with an enabled skill in B1-B4.
        "volumes": OrderedDict((volume, None) for volume in ("數學B1", "數學B2", "數學B3", "數學B4")),
    },
}


def mock_exam_cards() -> list[dict[str, str]]:
    return [
        {"exam_id": exam_id, "label": str(config["label"])}
        for exam_id, config in MOCK_EXAM_SCOPE.items()
    ]


def build_mock_exam_scope(exam_id: str) -> dict[str, Any] | None:
    config = MOCK_EXAM_SCOPE.get(str(exam_id or "").strip())
    if config is None:
        return None

    volume_policy: OrderedDict[str, tuple[str, ...] | None] = config["volumes"]
    rows = (
        db.session.query(SkillCurriculum, SkillInfo)
        .join(SkillInfo, SkillInfo.skill_id == SkillCurriculum.skill_id)
        .filter(
            SkillCurriculum.curriculum == VOCATIONAL_CURRICULUM,
            SkillCurriculum.volume.in_(tuple(volume_policy.keys())),
            SkillInfo.is_active.is_(True),
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .all()
    )

    skills_by_unit: dict[tuple[str, str], list[dict[str, str]]] = {}
    # A skill may legitimately have more than one vocational curriculum
    # placement.  De-duplicate only duplicate rows for the same chapter; a
    # global skill-id set would silently remove it from later chapters/volumes.
    seen_placements: set[tuple[str, str, str]] = set()
    for curriculum_row, skill in rows:
        volume = str(curriculum_row.volume or "").strip()
        chapter = str(curriculum_row.chapter or "").strip()
        allowed_chapters = volume_policy.get(volume)
        if not chapter or (allowed_chapters is not None and chapter not in allowed_chapters):
            continue
        skill_id = str(skill.skill_id or "").strip()
        placement = (volume, chapter, skill_id)
        if not skill_id or placement in seen_placements:
            continue
        seen_placements.add(placement)
        skills_by_unit.setdefault((volume, chapter), []).append(
            {
                "skill_id": skill_id,
                "skill_name": str(skill.skill_ch_name or skill_id),
                "skill_ch_name": str(skill.skill_ch_name or skill_id),
                "description": str(skill.description or ""),
                "section": str(curriculum_row.section or "").strip(),
            }
        )

    volumes: list[dict[str, Any]] = []
    for volume, configured_chapters in volume_policy.items():
        if configured_chapters is None:
            chapters = []
            for curriculum_row, _skill in rows:
                if str(curriculum_row.volume or "").strip() != volume:
                    continue
                chapter = str(curriculum_row.chapter or "").strip()
                if chapter and chapter not in chapters:
                    chapters.append(chapter)
        else:
            chapters = list(configured_chapters)

        units = [
            {"unit_name": chapter, "skills": skills_by_unit.get((volume, chapter), [])}
            for chapter in chapters
        ]
        if units:
            volumes.append({"volume": volume, "units": units})

    return {
        "exam_id": exam_id,
        "exam_label": str(config["label"]),
        "volumes": volumes,
    }
