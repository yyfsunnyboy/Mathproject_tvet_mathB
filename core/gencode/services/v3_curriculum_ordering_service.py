# -*- coding: utf-8 -*-
"""Shared Textbook Curriculum Ordering Service."""

from __future__ import annotations

import re
import sys
import warnings
from typing import Any
import sqlite3

# Priority sorting for source groups
_GROUP_PRIORITY = {
    "example": 0,
    "in_class": 0,
    "basic_practice": 1,
    "comprehensive": 2,
    "self_assessment": 3,
    "past_exam": 4,
}


def parse_source_description(desc: str) -> dict[str, Any]:
    """Parse source_description text to classify source_group and extract numbers.

    Returns:
        {
            "source_group": str,
            "source_number": int,
            "source_subnumber": int,
        }
    """
    text = str(desc or "").strip()
    group = None
    num = 0
    subnum = 0

    # Determine group
    if "隨堂" in text:
        group = "in_class"
    elif "例題" in text:
        group = "example"
    elif "綜合" in text or "綜合練習" in text:
        group = "comprehensive"
    elif "基礎" in text or "基礎練習" in text or "習題" in text:
        group = "basic_practice"
    elif "自我評量" in text or "評量" in text:
        group = "self_assessment"
    elif "歷屆" in text or "考題" in text or "學測" in text or "指考" in text:
        group = "past_exam"

    # Default logic or warning if unrecognized
    if not group:
        group = "example"
        warnings.warn(f"[Curriculum Ordering Warning] Unrecognized source_group for description: '{desc}'. Defaulting to 'example'.")

    # Extract numbers (e.g. "例題2-1" or "題2" or "題 3-2")
    m = re.search(r"(\d+)(?:\s*-\s*(\d+))?", text)
    if m:
        num = int(m.group(1))
        if m.group(2):
            subnum = int(m.group(2))
    else:
        warnings.warn(f"[Curriculum Ordering Warning] Unrecognized source_number / subnumber pattern in: '{desc}'. Using 0-0.")

    return {
        "source_group": group,
        "source_number": num,
        "source_subnumber": subnum,
    }


def get_sorted_component_ids_for_skill(conn: sqlite3.Connection, skill_id: str, verified_component_ids: list[str]) -> list[str]:
    """Fetch textbook examples from database for the given skill, parse and sort them,
    and return the ordered component_ids. Only returns components in the verified list.
    """
    if not verified_component_ids:
        return []

    cursor = conn.cursor()
    
    # Try to fetch columns including curriculum_order / display_order
    curriculum_order_field = "id"
    # Inspect schema to check if curriculum_order, display_order, or similar exists
    try:
        cursor.execute("PRAGMA table_info(textbook_examples)")
        columns = [c[1] for c in cursor.fetchall()]
        if "curriculum_order" in columns:
            curriculum_order_field = "curriculum_order"
        elif "display_order" in columns:
            curriculum_order_field = "display_order"
        else:
            warnings.warn(f"[Curriculum Ordering Warning] textbook_examples does not contain curriculum_order or display_order. Falling back to primary key 'id' for ordering.")
    except Exception:
        pass

    try:
        cursor.execute(
            f"""
            SELECT id, source_description, {curriculum_order_field}
            FROM textbook_examples
            WHERE skill_id = ?
            """,
            (skill_id,),
        )
        rows = cursor.fetchall()
    except Exception:
        rows = []

    # Map textbook example id to its ordering keys
    example_map = {}
    for r in rows:
        eid = int(r[0] or 0)
        desc = str(r[1] or "")
        parsed = parse_source_description(desc)
        parsed["curriculum_order"] = int(r[2] or 0)
        example_map[eid] = parsed

    # Diagnostics details container
    diagnostics = []

    def get_sort_key(cid: str) -> tuple[int, int, int, int, int, int]:
        eid = 0
        if str(cid).startswith("src_"):
            try:
                eid = int(str(cid).split("_")[1])
            except Exception:
                pass
        
        parsed = example_map.get(eid)
        if not parsed:
            # Fallback parsing
            parsed = parse_source_description(cid)
            parsed["curriculum_order"] = eid  # fallback to eid

        group = parsed["source_group"]
        source_number = parsed["source_number"]
        source_subnumber = parsed["source_subnumber"]
        curriculum_order = parsed["curriculum_order"]

        # Phase 0: example and in_class (paired)
        # Phase 1: other practices
        if group in ("example", "in_class"):
            phase = 0
            pair_order = 0 if group == "example" else 1
            group_priority = 0
            # Phase 0: (0, source_number, source_subnumber, pair_order, curriculum_order)
            key = (0, source_number, source_subnumber, pair_order, curriculum_order)
        else:
            phase = 1
            pair_order = 0
            group_priority = _GROUP_PRIORITY.get(group, 99)
            # Phase 1: (1, group_priority, curriculum_order, source_number, source_subnumber)
            key = (1, group_priority, curriculum_order, source_number, source_subnumber)

        diagnostics.append({
            "component_id": cid,
            "source_group": group,
            "source_number": source_number,
            "source_subnumber": source_subnumber,
            "curriculum_order": curriculum_order,
            "phase": phase,
            "pair_order": pair_order,
            "group_priority": group_priority,
            "final_sort_key": key,
        })
        return key

    sorted_ids = sorted(verified_component_ids, key=get_sort_key)

    # Output diagnostics for traceability
    sys.stdout.write(f"\n--- DIAGNOSTICS FOR SKILL: {skill_id} ---\n")
    # To associate positions correctly after sorting:
    sorted_positions = {cid: idx for idx, cid in enumerate(sorted_ids, 1)}
    for diag in diagnostics:
        cid = diag["component_id"]
        pos = sorted_positions.get(cid, -1)
        sys.stdout.write(
            f"Component: {cid} | Group: {diag['source_group']} | Num: {diag['source_number']}-{diag['source_subnumber']} | "
            f"Curriculum Order: {diag['curriculum_order']} | Phase: {diag['phase']} | Pair Order: {diag['pair_order']} | "
            f"Group Priority: {diag['group_priority']} | Sort Key: {diag['final_sort_key']} | Final Position: {pos}\n"
        )
    sys.stdout.flush()

    return sorted_ids

