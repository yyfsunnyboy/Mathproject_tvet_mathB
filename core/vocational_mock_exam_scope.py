from __future__ import annotations

from typing import Any

from models import SkillCurriculum, SkillInfo, db


VOCATIONAL_CURRICULUM = "vocational"
VOLUME_ORDER = ("數學B1", "數學B2", "數學B3", "數學B4")

# Official 108 mock-exam units. These are semantic identities, not a
# publisher's chapter numbers. SkillCurriculum.chapter stays the publisher title.
OFFICIAL_UNITS: dict[int, str] = {
    1: "坐標系與函數圖形",
    2: "直線方程式",
    3: "式的運算",
    4: "三角函數",
    5: "平面向量",
    6: "圓與直線",
    7: "數列與級數",
    8: "方程式",
    9: "二元一次不等式及其應用",
    10: "指數與對數",
    11: "三角函數的應用",
    12: "排列組合",
    13: "機率與統計",
}

MOCK_EXAM_SCOPE: dict[str, dict[str, Any]] = {
    "exam_1": {"label": "第一次模擬考", "units": (1, 2, 3, 8)},
    "exam_2": {"label": "第二次模擬考", "units": (1, 2, 3, 4, 5, 6, 8, 11)},
    "exam_5": {"label": "第五次模擬考", "units": tuple(range(1, 14))},
}


def _compact_title(text: str) -> str:
    from core.textbook_processor_v2 import _chapter_identity

    identity = _chapter_identity(text)
    bare = identity[1] if identity else str(text or "")
    return "".join(str(bare).split())


def official_unit_for_chapter(chapter: str) -> int | None:
    """Return the one official unit for a publisher chapter, or None.

    Exact title wins. Otherwise the longest official name that contains the
    chapter title, or is contained in it, wins. A tie is unresolved.
    """
    bare = _compact_title(chapter)
    if not bare:
        return None
    exact = [unit for unit, name in OFFICIAL_UNITS.items() if _compact_title(name) == bare]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None
    matches: list[tuple[int, int]] = []
    for unit, name in OFFICIAL_UNITS.items():
        official = _compact_title(name)
        if official and (bare in official or official in bare):
            matches.append((unit, len(official)))
    if not matches:
        return None
    best_length = max(length for _unit, length in matches)
    best = [unit for unit, length in matches if length == best_length]
    if len(best) == 1:
        return best[0]
    return None


def mock_exam_cards() -> list[dict[str, str]]:
    return [
        {"exam_id": exam_id, "label": str(config["label"])}
        for exam_id, config in MOCK_EXAM_SCOPE.items()
    ]


def build_mock_exam_scope(exam_id: str) -> dict[str, Any] | None:
    config = MOCK_EXAM_SCOPE.get(str(exam_id or "").strip())
    if config is None:
        return None
    allowed_units = {int(unit) for unit in config["units"]}
    rows = (
        db.session.query(SkillCurriculum, SkillInfo)
        .join(SkillInfo, SkillInfo.skill_id == SkillCurriculum.skill_id)
        .filter(
            SkillCurriculum.curriculum == VOCATIONAL_CURRICULUM,
            SkillCurriculum.volume.in_(VOLUME_ORDER),
            SkillInfo.is_active.is_(True),
        )
        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
        .all()
    )

    skills_by_unit: dict[tuple[str, str], list[dict[str, str]]] = {}
    chapter_order: dict[str, list[str]] = {volume: [] for volume in VOLUME_ORDER}
    # A skill may legitimately have more than one vocational curriculum
    # placement. De-duplicate only duplicate rows for the same chapter.
    seen_placements: set[tuple[str, str, str]] = set()
    for curriculum_row, skill in rows:
        volume = str(curriculum_row.volume or "").strip()
        chapter = str(curriculum_row.chapter or "").strip()
        if volume not in chapter_order or not chapter:
            continue
        if official_unit_for_chapter(chapter) not in allowed_units:
            continue
        skill_id = str(skill.skill_id or "").strip()
        placement = (volume, chapter, skill_id)
        if not skill_id or placement in seen_placements:
            continue
        seen_placements.add(placement)
        if chapter not in chapter_order[volume]:
            chapter_order[volume].append(chapter)
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
    for volume in VOLUME_ORDER:
        units = [
            {"unit_name": chapter, "skills": skills_by_unit.get((volume, chapter), [])}
            for chapter in chapter_order[volume]
            if skills_by_unit.get((volume, chapter))
        ]
        if units:
            volumes.append({"volume": volume, "units": units})

    return {
        "exam_id": exam_id,
        "exam_label": str(config["label"]),
        "volumes": volumes,
    }
