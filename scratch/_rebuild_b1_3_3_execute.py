# -*- coding: utf-8 -*-
"""B1 3-3 FULL rebuild: per-example Phase2 → 20-seed → package → publish → smoke.

Does not modify textbook_examples.skill_id / classification.
Does not commit/push.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sqlite3
import sys
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.gencode.runtime_skill_wrapper import check_answer
from core.gencode.schema.gencode_component_tracker_inspection import (
    ensure_gencode_component_tracker_table,
)
from core.gencode.services.admin_gencode_action_service import (
    run_admin_v3_dryrun_for_example,
    run_admin_v3_publish_for_skill,
)
from core.gencode.services.component_tracker_service import (
    derive_component_id,
    save_tracker_record,
    update_status,
)

FEAS = json.loads((ROOT / "scratch/_b1_3_3_source_feasibility.json").read_text(encoding="utf-8"))
SKIP_ROWS = [r for r in FEAS["rows"] if r["rebuild_decision"] == "EXCLUDE"]
INCLUDE_ROWS = [r for r in FEAS["rows"] if r["rebuild_decision"] == "INCLUDE"]
_db_tmp = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
DB_TEXTS = {
    int(r[0]): str(r[1] or "")
    for r in _db_tmp.execute(
        "SELECT id, problem_text FROM textbook_examples WHERE source_volume LIKE '%B1%' AND source_section LIKE '3-3%'"
    ).fetchall()
}
_TECH = re.compile(r"_(?:[123]|duplicate|copy)\b")
_db_tmp.close()

DRYRUN = "reports/gencode_v3_dryrun"
STAGING = str((ROOT / "reports" / "gencode_v3_publish_staging").resolve())


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _choice_texts(payload: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for item in payload.get("choices") or []:
        if isinstance(item, dict):
            texts.append(str(item.get("text") or item.get("value") or "").strip())
        else:
            texts.append(str(item).strip())
    return texts


def _choice_labels(payload: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for item in payload.get("choices") or []:
        if isinstance(item, dict):
            labels.append(str(item.get("label") or item.get("key") or "").strip())
        else:
            labels.append("")
    return labels


def _source_is_choice(eid: int) -> bool:
    text = DB_TEXTS.get(eid, "").replace("（", "(").replace("）", ")")
    return all(f"({lab})" in text for lab in "ABCD")


def _inject_source_text(comp_dir: Path, problem_text: str) -> None:
    gen_path = comp_dir / "generate.py"
    gen = gen_path.read_text(encoding="utf-8")
    literal = repr(problem_text)
    new_line = f"SOURCE_PROBLEM_TEXT = {literal}"
    if "SOURCE_PROBLEM_TEXT =" not in gen:
        needle = "DEFAULT_COMPONENT_ID = "
        idx = gen.find(needle)
        if idx >= 0:
            end = gen.find("\n", idx)
            insert_at = end + 1
            gen = gen[:insert_at] + f"\n{new_line}\n" + gen[insert_at:]
        else:
            gen = new_line + "\n" + gen
    else:
        lines = gen.splitlines(keepends=True)
        replaced = False
        for i, line in enumerate(lines):
            if line.startswith("SOURCE_PROBLEM_TEXT = "):
                nl = "\n" if line.endswith("\n") else ""
                lines[i] = new_line + nl
                replaced = True
                break
        gen = "".join(lines) if replaced else new_line + "\n" + gen
    inject = """
    constraints["source_problem_text"] = SOURCE_PROBLEM_TEXT
    constraints["source_question_text"] = SOURCE_PROBLEM_TEXT
    constraints["presentation_mode"] = PRESENTATION_MODE
