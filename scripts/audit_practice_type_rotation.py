# -*- coding: utf-8 -*-
"""Batch audit: which B1-B4 sections can use chapter dynamic practice (type rotation).

Reads curriculum rows, skills_info.is_active, runtime wrappers (skills/<id>.py) and
V3 component manifests; never reads textbook text and never infers type identity.

Per section status:
    READY     runtime module + every component has problem_type_id + reliable pool
    FALLBACK  legacy practice works but type rotation cannot be enabled safely
    BLOCKED   runtime/metadata problem that can break practice itself

Usage:
    python scripts/audit_practice_type_rotation.py            # full audit + generator smoke
    python scripts/audit_practice_type_rotation.py --no-smoke # metadata + scheduler only

Writes reports/practice_type_rotation_b1_b4_audit.{json,md}.  Not a runtime dependency.
"""

from __future__ import annotations

import argparse
import collections
import contextlib
import importlib
import io
import json
import os
import random
import re
import sqlite3
import statistics
import sys
import time
import warnings
from pathlib import Path
from typing import Any, Callable, NamedTuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import practice_type_rotation as ptr  # noqa: E402

VOLUMES: tuple[str, ...] = ("數學B1", "數學B2", "數學B3", "數學B4")
CURRICULUM = "vocational"
REPORT_JSON = ROOT / "reports" / "practice_type_rotation_b1_b4_audit.json"
REPORT_MD = ROOT / "reports" / "practice_type_rotation_b1_b4_audit.md"
PUBLISHED_MANIFEST_STATUS = "production_manifest_compiled"
# Mirrors core.routes.practice.get_skill: these ids never resolve to a runtime module.
RUNTIME_EXCLUDED = {"vh_數學B4_TreeDiagramCounting", "vh_數學B4_PascalTriangle"}


class CurriculumRow(NamedTuple):
    curriculum: str
    volume: str
    chapter: str
    section: str
    display_order: int
    skill_id: str
    is_active: bool


