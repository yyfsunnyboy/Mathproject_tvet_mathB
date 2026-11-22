# -*- coding: utf-8 -*-
"""B2 Chapter 1 full Skill quality audit (read-only on isolated DB copy).

Produces reports/b2_ch1_full_quality_audit/AUDIT_REPORT.json + .md
Does not write production DB or student mastery.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "reports" / "b2_ch1_full_quality_audit"
OUT.mkdir(parents=True, exist_ok=True)
ISO_DIR = ROOT / "tmp" / f"b2_ch1_audit_{STAMP}"
ISO_DIR.mkdir(parents=True, exist_ok=True)
ISO_DB = ISO_DIR / "kumon_math.db"
# Include WAL commits: plain shutil.copy2 of the main file can be stale.
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
from core.practice_type_mastery import (  # noqa: E402
    B2_TYPE_MASTERY_PILOT_SKILL_IDS,
    is_b1_type_mastery_skill,
    list_required_problem_types,
)
from core.gencode.domain_matrix_adapter import _humanize_answer_contract_parts  # noqa: E402
from models import SkillCurriculum, SkillInfo, TextbookExample, db  # noqa: E402

SAMPLE_N = 30
SEED_BASE = 20261122


def _chapter_is_1(chapter: str | None) -> bool:
    text = str(chapter or "").strip()
    if not text:
        return False
    if text in {"1", "01", "第1章", "第一章"}:
        return True
    if re.match(r"^第?\s*1\s*章", text):
        return True
    if re.match(r"^1[\.．、]", text):
        return True
    return "三角函數" in text and ("第1" in text or text.startswith("1"))


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
        return [str(s.get("component_id")) for s in specs if isinstance(s, dict) and s.get("component_id")]
    out = []
    for s in specs:
        if not isinstance(s, dict):
            continue
        if str(s.get("problem_type_id") or "") == str(problem_type_id) and s.get("component_id"):
            out.append(str(s["component_id"]))
    return out


def _generate_one(skill_id: str, problem_type_id: str | None, seed: int, sample_index: int = 0) -> dict:
    """Generate via published skills/*.py facade (dispatch_generate)."""
    try:
        facade = _load_facade(skill_id)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"import_facade:{exc}"}
    if not callable(getattr(facade, "generate", None)):
        return {"ok": False, "error": "facade_missing_generate"}
    comps = _components_for_type(facade, problem_type_id)
    component_id = comps[sample_index % len(comps)] if comps else None
    try:
        payload = facade.generate(level=1, seed=seed, component_id=component_id) if component_id else facade.generate(level=1, seed=seed)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}:{exc}", "component_id": component_id}
    return {"ok": True, "payload": payload, "component_id": component_id}


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
        # fall back: strip unstable ids from a shallow copy
        shallow = {
            k: payload.get(k)
            for k in ("known", "relations", "targets", "values", "figure", "source_id")
            if k in payload
        }
        params = shallow or None
    params_s = json.dumps(params, ensure_ascii=False, sort_keys=True, default=str) if params is not None else ""
    return {
        "stem": str(stem)[:400],
        "stem_hash": hashlib.sha1(str(stem).encode("utf-8")).hexdigest()[:12],
        "uid": uid,
        "answer_hash": hashlib.sha1(ans_s.encode("utf-8")).hexdigest()[:12],
        "params_hash": hashlib.sha1(params_s.encode("utf-8")).hexdigest()[:12] if params_s else None,
        "parts": _extract_parts(payload),
        "image_count": _count_images(payload),
        "source_id": payload.get("source_id") or payload.get("textbook_example_id"),
    }


def _extract_parts(payload: dict) -> list[dict]:
    contract = payload.get("answer_contract") or {}
    parts = contract.get("parts") if isinstance(contract, dict) else None
    if not isinstance(parts, list):
        # sometimes nested in answer
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
    return n


def _sample_types(skill_id: str, type_ids: list[str]) -> dict:
    per_type = {}
    for pt in type_ids:
        stems = Counter()
        params = Counter()
        answers = Counter()
        uids = set()
        errors = []
        label_samples = []
        image_counts = []
        ok_n = 0
        for i in range(SAMPLE_N):
            seed = SEED_BASE + i * 17 + (hash(pt) % 1000)
            res = _generate_one(skill_id, pt, seed, sample_index=i)
            if not res.get("ok"):
                errors.append({"seed": seed, "error": res.get("error"), "component_id": res.get("component_id")})
                continue
            dig = _payload_digest(res["payload"])
            dig["component_id"] = res.get("component_id")
            ok_n += 1
            stems[dig["stem_hash"]] += 1
            if dig["params_hash"]:
                params[dig["params_hash"]] += 1
            answers[dig["answer_hash"]] += 1
            if dig["uid"]:
                uids.add(str(dig["uid"]))
            if dig["parts"] and len(label_samples) < 3:
                label_samples.append(dig["parts"])
            image_counts.append(dig["image_count"])
        per_type[pt] = {
            "samples_ok": ok_n,
            "samples_requested": SAMPLE_N,
            "unique_stems": len(stems),
            "unique_params": len(params) if params else None,
            "unique_answers": len(answers),
            "unique_uids": len(uids),
            "errors": errors[:5],
            "error_count": len(errors),
            "label_samples": label_samples,
            "image_count_max": max(image_counts) if image_counts else 0,
            "diversity_note": _diversity_note(ok_n, len(stems), len(params) if params else 0),
        }
    return per_type


def _diversity_note(ok_n: int, unique_stems: int, unique_params: int) -> str:
    if ok_n == 0:
        return "NO_SAMPLES"
    if unique_stems <= 1 and unique_params <= 1:
        return "LOW_VARIATION_SUSPECT"
    if unique_stems < max(3, ok_n // 10):
        return "LIMITED_VARIATION"
    return "HAS_VARIATION"


def _check_11583_11584(skill_rows: list[dict]) -> dict:
    out = {}
    for te_id, expect_skill_substr in (
        (11583, "ArcLengthAndAreaOfSector"),
        (11584, "TrigonometricFunctionsOfAcuteAngles"),
    ):
        row = TextbookExample.query.get(te_id)
        if not row:
            out[str(te_id)] = {"status": "MISSING_TE"}
            continue
        out[str(te_id)] = {
            "skill_id": row.skill_id,
            "expect_contains": expect_skill_substr,
            "pass": expect_skill_substr in str(row.skill_id or ""),
            "has_image": bool(getattr(row, "image_path", None) or getattr(row, "notes", None)),
        }
    return out


def _probe_subsection_132_labels() -> dict:
    skill_id = "vh_數學B2_SubSection_1_3_2"
    types = list_required_problem_types(skill_id)
    samples = []
    issues = []
    for i in range(min(10, SAMPLE_N)):
        pt = types[0] if types else None
        res = _generate_one(skill_id, pt, SEED_BASE + i, sample_index=i)
        if not res.get("ok"):
            issues.append({"seed": SEED_BASE + i, "error": res.get("error")})
            continue
        dig = _payload_digest(res["payload"])
        samples.append({"stem": dig["stem"][:180], "parts": dig["parts"], "answer_hash": dig["answer_hash"]})
        for part in dig["parts"]:
            lab = str(part.get("display_label") or part.get("label") or "")
            key = str(part.get("key") or "")
            # Raw internal keys shown to students
            if lab in {"sin", "cos", "tan"}:
                issues.append({"kind": "raw_trig_key_label", "key": key, "label": lab})
            # Accept LaTeX or unicode classroom forms
            ok_labels = {
                r"$\sin\theta$",
                r"$\cos\theta$",
                r"$\tan\theta$",
                "sinθ",
                "cosθ",
                "tanθ",
                "sinθ",
            }
            if key in {"sin", "cos", "tan"} and lab not in ok_labels and "θ" not in lab and "theta" not in lab.lower() and "\\theta" not in lab:
                issues.append({"kind": "incomplete_trig_label", "key": key, "label": lab})
    # also unit-test humanize contract
    human = _humanize_answer_contract_parts(
        [
            {"key": "sin", "label": "sin"},
            {"key": "cos", "label": "cos"},
            {"key": "tan", "label": "tan"},
        ]
    )
    human_labels = [h.get("display_label") for h in human]
    human_ok = all("\\theta" in str(x) or "θ" in str(x) for x in human_labels)
    runtime_label_fail = any(
        i.get("kind") in {"raw_trig_key_label", "incomplete_trig_label"} for i in issues
    )
    return {
        "types": types,
        "humanize_raw_keys": human_labels,
        "humanize_ok": human_ok,
        "samples": samples[:5],
        "issues": issues[:20],
        "status": "FAIL" if (runtime_label_fail or not human_ok) else ("PASS" if samples else "NOT_TESTED"),
    }


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
        "scope": "B2 chapter 1 三角函數 only",
        "db_copy": str(ISO_DB),
        "sample_n": SAMPLE_N,
        "skills": [],
        "special_checks": {},
        "summary": {},
    }
    with flask_app.app_context():
        # Prefer curriculum chapter filter; also include all B2 skills whose id encodes 1_
        curr_rows = SkillCurriculum.query.filter(
            SkillCurriculum.skill_id.like("vh_數學B2_%")
        ).all()
        # skills_info for active flag / display name
        info_map = {s.skill_id: s for s in SkillInfo.query.filter(SkillInfo.skill_id.like("vh_數學B2_%")).all()}

        selected = []
        for row in curr_rows:
            sid = str(row.skill_id)
            ch = getattr(row, "chapter", None)
            # chapter 1 by curriculum chapter OR known ch1 skill id patterns
            is_ch1 = _chapter_is_1(ch)
            if not is_ch1:
                if sid.startswith("vh_數學B2_SubSection_1_"):
                    is_ch1 = True
                elif sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS and "SubSection_2_" not in sid:
                    # named pilot skills are ch1
                    is_ch1 = True
            if not is_ch1:
                # named trigonometry skills without subsection prefix still belong ch1
                named_ch1 = {
                    "vh_數學B2_RatioAndRatioValue",
                    "vh_數學B2_TrigonometricFunctionsOfAcuteAngles",
                    "vh_數學B2_AngleMeasurementAndConversion",
                    "vh_數學B2_TrigonometricValuesOfSpecialAngles",
                    "vh_數學B2_CoterminalAngles",
                    "vh_數學B2_FundamentalTrigonometricIdentities",
                    "vh_數學B2_ArcLengthAndAreaOfSector",
                    "vh_數學B2_CalculatingFunctionValuesUsingCalculator",
                }
                if sid in named_ch1:
                    is_ch1 = True
            if is_ch1:
                selected.append(row)

        # de-dupe by skill_id
        by_id = {}
        for row in selected:
            by_id[str(row.skill_id)] = row

        for sid, row in sorted(by_id.items(), key=lambda kv: (str(getattr(kv[1], "display_order", 9999)), kv[0])):
            info = info_map.get(sid)
            te_ids = _te_ids_for_skill(sid)
            types = []
            try:
                types = list_required_problem_types(sid)
            except Exception as exc:  # noqa: BLE001
                types = []
                inv_err = str(exc)
            else:
                inv_err = None
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
                "section": getattr(row, "section", None) or getattr(row, "paragraph", None),
                "display_order": getattr(row, "display_order", None),
                "is_active": is_active,
                "te_count": len(te_ids),
                "source_ids": te_ids[:40],
                "y": len(types),
                "problem_type_ids": types,
                "mastery_mode": "problem_type_mastery" if mastery else "consecutive_correct_legacy",
                "in_b2_pilot_allowlist": sid in B2_TYPE_MASTERY_PILOT_SKILL_IDS,
                "inventory": {
                    "facade": inv.get("facade_path") or inv.get("evidence", {}).get("facade") if isinstance(inv.get("evidence"), dict) else inv.get("facade_path"),
                    "usable": inv.get("usable_problem_type_ids"),
                    "health": inv.get("health"),
                    "error": inv.get("error") or inv_err,
                },
                "bugs": [],
                "decision_needed": None,
                "sample_status": "SKIPPED_INACTIVE" if not is_active else ("SKIPPED_Y0" if not types else "PENDING"),
                "generator_samples": {},
            }
            if sid in {"vh_數學B2_SubSection_1_4_1", "vh_數學B2_SubSection_1_4_2"}:
                if is_active:
                    rec["bugs"].append(
                        {
                            "severity": "P0",
                            "code": "EMPTY_SHELL_STILL_ACTIVE",
                            "detail": "TE=0/Y=0 shell should remain inactive",
                        }
                    )
                rec["sample_status"] = "INACTIVE_SHELL"
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
                    if fails:
                        rec["bugs"].append(
                            {
                                "severity": "P0",
                                "code": "GENERATOR_SAMPLE_FAIL",
                                "detail": fails,
                            }
                        )
                        rec["sample_status"] = "FAIL"
                    else:
                        rec["sample_status"] = "SAMPLED"
                    if low:
                        rec["bugs"].append(
                            {
                                "severity": "P2",
                                "code": "LOW_PARAM_VARIATION",
                                "detail": low,
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
            if (
                is_active
                and sid.startswith("vh_數學B2_SubSection_1_")
                and sid not in {"vh_數學B2_SubSection_1_4_1", "vh_數學B2_SubSection_1_4_2"}
                and not mastery
            ):
                rec["decision_needed"] = (
                    "A類 SubSection：是否納入 B2 題型掌握制 allowlist（目前仍顯示舊連對／暫無門檻語意）"
                )
            rec["status"] = _status_for_skill(rec)
            report["skills"].append(rec)

        report["special_checks"]["te_11583_11584"] = _check_11583_11584(report["skills"])
        try:
            report["special_checks"]["subsection_1_3_2_labels"] = _probe_subsection_132_labels()
        except Exception as exc:  # noqa: BLE001
            report["special_checks"]["subsection_1_3_2_labels"] = {
                "status": "NOT_TESTED",
                "error": str(exc),
            }

    # summary
    status_counts = Counter(s["status"] for s in report["skills"])
    report["summary"] = {
        "skill_count": len(report["skills"]),
        "active": sum(1 for s in report["skills"] if s["is_active"]),
        "inactive": sum(1 for s in report["skills"] if not s["is_active"]),
        "named_mastery_pilot": sum(1 for s in report["skills"] if s["in_b2_pilot_allowlist"]),
        "a_class_subsection": [
            s["skill_id"]
            for s in report["skills"]
            if s["is_active"]
            and s["skill_id"].startswith("vh_數學B2_SubSection_1_")
            and s["y"] > 0
        ],
        "status_counts": dict(status_counts),
    }

    json_path = OUT / "AUDIT_REPORT.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = _to_md(report)
    (OUT / "AUDIT_REPORT.md").write_text(md, encoding="utf-8")
    print(json.dumps({"out": str(OUT), "summary": report["summary"]}, ensure_ascii=False, indent=2))
    return 0


def _to_md(report: dict) -> str:
    lines = [
        f"# B2 第 1 章全 Skill 品質與 SOP 稽核報告",
        "",
        f"- stamp: `{report['stamp']}`",
        f"- sample_n: {report['sample_n']}",
        f"- skills: {report['summary'].get('skill_count')}",
        f"- status_counts: `{json.dumps(report['summary'].get('status_counts'), ensure_ascii=False)}`",
        "",
        "## Skill 清單",
        "",
        "| Skill | 名稱 | active | TE | Y | 掌握制 | status |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for s in report["skills"]:
        lines.append(
            f"| `{s['skill_id']}` | {s['display_name']} | {s['is_active']} | {s['te_count']} | {s['y']} | {s['mastery_mode']} | **{s['status']}** |"
        )
    lines.extend(["", "## 特別檢查", ""])
    lines.append("### TE 11583 / 11584")
    lines.append("```json")
    lines.append(json.dumps(report["special_checks"].get("te_11583_11584"), ensure_ascii=False, indent=2))
    lines.append("```")
    lines.append("### SubSection_1_3_2 labels")
    lines.append("```json")
    lines.append(json.dumps(report["special_checks"].get("subsection_1_3_2_labels"), ensure_ascii=False, indent=2)[:4000])
    lines.append("```")
    lines.extend(["", "## 各 Skill 抽樣摘要", ""])
    for s in report["skills"]:
        lines.append(f"### `{s['skill_id']}` — {s['status']}")
        if s.get("decision_needed"):
            lines.append(f"- NEEDS_DECISION: {s['decision_needed']}")
        if s.get("bugs"):
            lines.append(f"- bugs: `{json.dumps(s['bugs'], ensure_ascii=False)}`")
        samples = s.get("generator_samples") or {}
        if samples:
            lines.append("| problem_type | ok | unique_stems | unique_params | unique_answers | note |")
            lines.append("|---|---:|---:|---:|---:|---|")
            for pt, st in samples.items():
                lines.append(
                    f"| `{pt}` | {st.get('samples_ok')} | {st.get('unique_stems')} | {st.get('unique_params')} | {st.get('unique_answers')} | {st.get('diversity_note')} |"
                )
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
