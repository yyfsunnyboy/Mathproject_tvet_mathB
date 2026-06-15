from __future__ import annotations

import argparse
import hashlib
import importlib
import io
import json
import re
import sys
from collections import Counter
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any
from urllib.parse import quote


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"
PLACEHOLDER_RE = re.compile(r"\{\{[^{}]+\}\}|\{[^{}]+\}|TODO|\bNone\b")
STRING_FALLBACK_CHECKERS = {"text_short_checker", "text_checker", "string_checker"}
DEFAULT_DUPLICATE_THRESHOLD = 0.35


def _json_default(value: Any) -> str:
    return str(value)


def _safe_bool(value: Any) -> bool:
    return bool(value) is True


def _text(value: Any) -> str:
    return str(value if value is not None else "").strip()


def _answer_text(payload: dict[str, Any]) -> str:
    if payload.get("correct_answer") is not None:
        return _text(payload.get("correct_answer"))
    return _text(payload.get("answer"))


def _question_text(payload: dict[str, Any]) -> str:
    return _text(payload.get("question_text") or payload.get("new_question_text") or payload.get("question"))


def _question_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _has_generator_key(payload: dict[str, Any]) -> bool:
    for key in ("generator_key", "selected_generator_key"):
        if _text(payload.get(key)):
            return True
    meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    return bool(_text(meta.get("generator_key") or meta.get("selected_generator_key")))


def _wrong_answer_for(payload: dict[str, Any]) -> str:
    checker = _text(payload.get("checker") or payload.get("checker_type")).lower()
    answer_type = _text(payload.get("answer_type")).lower()
    if "choice" in checker or "choice" in answer_type:
        choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
        labels = {"A", "B", "C", "D", "E", "F"}
        answer = _answer_text(payload).strip().upper()
        for label in labels:
            if label != answer and (not choices or ord(label) - ord("A") < len(choices)):
                return label
    return "__WRONG_ANSWER_FOR_AUDIT__"


@contextmanager
def _suppress_db_writes():
    """Patch known practice write paths to no-op inside this audit process."""
    import core.routes.practice as practice
    from models import db

    originals: list[tuple[Any, str, Any]] = []

    def patch(obj: Any, name: str, value: Any) -> None:
        originals.append((obj, name, getattr(obj, name)))
        setattr(obj, name, value)

    def noop(*args: Any, **kwargs: Any) -> None:
        return None

    for name in ("update_progress", "update_node_competencies"):
        if hasattr(practice, name):
            patch(practice, name, noop)
    for name in ("update_student_ability", "apply_error_penalty"):
        if hasattr(practice, name):
            patch(practice, name, noop)
    if hasattr(practice, "diagnose_error"):
        patch(practice, "diagnose_error", lambda *args, **kwargs: {"error_type": "audit_noop"})

    patch(db.session, "add", noop)
    patch(db.session, "commit", noop)
    patch(db.session, "rollback", noop)
    try:
        yield
    finally:
        for obj, name, original in reversed(originals):
            setattr(obj, name, original)


def _load_existing_user_id(app: Any) -> str:
    from models import User

    with app.app_context():
        user = User.query.order_by(User.id.asc()).first()
        return str(user.id) if user else ""


def _formal_skill_check(skill_id: str, payload: dict[str, Any]) -> Any | None:
    formal_path = PROJECT_ROOT / "skills" / f"{skill_id}.py"
    flags = payload["flags"]
    payload["formal_skill_path"] = str(formal_path)
    flags["formal_skill_exists"] = formal_path.exists()
    if not formal_path.exists():
        payload["blockers"].append("formal_skill_file_missing")
        return None
    try:
        mod = importlib.import_module(f"skills.{skill_id}")
        flags["get_skill_import_passed"] = True
    except Exception as exc:
        payload["blockers"].append("formal_skill_import_failed")
        payload["warnings"].append(f"formal_skill_import_error:{type(exc).__name__}:{exc}")
        return None
    flags["generate_exists"] = callable(getattr(mod, "generate", None))
    flags["check_exists"] = callable(getattr(mod, "check", None))
    if not flags["generate_exists"]:
        payload["blockers"].append("generate_missing_or_not_callable")
    if not flags["check_exists"]:
        payload["blockers"].append("check_missing_or_not_callable")
    return mod


