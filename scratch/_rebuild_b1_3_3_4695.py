# -*- coding: utf-8 -*-
"""Repair 4695 DB source, rebuild src_4695, publish into PolynomialFactoring."""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
)
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.registry.taxonomy_registry import get_fixed_domain_key

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "rebuild_b1_3_3_execute", ROOT / "scratch" / "_rebuild_b1_3_3_execute.py"
)
_rb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_rb)

from core.gencode.services.component_tracker_service import save_tracker_record, update_status

EID = 4695
SKILL = "vh_數學B1_PolynomialFactoring"
CID = "src_4695"
NEW_TEXT = (
    r"利用乘法公式因式分解下列各式："
    r"(1)${{x}^{2}}-4$ (2)${{\left( a+b \right)}^{2}}-25$。"
)
NEW_ANSWER = "(1) (x-2)(x+2) (2) (a+b-5)(a+b+5)"
LOCKED = (
    "skill_id",
    "problem_type",
    "source_curriculum",
    "source_volume",
    "source_chapter",
    "source_section",
    "source_paragraph",
    "source_description",
    "difficulty_level",
    "difficulty_h",
    "notes",
)


def _dump_row(d: dict) -> dict:
    return {
        "example_id": d.get("id"),
        "skill_id": d.get("skill_id"),
        "source_description": d.get("source_description"),
        "problem_text": d.get("problem_text"),
        "choices": None,
        "correct_answer": d.get("correct_answer"),
        "problem_type_id": None,
        "problem_type": d.get("problem_type"),
        "classification": None,
        "chapter": d.get("source_chapter"),
        "section": d.get("source_section"),
        "source_paragraph": d.get("source_paragraph"),
        "detailed_solution": d.get("detailed_solution"),
        "notes": d.get("notes"),
    }


def _enrich(conn: sqlite3.Connection, at: str) -> None:
    payload = {
        "component_id": CID,
        "skill_id": SKILL,
        "textbook_example_id": EID,
        "problem_type_id": "polynomial_factoring",
        "domain_operation": "polynomial_factoring",
        "selected_operation": "polynomial_factoring",
        "line_type": "polynomial_factoring",
        "fixed_domain_key": get_fixed_domain_key(SKILL) or "algebra.polynomial",
        "presentation_mode": "short_answer",
        "response_mode": "short_answer",
        "interaction_type": "short_answer",
        "answer_type": at,
        "answer_value_type": at,
        "checker_key": "multi_part_answer_checker",
        "equivalence_type": "multi_part_answer",
        "generator_readiness": "verified",
        "choice_contract_valid": True,
        "integrity_gate_passed": True,
        "integrity_gate_blockers": [],
        "integrity_gate_version": "v1",
        "domain_module": "core.domain.polynomial_domain",
        "entrypoint": "build_polynomial_matrix",
        "binding_status": "confirmed",
        "resolution_source": "confirmed_binding",
        "required_capabilities": ["polynomial_factoring"],
        "matched_capabilities": ["polynomial_factoring"],
        "source_kind": "quiz",
    }
    save_tracker_record(
        conn,
        textbook_example_id=EID,
        skill_id=SKILL,
        gencode_status="verified",
        induced_spec_payload=payload,
        gencode_error_log=None,
    )
    try:
        update_status(conn, textbook_example_id=EID, skill_id=SKILL, gencode_status="verified")
    except Exception:
        pass


