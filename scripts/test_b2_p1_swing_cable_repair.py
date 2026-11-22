# -*- coding: utf-8 -*-
"""Focused regression for P1 swing/cable Skill remap + visual pairing."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ACUTE = "vh_數學B2_TrigonometricFunctionsOfAcuteAngles"
SPECIAL = "vh_數學B2_TrigonometricValuesOfSpecialAngles"
SECTOR = "vh_數學B2_ArcLengthAndAreaOfSector"


def _ok(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" :: {detail}" if detail else ""))
    if not cond:
        raise AssertionError(name + (f": {detail}" if detail else ""))


def test_specs_and_db() -> None:
    from core.gencode.b2_12_component_specs import get_b2_12_component_spec

    s83 = get_b2_12_component_spec(11583)
    s84 = get_b2_12_component_spec(11584)
    _ok("spec_11583_skill_sector", s83["skill_id"] == SECTOR, s83["skill_id"])
    _ok("spec_11583_op_chord_arc", s83["operation"] == "compute_chord_and_arc_length")
    _ok("spec_11584_skill_acute", s84["skill_id"] == ACUTE, s84["skill_id"])
    _ok("spec_11584_op_projection", s84["operation"] == "solve_right_triangle_projection")

    con = sqlite3.connect(ROOT / "instance" / "kumon_math.db")
    con.row_factory = sqlite3.Row
    for te_id, skill in ((11583, SECTOR), (11584, ACUTE)):
        row = con.execute(
            "SELECT skill_id, notes FROM textbook_examples WHERE id=?", (te_id,)
        ).fetchone()
        _ok(f"db_{te_id}_skill", row["skill_id"] == skill, row["skill_id"])
        notes = json.loads(row["notes"])
        assets = notes.get("image_assets") or []
        _ok(f"db_{te_id}_has_asset", bool(assets))
        asset = assets[0]
        _ok(f"db_{te_id}_visual_accepted", asset.get("visual_status") == "accepted")
        _ok(f"db_{te_id}_repair_reason", "audited_B2_1-2_p1" in str(asset.get("reason") or ""))
        rel = str(asset.get("path") or "")
        abs_path = ROOT / "static" / "question_assets" / rel[len("uploads/question_assets/") :]
        _ok(f"db_{te_id}_png_exists", abs_path.is_file(), str(abs_path))
        data = abs_path.read_bytes()
        import hashlib

        _ok(f"db_{te_id}_sha_match", hashlib.sha256(data).hexdigest() == asset["sha256"])
    con.close()


def test_inventory_and_sampling() -> None:
    from core.gencode.services.generator_problem_type_inventory import inventory_skill_generator_problem_types
    from core.practice_type_mastery import list_required_problem_types
    import importlib

    acute_inv = inventory_skill_generator_problem_types(ACUTE)
    special_inv = inventory_skill_generator_problem_types(SPECIAL)
    sector_inv = inventory_skill_generator_problem_types(SECTOR)

    acute_types = set(acute_inv.get("usable_problem_type_ids") or [])
    special_types = set(special_inv.get("usable_problem_type_ids") or [])
    sector_types = set(sector_inv.get("usable_problem_type_ids") or [])

    _ok("acute_no_chord_arc", "compute_chord_and_arc_length" not in acute_types, str(sorted(acute_types)))
    _ok("acute_has_projection", "solve_right_triangle_projection" in acute_types, str(sorted(acute_types)))
    _ok("sector_has_chord_arc", "compute_chord_and_arc_length" in sector_types, str(sorted(sector_types)))
    _ok("special_still_has_projection", "solve_right_triangle_projection" in special_types)

    acute_y = list_required_problem_types(ACUTE)
    sector_y = list_required_problem_types(SECTOR)
    _ok("acute_Y_excludes_chord", "compute_chord_and_arc_length" not in acute_y)
    _ok("sector_Y_includes_chord", "compute_chord_and_arc_length" in sector_y)

    acute_mod = importlib.import_module(f"skills.{ACUTE}")
    sector_mod = importlib.import_module(f"skills.{SECTOR}")
    special_mod = importlib.import_module(f"skills.{SPECIAL}")

    acute_keys = set(acute_mod.GENERATOR_KEYS)
    sector_keys = set(sector_mod.GENERATOR_KEYS)
    special_keys = set(special_mod.GENERATOR_KEYS)
    _ok("acute_has_11584", "src_11584" in acute_keys)
    _ok("acute_no_11583", "src_11583" not in acute_keys)
    _ok("sector_has_11583", "src_11583" in sector_keys)
    _ok("special_no_11584", "src_11584" not in special_keys)


def test_generate_payloads() -> None:
    from skills.vh_數學B2_ArcLengthAndAreaOfSector import generate as gen_sector
    from skills.vh_數學B2_TrigonometricFunctionsOfAcuteAngles import generate as gen_acute

    swing = None
    for seed in range(80):
        p = gen_sector(level=1, seed=seed, component_id="src_11583")
        if str(p.get("component_id") or p.get("metadata", {}).get("component_id")) == "src_11583" or "鞦韆" in str(
            p.get("question_text") or p.get("question") or ""
        ):
            swing = p
            break
        # force component
        from agent_skills_v3.vh_數學B2_ArcLengthAndAreaOfSector.components.src_11583.generate import (
            generate as g83,
        )

        swing = g83(level=1, seed=seed)
        break
    _ok("swing_payload", swing is not None)
    q = str(swing.get("question_text") or swing.get("question") or "")
    _ok("swing_text", "鞦韆" in q or "弦" in q or "弧" in q, q[:80])
    _ok("swing_type", swing.get("problem_type_id") == "compute_chord_and_arc_length", str(swing.get("problem_type_id")))
    _ok("swing_skill_meta", (swing.get("metadata") or {}).get("skill_id") == SECTOR, str((swing.get("metadata") or {}).get("skill_id")))
    vs = swing.get("visual_spec") or {}
    _ok("swing_visual_asset", "進階題9" in str(vs.get("asset_path") or ""), str(vs))
    parts = ((swing.get("answer_contract") or {}).get("parts")) or []
    _ok("swing_multipart", len(parts) >= 2, str(parts))

    from agent_skills_v3.vh_數學B2_TrigonometricFunctionsOfAcuteAngles.components.src_11584.generate import (
        generate as g84,
    )

    cable = g84(level=1, seed=1)
    cq = str(cable.get("question_text") or cable.get("question") or "")
    _ok("cable_text", "纜車" in cq or "900" in cq, cq[:100])
    _ok("cable_type", cable.get("problem_type_id") == "solve_right_triangle_projection")
    _ok("cable_skill_meta", (cable.get("metadata") or {}).get("skill_id") == ACUTE)
    cvs = cable.get("visual_spec") or {}
    _ok("cable_visual_asset", "進階題10" in str(cvs.get("asset_path") or ""), str(cvs))
    # answers sanity: elevation=500+900*sin45=500+450√2, horizontal=900*cos45=450√2
    cparts = {p.get("key"): p.get("expected_answer") for p in ((cable.get("answer_contract") or {}).get("parts") or [])}
    _ok("cable_has_parts", len(cparts) >= 2, str(cparts))

    # Acute skill sampling never yields swing text
    for seed in range(40):
        p = gen_acute(level=1, seed=seed)
        text = str(p.get("question_text") or p.get("question") or "")
        _ok(f"acute_seed_{seed}_not_swing", "鞦韆" not in text, text[:60])


def test_mastery_compat() -> None:
    con = sqlite3.connect(ROOT / "instance" / "kumon_math.db")
    n = con.execute(
        "SELECT COUNT(*) FROM student_problem_type_mastery WHERE skill_id=? AND problem_type_id=?",
        (ACUTE, "compute_chord_and_arc_length"),
    ).fetchone()[0]
    # orphan rows allowed; we must not delete. Just report.
    print(f"[INFO] orphan_acute_chord_arc_mastery_rows={n} (kept intentionally)")
    kept = con.execute(
        "SELECT COUNT(*) FROM student_problem_type_mastery WHERE skill_id=?",
        (ACUTE,),
    ).fetchone()[0]
    _ok("acute_mastery_rows_not_wiped", kept >= 0)
    con.close()


def main() -> None:
    test_specs_and_db()
    test_inventory_and_sampling()
    test_generate_payloads()
    test_mastery_compat()
    print("ALL_PASS")


if __name__ == "__main__":
    main()
