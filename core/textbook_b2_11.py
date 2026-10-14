"""Corrections for the audited B2 1-1 textbook only; no new skills or DB writes."""

from pathlib import Path
import hashlib
import re


SDG_TITLE = "SDG 14 保育海洋生態—扇形計算"
SOURCE_STEM = "第一章 1-1 角度的基本性質-課本"


def is_b2_11(info):
    info = info or {}
    name = str(info.get("parse_filename") or info.get("original_filename") or "")
    stem = Path(name).stem
    return (
        info.get("curriculum") == "vocational"
        and info.get("volume") == "數學B2"
        and info.get("section_code") == "1-1"
        and info.get("source_scope", "section_textbook") == "section_textbook"
        and stem in (SOURCE_STEM, SOURCE_STEM + "_Latex", SOURCE_STEM + "_latex")
    )


def existing_outline(info):
    from core.textbook_processor_v2 import _lookup_outline_section_curriculum_row

    row = _lookup_outline_section_curriculum_row(info, "1-1")
    if row is None:
        raise ValueError("B2 1-1 requires its existing outline")
    return dict(action="existing", wrote=False, skill_id=row.skill_id,
                chapter=row.chapter, section=row.section)


def existing_skill(info, name, sid=""):
    from models import SkillCurriculum, SkillInfo, db

    rows = SkillCurriculum.query.filter_by(
        curriculum=info["curriculum"], volume=info["volume"],
        chapter=info["chapter"], section=info["section"], paragraph=name,
    ).all()
    matches = {r.skill_id: r for r in rows if r.skill_id.startswith("vh_")}
    if len(matches) != 1 or (sid and sid not in matches):
        raise ValueError(f"B2 1-1 requires one existing skill for {name}")
    row = next(iter(matches.values()))
    if db.session.get(SkillInfo, row.skill_id) is None:
        raise ValueError(f"Missing existing B2 1-1 SkillInfo: {row.skill_id}")
    return row


def align_existing_skills(blocks_keys, block_meta, info):
    """Complete this section's metadata from reviewed question/heading identities.

    Phase3 allows empty answers/solutions. Keep source solutions; do not invent them.
    One concept entry per question preserves source order through Phase4's buckets.
    """
    from models import SkillCurriculum, SkillInfo, db

    rows = SkillCurriculum.query.filter_by(
        curriculum=info["curriculum"], volume=info["volume"],
        chapter=info["chapter"], section=info["section"],
    ).all()
    concepts = []
    if set(blocks_keys) != set(block_meta):
        raise ValueError("B2 1-1 Phase3 titles differ from authoritative blocks")
    for title, block in block_meta.items():
        name = block.get("concept_name") or ""
        exercise = re.fullmatch(r"1-1習題 (基礎題|進階題) (\d+)", title)
        if exercise:
            number = int(exercise[2])
            if exercise[1] == "基礎題" and 1 <= number <= 3:
                name = "角的度量與換算"
            elif ((exercise[1] == "基礎題" and number in (4, 5))
                  or (exercise[1] == "進階題" and number in (9, 10))):
                name = "扇形的弧長與面積"
            elif exercise[1] == "基礎題" and number in (6, 7, 8):
                name = "同界角"
            else:
                raise ValueError(f"Unreviewed B2 1-1 exercise: {title}")
        matches = {r.skill_id: r for r in rows
                   if r.paragraph == name and r.skill_id.startswith("vh_")}
        if len(matches) != 1:
            raise ValueError(f"B2 1-1 requires one existing skill for {title}: {name}")
        sid, row = next(iter(matches.items()))
        skill = db.session.get(SkillInfo, sid)
        if skill is None:
            raise ValueError(f"Missing existing B2 1-1 SkillInfo: {sid}")
        block.update(concept_name=name, formal_skill_id=sid,
                     concept_en_id=skill.skill_en_name, mapping_source="existing_curriculum")
        item = dict(title=title, source_description=title,
                    source_type=block["source_type"], skill_id=sid,
                    correct_answer="", detailed_solution=block.get("detailed_solution", ""))
        bucket = "examples" if block["source_type"] == "textbook_example" else "practice_questions"
        concepts.append(dict(concept_name=name, concept_en_id=skill.skill_en_name,
                             **{bucket: [item]}))
    return {"chapters": [{"chapter_title": info["chapter"], "sections": [{
        "section_code": "1-1", "section_title": info["section"], "concepts": concepts,
    }]}], "metadata_source": "B2_1-1_reviewed_existing_curriculum"}


# Audited source PDF coordinates in points (1-based physical pages). A checksum
# prevents these corrections from being applied to a different PDF/edition.
B2_11_PDF_SHA256 = "001d6a62ba34479f86fc3576b8ae38632a0100070391b923fc61d56830bc3c35"
# label: (page, question top, question bottom, optional figure bbox)
PDF_REGIONS = {
    "例1": (5, 480, 740, None),
    "隨堂練習1": (6, 92, 215, None),
    "例2": (7, 320, 615, [380, 320, 500, 525]),
    "隨堂練習2": (7, 640, 725, None),
    SDG_TITLE: (8, 165, 628, [355, 223, 509, 408]),
    "例3": (10, 280, 535, [365, 375, 505, 485]),
    "隨堂練習3": (10, 565, 635, None),
    "例4": (11, 100, 485, None),
    "隨堂練習4": (11, 520, 590, None),
    "108統測B": (12, 192, 403, None),
    "1-1習題 基礎題1": (13, 170, 255, None),
    "1-1習題 基礎題2": (13, 275, 325, None),
    "1-1習題 基礎題3": (13, 345, 406, None),
    "1-1習題 基礎題4": (13, 428, 472, None),
    "1-1習題 基礎題5": (13, 491, 640, [315, 533, 389, 606]),
    "1-1習題 基礎題6": (13, 628, 666, None),
    "1-1習題 基礎題7": (13, 692, 736, None),
    "1-1習題 基礎題8": (14, 134, 185, None),
    "1-1習題 進階題9": (14, 261, 355, [408, 232, 528, 352]),
    "1-1習題 進階題10": (14, 375, 605, [361, 369, 530, 602]),
}


def correct_pdf_regions(matches, pages, pdf_path, info):
    """Apply source-specific ownership/crop corrections after the existing detector."""
    from core.textbook_question_anchor import normalize_question_label

    if not is_b2_11(info):
        return matches
    if hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest() != B2_11_PDF_SHA256:
        return matches
    for row in matches:
        label = normalize_question_label(row.get("source_description", ""))
        correction = PDF_REGIONS.get(label)
        if correction is None:
            continue
        page, top, bottom, figure = correction
        bbox = [36.0, top, pages[page - 1]["width"] - 36, bottom]
        regions = [{"page": page, "bbox": bbox}]
        row.update(pdf_match={"page": page, "question_start_y": top,
                              "question_bbox": bbox, "regions": regions},
                   match_score=1.0, match_method="audited_B2_1-1_pdf_sha256",
                   regions=regions, question_bbox=bbox, cross_page_suspected=False,
                   visual_page=page, visual_bbox=list(figure) if figure else None,
                   should_mount=bool(figure), needs_review=False,
                   visual_type="diagram" if figure else None,
                   visual_classification="helpful" if figure else "none",
                   visual_reason="audited_B2_1-1_source_figure" if figure else "audited_text_or_preserved_table")
    return matches