def _record_get_payload(report: dict[str, Any], data: dict[str, Any], *, seed: int, phase: str) -> list[str]:
    blockers: list[str] = []
    quality = report["quality"]
    distribution = report["distribution"]
    route = report["route"]

    q_text = _question_text(data)
    answer = _answer_text(data)
    pt = _text(data.get("problem_type_id") or data.get("problem_type"))
    checker = _text(data.get("checker") or data.get("checker_type"))
    equivalence = _text(data.get("equivalence") or data.get("equivalence_type"))
    ac = data.get("answer_contract")
    source = _text(data.get("route_source") or data.get("source") or data.get("question_source") or "unknown")

    route["route_sources"][source] = route["route_sources"].get(source, 0) + 1
    if source == "gencode_wrapper":
        route["wrapper_loaded_count"] += 1
    elif source == "legacy":
        route["legacy_count"] += 1
    elif source == "db_fallback":
        route["db_fallback_count"] += 1

    if not q_text:
        quality["empty_question_count"] += 1
        blockers.append("empty_question_text")
    if not answer:
        quality["empty_answer_count"] += 1
        blockers.append("empty_answer")
    if q_text and PLACEHOLDER_RE.search(q_text):
        quality["placeholder_count"] += 1
        blockers.append("placeholder_question_text")
    if not _text(data.get("question_uid")):
        blockers.append("missing_question_uid")
    if not isinstance(ac, dict) or not ac:
        blockers.append("missing_answer_contract")
    if not checker:
        blockers.append("missing_checker")
    if not equivalence:
        blockers.append("missing_equivalence")
    if not pt:
        blockers.append("missing_problem_type_id")
    else:
        distribution["problem_type_counts"][pt] = distribution["problem_type_counts"].get(pt, 0) + 1
    if not _has_generator_key(data):
        quality["generator_key_missing_count"] += 1
    if checker in STRING_FALLBACK_CHECKERS:
        quality["string_fallback_checker_count"] += 1

    report["_question_hashes"].append(_question_hash(q_text) if q_text else "")
    report["samples"].append(
        {
            "phase": phase,
            "seed": seed,
            "http_status": 200,
            "question_uid": _text(data.get("question_uid")),
            "problem_type_id": pt,
            "route_source": source,
            "checker": checker,
            "equivalence": equivalence,
            "has_answer_contract": isinstance(ac, dict) and bool(ac),
            "has_generator_key": _has_generator_key(data),
            "question_hash": _question_hash(q_text) if q_text else "",
            "blockers": blockers,
        }
    )
    return blockers


def _post_check(client: Any, question: dict[str, Any], answer: Any) -> tuple[int, dict[str, Any]]:
    body = {
        "skill_id": _text(question.get("skill_id")),
        "question_uid": _text(question.get("question_uid")),
        "problem_type_id": _text(question.get("problem_type_id") or question.get("problem_type")),
        "answer": answer,
    }
    resp = client.post("/check_answer", json=body)
    return int(resp.status_code), (resp.get_json(silent=True) or {})


def run_audit(skill_id: str, *, samples: int, level: int, write_report: bool = False) -> dict[str, Any]:
    from app import create_app

    samples = max(1, int(samples))
    level = int(level)
    report: dict[str, Any] = {
        "schema_version": "practice_runtime_audit.v1",
        "skill_id": skill_id,
        "formal_skill_path": "",
        "audit_mode": "generated_only",
        "samples_requested": samples,
        "samples_completed": 0,
        "status": "FAIL",
        "can_feed_runtime_ready_gate": False,
        "flags": {
            "formal_skill_exists": False,
            "get_skill_import_passed": False,
            "generate_exists": False,
            "check_exists": False,
            "route_get_next_question_passed": False,
            "route_check_answer_correct_passed": False,
            "route_check_answer_wrong_passed": False,
            "server_side_store_passed": False,
            "stale_session_guard_passed": False,
            "checker_smoke_passed": False,
            "dynamic_sampling_passed": False,
            "equivalence_contract_passed": False,
            "generated_only_passed": False,
        },
        "distribution": {
            "observed_problem_types": [],
            "problem_type_counts": {},
            "duplicate_question_rate": 0.0,
        },
        "quality": {
            "empty_question_count": 0,
            "empty_answer_count": 0,
            "placeholder_count": 0,
            "generator_key_missing_count": 0,
            "string_fallback_checker_count": 0,
        },
        "route": {
            "route_sources": {},
            "wrapper_loaded_count": 0,
            "legacy_count": 0,
            "db_fallback_count": 0,
        },
        "grading": {
            "correct_answer_pass_count": 0,
            "wrong_answer_reject_count": 0,
            "invalid_wrong_answer_count": 0,
            "stale_question_count": 0,
            "duplicate_submission_count": 0,
            "checker_exception_count": 0,
        },
        "blockers": [],
        "warnings": [],
        "samples": [],
        "_question_hashes": [],
    }

    _formal_skill_check(skill_id, report)
    app = create_app()
    app.config.update(TESTING=True)
    user_id = _load_existing_user_id(app)
    if not user_id:
        report["blockers"].append("no_existing_user_for_login_required_route")
        _finalize(report, write_report=write_report)
        return report

    with _suppress_db_writes():
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["_user_id"] = user_id
                sess["_fresh"] = True
                sess["audit_mode"] = "gencode_practice_runtime_audit"

            for i in range(samples):
                correct_seed = i * 2
                wrong_seed = i * 2 + 1
                correct_q = _get_question(client, skill_id, level, correct_seed, report, "correct")
                if correct_q:
                    answer = correct_q.get("correct_answer", correct_q.get("answer"))
                    status, result = _post_check(client, correct_q, answer)
                    _record_check_result(report, result, status=status, expect_correct=True, seed=correct_seed)
                    report["samples_completed"] += 1

                wrong_q = _get_question(client, skill_id, level, wrong_seed, report, "wrong")
                if wrong_q:
                    wrong_answer = _wrong_answer_for(wrong_q)
                    status, result = _post_check(client, wrong_q, wrong_answer)
                    _record_check_result(report, result, status=status, expect_correct=False, seed=wrong_seed)

    _finalize(report, write_report=write_report)
    return report