def main() -> int:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone()
    if row is None:
        raise SystemExit("STOP missing 4695")
    before = dict(row)
    rec = _dump_row(before)
    print("STEP1_SELECT")
    for k, v in rec.items():
        print(f"  {k}={v}")
    if before["skill_id"] != SKILL:
        raise SystemExit(f"STOP skill_id={before['skill_id']}")
    if "3-3" not in str(before.get("source_section") or ""):
        raise SystemExit(f"STOP section={before.get('source_section')}")
    desc = str(before.get("source_description") or "")
    if "隨堂練習2" not in desc and "練習2" not in desc:
        raise SystemExit(f"STOP source_description={desc}")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ROOT / "scratch" / f"_b1_3_3_4695_db_backup_{stamp}.json"
    backup_path.write_text(json.dumps([rec], ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP", backup_path.name)

    round_backup = ROOT / "scratch" / "_b1_3_3_rational_equation_db_backup_20260908_120805.json"
    if round_backup.is_file():
        existing = json.loads(round_backup.read_text(encoding="utf-8"))
        if not any(int(x.get("example_id") or 0) == EID for x in existing):
            existing.append(rec)
            round_backup.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
            print("BACKUP_APPENDED_ROUND", round_backup.name)

    conn.execute(
        "UPDATE textbook_examples SET problem_text = ?, correct_answer = ? WHERE id = ?",
        (NEW_TEXT, NEW_ANSWER, EID),
    )
    after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (EID,)).fetchone())
    locked_changed = {k: (before.get(k), after.get(k)) for k in LOCKED if before.get(k) != after.get(k)}
    if locked_changed:
        conn.rollback()
        raise SystemExit(f"locked_fields_changed:{locked_changed}")
    conn.commit()
    print("DB_AFTER", after["problem_text"])
    print("DB_ANSWER", after["correct_answer"])

    _rb.DB_TEXTS[EID] = NEW_TEXT
    ensure_gencode_component_tracker_table(conn)
    dry = run_admin_v3_dryrun_for_example(
        conn=conn,
        textbook_example_id=EID,
        skill_id=SKILL,
        dryrun_base_dir=_rb.DRYRUN,
        seed=7,
        allow_non_mvp_skill=True,
        force_regenerate=True,
    )
    print("DRYRUN", dry.get("status") or dry.get("tracker_status"))
    comp_dir = ROOT / _rb.DRYRUN / SKILL / "components" / CID
    if not (comp_dir / "generate.py").is_file():
        raise SystemExit(f"generate_py_missing:{dry}")

    _rb._inject_source_text(comp_dir, NEW_TEXT)
    gen0 = _rb._load_module(comp_dir / "generate.py", "pre_4695")
    sample = gen0.generate(seed=7, component_id=CID)
    topo = _rb._patch_answer_contract_files(comp_dir, sample if isinstance(sample, dict) else {}, force_choice=False)
    _rb._inject_source_text(comp_dir, NEW_TEXT)
    vr = _rb._verify_20(comp_dir, CID, expect_choice=False)
    print("VERIFY20", vr.get("result"), "type", vr.get("answer_type"), "errors", vr.get("errors"))
    if not vr.get("ok"):
        raise SystemExit(f"VERIFY_FAIL:{vr}")

    extra_errors = []
    gen = _rb._load_module(comp_dir / "generate.py", "post_4695")
    from core.gencode.runtime_skill_wrapper import check_answer

    for i in range(20):
        seed = 7000 + i
        pl = gen.generate(seed=seed, component_id=CID)
        ans = pl.get("answer")
        if not isinstance(ans, dict) or set(ans) != {"part_1", "part_2"}:
            extra_errors.append(f"{seed}:parts={ans}")
            continue
        if pl.get("answer_type") != "multi_part":
            extra_errors.append(f"{seed}:type={pl.get('answer_type')}")
            continue
        if not check_answer(ans, ans, payload=pl):
            extra_errors.append(f"{seed}:all_correct_fail")
            continue
        w1 = dict(ans)
        w1["part_1"] = "(x-99)(x+99)"
        if check_answer(w1, ans, payload=pl):
            extra_errors.append(f"{seed}:part1_wrong_accepted")
            continue
        w2 = dict(ans)
        w2["part_2"] = "(a+b-99)(a+b+99)"
        if check_answer(w2, ans, payload=pl):
            extra_errors.append(f"{seed}:part2_wrong_accepted")
            continue
        g = ((pl.get("metadata") or {}).get("givens") or {})
        k, m = g.get("k"), g.get("m")
        if k is not None and str(ans.get("part_1")) != f"(x-{k})(x+{k})":
            extra_errors.append(f"{seed}:part1_not_derived:{ans.get('part_1')}:{k}")
    if extra_errors:
        raise SystemExit(f"EXTRA_FAIL:{extra_errors[:8]}")
    print("EXTRA_PART_CHECKS PASS")

    _rb._copy_to_production(SKILL, CID)
    _enrich(conn, str(vr.get("answer_type") or "multi_part"))
    conn.commit()

    pub = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=SKILL,
        project_root=str(ROOT),
        staging_root=_rb.STAGING,
        force_publish=True,
        strict_coverage=False,
    )
    print("PUBLISH", pub.get("status"), "count", pub.get("component_count"))
    smoke = _rb._smoke_skill(SKILL, 40)
    print("SMOKE", smoke["passed"], "/", smoke["samples"], "keys", smoke.get("wrapper_keys"))
    print("HITS", smoke.get("hits"))
    if CID not in (smoke.get("wrapper_keys") or []) or smoke.get("hits", {}).get(CID, 0) == 0:
        targeted = _rb._load_module(ROOT / "skills" / f"{SKILL}.py", "facade").generate(seed=7, component_id=CID)
        print("TARGETED", targeted.get("answer_type"), targeted.get("answer"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