"""
    if 'constraints["source_problem_text"]' not in gen:
        gen = gen.replace(
            '    constraints["skill_id"] = ',
            inject + '    constraints["skill_id"] = ',
            1,
        )
    gen_path.write_text(gen, encoding="utf-8")


def _patch_answer_contract_files(comp_dir: Path, sample: dict[str, Any], *, force_choice: bool) -> str:
    ans = sample.get("answer")
    choices = sample.get("choices") or sample.get("options") or []
    runtime_at = str(sample.get("answer_type") or "").strip()
    ac = sample.get("answer_contract") if isinstance(sample.get("answer_contract"), dict) else {}

    if force_choice or (isinstance(choices, list) and choices and runtime_at in {"choice", "single_choice"}):
        target_type = "single_choice"
        checker = "choice_label_checker"
        equiv = "choice_label"
        mode = "single_choice"
        topology = "choice"
    elif isinstance(ans, dict):
        target_type = "multi_part"
        checker = "multi_part_answer_checker"
        equiv = "multi_part_answer"
        mode = "short_answer"
        topology = "multi_part"
        if not isinstance(ac.get("parts"), list) or not ac.get("parts"):
            parts = []
            for k, v in sorted(ans.items(), key=lambda kv: str(kv[0])):
                part_checker = (
                    "integer_checker"
                    if re.fullmatch(r"-?\d+", str(v).strip())
                    else "expression_checker"
                )
                parts.append(
                    {
                        "key": str(k),
                        "label": str(k),
                        "checker": part_checker,
                        "checker_key": part_checker,
                        "equivalence_type": "numeric_exact" if part_checker == "integer_checker" else "algebraic_equivalent",
                        "expected_answer": v,
                    }
                )
            ac = {
                "answer_type": "multi_part",
                "checker": checker,
                "checker_key": checker,
                "equivalence_type": equiv,
                "parts": parts,
            }
    else:
        target_type = "expression"
        checker = "expression_checker"
        equiv = "algebraic_equivalent"
        mode = "short_answer"
        topology = "expression"

    gen_path = comp_dir / "generate.py"
    meta_path = comp_dir / "metadata.py"
    gen = gen_path.read_text(encoding="utf-8")
    meta = meta_path.read_text(encoding="utf-8")
    gen = re.sub(r'^ANSWER_TYPE\s*=\s*".*?"', f'ANSWER_TYPE = "{target_type}"', gen, count=1, flags=re.M)
    gen = re.sub(r'^PRESENTATION_MODE\s*=\s*".*?"', f'PRESENTATION_MODE = "{mode}"', gen, count=1, flags=re.M)
    if topology == "choice" and "3-3 force single_choice" not in gen:
        inject = '''
    # 3-3 force single_choice contract
    payload["presentation_mode"] = "single_choice"
    payload["answer_type"] = "single_choice"
    payload["interaction_type"] = "single_choice"
    payload["checker"] = "choice_label_checker"
    payload["checker_key"] = "choice_label_checker"
    _ac = dict(payload.get("answer_contract") or {})
    _ac.update({
        "presentation_mode": "single_choice",
        "answer_type": "single_choice",
        "checker": "choice_label_checker",
        "checker_key": "choice_label_checker",
        "answer_equivalence": "choice_label",
        "equivalence": "choice_label",
        "equivalence_type": "choice_label",
    })
    payload["answer_contract"] = _ac
'''
        gen = gen.replace(
            '    if component_id:\n        payload["component_id"] = component_id\n    payload["seed"] = seed\n    return payload',
            inject
            + '    if component_id:\n        payload["component_id"] = component_id\n    payload["seed"] = seed\n    return payload',
        )
    if topology == "multi_part" and "v1.12 topology alignment" not in gen:
        inject = '''
    # v1.12 topology alignment: ensure multi_part answer_contract.parts
    if isinstance(payload.get("answer"), dict):
        _ans = payload["answer"]
        _parts = []
        for _k, _v in sorted(_ans.items(), key=lambda kv: str(kv[0])):
            _chk = "integer_checker" if str(_v).strip().lstrip("+-").isdigit() else "expression_checker"
            _parts.append({
                "key": str(_k),
                "label": str(_k),
                "checker": _chk,
                "checker_key": _chk,
                "equivalence_type": "numeric_exact" if _chk == "integer_checker" else "algebraic_equivalent",
                "expected_answer": _v,
            })
        _ac = dict(payload.get("answer_contract") or {})
        _ac.update({
            "answer_type": "multi_part",
            "checker": "multi_part_answer_checker",
            "checker_key": "multi_part_answer_checker",
            "equivalence_type": "multi_part_answer",
            "parts": _parts,
        })
        payload["answer_type"] = "multi_part"
        payload["answer_contract"] = _ac
        payload["checker"] = "multi_part_answer_checker"
        payload["checker_key"] = "multi_part_answer_checker"
'''
        gen = gen.replace(
            '    if component_id:\n        payload["component_id"] = component_id\n    payload["seed"] = seed\n    return payload',
            inject
            + '    if component_id:\n        payload["component_id"] = component_id\n    payload["seed"] = seed\n    return payload',
        )

    meta = re.sub(r'^ANSWER_TYPE:\s*Final\[str\]\s*=\s*".*?"', f'ANSWER_TYPE: Final[str] = "{target_type}"', meta, count=1, flags=re.M)
    meta = re.sub(r'^ANSWER_VALUE_TYPE:\s*Final\[str\]\s*=\s*".*?"', f'ANSWER_VALUE_TYPE: Final[str] = "{target_type}"', meta, count=1, flags=re.M)
    meta = re.sub(r'^PRESENTATION_MODE:\s*Final\[str\]\s*=\s*".*?"', f'PRESENTATION_MODE: Final[str] = "{mode}"', meta, count=1, flags=re.M)
    meta = re.sub(r'"checker_key":\s*"[^"]*"', f'"checker_key": "{checker}"', meta, count=1)
    meta = re.sub(r'"equivalence_type":\s*"[^"]*"', f'"equivalence_type": "{equiv}"', meta, count=1)
    meta = re.sub(r'"answer_type":\s*"[^"]*"', f'"answer_type": "{target_type}"', meta)
    meta = re.sub(r'^GENERATOR_READINESS:\s*Final\[str\]\s*=\s*".*?"', 'GENERATOR_READINESS: Final[str] = "verified"', meta, count=1, flags=re.M)
    gen_path.write_text(gen, encoding="utf-8")
    meta_path.write_text(meta, encoding="utf-8")
    return topology


def _verify_20(comp_dir: Path, component_id: str, *, expect_choice: bool) -> dict[str, Any]:
    gen_mod = _load_module(comp_dir / "generate.py", f"verify_{component_id}_gen")
    passed = 0
    errors: list[str] = []
    last_type = ""
    for i in range(20):
        seed = 7000 + i
        try:
            p1 = gen_mod.generate(seed=seed, component_id=component_id)
            p2 = gen_mod.generate(seed=seed, component_id=component_id)
            if not isinstance(p1, dict):
                errors.append(f"{seed}:generate_not_dict")
                continue
            q = str(p1.get("question_text") or p1.get("question") or "").strip()
            if not q or "placeholder" in q.lower():
                errors.append(f"{seed}:empty_or_placeholder")
                continue
            if p1.get("answer") is None:
                errors.append(f"{seed}:missing_answer")
                continue
            if p1.get("answer") != p2.get("answer") or str(p1.get("question_text")) != str(p2.get("question_text")):
                errors.append(f"{seed}:not_reproducible")
                continue
            last_type = str(p1.get("answer_type") or "")
            if expect_choice and last_type != "single_choice":
                errors.append(f"{seed}:answer_type={last_type}")
                continue
            if not check_answer(p1.get("answer"), p1.get("answer"), payload=p1):
                errors.append(f"{seed}:checker_true_fail")
                continue
            texts_all = _choice_texts(p1)
            if any(_TECH.search(t) for t in texts_all):
                errors.append(f"{seed}:technical_suffix:{texts_all}")
                continue
            meta = p1.get("metadata") if isinstance(p1.get("metadata"), dict) else {}
            givens = meta.get("givens") if isinstance(meta.get("givens"), dict) else {}
            if not givens and isinstance(p1.get("givens"), dict):
                givens = p1.get("givens") or {}
            excluded = list(givens.get("excluded") or [])
            ans_s = str(p1.get("answer"))
            if not expect_choice:
                bad_ex = False
                for ex in excluded:
                    if ans_s in {str(ex), f"x={ex}", f"x = {ex}"}:
                        errors.append(f"{seed}:excluded_as_answer:{ex}")
                        bad_ex = True
                        break
                if bad_ex:
                    continue
            if component_id == "src_4680" and all(k in givens for k in ("a", "b", "c")):
                derived = int(givens["a"]) ** 2 + int(givens["b"]) ** 2 + int(givens["c"]) ** 2
                if int(givens.get("value") or 0) != derived:
                    errors.append(f"{seed}:4680_not_derived:{derived}:{givens}")
                    continue
                if int(givens["c"]) in {int(x) for x in excluded}:
                    errors.append(f"{seed}:4680_c_excluded")
                    continue
            ans = p1.get("answer")
            if isinstance(ans, dict):
                wrong: Any = {k: "___WRONG___" for k in ans}
            elif isinstance(ans, (int, float)):
                wrong = ans + 999
            else:
                wrong = "___WRONG_ANSWER___"
            if expect_choice:
                labels = _choice_labels(p1)
                texts = _choice_texts(p1)
                choices = p1.get("choices") or []
                if not isinstance(choices, list) or len(choices) != 4:
                    errors.append(f"{seed}:choices_n={len(choices) if isinstance(choices, list) else None}")
                    continue
                if len(set(texts)) != 4:
                    errors.append(f"{seed}:duplicate_choices:{texts}")
                    continue
                if str(ans) not in labels:
                    errors.append(f"{seed}:answer_not_in_labels:{ans}:{labels}")
                    continue
                if labels.count(str(ans)) != 1:
                    errors.append(f"{seed}:label_not_unique")
                    continue
                wrong_ok = True
                for lab in labels:
                    if lab == str(ans):
                        continue
                    if check_answer(lab, ans, payload=p1):
                        wrong_ok = False
                        errors.append(f"{seed}:wrong_accepted={lab}")
                        break
                if not wrong_ok:
                    continue
            else:
                if check_answer(wrong, ans, payload=p1):
                    errors.append(f"{seed}:checker_accepts_wrong")
                    continue
            passed += 1
        except Exception as exc:
            errors.append(f"{seed}:exc:{exc}")
    return {
        "ok": passed == 20,
        "passed": passed,
        "failed": 20 - passed,
        "answer_type": last_type,
        "errors": errors[:12],
        "n": 20,
        "result": f"{passed}/20",
    }


def _copy_to_production(skill_id: str, component_id: str) -> None:
    src = ROOT / DRYRUN / skill_id / "components" / component_id
    dst = ROOT / "agent_skills_v3" / skill_id / "components" / component_id
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _smoke_skill(skill: str, n: int = 40) -> dict[str, Any]:
    facade = ROOT / "skills" / f"{skill}.py"
    if not facade.is_file():
        return {"skill_id": skill, "samples": 0, "passed": 0, "failed": n, "error": "no_facade", "hits": {}}
    mod = _load_module(facade, f"smoke_{skill}")
    keys = list(getattr(mod, "GENERATOR_KEYS", []) or [])
    passed = 0
    failed = 0
    errors: list[str] = []
    hits: Counter[str] = Counter()
    for i in range(n):
        try:
            pl = mod.generate(seed=2000 + i)
            cid = str(pl.get("component_id") or pl.get("generator_key") or "")
            hits[cid or "unknown"] += 1
            q = str(pl.get("question_text") or pl.get("question") or "")
            if not q or pl.get("answer") is None:
                failed += 1
                errors.append(f"seed{2000+i}:empty")
                continue
            if pl.get("answer_type") == "single_choice":
                ch = pl.get("choices") or []
                if not isinstance(ch, list) or len(ch) != 4:
                    failed += 1
                    errors.append(f"seed{2000+i}:choices")
                    continue
                texts = [
                    str(item.get("text") if isinstance(item, dict) else item)
                    for item in ch
                ]
                if any(_TECH.search(t) for t in texts) or len(set(t.strip() for t in texts)) != 4:
                    failed += 1
                    errors.append(f"seed{2000+i}:dup_or_suffix")
                    continue
            if not check_answer(pl.get("answer"), pl.get("answer"), payload=pl):
                failed += 1
                errors.append(f"seed{2000+i}:checker")
                continue
            passed += 1
        except Exception as exc:
            failed += 1
            errors.append(f"seed{2000+i}:{exc}")
    missing = [k for k in keys if hits.get(k, 0) == 0]
    targeted = []
    for key in missing:
        try:
            pl = mod.generate(seed=7, component_id=key)
            ok = bool(pl.get("question_text") or pl.get("question")) and pl.get("answer") is not None
            if ok:
                ok = bool(check_answer(pl.get("answer"), pl.get("answer"), payload=pl))
            targeted.append({"component_id": key, "ok": ok})
        except Exception as exc:
            targeted.append({"component_id": key, "ok": False, "error": str(exc)})
    return {
        "skill_id": skill,
        "samples": n,
        "passed": passed,
        "failed": failed,
        "hits": dict(hits),
        "missing_in_40": missing,
        "targeted": targeted,
        "wrapper_keys": keys,
        "errors": errors[:8],
    }


def main() -> int:
    conn = sqlite3.connect(str(ROOT / "instance" / "kumon_math.db"))
    conn.row_factory = sqlite3.Row
    ensure_gencode_component_tracker_table(conn)
    results: list[dict[str, Any]] = []

    for r in SKIP_ROWS:
        eid = int(r["example_id"])
        skill = r["skill_id"]
        cid = derive_component_id(eid)
        save_tracker_record(
            conn,
            textbook_example_id=eid,
            skill_id=skill,
            gencode_status="needs_human_review",
            induced_spec_payload={
                "component_id": cid,
                "feasibility_status": r["feasibility_status"],
                "reason": r["reason"],
                "rebuild_decision": "EXCLUDE",
                "original_attempted_status": "skipped_source_incomplete",
            },
            gencode_error_log=f"SKIPPED_SOURCE_INCOMPLETE: {r['reason']}",
        )
        results.append(
            {
                "example_id": eid,
                "skill_id": skill,
                "component_id": cid,
                "problem_type": r.get("problem_type"),
                "required_operation": r.get("required_operation"),
                "selected_operation": r.get("required_operation"),
                "answer_type": "",
                "20-seed": "0/20",
                "status": "SKIPPED_SOURCE_INCOMPLETE",
                "reason": r["reason"],
            }
        )
    conn.commit()

    for r in INCLUDE_ROWS:
        eid = int(r["example_id"])
        skill = r["skill_id"]
        cid = derive_component_id(eid)
        expect_choice = _source_is_choice(eid)
        item: dict[str, Any] = {
            "example_id": eid,
            "skill_id": skill,
            "component_id": cid,
            "problem_type": r.get("problem_type"),
            "required_operation": r.get("required_operation"),
            "selected_operation": r.get("required_operation"),
            "answer_type": "single_choice" if expect_choice else "",
            "20-seed": "0/20",
            "status": "FAILED",
            "reason": "",
        }
        try:
            dry = run_admin_v3_dryrun_for_example(
                conn=conn,
                textbook_example_id=eid,
                skill_id=skill,
                dryrun_base_dir=DRYRUN,
                seed=7,
                allow_non_mvp_skill=True,
                force_regenerate=True,
            )
            status = str(dry.get("status") or dry.get("tracker_status") or "")
            item["selected_operation"] = (
                (dry.get("domain_resolution") or {}).get("selected_operation")
                or dry.get("selected_operation")
                or r.get("required_operation")
            )
            comp_dir = ROOT / DRYRUN / skill / "components" / cid
            if status in {"needs_human_review", "failed"} and not (comp_dir / "generate.py").is_file():
                item["reason"] = (
                    f"dryrun_{status}:{dry.get('error_code') or dry.get('gencode_error_log') or dry.get('skip_reason') or dry.get('error') or status}"
                )
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid, "dryrun": {k: dry.get(k) for k in dry if k != "trace"}},
                    gencode_error_log=item["reason"][:2000],
                )
                conn.commit()
                results.append(item)
                print("FAIL", eid, item["reason"][:180])
                continue
            if not (comp_dir / "generate.py").is_file():
                item["reason"] = "generate_py_missing_after_dryrun"
                results.append(item)
                print("FAIL", eid, item["reason"])
                continue

            _inject_source_text(comp_dir, DB_TEXTS.get(eid, ""))
            gen0 = _load_module(comp_dir / "generate.py", f"prepatch_{cid}")
            sample = gen0.generate(seed=7, component_id=cid)
            topo = _patch_answer_contract_files(
                comp_dir,
                sample if isinstance(sample, dict) else {},
                force_choice=expect_choice,
            )
            # re-inject in case patch rewrote generate.py constants area only
            _inject_source_text(comp_dir, DB_TEXTS.get(eid, ""))
            vr = _verify_20(comp_dir, cid, expect_choice=expect_choice)
            item["20-seed"] = vr.get("result")
            item["answer_type"] = vr.get("answer_type") or ("single_choice" if expect_choice else topo)
            if not vr.get("ok"):
                item["reason"] = str(vr.get("errors") or vr)
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid, "topology": topo, "verify": vr},
                    gencode_error_log=str(item["reason"])[:2000],
                )
                conn.commit()
                results.append(item)
                print("FAIL", eid, vr.get("result"), (vr.get("errors") or [""])[0])
                continue

            _copy_to_production(skill, cid)
            save_tracker_record(
                conn,
                textbook_example_id=eid,
                skill_id=skill,
                gencode_status="verified",
                induced_spec_payload={
                    "component_id": cid,
                    "topology": topo,
                    "verify": vr,
                    "problem_type_id": r.get("problem_type_id"),
                    "generator_readiness": "verified",
                    "selected_operation": item["selected_operation"],
                },
                gencode_error_log=None,
            )
            try:
                update_status(conn, textbook_example_id=eid, skill_id=skill, gencode_status="verified")
            except Exception:
                pass
            conn.commit()
            item["status"] = "VERIFIED"
            item["reason"] = f"verified:{topo}"
            results.append(item)
            print("OK", eid, topo, vr.get("result"), item["answer_type"])
        except Exception as exc:
            item["reason"] = f"exception:{exc}"
            try:
                save_tracker_record(
                    conn,
                    textbook_example_id=eid,
                    skill_id=skill,
                    gencode_status="failed",
                    induced_spec_payload={"component_id": cid},
                    gencode_error_log=item["reason"][:2000],
                )
                conn.commit()
            except Exception:
                pass
            results.append(item)
            print("EXC", eid, exc)
            print(traceback.format_exc()[-800:])

    skills = sorted({str(r["skill_id"]) for r in FEAS["rows"]})
    # Keep only verified components in production packages for these 3-3 skills.
    for skill in skills:
        verified_cids = {
            x["component_id"]
            for x in results
            if x["skill_id"] == skill and x["status"] == "VERIFIED"
        }
        prod = ROOT / "agent_skills_v3" / skill / "components"
        if prod.is_dir():
            for d in list(prod.iterdir()):
                if d.is_dir() and d.name.startswith("src_") and d.name not in verified_cids:
                    shutil.rmtree(d)
                    print("PRUNE", skill, d.name)

    publish_results = []
    for skill in skills:
        verified = [x for x in results if x["skill_id"] == skill and x["status"] == "VERIFIED"]
        if not verified:
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": 0,
                    "package_status": "skipped_no_verified",
                    "publish_status": "skipped",
                    "wrapper_path": f"skills/{skill}.py",
                }
            )
            continue
        try:
            pub = run_admin_v3_publish_for_skill(
                conn=conn,
                skill_id=skill,
                project_root=str(ROOT),
                staging_root=STAGING,
                force_publish=True,
                strict_coverage=False,
            )
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": len(verified),
                    "wrapper_path": f"skills/{skill}.py",
                    "package_status": "compiled",
                    "publish_status": pub.get("status"),
                    "publish": {k: pub.get(k) for k in pub if k != "trace"},
                }
            )
            print("PUBLISH", skill, pub.get("status"), "n=", len(verified))
        except Exception as exc:
            publish_results.append(
                {
                    "skill_id": skill,
                    "verified_component_count": len(verified),
                    "wrapper_path": f"skills/{skill}.py",
                    "package_status": "failed",
                    "publish_status": f"error:{exc}",
                    "trace": traceback.format_exc()[-2000:],
                }
            )
            print("PUBLISH_FAIL", skill, exc)

    smoke = [_smoke_skill(skill, 40) for skill in skills]
    for row in smoke:
        print("SMOKE", row["skill_id"], row["passed"], "/", row["samples"], "hits", row.get("hits"))

    summary = {
        "finished_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(results),
        "verified": sum(1 for x in results if x["status"] == "VERIFIED"),
        "failed": sum(1 for x in results if x["status"] == "FAILED"),
        "skipped": sum(1 for x in results if x["status"] == "SKIPPED_SOURCE_INCOMPLETE"),
        "results": results,
        "publish": publish_results,
        "smoke": smoke,
    }
    out = ROOT / "scratch" / "_b1_3_3_rebuild_results.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("SUMMARY", {k: summary[k] for k in ("total", "verified", "failed", "skipped")})
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
