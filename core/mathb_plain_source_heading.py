# -*- coding: utf-8 -*-
"""Source-authored plain headings that are not printed N-N.N concept codes.

These titles are pedagogical headings in the section exposition, for example
``1. 二元一次不等式的定義``.  The internal coordinate is ``3-2#1``.  It is not
a publisher concept code, and the skill id uses ``PlainHeading_`` so it cannot
be read as ``SubSection_3_2_1``.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

PLAIN_SOURCE_HEADING_STYLE = "02-內文1."
AUTHORITY_SOURCE = "source_authored_plain_heading"
B3_SECTION_3_2_EXAMPLE_COUNTS = {
    "vh_數學B3_PlainHeading_3_2_1": 0,
    "vh_數學B3_PlainHeading_3_2_2": 1,
    "vh_數學B3_PlainHeading_3_2_3": 14,
    "vh_數學B3_PlainHeading_3_2_4": 6,
}
_EXERCISE_HEADING_RE = re.compile(r"^\s*\d+\s*[-－–—]\s*\d+\s*習題")
_PLAIN_HEADING_RE = re.compile(
    r"^\s*(?P<number>[0-9０-９]+)[.．]\s*(?P<title>\S.+?)\s*$"
)
_QUESTION_TITLE_CUES = (
    "試求",
    "試判斷",
    "試寫",
    "試問",
    "圖示",
    "下列",
    "是否",
    "設點",
    "如圖",
    "已知",
)
_MAX_TITLE_LEN = 24


def _normalize(text: str) -> str:
    value = unicodedata.normalize("NFKC", str(text or ""))
    value = value.replace("\t", " ").replace("\u3000", " ")
    return re.sub(r" +", " ", value).strip()


def _ascii_digits(text: str) -> str:
    return str(text or "").translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def is_exercise_zone_heading(text: str) -> bool:
    return bool(_EXERCISE_HEADING_RE.match(_normalize(text)))


def parse_plain_source_heading(text: str, *, style_name: str) -> dict[str, Any] | None:
    """Accept one exposition heading. Reject exercise numbering and prompts."""
    if str(style_name or "") != PLAIN_SOURCE_HEADING_STYLE:
        return None
    raw = str(text or "")
    if "\n" in raw or "\r" in raw:
        return None
    norm = _normalize(raw)
    match = _PLAIN_HEADING_RE.match(norm)
    if not match:
        return None
    number = int(_ascii_digits(match.group("number")))
    title = _normalize(match.group("title"))
    if number < 1 or not title or len(title) > _MAX_TITLE_LEN:
        return None
    if title.endswith(("?", "？")):
        return None
    if any(cue in title for cue in _QUESTION_TITLE_CUES):
        return None
    return {
        "source_heading_number": number,
        "concept_name": title,
        "source_heading_text": norm,
    }


def collect_plain_source_headings(
    paragraphs: list[dict[str, Any]],
    *,
    section_code: str,
    volume: str,
) -> dict[str, Any]:
    """Collect contiguous exposition headings that appear before 習題."""
    accepted: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        text = str(paragraph.get("text") or "")
        if is_exercise_zone_heading(text):
            break
        parsed = parse_plain_source_heading(text, style_name=str(paragraph.get("style") or ""))
        if not parsed:
            continue
        nxt = paragraph.get("next_text") or ""
        if not str(nxt).strip():
            continue
        accepted.append(
            dict(
                parsed,
                source_order=paragraph.get("source_order"),
                style=paragraph.get("style"),
                font=paragraph.get("font"),
                size=paragraph.get("size"),
                bold=paragraph.get("bold"),
            )
        )
    numbers = [int(item["source_heading_number"]) for item in accepted]
    if not numbers:
        return {
            "plain_source_headings": [],
            "plain_source_heading_count": 0,
            "plain_source_rejected": [],
            "plain_source_sequence_ok": None,
        }
    contiguous = numbers == list(range(1, len(numbers) + 1))
    if not contiguous:
        return {
            "plain_source_headings": [],
            "plain_source_heading_count": 0,
            "plain_source_rejected": accepted,
            "plain_source_sequence_ok": False,
        }
    headings = []
    for item in accepted:
        number = int(item["source_heading_number"])
        coordinate = f"{section_code}#{number}"
        en_id = plain_heading_en_id(section_code, number)
        headings.append(
            {
                "authority_source": AUTHORITY_SOURCE,
                "source_heading_text": item["source_heading_text"],
                "concept_name": item["concept_name"],
                "source_heading_number": number,
                "source_order": item.get("source_order"),
                "source_style": item.get("style"),
                "font": item.get("font"),
                "size": item.get("size"),
                "bold": item.get("bold"),
                "source_page_start": None,
                "printed_concept_code": None,
                "source_concept_code": None,
                "internal_coordinate": coordinate,
                "concept_en_id": en_id,
                "formal_skill_id": plain_heading_skill_id(volume, section_code, number),
                "section_code": section_code,
            }
        )
    return {
        "plain_source_headings": headings,
        "plain_source_heading_count": len(headings),
        "plain_source_rejected": [],
        "plain_source_sequence_ok": True,
    }


def plain_heading_en_id(section_code: str, source_heading_number: int) -> str:
    chapter, section = str(section_code or "").split("-", 1)
    return f"PlainHeading_{int(chapter)}_{int(section)}_{int(source_heading_number)}"


def plain_heading_skill_id(volume: str, section_code: str, source_heading_number: int) -> str:
    from core.textbook_formal_concept import build_formal_skill_id_from_en_id

    return build_formal_skill_id_from_en_id(
        volume=volume,
        concept_en_id=plain_heading_en_id(section_code, source_heading_number),
    )


def classify_plain_heading_question(problem_text: str, headings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the primary source heading for one question. Does not invent names."""
    text = _normalize(problem_text)
    if not text or not headings:
        return None
    by_number = {int(item["source_heading_number"]): item for item in headings}

    def pick(number: int, reason: str) -> dict[str, Any] | None:
        heading = by_number.get(number)
        if heading is None:
            return None
        return dict(heading, assignment_reason=reason)

    if any(cue in text for cue in ("同側", "異側", "哪一區", "同一區", "東區", "西區")):
        return pick(4, "same_side_or_region_language")
    if any(cue in text for cue in ("半平面", "塗上顏色", "畫斜線", "鋪色", "圖示下列", "圖示二元", "解區域")):
        return pick(3, "half_plane_graph")
    if "寫出滿足" in text and "不等式" in text:
        return pick(3, "inequality_from_figure")
    if any(cue in text for cue in ("是否為不等式的解", "不能超過", "攝取")):
        return pick(2, "solution_pair")
    if any(cue in text for cue in ("是否為二元一次不等式", "二元一次不等式的定義")):
        return pick(1, "definition")
    return None


