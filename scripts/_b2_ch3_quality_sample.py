# -*- coding: utf-8 -*-
"""B2 Chapter 3 fast generator/checker sample before mastery allowlist."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
OUT = ROOT / "reports" / "b2_ch3_mastery_intro"
OUT.mkdir(parents=True, exist_ok=True)
ISO_DIR = ROOT / "tmp" / f"b2_ch3_sample_{STAMP}"
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

from app import app as flask_app
from core.gencode.domain_matrix_adapter import _humanize_answer_contract_parts
from core.practice_type_mastery import list_required_problem_types

SAMPLE_N = 10
SEED_BASE = 20261123
INV = json.loads((OUT / "ch3_runtime_inventory.json").read_text(encoding="utf-8"))
SKILLS = [s["skill_id"] for s in INV["skills"] if s["decision"] == "INCLUDE_CANDIDATE"]

FUZZY = {"sum", "sin", "cos", "tan", "elevation", "小題1", "小題2", "part1", "part2"}


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
    return _humanize_answer_contract_parts(parts)


def _check(fac, payload: dict, user_answer: Any) -> bool | None:
    fn = getattr(fac, "check", None)
    if not callable(fn):
        return None
    correct = payload.get("correct_answer")
    try:
        r = fn(user_answer, correct, question_payload=payload)
    except Exception:  # noqa: BLE001
        return None
    if isinstance(r, bool):
        return r
    if isinstance(r, dict):
        v = r.get("overall_correct")
        if v is None:
            v = r.get("is_correct")
        return bool(v) if v is not None else None
    return bool(r)


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
                out[k] = v + "_x"
                return out
        out["__probe"] = "wrong"
        return out
    if isinstance(ans, (int, float)):
        return ans + 1 if ans != 0 else 2
    if isinstance(ans, str):
        return ans + "_x" if ans else "999"
    return "999"


def main() -> int:
    report = {"stamp": STAMP, "skills": [], "summary": {}}
    with flask_app.app_context():
        for sid in SKILLS:
            fac = _load(sid)
            types = list_required_problem_types(sid)
            per = {}
            bugs = []
            for pt in types:
                comps = _comps(fac, pt)
                ok_n = 0
                err_n = 0
                label_issues = []
                checker = "NOT_TESTED"
                stems = set()
                for i in range(SAMPLE_N):
                    seed = SEED_BASE + i * 19 + (abs(hash(pt)) % 900)
                    cid = comps[i % len(comps)] if comps else None
                    try:
                        payload = (
                            fac.generate(level=1, seed=seed, component_id=cid)
                            if cid
                            else fac.generate(level=1, seed=seed)
                        )
                    except Exception as exc:  # noqa: BLE001
                        err_n += 1
                        if err_n <= 2:
                            bugs.append({"severity": "P0", "code": "GEN_FAIL", "pt": pt, "detail": str(exc)})
                        continue
                    ok_n += 1
                    stem = str(
                        payload.get("question_text")
                        or payload.get("question")
                        or payload.get("problem_text")
                        or ""
                    )
                    stems.add(stem[:120])
                    for p in _parts(payload):
                        lab = str(p.get("display_label") or p.get("label") or "").strip()
                        if lab.lower() in FUZZY or lab in FUZZY:
                            label_issues.append({"key": p.get("key"), "label": lab})
                    if checker == "NOT_TESTED":
                        ans = payload.get("correct_answer")
                        good = _check(fac, payload, ans)
                        bad = _check(fac, payload, _wrong(ans))
                        if good is True and bad is False:
                            checker = "PASS"
                        elif good is None or bad is None:
                            checker = "SKIPPED_NO_CHECK"
                        else:
                            checker = "FAIL"
                            bugs.append(
                                {
                                    "severity": "P0",
                                    "code": "CHECKER_MISJUDGE",
                                    "pt": pt,
                                    "good": good,
                                    "bad": bad,
                                }
                            )
                if ok_n == 0:
                    bugs.append({"severity": "P0", "code": "NO_SAMPLES", "pt": pt})
                if label_issues:
                    bugs.append(
                        {
                            "severity": "P1",
                            "code": "FUZZY_LABEL",
                            "pt": pt,
                            "detail": label_issues[:5],
                        }
                    )
                note = (
                    "LOW_VARIATION_SUSPECT"
                    if ok_n > 0 and len(stems) <= 1
                    else ("HAS_VARIATION" if len(stems) >= 3 else "LIMITED_VARIATION")
                )
                if note == "LOW_VARIATION_SUSPECT":
                    bugs.append({"severity": "P2", "code": "LOW_PARAM_VARIATION", "pt": pt})
                per[pt] = {
                    "ok": ok_n,
                    "err": err_n,
                    "unique_stems": len(stems),
                    "checker": checker,
                    "diversity": note,
                    "label_issues": label_issues[:5],
                }
            p0 = [b for b in bugs if b.get("severity") == "P0"]
            p1 = [b for b in bugs if b.get("severity") == "P1"]
            status = "BLOCKED" if p0 else ("NEEDS_FIX" if p1 else "PASS")
            rec = {
                "skill_id": sid,
                "y": len(types),
                "status": status,
                "types": per,
                "bugs": bugs,
            }
            report["skills"].append(rec)
            print(f"[{status}] {sid} Y={len(types)} bugs={len(bugs)}")

    include = [s["skill_id"] for s in report["skills"] if s["status"] == "PASS"]
    blocked = [s["skill_id"] for s in report["skills"] if s["status"] != "PASS"]
    report["summary"] = {
        "include": include,
        "blocked": blocked,
        "gate": "PASS_BATCH" if not blocked else "PARTIAL",
    }
    path = OUT / "ch3_quality_sample.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print("wrote", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