def _get_question(client: Any, skill_id: str, level: int, seed: int, report: dict[str, Any], phase: str) -> dict[str, Any] | None:
    url = f"/get_next_question?skill={quote(skill_id)}&level={level}&gen_seed={seed}"
    try:
        resp = client.get(url)
    except Exception as exc:
        report["blockers"].append(f"get_next_question_exception:{type(exc).__name__}")
        report["samples"].append({"phase": phase, "seed": seed, "exception": str(exc)})
        return None
    if int(resp.status_code) != 200:
        report["blockers"].append(f"get_next_question_http_{resp.status_code}")
        report["samples"].append({"phase": phase, "seed": seed, "http_status": int(resp.status_code)})
        return None
    data = resp.get_json(silent=True)
    if not isinstance(data, dict):
        report["blockers"].append("get_next_question_json_parse_failed")
        report["samples"].append({"phase": phase, "seed": seed, "http_status": int(resp.status_code), "json_parse_failed": True})
        return None
    if data.get("error"):
        report["blockers"].append("get_next_question_error_response")
    blockers = _record_get_payload(report, data, seed=seed, phase=phase)
    report["blockers"].extend(blockers)
    return data


def _record_check_result(report: dict[str, Any], result: dict[str, Any], *, status: int, expect_correct: bool, seed: int) -> None:
    grading = report["grading"]
    if status >= 500:
        report["blockers"].append(f"check_answer_http_{status}")
    if result.get("stale_question"):
        grading["stale_question_count"] += 1
        report["blockers"].append("stale_question")
    if result.get("duplicate_submission"):
        grading["duplicate_submission_count"] += 1
        report["blockers"].append("duplicate_submission")
    result_text = _text(result.get("result") or result.get("error") or result.get("message")).lower()
    if "exception" in result_text or "traceback" in result_text:
        grading["checker_exception_count"] += 1
        report["blockers"].append("checker_exception")

    correct = _safe_bool(result.get("correct"))
    invalid_wrong = any(token in result_text for token in ("invalid_format", "invalid format", "格式"))
    if expect_correct:
        if correct:
            grading["correct_answer_pass_count"] += 1
        else:
            report["blockers"].append("correct_answer_not_accepted")
    else:
        if correct:
            report["blockers"].append("wrong_answer_accepted")
        else:
            grading["wrong_answer_reject_count"] += 1
            if invalid_wrong:
                grading["invalid_wrong_answer_count"] += 1
                report["warnings"].append("wrong_answer_rejected_as_invalid_format")
    report["samples"].append(
        {
            "phase": "check_correct" if expect_correct else "check_wrong",
            "seed": seed,
            "http_status": status,
            "correct": result.get("correct"),
            "stale_question": bool(result.get("stale_question")),
            "duplicate_submission": bool(result.get("duplicate_submission")),
        }
    )


