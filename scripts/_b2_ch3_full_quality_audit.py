# -*- coding: utf-8 -*-
"""B2 Chapter 3 full Skill quality seal (isolated DB; no production writes).

Per usable problem_type: 10-seed sample, expand to 30 on low variation.
Checker: correct PASS, wrong FAIL, simple equivalent variant when applicable.
Also records TE/source fidelity hints and shared type-id overlaps.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "reports" / "b2_ch3_full_quality_audit"
OUT.mkdir(parents=True, exist_ok=True)
ISO_DIR = ROOT / "tmp" / f"b2_ch3_full_audit_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
_src = __import__("sqlite3").connect(str(ROOT / "instance" / "kumon_math.db"))
try:
    _src.execute(f"VACUUM INTO '{ISO_DB.as_posix()}'")
finally:
    _src.close()
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
from models import SkillCurriculum, SkillInfo, TextbookExample  # noqa: E402

SAMPLE_FAST = 10
SAMPLE_EXPAND = 30
SEED_BASE = 20261123
FUZZY = {"sum", "sin", "cos", "tan", "elevation", "小題1", "小題2", "part1", "part2"}


def _is_ch3(chapter: str | None, skill_id: str) -> bool:
    if str(skill_id).startswith("vh_數學B2_SubSection_3_"):
        return True
    text = str(chapter or "")
    return bool(re.match(r"^第?\s*3\s*章", text))


def _load(sid: str):
    import importlib

    return importlib.import_module(f"skills.{sid}")


def _comps(fac, pt: str) -> list[str]:
    out = []
    for s in getattr(fac, "GENERATOR_SPECS", []) or []:
        if isinstance(s, dict) and str(s.get("problem_type_id") or "") == pt and s.get("component_id"):
            out.append(str(s["component_id"]))
    return out


def _parts(payload: dict) -> list[dict]:
    contract = payload.get("answer_contract") or {}
    parts = contract.get("parts") if isinstance(contract, dict) else None
    if not isinstance(parts, list):
        return []
    return [
        {
            "key": p.get("key") or p.get("field_key"),
            "label": p.get("label"),
            "display_label": p.get("display_label"),
        }
        for p in _humanize_answer_contract_parts(parts)
    ]


def _stem(payload: dict) -> str:
    stem = (
        payload.get("question_text")
        or payload.get("question")
        or payload.get("problem_text")
        or payload.get("stem")
        or ""
    )
    if isinstance(stem, list):
        stem = "\n".join(str(x) for x in stem)
    return str(stem)


def _answer(payload: dict) -> Any:
    return payload.get("correct_answer") or payload.get("canonical_answer") or payload.get("answer")


def _hash(obj: Any) -> str:
    if isinstance(obj, (dict, list)):
        s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    else:
        s = str(obj)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def _image_info(payload: dict) -> dict:
    urls = []
    for key in ("image_url", "image", "figure_url"):
        if payload.get(key):
            urls.append(str(payload.get(key))[:120])
    notes = payload.get("notes") if isinstance(payload.get("notes"), dict) else {}
    assets = notes.get("image_assets") if isinstance(notes, dict) else None
    if isinstance(assets, list):
        urls.extend(str(a)[:120] for a in assets[:3])
    has_visual = bool(
        payload.get("visual_spec")
        or payload.get("diagram_spec")
        or payload.get("figure")
        or payload.get("image_base64")
        or urls
    )
    return {"has_visual": has_visual, "url_samples": urls[:3], "count": len(urls)}


def _label_issues(parts: list[dict]) -> list[dict]:
    issues = []
    for p in parts:
        lab = str(p.get("display_label") or p.get("label") or "").strip()
        key = str(p.get("key") or "").strip()
        if lab.lower() in FUZZY or lab in FUZZY:
            issues.append({"kind": "fuzzy_display_label", "key": key, "label": lab})
        if not lab and key:
            issues.append({"kind": "missing_display_label", "key": key, "label": lab})
    return issues


def _check(fac, payload: dict, user_answer: Any) -> dict:
    fn = getattr(fac, "check", None)
    if not callable(fn):
        return {"ok": False, "skipped": True}
    correct = _answer(payload)
    try:
        r = fn(user_answer, correct, question_payload=payload)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}:{exc}"}
    if isinstance(r, bool):
        return {"ok": True, "correct": r}
    if isinstance(r, dict):
        v = r.get("overall_correct")
        if v is None:
            v = r.get("is_correct")
        if v is None:
            v = r.get("correct")
        return {"ok": True, "correct": bool(v) if v is not None else None, "raw_keys": list(r.keys())[:8]}
    return {"ok": True, "correct": bool(r)}


def _wrong(ans: Any) -> Any:
    if isinstance(ans, dict):
        out = dict(ans)
        for k, v in list(out.items()):
            if k in {"answer_contract", "parts", "meta"}:
                continue
            if isinstance(v, (int, float)):
                out[k] = v + 1 if v != 0 else 2
                return out
            if isinstance(v, str):
                out[k] = (v + "_x") if v else "999"
                return out
            if isinstance(v, list) and v:
                nv = list(v)
                nv[0] = _wrong(nv[0])
                out[k] = nv
                return out
        out["__probe"] = "wrong"
        return out
    if isinstance(ans, (int, float)):
        return ans + 1 if ans != 0 else 2
    if isinstance(ans, str):
        return (ans + "_x") if ans else "999"
    if isinstance(ans, list) and ans:
        out = list(ans)
        out[0] = _wrong(out[0])
        return out
    return "999"


def _equiv_variants(ans: Any) -> list[Any]:
    """Cheap equivalent forms for common scalar/string answers; empty if unknown."""
    variants: list[Any] = []
    if isinstance(ans, dict) and len(ans) == 1:
        k, v = next(iter(ans.items()))
        if isinstance(v, str):
            s = v.strip()
            # whitespace
            variants.append({k: f" {s} "})
            # * vs implicit (limited)
            if "*sqrt" in s.replace(" ", ""):
                variants.append({k: s.replace("*", "")})
            if s.startswith("+"):
                variants.append({k: s[1:]})
        elif isinstance(v, (int, float)):
            variants.append({k: str(v)})
    elif isinstance(ans, str):
        variants.append(f" {ans} ")
        if "*sqrt" in ans.replace(" ", ""):
            variants.append(ans.replace("*", ""))
    elif isinstance(ans, (int, float)):
        variants.append(str(ans))
    return variants[:3]


def _diversity(ok_n: int, stems: int, params: int) -> str:
    if ok_n == 0:
        return "NO_SAMPLES"
    if stems <= 1 and params <= 1:
        return "LOW_VARIATION_SUSPECT"
    if stems < max(3, ok_n // 10):
        return "LIMITED_VARIATION"
    return "HAS_VARIATION"


def _sample_type(sid: str, fac, pt: str) -> dict:
    comps = _comps(fac, pt)
    stems: Counter = Counter()
    params: Counter = Counter()
    answers: Counter = Counter()
    uids: set[str] = set()
    te_ids: Counter = Counter()
    skill_mismatch = []
    errors = []
    label_bugs: list[dict] = []
    label_samples = []
    images = []
    ok_n = 0
    first_payload = None
    n = SAMPLE_FAST
    expanded = False

    def one(i: int) -> None:
        nonlocal ok_n, first_payload
        seed = SEED_BASE + i * 19 + (abs(hash(pt + sid)) % 900)
        cid = comps[i % len(comps)] if comps else None
        try:
            payload = (
                fac.generate(level=1, seed=seed, component_id=cid)
                if cid
                else fac.generate(level=1, seed=seed)
            )
        except Exception as exc:  # noqa: BLE001
            errors.append({"seed": seed, "error": f"{type(exc).__name__}:{exc}", "component_id": cid})
            return
        if not isinstance(payload, dict):
            errors.append({"seed": seed, "error": "non_dict_payload"})
            return
        ok_n += 1
        if first_payload is None:
            first_payload = payload
        stem = _stem(payload)
        stems[_hash(stem)] += 1
        # param fingerprint: prefer explicit params; else answer+source+component
        pobj = payload.get("parameters") or payload.get("params") or payload.get("sample")
        if pobj is None:
            pobj = {
                "answer": _answer(payload),
                "te": payload.get("textbook_example_id") or payload.get("source_id"),
                "component_id": payload.get("component_id") or cid,
            }
        params[_hash(pobj)] += 1
        answers[_hash(_answer(payload))] += 1
        uid = payload.get("question_uid") or payload.get("uid")
        if uid:
            uids.add(str(uid))
        te = payload.get("textbook_example_id") or payload.get("source_id")
        if te is not None:
            te_ids[str(te)] += 1
        p_skill = str(payload.get("skill_id") or "")
        if p_skill and p_skill != sid:
            skill_mismatch.append({"seed": seed, "payload_skill": p_skill})
        parts = _parts(payload)
        if parts and len(label_samples) < 2:
            label_samples.append(parts)
        label_bugs.extend(_label_issues(parts))
        images.append(_image_info(payload))

    for i in range(n):
        one(i)
    note = _diversity(ok_n, len(stems), len(params))
    if note in {"LOW_VARIATION_SUSPECT", "LIMITED_VARIATION"} and ok_n > 0:
        expanded = True
        for i in range(SAMPLE_FAST, SAMPLE_EXPAND):
            one(i)
        note = _diversity(ok_n, len(stems), len(params))

    checker = {"status": "NOT_TESTED"}
    if first_payload is not None:
        ans = _answer(first_payload)
        good = _check(fac, first_payload, ans)
        bad = _check(fac, first_payload, _wrong(ans))
        equiv_results = []
        for var in _equiv_variants(ans):
            er = _check(fac, first_payload, var)
            equiv_results.append({"variant": var, "result": er})
        if good.get("skipped") or bad.get("skipped"):
            checker = {"status": "SKIPPED_NO_CHECK"}
        elif not good.get("ok") or not bad.get("ok"):
            checker = {"status": "ERROR", "good": good, "bad": bad}
        elif good.get("correct") is True and bad.get("correct") is False:
            # equivalent: if any variant returns False, note as P2 contract gap (not auto P0)
            equiv_fail = [
                e
                for e in equiv_results
                if e["result"].get("ok") and e["result"].get("correct") is False
            ]
            checker = {
                "status": "PASS",
                "equiv_tested": len(equiv_results),
                "equiv_fail_count": len(equiv_fail),
                "equiv_fail_samples": equiv_fail[:2],
            }
        else:
            checker = {
                "status": "FAIL",
                "good_correct": good.get("correct"),
                "bad_correct": bad.get("correct"),
            }

    # dedupe labels
    seen = set()
    uniq_labels = []
    for b in label_bugs:
        key = (b.get("kind"), b.get("key"), b.get("label"))
        if key in seen:
            continue
        seen.add(key)
        uniq_labels.append(b)

    return {
        "samples_ok": ok_n,
        "samples_requested": SAMPLE_EXPAND if expanded else SAMPLE_FAST,
        "expanded_to_30": expanded,
        "unique_stems": len(stems),
        "unique_params": len(params),
        "unique_answers": len(answers),
        "unique_uids": len(uids),
        "error_count": len(errors),
        "errors": errors[:5],
        "diversity_note": note,
        "checker": checker,
        "label_issues": uniq_labels[:8],
        "label_samples": label_samples,
        "te_ids_seen": dict(te_ids.most_common(8)),
        "skill_mismatch": skill_mismatch[:5],
        "image_any": any(x.get("has_visual") for x in images),
        "image_count_max": max((x.get("count") or 0) for x in images) if images else 0,
        "component_ids": comps,
    }


def _status(rec: dict) -> str:
    if not rec.get("is_active"):
        return "INACTIVE_OK"
    bugs = rec.get("bugs") or []
    if any(b.get("severity") == "P0" for b in bugs):
        return "BLOCKED"
    if any(b.get("severity") == "P1" for b in bugs):
        return "NEEDS_FIX"
    if rec.get("sample_status") == "FAIL":
        return "BLOCKED"
    if rec.get("sample_status") == "NOT_TESTED":
        return "NOT_TESTED"
    return "PASS"


def main() -> int:
    report: dict[str, Any] = {
        "stamp": STAMP,
        "scope": "B2 chapter 3 向量 full quality seal",
        "git_head": "dc21df72",
        "db_copy": str(ISO_DB),
        "sample_fast": SAMPLE_FAST,
        "sample_expand": SAMPLE_EXPAND,
        "skills": [],
        "shared_types": {},
        "summary": {},
    }
    type_owners: dict[str, list[str]] = defaultdict(list)

    with flask_app.app_context():
        curr = SkillCurriculum.query.filter(SkillCurriculum.skill_id.like("vh_數學B2_%")).all()
        info_map = {
            s.skill_id: s for s in SkillInfo.query.filter(SkillInfo.skill_id.like("vh_數學B2_%")).all()
        }
        selected = {
            str(r.skill_id): r
            for r in curr
            if _is_ch3(getattr(r, "chapter", None), str(r.skill_id))
        }
        for sid, row in sorted(
            selected.items(),
            key=lambda kv: (
                str(getattr(kv[1], "section", "") or ""),
                kv[1].display_order or 0,
                kv[0],
            ),
        ):
            info = info_map.get(sid)
            te_rows = (
                TextbookExample.query.filter_by(skill_id=sid)
                .order_by(TextbookExample.id.asc())
                .all()
            )
            te_ids = [int(t.id) for t in te_rows]
            try:
                types = list_required_problem_types(sid)
            except Exception as exc:  # noqa: BLE001
                types = []
                inv_err = str(exc)
            else:
                inv_err = None
            for pt in types:
                type_owners[pt].append(sid)
            is_active = bool(getattr(info, "is_active", True)) if info else True
            name = (
                getattr(info, "skill_ch_name", None)
                or getattr(info, "skill_en_name", None)
                or sid
            )
            rec = {
                "skill_id": sid,
                "display_name": name,
                "chapter": getattr(row, "chapter", None),
                "section": getattr(row, "section", None),
                "display_order": getattr(row, "display_order", None),
                "is_active": is_active,
                "te_count": len(te_ids),
                "source_ids": te_ids[:40],
                "y": len(types),
                "problem_type_ids": types,
                "mastery_enabled": is_b1_type_mastery_skill(sid),
                "in_allowlist": sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS,
                "bugs": [],
                "sample_status": "SKIPPED_INACTIVE" if not is_active else ("SKIPPED_Y0" if not types else "PENDING"),
                "generator_samples": {},
                "inventory_error": inv_err,
            }
            if is_active and types:
                try:
                    fac = _load(sid)
                    for pt in types:
                        rec["generator_samples"][pt] = _sample_type(sid, fac, pt)
                    fails = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if st.get("samples_ok", 0) == 0
                    ]
                    checker_fail = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if (st.get("checker") or {}).get("status") == "FAIL"
                    ]
                    checker_err = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if (st.get("checker") or {}).get("status") == "ERROR"
                    ]
                    low = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if st.get("diversity_note") == "LOW_VARIATION_SUSPECT"
                    ]
                    labels = {
                        pt: st.get("label_issues")
                        for pt, st in rec["generator_samples"].items()
                        if st.get("label_issues")
                    }
                    mismatch = {
                        pt: st.get("skill_mismatch")
                        for pt, st in rec["generator_samples"].items()
                        if st.get("skill_mismatch")
                    }
                    if fails:
                        rec["bugs"].append({"severity": "P0", "code": "GENERATOR_SAMPLE_FAIL", "detail": fails})
                        rec["sample_status"] = "FAIL"
                    elif checker_fail or checker_err:
                        rec["bugs"].append(
                            {
                                "severity": "P0",
                                "code": "CHECKER_MISJUDGE",
                                "detail": {"fail": checker_fail, "error": checker_err},
                            }
                        )
                        rec["sample_status"] = "FAIL"
                    else:
                        rec["sample_status"] = "SAMPLED"
                    if labels:
                        rec["bugs"].append(
                            {"severity": "P1", "code": "FUZZY_OR_MISSING_LABEL", "detail": labels}
                        )
                    if mismatch:
                        rec["bugs"].append(
                            {"severity": "P1", "code": "PAYLOAD_SKILL_MISMATCH", "detail": mismatch}
                        )
                    if low:
                        rec["bugs"].append(
                            {"severity": "P2", "code": "LOW_PARAM_VARIATION", "detail": low}
                        )
                    # equiv contract gaps -> P2
                    equiv_gaps = [
                        pt
                        for pt, st in rec["generator_samples"].items()
                        if (st.get("checker") or {}).get("equiv_fail_count", 0) > 0
                    ]
                    if equiv_gaps:
                        rec["bugs"].append(
                            {
                                "severity": "P2",
                                "code": "EQUIV_VARIANT_NOT_ACCEPTED",
                                "detail": equiv_gaps,
                            }
                        )
                except Exception as exc:  # noqa: BLE001
                    rec["sample_status"] = "NOT_TESTED"
                    rec["bugs"].append(
                        {
                            "severity": "P1",
                            "code": "SAMPLE_EXCEPTION",
                            "detail": f"{exc}\n{traceback.format_exc()[-400:]}",
                        }
                    )
            elif is_active and not types:
                rec["bugs"].append(
                    {"severity": "P1", "code": "ACTIVE_Y0", "detail": "active but no usable types"}
                )
            rec["status"] = _status(rec)
            report["skills"].append(rec)
            print(
                f"[{rec['status']}] {sid} Y={rec['y']} TE={rec['te_count']} "
                f"sample={rec['sample_status']} bugs={len(rec['bugs'])}"
            )

    report["shared_types"] = {k: v for k, v in sorted(type_owners.items()) if len(v) > 1}
    status_counts = Counter(s["status"] for s in report["skills"])
    p0 = [s["skill_id"] for s in report["skills"] if any(b.get("severity") == "P0" for b in s["bugs"])]
    p1 = [s["skill_id"] for s in report["skills"] if any(b.get("severity") == "P1" for b in s["bugs"])]
    p2 = [s["skill_id"] for s in report["skills"] if any(b.get("severity") == "P2" for b in s["bugs"])]
    report["summary"] = {
        "skill_count": len(report["skills"]),
        "active": sum(1 for s in report["skills"] if s["is_active"]),
        "y_sum": sum(s["y"] for s in report["skills"]),
        "unique_problem_types": len(type_owners),
        "shared_type_count": len(report["shared_types"]),
        "status_counts": dict(status_counts),
        "p0_skills": p0,
        "p1_skills": p1,
        "p2_skills": p2,
        "gate": "BLOCKED" if p0 else ("NEEDS_FIX" if p1 else "PASS_ENGINEERING"),
        "ui_browser": "NOT_TESTED",
        "canvas_layout": "NOT_TESTED",
        "ai_tutor": "NOT_TESTED",
    }
    (OUT / "AUDIT_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "AUDIT_REPORT.md").write_text(_to_md(report), encoding="utf-8")
    print(json.dumps({"out": str(OUT), "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


def _to_md(report: dict) -> str:
    lines = [
        "# B2 第 3 章全 Skill 品質稽核報告",
        "",
        f"- stamp: `{report['stamp']}`",
        f"- gate: **{report['summary'].get('gate')}**",
        f"- skills: {report['summary'].get('skill_count')}；Y 合計（非去重）={report['summary'].get('y_sum')}；"
        f"全章去重 problem_type={report['summary'].get('unique_problem_types')}",
        f"- status: `{json.dumps(report['summary'].get('status_counts'), ensure_ascii=False)}`",
        f"- UI/Canvas/AI Tutor: NOT_TESTED",
        "",
        "## Skill 清單",
        "",
        "| Skill | 名稱 | TE | Y | 掌握 | status |",
        "|---|---|---:|---:|---|---|",
    ]
    for s in report["skills"]:
        lines.append(
            f"| `{s['skill_id']}` | {s['display_name']} | {s['te_count']} | {s['y']} | "
            f"{'X/Y' if s['mastery_enabled'] else 'legacy'} | **{s['status']}** |"
        )
    lines.extend(["", "## Shared problem_type_id", ""])
    lines.append("```json")
    lines.append(json.dumps(report.get("shared_types"), ensure_ascii=False, indent=2))
    lines.append("```")
    lines.extend(["", "## 抽樣摘要", ""])
    for s in report["skills"]:
        lines.append(f"### `{s['skill_id']}` — {s['status']}")
        if s.get("bugs"):
            lines.append(f"- bugs: `{json.dumps(s['bugs'], ensure_ascii=False)}`")
        samples = s.get("generator_samples") or {}
        if samples:
            lines.append(
                "| pt | ok | stems | params | answers | note | checker | labels | visual |"
            )
            lines.append("|---|---:|---:|---:|---:|---|---|---:|---|")
            for pt, st in samples.items():
                lines.append(
                    f"| `{pt}` | {st.get('samples_ok')} | {st.get('unique_stems')} | "
                    f"{st.get('unique_params')} | {st.get('unique_answers')} | "
                    f"{st.get('diversity_note')} | {(st.get('checker') or {}).get('status')} | "
                    f"{len(st.get('label_issues') or [])} | {st.get('image_any')} |"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