def assign_plain_source_questions(
    block_meta: dict[str, dict[str, Any]],
    headings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for title, block in block_meta.items():
        heading = classify_plain_heading_question(str((block or {}).get("problem_text") or ""), headings)
        rows.append(
            {
                "title": title,
                "source_type": str((block or {}).get("source_type") or ""),
                "assigned": heading is not None,
                "concept_name": heading["concept_name"] if heading else "",
                "formal_skill_id": heading["formal_skill_id"] if heading else "",
                "internal_coordinate": heading["internal_coordinate"] if heading else "",
                "source_heading_number": heading["source_heading_number"] if heading else None,
                "printed_concept_code": None,
                "assignment_reason": heading.get("assignment_reason") if heading else "unassigned",
            }
        )
    return rows


def align_plain_source_heading_metadata(
    keys: list[str],
    block_meta: dict[str, dict[str, Any]],
    info: dict[str, Any],
) -> dict[str, Any]:
    """Bind every parsed question to a source heading without Gemini skill ids."""
    headings = list(info.get("plain_source_headings") or [])
    ordered = [(key, block_meta[key]) for key in keys if key in block_meta]
    assignments = assign_plain_source_questions(dict(ordered), headings)
    by_title = {row["title"]: row for row in assignments}
    unresolved = [row["title"] for row in assignments if not row["assigned"]]
    concepts = []
    for order, (title, block) in enumerate(ordered, 1):
        row = by_title[title]
        item = {
            "title": title,
            "source_description": title,
            "source_order": order,
            "source_type": block.get("source_type"),
            "skill_id": row["formal_skill_id"],
            "correct_answer": "",
            "detailed_solution": block.get("detailed_solution", ""),
            "mapping_status": "plain_source_heading" if row["assigned"] else "unassigned",
            "needs_skill_resolution": not row["assigned"],
            "printed_concept_code": None,
            "internal_coordinate": row["internal_coordinate"],
            "notes": json.dumps(
                {"plain_source_heading": provenance_payload(row)},
                ensure_ascii=False,
            ) if row["assigned"] else None,
        }
        bucket = "examples" if block.get("source_type") == "textbook_example" else "practice_questions"
        concepts.append({"concept_name": row["concept_name"], "concept_en_id": "", bucket: [item]})
    return {
        "chapters": [
            {
                "chapter_title": info.get("chapter"),
                "sections": [
                    {
                        "section_code": info.get("section_code"),
                        "section_title": info.get("section"),
                        "concepts": concepts,
                    }
                ],
            }
        ],
        "metadata_source": "source_authored_plain_heading",
        "metadata_alignment": "PASS" if not unresolved and len(assignments) == len(ordered) else "FAIL",
        "unresolved_skill_bindings": unresolved,
        "needs_skill_resolution": [],
        "section_outline_fallback_count": 0,
        "plain_source_assignments": assignments,
    }


def _pdf_page_texts(pdf_path: str) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None
    if PdfReader is not None:
        reader = PdfReader(pdf_path)
        return [_normalize(page.extract_text() or "").replace(" ", "") for page in reader.pages]
    import fitz

    with fitz.open(pdf_path) as document:
        return [_normalize(page.get_text() or "").replace(" ", "") for page in document]


def provenance_payload(heading: dict[str, Any]) -> dict[str, Any]:
    """Persist source evidence without inventing a printed concept code."""
    return {
        "authority_source": AUTHORITY_SOURCE,
        "source_heading_text": heading.get("source_heading_text"),
        "source_order": heading.get("source_order"),
        "source_page_start": heading.get("source_page_start"),
        "source_heading_number": heading.get("source_heading_number"),
        "printed_concept_code": None,
        "source_concept_code": None,
        "internal_coordinate": heading.get("internal_coordinate"),
        "formal_skill_id": heading.get("formal_skill_id"),
        "concept_name": heading.get("concept_name"),
    }


def provenance_setting_key(skill_id: str) -> str:
    return f"plain_source_heading:{skill_id}"


def stamp_plain_heading_question_bindings(
    block_meta: dict[str, dict[str, Any]],
    assignments: list[dict[str, Any]],
) -> None:
    """Copy the already chosen skill onto Phase2 blocks. Does not reclassify."""
    for row in assignments:
        block = block_meta.get(str(row.get("title") or ""))
        if block is None or not row.get("assigned"):
            continue
        block["formal_skill_id"] = row.get("formal_skill_id")
        block["concept_name"] = row.get("concept_name")
        block["concept_code"] = ""
        block["display_order"] = int(row.get("source_heading_number") or 0)
        block["internal_coordinate"] = row.get("internal_coordinate")


def ensure_plain_source_heading_formal_skills(curriculum_info: dict[str, Any]) -> list[dict[str, Any]]:
    """Create or reuse the four source-authored skills, including one with no examples."""
    from models import SkillInfo, SystemSetting, db
    from core.textbook_processor_v2 import _ensure_formal_skill_info_and_curriculum_v2

    results = []
    for heading in list(curriculum_info.get("plain_source_headings") or []):
        skill_id = str(heading.get("formal_skill_id") or "").strip()
        concept_name = str(heading.get("concept_name") or "").strip()
        existed = db.session.get(SkillInfo, skill_id) is not None
        _ensure_formal_skill_info_and_curriculum_v2(
            formal_skill_id=skill_id,
            concept_name=concept_name,
            concept_en_id=str(heading.get("concept_en_id") or ""),
            curriculum=str(curriculum_info.get("curriculum") or ""),
            grade=int(curriculum_info.get("grade") or 10),
            volume=str(curriculum_info.get("volume") or ""),
            chapter_title=str(curriculum_info.get("chapter") or ""),
            section_title=str(curriculum_info.get("section") or ""),
            paragraph=concept_name,
            display_order=int(heading.get("source_heading_number") or 0),
            section_code=str(curriculum_info.get("section_code") or ""),
            concept_code="",
            allow_ai_description=False,
        )
        payload = provenance_payload(heading)
        key = provenance_setting_key(skill_id)
        setting = SystemSetting.query.filter_by(key=key).one_or_none()
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        if setting is None:
            db.session.add(
                SystemSetting(
                    key=key,
                    value=encoded,
                    description="Source-authored plain heading provenance. Not a publisher concept code.",
                )
            )
        else:
            setting.value = encoded
        results.append(
            {
                "action": "existing" if existed else "created",
                "skill_id": skill_id,
                "concept_name": concept_name,
                "internal_coordinate": heading.get("internal_coordinate"),
                "printed_concept_code": None,
            }
        )
    return results


def plain_heading_example_distribution(rows: list[Any], skill_ids: list[str]) -> dict[str, int]:
    counts = {skill_id: 0 for skill_id in skill_ids}
    for row in rows:
        skill_id = str(getattr(row, "skill_id", "") or "")
        if skill_id in counts:
            counts[skill_id] += 1
    return counts


def classify_question_visual_dependency(problem_text: str) -> dict[str, str]:
    """Inventory only. Does not generate a figure or a question."""
    text = _normalize(problem_text)
    if "如下圖" in text and any(cue in text for cue in ("哪一區", "同一區", "東區", "西區")):
        return {
            "visual_dependency": "TEXT_RECOVERABLE",
            "depends_on_image": "illustrative",
            "image_role": "同側異側示意；直線與點座標已寫在題幹",
        }
    if any(cue in text for cue in ("寫出滿足", "鋪色", "如圖")):
        role = "由圖寫不等式"
        if "鋪色" in text:
            role = "由鋪色區域寫不等式"
        elif "如圖" in text:
            role = "由圖讀截距並寫出不等式"
        return {
            "visual_dependency": "VISUAL_REQUIRED",
            "depends_on_image": "required",
            "image_role": role,
        }
    if any(cue in text for cue in ("半平面", "塗上顏色", "畫斜線", "圖示下列", "圖示二元", "解區域")):
        return {
            "visual_dependency": "DETERMINISTIC_VISUAL",
            "depends_on_image": "generated_from_stem",
            "image_role": "畫半平面；不等式已寫在題幹",
        }
    return {
        "visual_dependency": "TEXT_ONLY",
        "depends_on_image": "no",
        "image_role": "",
    }


def attach_pdf_page_starts(pdf_path: str, headings: list[dict[str, Any]]) -> None:
    """Record the first PDF page whose text contains each source heading."""
    try:
        pages = _pdf_page_texts(pdf_path)
    except Exception:
        return
    for heading in headings:
        needle = _normalize(heading.get("concept_name") or "").replace(" ", "")
        heading["source_page_start"] = next(
            (index for index, text in enumerate(pages, 1) if needle and needle in text),
            None,
        )