def _finalize(report: dict[str, Any], *, write_report: bool) -> None:
    hashes = [x for x in report.pop("_question_hashes", []) if x]
    duplicate_count = len(hashes) - len(set(hashes)) if hashes else 0
    duplicate_rate = duplicate_count / len(hashes) if hashes else 0.0
    report["distribution"]["duplicate_question_rate"] = round(duplicate_rate, 4)
    report["distribution"]["observed_problem_types"] = sorted(report["distribution"]["problem_type_counts"].keys())
    if report["quality"]["generator_key_missing_count"] > 0:
        report["warnings"].append("generator_key_missing_from_practice_payload")
    if duplicate_rate > DEFAULT_DUPLICATE_THRESHOLD:
        report["blockers"].append("duplicate_question_rate_too_high")

    flags = report["flags"]
    samples_completed = int(report["samples_completed"])
    requested = int(report["samples_requested"])
    flags["route_get_next_question_passed"] = samples_completed == requested and not any(
        str(b).startswith("get_next_question") for b in report["blockers"]
    )
    flags["route_check_answer_correct_passed"] = report["grading"]["correct_answer_pass_count"] == requested
    flags["route_check_answer_wrong_passed"] = report["grading"]["wrong_answer_reject_count"] == requested
    flags["server_side_store_passed"] = report["grading"]["stale_question_count"] == 0 and samples_completed > 0
    flags["stale_session_guard_passed"] = report["grading"]["stale_question_count"] == 0
    flags["checker_smoke_passed"] = (
        flags["route_check_answer_correct_passed"]
        and flags["route_check_answer_wrong_passed"]
        and report["grading"]["checker_exception_count"] == 0
        and not any(str(b).startswith("check_answer_http_5") for b in report["blockers"])
    )
    flags["dynamic_sampling_passed"] = (
        flags["route_get_next_question_passed"]
        and report["quality"]["empty_question_count"] == 0
        and report["quality"]["empty_answer_count"] == 0
        and report["quality"]["placeholder_count"] == 0
        and duplicate_rate <= DEFAULT_DUPLICATE_THRESHOLD
        and bool(report["distribution"]["observed_problem_types"])
    )
    flags["equivalence_contract_passed"] = (
        flags["route_check_answer_correct_passed"]
        and report["quality"]["string_fallback_checker_count"] >= 0
        and not any(
            b in {"missing_answer_contract", "missing_checker", "missing_equivalence"} for b in report["blockers"]
        )
    )
    flags["generated_only_passed"] = report["route"]["wrapper_loaded_count"] > 0 and report["route"]["legacy_count"] == 0

    gate_flags = (
        "formal_skill_exists",
        "get_skill_import_passed",
        "generate_exists",
        "check_exists",
        "route_get_next_question_passed",
        "route_check_answer_correct_passed",
        "route_check_answer_wrong_passed",
        "server_side_store_passed",
        "stale_session_guard_passed",
        "checker_smoke_passed",
        "dynamic_sampling_passed",
        "equivalence_contract_passed",
        "generated_only_passed",
    )
    report["blockers"] = sorted(set(_text(x) for x in report["blockers"] if _text(x)))
    report["warnings"] = sorted(set(_text(x) for x in report["warnings"] if _text(x)))
    report["status"] = "PASS" if not report["blockers"] and all(flags.get(k) for k in gate_flags) else "FAIL"
    report["can_feed_runtime_ready_gate"] = report["status"] == "PASS"
    if write_report:
        _write_report(report)


def _write_report(report: dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    skill_id = _text(report.get("skill_id"))
    out_json = REPORT_DIR / f"{skill_id}_practice_runtime_audit.json"
    out_md = REPORT_DIR / f"{skill_id}_practice_runtime_audit.md"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=_json_default) + "\n", encoding="utf-8")
    lines = [
        f"# Practice Runtime Audit: {skill_id}",
        "",
        f"- status: {report.get('status')}",
        f"- samples_requested: {report.get('samples_requested')}",
        f"- samples_completed: {report.get('samples_completed')}",
        f"- can_feed_runtime_ready_gate: {str(bool(report.get('can_feed_runtime_ready_gate'))).lower()}",
        f"- blockers: {report.get('blockers', [])}",
        f"- warnings: {report.get('warnings', [])}",
    ]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a published Gencode skill through /practice runtime routes.")
    parser.add_argument("--skill", required=True, help="Published skill id, matching skills/<skill_id>.py")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--write-report", action="store_true", help="Write JSON/MD reports under reports/gencode_closed_loop.")
    parser.add_argument("--json-only", action="store_true", help="Print compact JSON only.")
    args = parser.parse_args()

    if args.json_only:
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            report = run_audit(
                _text(args.skill),
                samples=int(args.samples),
                level=int(args.level),
                write_report=bool(args.write_report),
            )
        print(json.dumps(report, ensure_ascii=False, separators=(",", ":"), default=_json_default))
    else:
        report = run_audit(
            _text(args.skill),
            samples=int(args.samples),
            level=int(args.level),
            write_report=bool(args.write_report),
        )
        print(json.dumps(report, ensure_ascii=False, indent=2, default=_json_default))
    raise SystemExit(0 if report.get("status") == "PASS" else 1)


if __name__ == "__main__":
    main()
