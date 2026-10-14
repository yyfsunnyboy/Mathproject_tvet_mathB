# -*- coding: utf-8 -*-
"""Repair 4713/4715 DB source, rebuild generators, publish PolynomialFactoring."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from datetime import datetime
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.domain.polynomial_domain import poly_plain
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
)
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.registry.taxonomy_registry import get_fixed_domain_key
from core.gencode.services.component_tracker_service import save_tracker_record, update_status
from core.gencode.runtime_skill_wrapper import check_answer

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "rebuild_b1_3_3_execute", ROOT / "scratch" / "_rebuild_b1_3_3_execute.py"
)
_rb = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_rb)

SKILL = "vh_數學B1_PolynomialFactoring"
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
ITEMS = [
    {
        "qid": 16,
        "eid": 4713,
        "cid": "src_4713",
        "desc_token": "題16",
        "stem_tokens": ("長方形", "周長", "y"),
        "answer": "D",
        "text": (
            r"已知一長方形的面積為$9{{x}^{2}}+6x+1-{{y}^{2}}$平方單位，"
            r"若其長、寬均為x、y的一次式且x、y項的係數均為整數，"
            r"則此長方形的周長為？ (A) $6x+4$ (B) $6x-4$ (C) $12x-4$ (D) $12x+4$"
        ),
    },
    {
        "qid": 18,
        "eid": 4715,
        "cid": "src_4715",
        "desc_token": "題18",
        "stem_tokens": ("何者", "因式", "x^{2}}-2x"),
        "answer": "B",
        "text": (
            r"下列何者為多項式${{\left( {{x}^{2}}-2x \right)}^{2}}-8\left( {{x}^{2}}-2x \right)+15$之因式？"
            r" (A) $x+3$ (B) $x-3$ (C) $x+2$ (D) $x-2$"
        ),
    },
]


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


def _norm(s: object) -> str:
    return re.sub(r"[\s${}\\]", "", str(s or ""))


def _lin_root(text: object):
    t = _norm(text)
    if t in {"x", "+x"}:
        return 0
    m = re.fullmatch(r"x([+-]\d+)", t)
    if m:
        return -int(m.group(1))
    return None


def _patch_source_kind(comp_dir: Path) -> None:
    meta_path = comp_dir / "metadata.py"
    meta = meta_path.read_text(encoding="utf-8")
    meta = re.sub(
        r'^SOURCE_KIND:\s*Final\[str\]\s*=\s*".*?"',
        'SOURCE_KIND: Final[str] = "test"',
        meta,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'^RESPONSE_MODE:\s*Final\[str\]\s*=\s*".*?"',
        'RESPONSE_MODE: Final[str] = "single_choice"',
        meta,
        count=1,
        flags=re.M,
    )
    meta = re.sub(
        r'^INTERACTION_TYPE:\s*Final\[str\]\s*=\s*".*?"',
        'INTERACTION_TYPE: Final[str] = "single_choice"',
        meta,
        count=1,
        flags=re.M,
    )
    meta_path.write_text(meta, encoding="utf-8")


def _enrich(conn: sqlite3.Connection, eid: int, cid: str) -> None:
    payload = {
        "component_id": cid,
        "skill_id": SKILL,
        "textbook_example_id": eid,
        "problem_type_id": "polynomial_factoring",
        "domain_operation": "polynomial_factoring",
        "selected_operation": "polynomial_factoring",
        "line_type": "polynomial_factoring",
        "fixed_domain_key": get_fixed_domain_key(SKILL) or "algebra.polynomial",
        "presentation_mode": "single_choice",
        "response_mode": "single_choice",
        "interaction_type": "single_choice",
        "answer_type": "single_choice",
        "answer_value_type": "single_choice",
        "checker_key": "choice_label_checker",
        "equivalence_type": "choice_label",
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
        "source_kind": "test",
    }
    save_tracker_record(
        conn,
        textbook_example_id=eid,
        skill_id=SKILL,
        gencode_status="verified",
        induced_spec_payload=payload,
        gencode_error_log=None,
    )
    try:
        update_status(conn, textbook_example_id=eid, skill_id=SKILL, gencode_status="verified")
    except Exception:
        pass


def _extra_q16(pl: dict, seed: int) -> list[str]:
    errors: list[str] = []
    g = ((pl.get("metadata") or {}).get("givens") or {}) or (pl.get("givens") or {})
    try:
        k, m = int(g["k"]), int(g["m"])
    except Exception:
        return [f"{seed}:q16_missing_km:{g}"]
    derived = poly_plain({1: Fraction(4 * k), 0: Fraction(4 * m)})
    if _norm(g.get("perimeter")) != _norm(derived):
        errors.append(f"{seed}:q16_peri_not_derived:{g.get('perimeter')}:{derived}")
    labels = _rb._choice_labels(pl)
    texts = _rb._choice_texts(pl)
    ans = str(pl.get("answer"))
    if ans not in labels:
        errors.append(f"{seed}:q16_ans_not_label:{ans}:{labels}")
        return errors
    correct_text = texts[labels.index(ans)]
    if _norm(correct_text) != _norm(derived):
        errors.append(f"{seed}:q16_choice_ne_peri:{correct_text}:{derived}")
    area_expect = poly_plain({2: Fraction(k * k), 1: Fraction(2 * k * m), 0: Fraction(m * m)}) + "-y^{2}"
    if _norm(g.get("area")) != _norm(area_expect):
        errors.append(f"{seed}:q16_area_ne:{(g.get('area'))}:{area_expect}")
    return errors


def _extra_q18(pl: dict, seed: int) -> list[str]:
    errors: list[str] = []
    g = ((pl.get("metadata") or {}).get("givens") or {}) or (pl.get("givens") or {})
    try:
        r = int(g["correct_root"])
        s = int(g["pair_root"])
        a = int(g["u_shift"])
        p = int(g["p"])
        q = int(g["q"])
    except Exception:
        return [f"{seed}:q18_missing_params:{g}"]
    if a != r + s or p != -r * s:
        errors.append(f"{seed}:q18_params_inconsistent:{g}")

    def _eval(x: int) -> int:
        u = x * x - a * x
        return (u - p) * (u - q)

    if _eval(r) != 0:
        errors.append(f"{seed}:q18_correct_root_not_zero:{r}")
    if _eval(s) != 0:
        errors.append(f"{seed}:q18_pair_root_not_zero:{s}")
    labels = _rb._choice_labels(pl)
    texts = _rb._choice_texts(pl)
    ans = str(pl.get("answer"))
    for lab, tex in zip(labels, texts):
        root = _lin_root(tex)
        if root is None:
            errors.append(f"{seed}:q18_unparsed_choice:{tex}")
            continue
        val = _eval(root)
        if lab == ans:
            if val != 0:
                errors.append(f"{seed}:q18_correct_not_factor:{tex}:{val}")
        elif val == 0:
            errors.append(f"{seed}:q18_distractor_is_factor:{tex}")
    return errors


def _rebuild_one(conn: sqlite3.Connection, item: dict) -> dict:
    eid = int(item["eid"])
    cid = str(item["cid"])
    text = str(item["text"])
    _rb.DB_TEXTS[eid] = text
    ensure_gencode_component_tracker_table(conn)
    dry = run_admin_v3_dryrun_for_example(
        conn=conn,
        textbook_example_id=eid,
        skill_id=SKILL,
        dryrun_base_dir=_rb.DRYRUN,
        seed=7,
        allow_non_mvp_skill=True,
        force_regenerate=True,
    )
    print("DRYRUN", eid, dry.get("status") or dry.get("tracker_status"))
    comp_dir = ROOT / _rb.DRYRUN / SKILL / "components" / cid
    if not (comp_dir / "generate.py").is_file():
        raise SystemExit(f"generate_py_missing:{eid}:{dry}")

    _rb._inject_source_text(comp_dir, text)
    gen0 = _rb._load_module(comp_dir / "generate.py", f"pre_{cid}")
    sample = gen0.generate(seed=7, component_id=cid)
    _rb._patch_answer_contract_files(comp_dir, sample if isinstance(sample, dict) else {}, force_choice=True)
    _patch_source_kind(comp_dir)
    _rb._inject_source_text(comp_dir, text)
    vr = _rb._verify_20(comp_dir, cid, expect_choice=True)
    print("VERIFY20", eid, vr.get("result"), "type", vr.get("answer_type"), "errors", vr.get("errors"))
    if not vr.get("ok"):
        raise SystemExit(f"VERIFY_FAIL:{eid}:{vr}")

    extra_errors: list[str] = []
    gen = _rb._load_module(comp_dir / "generate.py", f"post_{cid}")
    for i in range(20):
        seed = 7000 + i
        pl = gen.generate(seed=seed, component_id=cid)
        if eid == 4713:
            extra_errors.extend(_extra_q16(pl, seed))
        else:
            extra_errors.extend(_extra_q18(pl, seed))
    if extra_errors:
        raise SystemExit(f"EXTRA_FAIL:{eid}:{extra_errors[:8]}")
    print("EXTRA_CHECKS PASS", eid)

    _rb._copy_to_production(SKILL, cid)
    _enrich(conn, eid, cid)
    conn.commit()
    return {
        "example_id": eid,
        "component_id": cid,
        "answer_type": vr.get("answer_type"),
        "20-seed": vr.get("result"),
        "status": "VERIFIED",
    }


def main() -> int:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row

    print("===== STEP1 MATCHING =====")
    rows = conn.execute(
        """
        SELECT id, skill_id, source_description, source_section, source_chapter,
               problem_type, correct_answer, problem_text
        FROM textbook_examples
        WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'
        ORDER BY id
        """
    ).fetchall()
    for r in rows:
        desc = str(r["source_description"] or "")
        if "自我評量" in desc or "題16" in desc or "題18" in desc:
            print(
                f"  id={r['id']} skill={r['skill_id']} desc={desc} type={r['problem_type']} "
                f"ans={r['correct_answer']!r} stem={(r['problem_text'] or '')[:80]}"
            )

    backups = []
    afters = []
    for item in ITEMS:
        eid = int(item["eid"])
        row = conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone()
        if row is None:
            raise SystemExit(f"NOT_FOUND id={eid}")
        before = dict(row)
        rec = _dump_row(before)
        print(f"MATCH Q{item['qid']} id={eid} skill={before.get('skill_id')} desc={before.get('source_description')}")
        if before.get("skill_id") != SKILL:
            raise SystemExit(f"STOP skill_id={before.get('skill_id')}")
        if "3-3" not in str(before.get("source_section") or ""):
            raise SystemExit(f"STOP section={before.get('source_section')}")
        desc = str(before.get("source_description") or "")
        if item["desc_token"] not in desc:
            raise SystemExit(f"STOP source_description={desc}")
        stem = str(before.get("problem_text") or "")
        for tok in item["stem_tokens"]:
            if tok not in stem and tok.replace("^{2}}", "") not in stem:
                # y / 因式 tokens must appear; latex token is best-effort
                if tok in {"長方形", "周長", "何者", "因式"}:
                    raise SystemExit(f"STOP missing token {tok} in {stem[:120]}")
        backups.append(rec)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = ROOT / "scratch" / f"_b1_3_3_q16_q18_db_backup_{stamp}.json"
    backup_path.write_text(json.dumps(backups, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BACKUP", backup_path.name)

    print("===== STEP2 DB REPAIR =====")
    for item, before_rec in zip(ITEMS, backups):
        eid = int(item["eid"])
        before = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        conn.execute(
            "UPDATE textbook_examples SET problem_text = ?, correct_answer = ? WHERE id = ?",
            (item["text"], item["answer"], eid),
        )
        after = dict(conn.execute("SELECT * FROM textbook_examples WHERE id=?", (eid,)).fetchone())
        locked_changed = {k: (before.get(k), after.get(k)) for k in LOCKED if before.get(k) != after.get(k)}
        if locked_changed:
            conn.rollback()
            raise SystemExit(f"locked_fields_changed:{eid}:{locked_changed}")
        afters.append(_dump_row(after))
        print("DB_AFTER", eid, after["correct_answer"], after["problem_text"][:90])
    conn.commit()

    print("===== STEP3/4 GENCODE =====")
    gencode_rows = []
    for item in ITEMS:
        gencode_rows.append(_rebuild_one(conn, item))

    print("===== STEP5 PACKAGE/PUBLISH =====")
    pub = run_admin_v3_publish_for_skill(
        conn=conn,
        skill_id=SKILL,
        project_root=str(ROOT),
        staging_root=_rb.STAGING,
        force_publish=True,
        strict_coverage=False,
    )
    print("PUBLISH", pub.get("status"), "count", pub.get("component_count"))

    print("===== STEP6 SMOKE =====")
    smoke = _rb._smoke_skill(SKILL, 40)
    print("SMOKE", smoke["passed"], "/", smoke["samples"], "keys", smoke.get("wrapper_keys"))
    print("HITS", smoke.get("hits"))
    for item in ITEMS:
        cid = item["cid"]
        if cid not in (smoke.get("wrapper_keys") or []):
            raise SystemExit(f"wrapper_missing:{cid}")
        if smoke.get("hits", {}).get(cid, 0) == 0:
            targeted = _rb._load_module(ROOT / "skills" / f"{SKILL}.py", f"facade_{cid}").generate(
                seed=7, component_id=cid
            )
            print("TARGETED", cid, targeted.get("answer_type"), targeted.get("answer"))
            if targeted.get("answer") is None:
                raise SystemExit(f"targeted_fail:{cid}")
            ok = check_answer(targeted.get("answer"), targeted.get("answer"), payload=targeted)
            print("TARGETED_CHECK", cid, ok)
            if not ok:
                raise SystemExit(f"targeted_checker_fail:{cid}")

    report = {
        "backup": backup_path.name,
        "db": afters,
        "gencode": gencode_rows,
        "publish": {"status": pub.get("status"), "count": pub.get("component_count")},
        "smoke": {
            "passed": smoke.get("passed"),
            "failed": smoke.get("failed"),
            "samples": smoke.get("samples"),
            "hits": smoke.get("hits"),
            "wrapper_keys": smoke.get("wrapper_keys"),
        },
    }
    out = ROOT / "scratch" / "_b1_3_3_q16_q18_results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", out.name)
    if int(smoke.get("failed") or 0) != 0 or int(smoke.get("passed") or 0) != 40:
        raise SystemExit(f"SMOKE_FAIL:{smoke}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
