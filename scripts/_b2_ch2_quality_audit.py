# -*- coding: utf-8 -*-
"""B2 Chapter 2 quality seal audit (isolated DB copy; no production writes).

10-seed fast sample per usable problem_type; expand low-variation types to 30.
Also probes checker PASS/FAIL on one sample per type when check() exists.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "reports" / "b2_ch2_quality_seal"
OUT.mkdir(parents=True, exist_ok=True)
ISO_DIR = ROOT / "tmp" / f"b2_ch2_audit_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
_src_db = ROOT / "instance" / "kumon_math.db"
_src_con = __import__("sqlite3").connect(str(_src_db))
try:
    _src_con.execute(f"VACUUM INTO '{ISO_DB.as_posix()}'")
finally:
    _src_con.close()
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{ISO_DB.as_posix()}"

import config as app_config

app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]

from app import app as flask_app  # noqa: E402
from core.gencode.domain_matrix_adapter import _humanize_answer_contract_parts  # noqa: E402
from core.practice_type_mastery import (  # noqa: E402
    B2_TYPE_MASTERY_PILOT_SKILL_IDS,
    is_b1_type_mastery_skill,
    list_required_problem_types,
)
from models import SkillCurriculum, SkillInfo, TextbookExample, db  # noqa: E402

SAMPLE_FAST = 10
SAMPLE_EXPAND = 30
SEED_BASE = 20261123

FUZZY_LABELS = {
    "sum",
    "sin",
    "cos",
    "tan",
    "elevation",
    "小題1",
    "小題2",
    "part1",
    "part2",
}


def _chapter_is_2(chapter: str | None) -> bool:
    text = str(chapter or "").strip()
    if not text:
        return False
    if re.match(r"^第?\s*2\s*章", text):
        return True
    return "三角函數的應用" in text


def _te_ids_for_skill(skill_id: str) -> list[int]:
    rows = (
        TextbookExample.query.filter_by(skill_id=skill_id)
        .order_by(TextbookExample.id.asc())
        .all()
    )
    return [int(r.id) for r in rows]


def _inventory(skill_id: str) -> dict:
    try:
        from core.gencode.services.generator_problem_type_inventory import (
            inventory_skill_generator_problem_types,
        )

        return inventory_skill_generator_problem_types(skill_id) or {}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


_FACADES: dict[str, Any] = {}


def _load_facade(skill_id: str):
    if skill_id in _FACADES:
        return _FACADES[skill_id]
    import importlib

    mod = importlib.import_module(f"skills.{skill_id}")
    _FACADES[skill_id] = mod
    return mod


def _components_for_type(facade, problem_type_id: str | None) -> list[str]:
    specs = list(getattr(facade, "GENERATOR_SPECS", []) or [])
    if not problem_type_id:
        return [
            str(s.get("component_id"))
            for s in specs
            if isinstance(s, dict) and s.get("component_id")
        ]
    out = []
    for s in specs:
        if not isinstance(s, dict):
            continue
        if str(s.get("problem_type_id") or "") == str(problem_type_id) and s.get("component_id"):
            out.append(str(s["component_id"]))
    return out


def _generate_one(skill_id: str, problem_type_id: str | None, seed: int, sample_index: int = 0) -> dict:
    try:
        facade = _load_facade(skill_id)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"import_facade:{exc}"}
    if not callable(getattr(facade, "generate", None)):
        return {"ok": False, "error": "facade_missing_generate"}
    comps = _components_for_type(facade, problem_type_id)
    component_id = comps[sample_index % len(comps)] if comps else None
    try:
        payload = (
            facade.generate(level=1, seed=seed, component_id=component_id)
            if component_id
            else facade.generate(level=1, seed=seed)
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": f"{type(exc).__name__}:{exc}",
            "component_id": component_id,
        }
    return {"ok": True, "payload": payload, "component_id": component_id, "facade": facade}


def _extract_parts(payload: dict) -> list[dict]:
    contract = payload.get("answer_contract") or {}
    parts = contract.get("parts") if isinstance(contract, dict) else None
    if not isinstance(parts, list):
        ans = payload.get("answer") if isinstance(payload.get("answer"), dict) else {}
        ac = ans.get("answer_contract") if isinstance(ans, dict) else None
        if isinstance(ac, dict):
            parts = ac.get("parts")
    if not isinstance(parts, list):
        return []
    human = _humanize_answer_contract_parts(parts)
    out = []
    for p in human:
        out.append(
            {
                "key": p.get("key") or p.get("field_key"),
                "label": p.get("label"),
                "display_label": p.get("display_label"),
            }
        )
    return out


def _count_images(payload: dict) -> int:
    n = 0
    for key in ("image_url", "image", "figure_url"):
        if payload.get(key):
            n += 1
    notes = payload.get("notes") if isinstance(payload.get("notes"), dict) else {}
    assets = notes.get("image_assets") if isinstance(notes, dict) else None
    if isinstance(assets, list):
        n += len(assets)
    imgs = payload.get("images")
    if isinstance(imgs, list):
        n += len(imgs)
    visual = payload.get("visual_spec") or payload.get("figure")
    if visual:
        n += 1
    return n


def _payload_digest(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"stem": str(payload)[:200], "uid": None, "answer": None, "params": None}
    stem = (
        payload.get("question_text")
        or payload.get("question")
        or payload.get("problem_text")
        or payload.get("stem")
        or ""
    )
    if isinstance(stem, list):
        stem = "\n".join(str(x) for x in stem)
    uid = payload.get("question_uid") or payload.get("uid")
    ans = payload.get("correct_answer") or payload.get("canonical_answer") or payload.get("answer")
    if isinstance(ans, dict):
        ans_s = json.dumps(ans, ensure_ascii=False, sort_keys=True, default=str)
    else:
        ans_s = str(ans)
    params = payload.get("parameters") or payload.get("params") or payload.get("sample")
    if params is None:
        shallow = {
            k: payload.get(k)
            for k in ("known", "relations", "targets", "values", "figure", "source_id")
            if k in payload
        }
        params = shallow or None
    params_s = (
        json.dumps(params, ensure_ascii=False, sort_keys=True, default=str) if params is not None else ""
    )
    return {
        "stem": str(stem)[:400],
        "stem_hash": hashlib.sha1(str(stem).encode("utf-8")).hexdigest()[:12],
        "uid": uid,
        "answer": ans,
        "answer_hash": hashlib.sha1(ans_s.encode("utf-8")).hexdigest()[:12],
        "params_hash": hashlib.sha1(params_s.encode("utf-8")).hexdigest()[:12] if params_s else None,
        "parts": _extract_parts(payload),
        "image_count": _count_images(payload),
        "source_id": payload.get("source_id") or payload.get("textbook_example_id"),
    }


def _diversity_note(ok_n: int, unique_stems: int, unique_params: int) -> str:
    if ok_n == 0:
        return "NO_SAMPLES"
    if unique_stems <= 1 and unique_params <= 1:
        return "LOW_VARIATION_SUSPECT"
    if unique_stems < max(3, ok_n // 10):
        return "LIMITED_VARIATION"
    return "HAS_VARIATION"


def _label_issues(parts: list[dict]) -> list[dict]:
    issues = []
    for p in parts:
        lab = str(p.get("display_label") or p.get("label") or "").strip()
        key = str(p.get("key") or "").strip()
        if lab.lower() in FUZZY_LABELS or lab in FUZZY_LABELS:
            issues.append({"kind": "fuzzy_display_label", "key": key, "label": lab})
        if not lab and key:
            issues.append({"kind": "missing_display_label", "key": key, "label": lab})
    return issues


def _try_check(facade, payload: dict, student_answer: Any) -> dict:
    """Vocational V3 facade: check(user_answer, correct_answer, question_payload=...)."""
    check_fn = getattr(facade, "check", None) or getattr(facade, "check_answer", None)
    if not callable(check_fn):
        return {"ok": False, "skipped": True, "reason": "no_check"}
    correct_answer = (
        payload.get("correct_answer")
        if isinstance(payload, dict)
        else None
    )
    if correct_answer is None and isinstance(payload, dict):
        correct_answer = payload.get("canonical_answer") or payload.get("answer")
    try:
        result = check_fn(
            student_answer,
            correct_answer,
            question_payload=payload,
        )
    except TypeError:
        try:
            result = check_fn(student_answer, correct_answer, payload)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{type(exc).__name__}:{exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}:{exc}"}
    if isinstance(result, dict):
        correct = result.get("overall_correct")
        if correct is None:
            correct = result.get("is_correct")
        if correct is None:
            correct = result.get("correct")
        return {"ok": True, "correct": bool(correct), "raw_keys": list(result.keys())[:12]}
    if isinstance(result, bool):
        return {"ok": True, "correct": result}
    return {"ok": True, "correct": bool(result), "raw_type": type(result).__name__}


def _wrong_answer(ans: Any) -> Any:
    if isinstance(ans, (int, float)):
        return ans + 1 if ans != 0 else 2
    if isinstance(ans, str):
        return ans + "_x" if ans else "999"
    if isinstance(ans, dict):
        out = dict(ans)
        for k, v in list(out.items()):
            if k in {"answer_contract", "parts", "meta"}:
                continue
            if isinstance(v, (int, float)):
                out[k] = v + 1 if v != 0 else 2
                return out
            if isinstance(v, str):
                out[k] = v + "_x"
                return out
        out["__probe"] = "wrong"
        return out
    if isinstance(ans, list) and ans:
        wrong = list(ans)
        wrong[0] = _wrong_answer(wrong[0])
        return wrong
    return "999"


def _sample_types(skill_id: str, type_ids: list[str]) -> dict:
    per_type = {}
    for pt in type_ids:
        n = SAMPLE_FAST
        stems: Counter = Counter()
        params: Counter = Counter()
        answers: Counter = Counter()
        uids: set = set()
        errors = []
        label_samples = []
        label_bugs = []
        image_counts = []
        ok_n = 0
        first_payload = None
        first_facade = None
        for i in range(n):
            seed = SEED_BASE + i * 17 + (abs(hash(pt)) % 1000)
            res = _generate_one(skill_id, pt, seed, sample_index=i)
            if not res.get("ok"):
                errors.append(
                    {"seed": seed, "error": res.get("error"), "component_id": res.get("component_id")}
                )
                continue
            dig = _payload_digest(res["payload"])
            dig["component_id"] = res.get("component_id")
            ok_n += 1
            if first_payload is None:
                first_payload = res["payload"]
                first_facade = res.get("facade")
            stems[dig["stem_hash"]] += 1
            if dig["params_hash"]:
                params[dig["params_hash"]] += 1
            answers[dig["answer_hash"]] += 1
            if dig["uid"]:
                uids.add(str(dig["uid"]))
            if dig["parts"] and len(label_samples) < 3:
                label_samples.append(dig["parts"])
            label_bugs.extend(_label_issues(dig["parts"]))
            image_counts.append(dig["image_count"])

        note = _diversity_note(ok_n, len(stems), len(params) if params else 0)
        expanded = False
        if note in {"LOW_VARIATION_SUSPECT", "LIMITED_VARIATION"} and ok_n > 0:
            expanded = True
            for i in range(SAMPLE_FAST, SAMPLE_EXPAND):
                seed = SEED_BASE + i * 17 + (abs(hash(pt)) % 1000)
                res = _generate_one(skill_id, pt, seed, sample_index=i)
                if not res.get("ok"):
                    errors.append(
                        {
                            "seed": seed,
                            "error": res.get("error"),
                            "component_id": res.get("component_id"),
                        }
                    )
                    continue
                dig = _payload_digest(res["payload"])
                ok_n += 1
                stems[dig["stem_hash"]] += 1
                if dig["params_hash"]:
                    params[dig["params_hash"]] += 1
                answers[dig["answer_hash"]] += 1
                if dig["uid"]:
                    uids.add(str(dig["uid"]))
                label_bugs.extend(_label_issues(dig["parts"]))
                image_counts.append(dig["image_count"])
            note = _diversity_note(ok_n, len(stems), len(params) if params else 0)

        checker = {"status": "NOT_TESTED"}
        if first_payload is not None and first_facade is not None:
            dig0 = _payload_digest(first_payload)
            ans = dig0.get("answer")
            good = _try_check(first_facade, first_payload, ans)
            bad = _try_check(first_facade, first_payload, _wrong_answer(ans))
            if good.get("skipped") or bad.get("skipped"):
                checker = {"status": "SKIPPED_NO_CHECK"}
            elif not good.get("ok") or not bad.get("ok"):
                checker = {
                    "status": "ERROR",
                    "good": good,
                    "bad": bad,
                }
            elif good.get("correct") is True and bad.get("correct") is False:
                checker = {"status": "PASS"}
            else:
                checker = {
                    "status": "FAIL",
                    "good_correct": good.get("correct"),
                    "bad_correct": bad.get("correct"),
                }

        # dedupe label bugs
        seen = set()
        uniq_bugs = []
        for b in label_bugs:
            key = (b.get("kind"), b.get("key"), b.get("label"))
            if key in seen:
                continue
            seen.add(key)
            uniq_bugs.append(b)

        per_type[pt] = {
            "samples_ok": ok_n,
            "samples_requested": SAMPLE_EXPAND if expanded else SAMPLE_FAST,
            "expanded_to_30": expanded,
            "unique_stems": len(stems),
            "unique_params": len(params) if params else None,
            "unique_answers": len(answers),
            "unique_uids": len(uids),
            "errors": errors[:5],
            "error_count": len(errors),
            "label_samples": label_samples,
            "label_issues": uniq_bugs[:10],
            "image_count_max": max(image_counts) if image_counts else 0,
            "diversity_note": note,
            "checker": checker,
        }
    return per_type


def _status_for_skill(rec: dict) -> str:
    if not rec.get("is_active"):
        return "INACTIVE_OK" if rec.get("te_count", 0) == 0 or rec.get("y", 0) == 0 else "INACTIVE"
    if rec.get("y", 0) == 0 and rec.get("te_count", 0) == 0:
        return "BLOCKED"
    bugs = rec.get("bugs") or []
    if any(b.get("severity") == "P0" for b in bugs):
        return "BLOCKED"
    if any(b.get("severity") == "P1" for b in bugs):
        return "NEEDS_FIX"
    if rec.get("decision_needed"):
        return "NEEDS_DECISION"
    if rec.get("sample_status") == "NOT_TESTED":
        return "NOT_TESTED"
    if rec.get("sample_status") == "FAIL":
        return "BLOCKED"
    return "PASS"


def main() -> int:
    report: dict = {
        "stamp": STAMP,
        "scope": "B2 chapter 2 三角函數的應用",
        "git_head_expected": "8f0ae5b3",
        "db_copy": str(ISO_DB),
        "sample_fast": SAMPLE_FAST,
        "sample_expand": SAMPLE_EXPAND,
        "skills": [],
        "summary": {},
    }
    with flask_app.app_context():
        curr_rows = SkillCurriculum.query.filter(SkillCurriculum.skill_id.like("vh_數學B2_%")).all()
        info_map = {
            s.skill_id: s for s in SkillInfo.query.filter(SkillInfo.skill_id.like("vh_數學B2_%")).all()
        }
        selected = []
        for row in curr_rows:
            sid = str(row.skill_id)
            if _chapter_is_2(getattr(row, "chapter", None)) or sid.startswith(
                "vh_數學B2_SubSection_2_"
            ):
                selected.append(row)
        by_id = {str(r.skill_id): r for r in selected}

        for sid, row in sorted(
            by_id.items(), key=lambda kv: (str(getattr(kv[1], "display_order", 9999)), kv[0])
        ):
            info = info_map.get(sid)
            te_ids = _te_ids_for_skill(sid)
            try:
                types = list_required_problem_types(sid)
                inv_err = None
            except Exception as exc:  # noqa: BLE001
                types = []
                inv_err = str(exc)
            inv = _inventory(sid)
            mastery = is_b1_type_mastery_skill(sid)
            is_active = bool(getattr(info, "is_active", True)) if info else True
            display = (
                getattr(info, "skill_ch_name", None)
                or getattr(info, "skill_en_name", None)
                or sid
            )
            rec = {
                "skill_id": sid,
                "display_name": display,
                "chapter": getattr(row, "chapter", None),
                "section": getattr(row, "section", None),
                "display_order": getattr(row, "display_order", None),
                "is_active": is_active,
                "te_count": len(te_ids),
                "source_ids": te_ids[:40],
                "y": len(types),
                "problem_type_ids": types,
                "mastery_mode": "problem_type_mastery" if mastery else "consecutive_correct_legacy",
                "in_b2_pilot_allowlist": sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS,
                "inventory": {
                    "usable": inv.get("usable_problem_type_ids"),
                    "health": inv.get("health"),
                    "error": inv.get("error") or inv_err,
                },
                "bugs": [],
                "decision_needed": None,
                "sample_status": (
                    "SKIPPED_INACTIVE"
                    if not is_active
                    else ("SKIPPED_Y0" if not types else "PENDING")
                ),
                "generator_samples": {},
            }
            if is_active and types:
                try:
                    rec["generator_samples"] = _sample_types(sid, types)
                    fails = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if st.get("samples_ok", 0) == 0
                    ]
                    low = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if st.get("diversity_note") == "LOW_VARIATION_SUSPECT"
                    ]
                    checker_fail = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if (st.get("checker") or {}).get("status") == "FAIL"
                    ]
                    label_bad = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if st.get("label_issues")
                    ]
                    if fails:
                        rec["bugs"].append(
                            {"severity": "P0", "code": "GENERATOR_SAMPLE_FAIL", "detail": fails}
                        )
                        rec["sample_status"] = "FAIL"
                    else:
                        rec["sample_status"] = "SAMPLED"
                    if checker_fail:
                        rec["bugs"].append(
                            {
                                "severity": "P0",
                                "code": "CHECKER_MISJUDGE",
                                "detail": checker_fail,
                            }
                        )
                        rec["sample_status"] = "FAIL"
                    if low:
                        rec["bugs"].append(
                            {"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": low}
                        )
                    if label_bad:
                        rec["bugs"].append(
                            {
                                "severity": "P1",
                                "code": "FUZZY_OR_MISSING_LABEL",
                                "detail": {
                                    pt: rec["generator_samples"][pt].get("label_issues")
                                    for pt in label_bad
                                },
                            }
                        )
                except Exception as exc:  # noqa: BLE001
                    rec["sample_status"] = "NOT_TESTED"
                    rec["bugs"].append(
                        {
                            "severity": "P1",
                            "code": "SAMPLE_EXCEPTION",
                            "detail": f"{exc}\n{traceback.format_exc()[-500:]}",
                        }
                    )
            elif is_active and not types and len(te_ids) > 0:
                rec["bugs"].append(
                    {
                        "severity": "P1",
                        "code": "ACTIVE_WITH_TE_BUT_Y0",
                        "detail": "active skill has textbook examples but no usable runtime types",
                    }
                )
                rec["decision_needed"] = "是否維持連對語意或補 Generator 後納入掌握制"
            rec["status"] = _status_for_skill(rec)
            report["skills"].append(rec)
            print(
                f"[{rec['status']}] {sid} Y={rec['y']} TE={rec['te_count']} "
                f"sample={rec['sample_status']} bugs={len(rec['bugs'])}"
            )

    status_counts = Counter(s["status"] for s in report["skills"])
    p0 = [
        {"skill_id": s["skill_id"], "bugs": [b for b in s["bugs"] if b.get("severity") == "P0"]}
        for s in report["skills"]
        if any(b.get("severity") == "P0" for b in s["bugs"])
    ]
    p1 = [
        {"skill_id": s["skill_id"], "bugs": [b for b in s["bugs"] if b.get("severity") == "P1"]}
        for s in report["skills"]
        if any(b.get("severity") == "P1" for b in s["bugs"])
    ]
    p2 = [
        {"skill_id": s["skill_id"], "bugs": [b for b in s["bugs"] if b.get("severity") == "P2"]}
        for s in report["skills"]
        if any(b.get("severity") == "P2" for b in s["bugs"])
    ]
    report["summary"] = {
        "skill_count": len(report["skills"]),
        "active": sum(1 for s in report["skills"] if s["is_active"]),
        "inactive": sum(1 for s in report["skills"] if not s["is_active"]),
        "mastery_pilot": sum(1 for s in report["skills"] if s["in_b2_pilot_allowlist"]),
        "status_counts": dict(status_counts),
        "p0": p0,
        "p1": p1,
        "p2": p2,
        "gate": "BLOCKED" if p0 else ("NEEDS_FIX" if p1 else "PASS_ENGINEERING"),
    }

    json_path = OUT / "AUDIT_REPORT.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "AUDIT_REPORT.md").write_text(_to_md(report), encoding="utf-8")
    print(json.dumps({"out": str(OUT), "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


def _to_md(report: dict) -> str:
    lines = [
        "# B2 第 2 章品質稽核報告（工程）",
        "",
        f"- stamp: `{report['stamp']}`",
        f"- sample_fast/expand: {report['sample_fast']}/{report['sample_expand']}",
        f"- skills: {report['summary'].get('skill_count')}",
        f"- gate: **{report['summary'].get('gate')}**",
        f"- status_counts: `{json.dumps(report['summary'].get('status_counts'), ensure_ascii=False)}`",
        "",
        "## Skill 清單",
        "",
        "| Skill | 名稱 | active | TE | Y | 掌握制 | status |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for s in report["skills"]:
        lines.append(
            f"| `{s['skill_id']}` | {s['display_name']} | {s['is_active']} | "
            f"{s['te_count']} | {s['y']} | {s['mastery_mode']} | **{s['status']}** |"
        )
    lines.extend(["", "## P0 / P1 / P2", ""])
    lines.append("```json")
    lines.append(
        json.dumps(
            {
                "p0": report["summary"].get("p0"),
                "p1": report["summary"].get("p1"),
                "p2": report["summary"].get("p2"),
            },
            ensure_ascii=False,
            indent=2,
        )[:8000]
    )
    lines.append("```")
    lines.extend(["", "## 各 Skill 抽樣摘要", ""])
    for s in report["skills"]:
        lines.append(f"### `{s['skill_id']}` — {s['status']}")
        if s.get("bugs"):
            lines.append(f"- bugs: `{json.dumps(s['bugs'], ensure_ascii=False)}`")
        samples = s.get("generator_samples") or {}
        if samples:
            lines.append(
                "| problem_type | ok | stems | params | answers | note | checker | labels |"
            )
            lines.append("|---|---:|---:|---:|---:|---|---|---|")
            for pt, st in samples.items():
                lines.append(
                    f"| `{pt}` | {st.get('samples_ok')} | {st.get('unique_stems')} | "
                    f"{st.get('unique_params')} | {st.get('unique_answers')} | "
                    f"{st.get('diversity_note')} | {(st.get('checker') or {}).get('status')} | "
                    f"{len(st.get('label_issues') or [])} |"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