def _db_path(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit)
    uri = os.environ.get("MATHPROJECT_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        return Path(uri[len("sqlite:///"):])
    return ROOT / "instance" / "kumon_math.db"


def load_curriculum_rows(db_path: Path | None = None) -> list[CurriculumRow]:
    path = db_path or _db_path()
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        placeholders = ",".join("?" for _ in VOLUMES)
        rows = con.execute(
            "SELECT c.curriculum, c.volume, c.chapter, c.section, COALESCE(c.display_order, 0), "
            "c.skill_id, COALESCE(i.is_active, 0) "
            "FROM skill_curriculum c LEFT JOIN skills_info i ON i.skill_id = c.skill_id "
            f"WHERE c.curriculum = ? AND c.volume IN ({placeholders})",
            (CURRICULUM, *VOLUMES),
        ).fetchall()
    finally:
        con.close()
    return [
        CurriculumRow(str(a), str(b), str(c or ""), str(d or ""), int(e or 0), str(f), bool(g))
        for a, b, c, d, e, f, g in rows
    ]


def load_manifest(skill_id: str) -> dict[str, Any] | None:
    path = ROOT / "agent_skills_v3" / skill_id / "component_manifest.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {"_error": "manifest_unreadable"}


def import_runtime(skill_id: str) -> tuple[Any | None, str]:
    if skill_id in RUNTIME_EXCLUDED:
        return None, "runtime_excluded"
    if not (ROOT / "skills" / f"{skill_id}.py").is_file():
        return None, "module_file_missing"
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return importlib.import_module(f"skills.{skill_id}"), ""
    except Exception as exc:  # pragma: no cover - reported, not raised
        return None, f"import_error:{type(exc).__name__}:{exc}"


def _leading_int(text: str) -> int | None:
    m = re.search(r"\d+", str(text or ""))
    return int(m.group()) if m else None


def _order_key(row: CurriculumRow) -> tuple:
    return (ptr._leading_numbers(row.section), int(row.display_order or 0), row.skill_id)


def inspect_section(row: CurriculumRow) -> dict[str, Any]:
    """Metadata-only inspection of one curriculum row."""
    info: dict[str, Any] = {
        "volume": row.volume,
        "chapter": row.chapter,
        "section": row.section,
        "display_order": row.display_order,
        "skill_id": row.skill_id,
        "is_active": row.is_active,
        "runtime_module": False,
        "runtime_error": "",
        "manifest_status": None,
        "components": 0,
        "components_with_problem_type_id": 0,
        "missing_problem_type_id": 0,
        "missing_components": [],
        "unique_types": 0,
        "type_candidates": {},
        "type_key_sources": {},
        "pool_buildable": False,
        "issues": [],
    }
    manifest = load_manifest(row.skill_id)
    if manifest is not None:
        info["manifest_status"] = manifest.get("publish_status") or manifest.get("_error")

    if row.skill_id.startswith("outline_"):
        info["kind"] = "outline_placeholder"
    elif not row.is_active:
        info["kind"] = "unpublished_inactive"
    else:
        info["kind"] = "published"

    module, err = import_runtime(row.skill_id)
    info["runtime_module"] = module is not None
    info["runtime_error"] = err
    if info["kind"] == "published" and module is None:
        info["kind"] = "runtime_missing"
    if module is None:
        return info

    raw_specs = [s for s in (getattr(module, "GENERATOR_SPECS", None) or []) if isinstance(s, dict)]
    keys = [str(k) for k in (getattr(module, "GENERATOR_KEYS", None) or [])]
    specs = ptr._runtime_specs(module)
    spec_ids = {ptr._candidate_id(s) for s in raw_specs} - {""}
    if not spec_ids:
        # Legacy wrapper (skill-level generate_for_skill / question_router): no component
        # dispatch, so type rotation cannot address candidates.
        info["legacy_wrapper"] = True
        info["legacy_specs_with_problem_type_id"] = sum(
            1 for s in raw_specs if str(s.get("problem_type_id") or "").strip()
        )
        info["issues"].append({"code": "legacy_wrapper_no_component_dispatch", "raw_specs": len(raw_specs)})
    else:
        keys_without_spec = [k for k in keys if k not in spec_ids]
        if keys_without_spec:
            info["issues"].append({"code": "generator_key_without_spec", "components": keys_without_spec})
        if not specs:
            info["issues"].append({"code": "no_generator_specs"})

    info["components"] = len(specs)
    with_pt = [s for s in specs if str(s.get("problem_type_id") or "").strip()]
    info["components_with_problem_type_id"] = len(with_pt)
    missing = [ptr._candidate_id(s) for s in specs if not str(s.get("problem_type_id") or "").strip()]
    info["missing_problem_type_id"] = len(missing)
    info["missing_components"] = missing

    pool = ptr.build_type_pool(specs)
    types = pool["types"]
    info["unique_types"] = len(types)
    info["type_candidates"] = {k: [c["component_id"] for c in v] for k, v in sorted(types.items())}
    info["type_key_sources"] = dict(
        collections.Counter(c["type_key_source"] for v in types.values() for c in v)
    )
    info["pool_buildable"] = bool(pool["reliable"])

    manifest_components = {
        str(c.get("component_id")): c
        for c in ((manifest or {}).get("components") or [])
        if isinstance(c, dict) and c.get("component_id")
    }
    if manifest_components:
        mismatch, not_in_manifest, ssot_fix = [], [], {}
        for spec in specs:
            cid = ptr._candidate_id(spec)
            mc = manifest_components.get(cid)
            if mc is None:
                not_in_manifest.append(cid)
                continue
            m_pt = str(mc.get("problem_type_id") or "").strip()
            w_pt = str(spec.get("problem_type_id") or "").strip()
            if w_pt and m_pt and w_pt != m_pt:
                mismatch.append({"component_id": cid, "wrapper": w_pt, "manifest": m_pt})
            if not w_pt and m_pt:
                ssot_fix[cid] = m_pt
        if mismatch:
            info["issues"].append({"code": "problem_type_id_manifest_mismatch", "components": mismatch})
        if not_in_manifest:
            info["issues"].append({"code": "component_not_in_manifest", "components": not_in_manifest})
        if ssot_fix:
            info["ssot_problem_type_fix"] = ssot_fix
    return info


def classify(info: dict[str, Any]) -> str:
    if info["kind"] != "published":
        return "EXCLUDED"
    if info.get("legacy_wrapper"):
        return "BLOCKED" if info.get("legacy_smoke_failed") else "FALLBACK"
    blocking = {"generator_key_without_spec", "no_generator_specs", "problem_type_id_manifest_mismatch"}
    if (any(i["code"] in blocking for i in info["issues"]) or info.get("undeliverable_types")
            or info.get("unanswerable_types")):
        return "BLOCKED"
    non_ptid = {k: v for k, v in info["type_key_sources"].items() if k != "problem_type_id"}
    if not info["pool_buildable"] or info["missing_problem_type_id"] or non_ptid:
        return "FALLBACK"
    if any(not v for v in info["type_candidates"].values()):
        return "FALLBACK"
    return "READY"


def scheduler_smoke(section: str, types: dict[str, list[dict[str, Any]]], seed: int = 0) -> dict[str, Any]:
    """Drive the real scheduler: full first round, one weak type, retry, completion."""
    rng = random.Random(seed)
    result: dict[str, Any] = {"ok": True, "errors": []}

    def fail(msg: str) -> None:
        result["ok"] = False
        result["errors"].append(msg)

    state = ptr.new_state(section, types, rng)
    first: list[dict[str, Any]] = []
    weak_pick: dict[str, Any] | None = None
    for i in range(len(types)):
        pick = ptr.next_pick(state, types, rng)
        if pick is None:
            fail("first_round_ended_early")
            break
        first.append(pick)
        uid = f"{section}:r1:{i}"
        ptr.register_served_question(state, types, uid, pick["type_key"])
        correct = i != 0
        if not correct:
            weak_pick = pick
        ptr.record_result(state, types, uid, correct)
    served_types = [p["type_key"] for p in first]
    result["first_round_size"] = len(first)
    result["state_first_round_size"] = int(state.get("n", -1))
    if len(first) != len(types) or int(state.get("n", -1)) != len(types):
        fail(f"first_round_size {len(first)} != unique types {len(types)}")
    if len(set(served_types)) != len(served_types):
        fail("duplicate_type_in_first_round")
    if any(p["round"] != 1 for p in first):
        fail("first_round_contains_round_gt_1")

    if weak_pick is not None:
        retry = ptr.next_pick(state, types, rng)
        if retry is None:
            fail("weak_type_not_retried")
        else:
            if retry["type_key"] != weak_pick["type_key"] or retry["round"] != 2:
                fail(f"retry picked {retry['type_key']} round {retry['round']}")
            multi = len(types[weak_pick["type_key"]]) > 1
            result["retry_candidate_changed"] = retry["component_id"] != weak_pick["component_id"]
            result["retry_policy"] = "different_candidate" if multi else "same_generator_new_seed"
            if multi and not result["retry_candidate_changed"]:
                fail("multi_candidate_retry_reused_component")
            uid = f"{section}:r2"
            ptr.register_served_question(state, types, uid, retry["type_key"])
            ptr.record_result(state, types, uid, True)
            if ptr.next_pick(state, types, rng) is not None or not state.get("c"):
                fail("section_not_completed_after_all_passed")
    return result


ROUTE_ATTEMPTS = 5  # core.routes.practice get_next_question max_retries
ROUTE_SEED_STRIDE = 7919  # core.routes.practice _RETRY_SEED_STRIDE


def _has_visual_stem(q: dict[str, Any]) -> bool:
    return bool(q.get("image_base64") or q.get("visual_spec") or q.get("diagram_spec") or q.get("visual_aids"))


def _generated_ok(q: Any, cid: str, type_key: str) -> str:
    if not isinstance(q, dict):
        return "payload_not_dict"
    if not str(q.get("question_text") or "").strip() and not _has_visual_stem(q):
        return "empty_question_text"
    ans = q.get("correct_answer", q.get("answer"))
    if ans is None or (isinstance(ans, str) and not ans.strip()):
        return "missing_correct_answer"
    got_cid = str(q.get("component_id") or "")
    if got_cid and got_cid != cid:
        return f"component_mismatch:{got_cid}"
    got_pt = str(q.get("problem_type_id") or "")
    if got_pt and got_pt != type_key:
        return f"problem_type_mismatch:{got_pt}"
    return ""


def _route_session(q: dict[str, Any], skill_id: str) -> tuple[Any, str]:
    """Mirror get_next_question: canonicalize, session-normalize, then the delivery gate."""
    try:
        from core.gencode.answer_payload import refresh_runtime_question_session
        from core.gencode.question_delivery_contract import canonicalize_question_text, question_delivery_errors

        sink = io.StringIO()
        with warnings.catch_warnings(), contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            warnings.simplefilter("ignore")
            data = canonicalize_question_text(dict(q))
            if "answer" in data and "correct_answer" not in data:
                data["correct_answer"] = data["answer"]
            session = refresh_runtime_question_session(dict(data), skill_id=skill_id)
            delivery_errors = question_delivery_errors(session)
    except Exception as exc:
        return None, f"session_{type(exc).__name__}:{str(exc)[:120]}"
    if delivery_errors:
        return None, "delivery_gate:" + ",".join(str(e) for e in delivery_errors)[:160]
    return session, ""


def _generate_once(module: Any, seed: int, **kwargs: Any) -> tuple[Any, str]:
    sink = io.StringIO()
    try:
        with warnings.catch_warnings(), contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            warnings.simplefilter("ignore")
            return module.generate(level=1, seed=seed, **kwargs), ""
    except Exception as exc:
        return None, f"{type(exc).__name__}:{str(exc)[:160]}"


def _self_grade(q: dict[str, Any], skill_id: str) -> str:
    """Grade the payload's own correct answer with the formal grader; "" when correct or not gradable."""
    if q.get("auto_checkable") is False or str(q.get("interaction_type") or "") == "handwriting_drawing":
        return ""
    contract = q.get("answer_contract") if isinstance(q.get("answer_contract"), dict) else {}
    parts = [p for p in (contract.get("parts") or []) if isinstance(p, dict) and p.get("key")]
    if parts and all(p.get("expected_answer") is not None for p in parts):
        answer: Any = {str(p["key"]): str(p["expected_answer"]) for p in parts}
    else:
        answer = q.get("correct_answer", q.get("answer"))
        if isinstance(answer, (list, tuple)):
            answer = ", ".join(str(a) for a in answer)
    labels = [str(c.get("label")) for c in (q.get("choices") or []) if isinstance(c, dict) and c.get("label")]
    if labels and str(contract.get("checker") or "") == "choice_label_checker":
        # Students submit a choice label; the question is answerable when some label grades correct.
        errors = [_grade_once(label, q, skill_id) for label in labels]
        return "" if "" in errors else (errors[0] or "own_answer_graded_incorrect")
    return _grade_once(answer, q, skill_id)


def _grade_once(answer: Any, q: dict[str, Any], skill_id: str) -> str:
    try:
        import logging

        from core.gencode.answer_grading import grade_answer_for_current_question

        sink = io.StringIO()
        with warnings.catch_warnings(), contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            warnings.simplefilter("ignore")
            result = grade_answer_for_current_question(answer, q, skill_id, log=logging.getLogger("audit"))
    except Exception as exc:
        return f"grader_exception:{type(exc).__name__}"
    if result is None:
        return ""
    if result.get("correct") is True:
        return ""
    return f"own_answer_graded_{result.get('status') or result.get('correct')}"


def generator_smoke(skill_id: str, types: dict[str, list[str]], seed: int = 20260930) -> dict[str, Any]:
    """Per candidate, emulate one practice request: up to ROUTE_ATTEMPTS seeds.

    A candidate fails only when every attempt fails (the route would answer 題目載入失敗);
    a type is undeliverable when all of its candidates fail, which would stall rotation.
    """
    module, _ = import_runtime(skill_id)
    out: dict[str, Any] = {"generated": 0, "failures": [], "retried": [], "notes": [], "undeliverable_types": [],
                           "self_grade_failures": [], "unanswerable_types": []}
    if module is None:
        return out
    for type_key, cids in types.items():
        type_ok = False
        type_answerable = False
        for cid in cids:
            errors: list[str] = []
            for attempt in range(ROUTE_ATTEMPTS):
                q, err = _generate_once(module, seed + attempt * ROUTE_SEED_STRIDE, component_id=cid)
                err = err or _generated_ok(q, cid, type_key)
                if not err:
                    q, err = _route_session(q, skill_id)
                out["generated"] += 1
                if not err:
                    if not str(q.get("question_text") or "").strip():
                        out["notes"].append({"type": type_key, "component_id": cid, "note": "visual_only_stem"})
                    grade_err = _self_grade(q, skill_id)
                    if grade_err:
                        out["self_grade_failures"].append({"type": type_key, "component_id": cid, "error": grade_err})
                    else:
                        type_answerable = True
                    break
                errors.append(err)
            if len(errors) == ROUTE_ATTEMPTS:
                out["failures"].append({"type": type_key, "component_id": cid, "error": errors[-1]})
            else:
                type_ok = True
                if errors:
                    out["retried"].append({"type": type_key, "component_id": cid, "failed_attempts": len(errors),
                                           "error": errors[-1]})
        if not type_ok:
            out["undeliverable_types"].append(type_key)
        elif not type_answerable:
            out["unanswerable_types"].append(type_key)
    return out


def legacy_smoke(skill_id: str, seed: int = 20260930, requests: int = 3) -> dict[str, Any]:
    """Legacy wrappers: a few plain generate() requests with the route's retry budget."""
    module, _ = import_runtime(skill_id)
    out: dict[str, Any] = {"generated": 0, "failed_requests": 0, "error": ""}
    if module is None or not callable(getattr(module, "generate", None)):
        out["failed_requests"] = requests
        out["error"] = "no_generate_callable"
        return out
    for r in range(requests):
        ok = False
        for attempt in range(ROUTE_ATTEMPTS):
            q, err = _generate_once(module, seed + r * 101 + attempt * ROUTE_SEED_STRIDE)
            out["generated"] += 1
            if not err and isinstance(q, dict) and (str(q.get("question_text") or "").strip() or _has_visual_stem(q)):
                _, err = _route_session(q, skill_id)
                if not err:
                    ok = True
                    break
            out["error"] = err or "empty_payload"
        out["failed_requests"] += int(not ok)
    return out


def validate_progression(
    rows: list[CurriculumRow],
    ready: set[str],
    runtime_available: Callable[[str], bool],
    skill_ids_with_runtime: set[str],
) -> dict[str, Any]:
    chapters: dict[tuple[str, str], list[CurriculumRow]] = collections.defaultdict(list)
    for r in rows:
        chapters[(r.volume, r.chapter)].append(r)
    report: dict[str, Any] = {"chapters": [], "issues": []}
    skill_rows = collections.Counter(r.skill_id for r in rows)
    for sid, n in sorted(skill_rows.items()):
        if n > 1:
            report["issues"].append({"code": "skill_in_multiple_rows", "skill_id": sid, "rows": n})

    for (volume, chapter), chapter_rows in sorted(chapters.items(), key=lambda kv: (kv[0][0], _leading_int(kv[0][1]) or 0)):
        ordered = sorted(chapter_rows, key=_order_key)
        ch_no = _leading_int(chapter)
        dup = collections.Counter((r.section, r.display_order) for r in ordered)
        for (sec, order), n in dup.items():
            if n > 1:
                report["issues"].append(
                    {"code": "duplicate_order", "volume": volume, "chapter": chapter, "section": sec, "display_order": order}
                )
        for r in ordered:
            sec_no = _leading_int(r.section)
            if ch_no is not None and sec_no is not None and sec_no != ch_no:
                report["issues"].append(
                    {"code": "orphan_section_chapter_mismatch", "volume": volume, "chapter": chapter,
                     "section": r.section, "skill_id": r.skill_id}
                )
        seq = [r.skill_id for r in ordered if r.skill_id in ready]
        transitions = []
        for sid in seq:
            nxt = ptr.resolve_next_section(sid, chapter_rows, is_available=lambda s: s in ready)
            nxt_runtime = ptr.resolve_next_section(sid, chapter_rows, is_available=runtime_available)
            leak = bool(nxt) and all(r.skill_id != nxt for r in chapter_rows)
            transitions.append({"from": sid, "next": nxt, "next_runtime_rule": nxt_runtime})
            if leak:
                report["issues"].append({"code": "chapter_boundary_leak", "from": sid, "next": nxt})
            if nxt_runtime != nxt:
                report["issues"].append(
                    {"code": "runtime_next_targets_non_ready_section", "volume": volume, "chapter": chapter,
                     "from": sid, "runtime_next": nxt_runtime, "expected_next": nxt}
                )
        skipped_middle = []
        if seq:
            first_i = next(i for i, r in enumerate(ordered) if r.skill_id == seq[0])
            last_i = max(i for i, r in enumerate(ordered) if r.skill_id == seq[-1])
            skipped_middle = [
                {"skill_id": r.skill_id, "section": r.section,
                 "reason": "no_runtime" if r.skill_id not in skill_ids_with_runtime else "not_ready"}
                for r in ordered[first_i:last_i + 1] if r.skill_id not in ready
            ]
        chapter_end = seq[-1] if seq else ""
        end_next = transitions[-1]["next"] if transitions else ""
        report["chapters"].append(
            {
                "volume": volume,
                "chapter": chapter,
                "rows": len(ordered),
                "ready_sequence": seq,
                "transitions": transitions,
                "skipped_middle": skipped_middle,
                "chapter_end": chapter_end,
                "chapter_end_next": end_next,
                "chapter_completion_reachable": bool(seq) and end_next == "",
            }
        )
    return report


def _severity_and_action(sec: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    base = {"skill_id": sec["skill_id"], "volume": sec["volume"], "section": sec["section"]}
    kind, status = sec["kind"], sec["status"]
    if kind == "runtime_missing":
        published = sec["manifest_status"] == PUBLISHED_MANIFEST_STATUS
        out.append({**base, "category": "runtime_missing",
                    "reason": f"active in curriculum but no runtime module (manifest={sec['manifest_status']})",
                    "severity": "P1" if published else "info",
                    "action": "publish runtime wrapper" if published else "not published yet; excluded from rotation"})
    elif kind == "unpublished_inactive" and sec["runtime_module"]:
        out.append({**base, "category": "unpublished/dryrun",
                    "reason": "runtime module exists but skills_info.is_active=0",
                    "severity": "info", "action": "stay hidden; must not be a next-section target"})
    if sec.get("legacy_wrapper") and kind == "published":
        leg = sec.get("legacy_smoke") or {}
        broken = bool(sec.get("legacy_smoke_failed"))
        out.append({**base, "category": "runtime metadata incomplete (legacy wrapper)",
                    "reason": "skill-level generator without component dispatch "
                              f"(specs with problem_type_id: {sec.get('legacy_specs_with_problem_type_id', 0)}); "
                              + (f"legacy generate failed: {leg.get('error')}" if broken else "legacy practice OK"),
                    "severity": "P1" if broken else "P2",
                    "action": "legacy practice stays (curriculum_sequence); rotation needs V3 component wrapper"})
    for issue in sec["issues"]:
        if status == "BLOCKED" and issue["code"] in {"generator_key_without_spec", "no_generator_specs",
                                                     "problem_type_id_manifest_mismatch"}:
            out.append({**base, "category": "metadata contradiction", "reason": issue["code"],
                        "severity": "P1", "action": "reconcile wrapper with manifest SSOT"})
    fails = sec.get("smoke_failures") or []
    undeliverable = sec.get("undeliverable_types") or []
    if fails:
        out.append({**base, "category": "content issue",
                    "reason": f"component(s) fail all {ROUTE_ATTEMPTS} route attempts: "
                              + "; ".join(f"{f['component_id']} {f['error']}" for f in fails[:3])
                              + (f"; undeliverable types: {undeliverable}" if undeliverable else ""),
                    "severity": "P1" if undeliverable else "P2",
                    "action": "fix component generator" + (" (rotation would stall on this type)" if undeliverable else "")})
    for r in sec.get("smoke_retried") or []:
        out.append({**base, "category": "content issue",
                    "reason": f"{r['component_id']} intermittent: {r['failed_attempts']} failed seed(s) before success ({r['error']})",
                    "severity": "P2", "action": "route retry covers it; improve generator validity"})
    grade_fails = sec.get("self_grade_failures") or []
    unanswerable = sec.get("unanswerable_types") or []
    if grade_fails:
        out.append({**base, "category": "content issue",
                    "reason": "payload's own correct answer is not accepted by the formal grader: "
                              + "; ".join(f"{g['component_id']} {g['error']}" for g in grade_fails[:3])
                              + (f"; unanswerable types: {unanswerable}" if unanswerable else ""),
                    "severity": "P1" if unanswerable else "P2",
                    "action": "align answer_contract with displayed answer"
                              + (" (no candidate of this type can be answered)" if unanswerable else "")})
    visual_only = sorted({n["component_id"] for n in sec.get("smoke_notes") or [] if n["note"] == "visual_only_stem"})
    if visual_only:
        out.append({**base, "category": "content issue",
                    "reason": f"empty question_text, stem only in visual/table: {','.join(visual_only)}",
                    "severity": "P2", "action": "add instruction text to stem"})
    if status == "FALLBACK" and not sec.get("legacy_wrapper"):
        fix = sec.get("ssot_problem_type_fix") or {}
        out.append({**base, "category": "metadata missing",
                    "reason": f"missing problem_type_id on {sec['missing_problem_type_id']} component(s): "
                              + ",".join(sec["missing_components"][:6]),
                    "severity": "P1" if fix else "P2",
                    "action": "backfill from manifest SSOT" if fix else "no authoritative SSOT; keep curriculum_sequence"})
    return out


def run_audit(*, smoke: bool = True, db_path: Path | None = None) -> dict[str, Any]:
    started = time.time()
    rows = load_curriculum_rows(db_path)
    sections = [inspect_section(r) for r in sorted(rows, key=lambda r: (r.volume, _leading_int(r.chapter) or 0, _order_key(r)))]
    by_id = {s["skill_id"]: s for s in sections}

    smoke_summary = {"ready_checked": 0, "pools_built": 0, "scheduler_failures": 0, "generated": 0,
                     "generator_failures": 0, "undeliverable_types": 0, "self_grade_failures": 0,
                     "unanswerable_types": 0, "legacy_checked": 0, "legacy_failures": 0}
    for sec in sections:
        if smoke and sec["kind"] == "published" and sec.get("legacy_wrapper"):
            leg = legacy_smoke(sec["skill_id"])
            sec["legacy_smoke"] = leg
            sec["legacy_smoke_failed"] = leg["failed_requests"] > 0
            smoke_summary["legacy_checked"] += 1
            smoke_summary["legacy_failures"] += int(sec["legacy_smoke_failed"])
        sec["status"] = classify(sec)
    for sec in sections:
        if sec["status"] != "READY":
            continue
        module, _ = import_runtime(sec["skill_id"])
        pool = ptr.load_section_pool(sec["skill_id"], module=module)
        types = pool["types"]
        smoke_summary["ready_checked"] += 1
        ok_pool = (
            pool["reliable"]
            and len(ptr.get_practice_type_pool(sec["skill_id"], module=module)) == sec["unique_types"]
            and all(types.values())
        )
        smoke_summary["pools_built"] += int(ok_pool)
        sched = scheduler_smoke(sec["skill_id"], types)
        sec["scheduler"] = sched
        if not sched["ok"] or not ok_pool:
            smoke_summary["scheduler_failures"] += 1
            sec["issues"].append({"code": "scheduler_smoke_failed", "errors": sched["errors"]})
        if smoke:
            gen = generator_smoke(sec["skill_id"], sec["type_candidates"])
            smoke_summary["generated"] += gen["generated"]
            smoke_summary["generator_failures"] += len(gen["failures"])
            smoke_summary["undeliverable_types"] += len(gen["undeliverable_types"])
            sec["smoke_failures"] = gen["failures"]
            sec["smoke_retried"] = gen["retried"]
            sec["smoke_notes"] = gen["notes"]
            sec["undeliverable_types"] = gen["undeliverable_types"]
            sec["self_grade_failures"] = gen["self_grade_failures"]
            sec["unanswerable_types"] = gen["unanswerable_types"]
            smoke_summary["self_grade_failures"] += len(gen["self_grade_failures"])
            smoke_summary["unanswerable_types"] += len(gen["unanswerable_types"])
        sec["status"] = classify(sec)

    ready = {s["skill_id"] for s in sections if s["status"] == "READY"}
    with_runtime = {s["skill_id"] for s in sections if s["runtime_module"]}

    def runtime_available(skill_id: str) -> bool:
        # Same rule as core.routes.practice._practice_type_rotation_section_available.
        sec = by_id.get(skill_id)
        return bool(sec and sec["runtime_module"] and sec["unique_types"] and sec["pool_buildable"])

    progression = validate_progression(rows, ready, runtime_available, with_runtime)
    for ch in progression["chapters"]:
        skipped = [
            s for s in sections
            if s["volume"] == ch["volume"] and s["chapter"] == ch["chapter"]
            and s["kind"] == "published" and s["status"] in {"FALLBACK", "BLOCKED"}
        ]
        ch["skipped_published_non_ready"] = [s["skill_id"] for s in skipped]
        if skipped:
            progression["issues"].append({
                "code": "published_non_ready_sections_skipped",
                "volume": ch["volume"],
                "chapter": ch["chapter"],
                "skills": [s["skill_id"] for s in skipped],
                "chapter_has_ready_sections": bool(ch["ready_sequence"]),
            })

    summary: dict[str, Any] = {}
    for vol in VOLUMES:
        vs = [s for s in sections if s["volume"] == vol]
        pub = [s for s in vs if s["kind"] == "published"]
        c = collections.Counter(s["status"] for s in pub)
        summary[vol] = {
            "curriculum_rows": len(vs),
            "sections": len(pub),
            "READY": c.get("READY", 0),
            "FALLBACK": c.get("FALLBACK", 0),
            "BLOCKED": c.get("BLOCKED", 0),
            "coverage_pct": round(100.0 * c.get("READY", 0) / len(pub), 1) if pub else 0.0,
            "excluded": dict(collections.Counter(s["kind"] for s in vs if s["kind"] != "published")),
        }
    published_total = sum(v["sections"] for v in summary.values())
    ready_total = sum(v["READY"] for v in summary.values())
    summary["overall"] = {
        "published_sections": published_total,
        "rotation_ready_sections": ready_total,
        "coverage_pct": round(100.0 * ready_total / published_total, 1) if published_total else 0.0,
    }

    type_counts = [s["unique_types"] for s in sections if s["status"] == "READY"]
    distribution = {
        "min": min(type_counts) if type_counts else 0,
        "max": max(type_counts) if type_counts else 0,
        "median": statistics.median(type_counts) if type_counts else 0,
        "sections_with_1_type": sum(1 for n in type_counts if n == 1),
        "sections_with_ge_7_types": sum(1 for n in type_counts if n >= 7),
        "histogram": dict(sorted(collections.Counter(type_counts).items())),
        "multi_candidate_sections": sum(
            1 for s in sections if s["status"] == "READY"
            and any(len(v) > 1 for v in s["type_candidates"].values())
        ),
    }

    exceptions: list[dict[str, Any]] = []
    for sec in sections:
        exceptions.extend(_severity_and_action(sec))
    for issue in progression["issues"]:
        code = issue["code"]
        if code == "published_non_ready_sections_skipped":
            exceptions.append({
                "skill_id": ",".join(issue["skills"]), "volume": issue["volume"], "section": issue["chapter"],
                "category": "progression",
                "reason": f"{len(issue['skills'])} published non-READY section(s) are skipped by rotation; "
                          + ("chapter_completed is reached without them" if issue["chapter_has_ready_sections"]
                             else "chapter has no READY section (rotation never starts)"),
                "severity": "P1" if issue["chapter_has_ready_sections"] else "P2",
                "action": "convert these wrappers to V3 component specs, or accept legacy practice for them",
            })
            continue
        sev = "P1" if code in {"chapter_boundary_leak", "runtime_next_targets_non_ready_section"} else "P2"
        exceptions.append({"skill_id": issue.get("from") or issue.get("skill_id", ""), "volume": issue.get("volume", ""),
                           "section": issue.get("section", issue.get("chapter", "")), "category": "progression",
                           "reason": json.dumps(issue, ensure_ascii=False), "severity": sev,
                           "action": "review curriculum ordering" if sev == "P2" else "fix next-section availability"})

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_sec": round(time.time() - started, 1),
        "generator_smoke": smoke,
        "summary": summary,
        "type_distribution": distribution,
        "automated_validation": smoke_summary,
        "progression": progression,
        "exceptions": exceptions,
        "sections": sections,
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = ["# Practice Type Rotation B1-B4 Audit", "",
             f"generated_at: {report['generated_at']}  elapsed: {report['elapsed_sec']}s  "
             f"generator_smoke: {report['generator_smoke']}", "", "# Summary", "",
             "| Volume | Curriculum rows | Sections (published) | READY | FALLBACK | BLOCKED | Coverage | Excluded |",
             "|---|---:|---:|---:|---:|---:|---:|---|"]
    for vol in VOLUMES:
        v = s[vol]
        excl = ", ".join(f"{k}={n}" for k, n in sorted(v["excluded"].items()))
        lines.append(f"| {vol} | {v['curriculum_rows']} | {v['sections']} | {v['READY']} | {v['FALLBACK']} | "
                     f"{v['BLOCKED']} | {v['coverage_pct']}% | {excl} |")
    o = s["overall"]
    lines += ["", f"overall: published sections={o['published_sections']}, rotation-ready sections="
                  f"{o['rotation_ready_sections']}, coverage={o['coverage_pct']}%", ""]

    lines += ["# Exceptions", "", "| skill_id | section | category | reason | severity | recommended action |",
              "|---|---|---|---|---|---|"]
    for e in sorted(report["exceptions"], key=lambda e: (e["severity"] == "info", e["severity"], e["skill_id"])):
        reason = str(e["reason"]).replace("|", "\\|")
        lines.append(f"| {e['skill_id']} | {e['section']} | {e['category']} | {reason} | {e['severity']} | {e['action']} |")

    d = report["type_distribution"]
    lines += ["", "# Type distribution", "",
              f"min={d['min']} max={d['max']} median={d['median']} sections_with_1_type={d['sections_with_1_type']} "
              f"sections_with_>=7_types={d['sections_with_ge_7_types']} multi_candidate_sections={d['multi_candidate_sections']}",
              "", f"histogram (types -> sections): {d['histogram']}", "",
              "| Volume | Chapter | Section | skill_id | status | components | unique types | candidates per type |",
              "|---|---|---|---|---|---:|---:|---|"]
    for sec in report["sections"]:
        if sec["kind"] != "published":
            continue
        cand = ", ".join(str(len(v)) for v in sec["type_candidates"].values())
        lines.append(f"| {sec['volume']} | {sec['chapter']} | {sec['section']} | {sec['skill_id']} | {sec['status']} | "
                     f"{sec['components']} | {sec['unique_types']} | {cand} |")

    lines += ["", "# Progression", ""]
    for ch in report["progression"]["chapters"]:
        seq = " -> ".join(x.split("_", 1)[-1] for x in ch["ready_sequence"]) or "(no READY section)"
        skipped = ", ".join(f"{x['skill_id']}({x['reason']})" for x in ch["skipped_middle"])
        lines.append(f"- {ch['volume']} {ch['chapter']}: {seq} -> chapter_completed"
                     + (f"  | skipped: {skipped}" if skipped else ""))
    a = report["automated_validation"]
    lines += ["", "# Automated validation", "",
              f"READY sections checked: {a['ready_checked']}  type pools built: {a['pools_built']}  "
              f"scheduler failures: {a['scheduler_failures']}  generated: {a['generated']}  "
              f"generator failures: {a['generator_failures']}  undeliverable types: {a['undeliverable_types']}  "
              f"self-grade failures: {a['self_grade_failures']}  unanswerable types: {a['unanswerable_types']}  "
              f"legacy checked: {a['legacy_checked']}  legacy failures: {a['legacy_failures']}", "",
              "Generator smoke mirrors get_next_question: up to 5 seeds per candidate, session normalization, "
              "delivery gate, then the payload's own correct answer is graded by the formal grader.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-smoke", action="store_true", help="skip generator smoke")
    parser.add_argument("--db", default=None)
    args = parser.parse_args(argv)
    report = run_audit(smoke=not args.no_smoke, db_path=_db_path(args.db))
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(report), encoding="utf-8")
    s = report["summary"]
    for vol in VOLUMES:
        v = s[vol]
        print(f"{vol}: sections={v['sections']} READY={v['READY']} FALLBACK={v['FALLBACK']} "
              f"BLOCKED={v['BLOCKED']} coverage={v['coverage_pct']}%")
    print("overall:", s["overall"])
    print("validation:", report["automated_validation"])
    print("exceptions:", collections.Counter(e["severity"] for e in report["exceptions"]))
    print("elapsed:", report["elapsed_sec"], "s ->", REPORT_JSON.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
