"""Low-cost B1–B4 runtime quality scan (generation + real /check_answer routing).

The scan never touches the real database: it points the app at a throwaway
SQLite file and replaces every persistence hook of the check_answer view with a
no-op, so verdicts come from the production grading branches without writes.

Usage:
    python scripts/audit_b1_b4_runtime_quality_scan.py --seeds 5
    python scripts/audit_b1_b4_runtime_quality_scan.py --seeds 30 --only vh_數學B1_AbsoluteValueInequality:src_4400
"""
from __future__ import annotations

import argparse
import copy
import importlib
import inspect
import json
import os
import re
import sys
import tempfile
import time
import traceback
import warnings
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
_SCAN_DB = Path(tempfile.gettempdir()) / "mathproject_quality_scan.db"
os.environ["MATHPROJECT_DATABASE_URI"] = "sqlite:///" + str(_SCAN_DB).replace("\\", "/")
warnings.filterwarnings("ignore")

import logging  # noqa: E402

logging.disable(logging.CRITICAL)

BOOKS = ("B1", "B2", "B3", "B4")
SEED_BASE = 1009


def _load_app():
    import contextlib
    import io

    with contextlib.redirect_stdout(io.StringIO()):
        from app import app as flask_app
    import core.routes.practice as practice

    def _emit(question_uid, skill_id, result, *, record_progress=True, attempt_context=None, skip_practice_attempt=False):
        out = dict(result)
        ctx = attempt_context if isinstance(attempt_context, dict) else {}
        current_question = ctx.get("current_question")
        if isinstance(current_question, dict):
            from core.gencode.answer_grading import attach_correct_answer_feedback

            out = attach_correct_answer_feedback(out, current_question)
        return out

    practice._emit_check_result = _emit
    practice._record_compact_practice_progress = lambda *a, **k: None
    practice.persist_b4_chap2_deterministic_answer_event = lambda *a, **k: None
    practice._practice_type_rotation_apply_verdict = lambda *a, **k: None
    practice.mark_question_answered = lambda *a, **k: None
    return flask_app, practice


def _skill_ids(books: tuple[str, ...]) -> list[str]:
    out = []
    for path in sorted((ROOT / "skills").glob("vh_*.py")):
        stem = path.stem
        if any(stem.startswith(f"vh_數學{book}_") for book in books):
            out.append(stem)
    return out


def _accepts(fn: Any, name: str) -> bool:
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False
    return name in params or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


def _spec_components(module: Any) -> list[str]:
    rows = getattr(module, "GENERATOR_SPECS", None) or []
    out = []
    for row in rows:
        if isinstance(row, dict) and row.get("component_id"):
            readiness = str(row.get("generator_readiness") or "runtime_ready")
            if readiness == "runtime_ready" or "readiness" not in readiness:
                out.append(str(row["component_id"]))
    return list(dict.fromkeys(out))


def _session_payload(practice: Any, raw: dict[str, Any], skill_id: str) -> dict[str, Any]:
    data = practice._canonicalize_route_payload(copy.deepcopy(raw))
    data.setdefault("skill_id", skill_id)
    data["skill"] = skill_id
    return practice._prepare_runtime_session_payload(data, skill_id, [])


def _grade(app: Any, practice: Any, current: dict[str, Any], skill_id: str, answer: Any) -> dict[str, Any]:
    practice.resolve_check_context = lambda body: (copy.deepcopy(current), None)
    body: dict[str, Any] = {"skill_id": skill_id, "question_uid": "quality-scan"}
    if isinstance(answer, (dict, list)):
        body["answers"] = answer
    else:
        body["answer"] = answer
    with app.test_request_context("/check_answer", method="POST", json=body):
        rv = practice.check_answer()
    if isinstance(rv, tuple):
        rv = rv[0]
    if hasattr(rv, "get_json"):
        rv = rv.get_json(silent=True) or {}
    return rv if isinstance(rv, dict) else {"correct": None, "raw": str(rv)}


def _choice_labels(current: dict[str, Any]) -> list[str]:
    raw = current.get("choices") or current.get("options") or []
    labels = []
    for index, choice in enumerate(raw if isinstance(raw, list) else []):
        label = chr(65 + index)
        if isinstance(choice, dict) and str(choice.get("label") or "").strip():
            label = str(choice["label"]).strip().upper()
        labels.append(label)
    return labels


def _correct_choice_label(practice: Any, current: dict[str, Any]) -> str | None:
    choices = current.get("choices") or current.get("options") or []
    raw = current.get("correct_answer") or current.get("answer")
    label = practice._choice_value_to_label(raw, choices if isinstance(choices, list) else [])
    return str(label) if label else None


_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


def _mutate_scalar(value: Any, *, relational: bool = False) -> str:
    text = str(value)
    if not relational and re.search(r"[a-z]", text) and not re.fullmatch(r"[A-Za-z\u4e00-\u9fff ]+", text):
        return f"({text})+1"
    matches = list(_NUMBER_RE.finditer(text))
    if not matches:
        return "答案錯誤"
    target = matches[-1]
    number = target.group(0)
    bumped = str(int(number) + 1) if number.isdigit() else str(round(float(number) + 1, 6))
    return text[: target.start()] + bumped + text[target.end():]


def _canonical(current: dict[str, Any]) -> Any:
    ac = current.get("answer_contract") if isinstance(current.get("answer_contract"), dict) else {}
    value = ac.get("canonical_answer")
    if value is None:
        value = current.get("correct_answer", current.get("answer"))
    return value


def _inequality_variants(current: dict[str, Any]) -> list[str]:
    from core.checkers.inequality_solution_checker import parse_real_solution_set
    from core.gencode.question_quality_gate import _solution_variable, solution_set_to_natural_text
    from sympy import Interval, Union

    from core.gencode.question_quality_gate import is_inequality_solution_payload

    canonical = _canonical(current)
    if not isinstance(canonical, str) or not re.search(r"<|>|≤|≥|\\le|\\ge|[\[\(].*,.*[\]\)]", canonical):
        return []
    if not is_inequality_solution_payload(current):
        return []
    solution = parse_real_solution_set(canonical)
    if solution is None:
        return []
    var = _solution_variable(current)
    natural = solution_set_to_natural_text(solution, var)
    if not natural:
        return []
    variants = [natural, natural.replace(" ", "")]
    pieces = natural.split(" 或 ")
    if len(pieces) > 1:
        variants.append(",".join(piece.replace(" ", "") for piece in pieces))
        variants.append(",".join(piece.replace(" ", "") for piece in reversed(pieces)))
        variants.append(" 或 ".join(reversed(pieces)))
    intervals = list(solution.args) if isinstance(solution, Union) else [solution]
    if all(isinstance(item, Interval) for item in intervals):
        def _fmt(iv: Any) -> str:
            lo = "-inf" if iv.start.is_infinite else str(iv.start)
            hi = "inf" if iv.end.is_infinite else str(iv.end)
            lb = "(" if iv.left_open or iv.start.is_infinite else "["
            rb = ")" if iv.right_open or iv.end.is_infinite else "]"
            return f"{lb}{lo},{hi}{rb}"
        variants.append(" U ".join(_fmt(iv) for iv in intervals))
    return list(dict.fromkeys(variants))


def _multipart_answer(current: dict[str, Any]) -> dict[str, Any] | None:
    """Student-shaped multi-input submission built from the answer contract."""
    canonical = _canonical(current)
    ac = current.get("answer_contract") if isinstance(current.get("answer_contract"), dict) else {}
    parts = ac.get("parts") or ac.get("field_specs") or []
    if isinstance(canonical, dict) and not parts:
        return {str(k): v for k, v in canonical.items()}
    if not isinstance(parts, list) or not parts:
        return {str(k): v for k, v in canonical.items()} if isinstance(canonical, dict) else None
    out: dict[str, Any] = {}
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            return None
        key = str(part.get("key") or part.get("field_key") or index)
        if isinstance(canonical, dict) and key in canonical:
            value = canonical[key]
        elif part.get("expected_answer") is not None:
            value = part.get("expected_answer")
        elif part.get("canonical_answer") is not None:
            value = part.get("canonical_answer")
        elif isinstance(canonical, (list, tuple)) and index < len(canonical):
            value = canonical[index]
        else:
            return None
        out[key] = value
    return out


def _is_drawing(current: dict[str, Any]) -> bool:
    ac = current.get("answer_contract") if isinstance(current.get("answer_contract"), dict) else {}
    blob = " ".join(str(x) for x in (ac.get("answer_type"), ac.get("checker"), current.get("checker"), current.get("answer_type")))
    return "drawing" in blob


def _check_mode(current: dict[str, Any]) -> str:
    return str(current.get("check_mode") or current.get("grading_mode") or "").strip().lower()


def audit_sample(app: Any, practice: Any, module: Any, skill_id: str, component: str | None, problem_type: str | None, seed: int) -> dict[str, Any]:
    from core.gencode.question_delivery_contract import question_delivery_errors
    from core.gencode.question_quality_gate import question_quality_errors

    rec: dict[str, Any] = {"skill_id": skill_id, "component": component, "problem_type": problem_type, "seed": seed, "issues": []}
    kwargs: dict[str, Any] = {"level": 1, "seed": seed}
    if component:
        kwargs["component_id"] = component
    if problem_type and _accepts(module.generate, "problem_type_id"):
        kwargs["problem_type_id"] = problem_type
    try:
        raw = module.generate(**kwargs)
    except Exception as exc:
        rec["issues"].append(f"generate_exception:{type(exc).__name__}:{str(exc)[:160]}")
        return rec
    if not isinstance(raw, dict):
        rec["issues"].append("generate_not_dict")
        return rec
    current = _session_payload(practice, raw, skill_id)
    rec["problem_type"] = str(current.get("problem_type_id") or problem_type or "")
    rec["component"] = str(current.get("component_id") or component or "")
    rec["question"] = str(current.get("question_text") or "")[:400]
    rec["answer"] = _canonical(current) if not isinstance(_canonical(current), (dict, list)) else _canonical(current)
    rec["display_answer"] = current.get("display_answer")
    rec["visual"] = bool(any(current.get(k) for k in ("visual_spec", "diagram_spec", "visual", "diagram", "image_base64", "table", "chart")))
    rec["multipart"] = isinstance(_canonical(current), dict)

    if not str(current.get("question_text") or "").strip():
        rec["issues"].append("question_empty")
    canonical = _canonical(current)
    if canonical in (None, "", [], {}):
        rec["issues"].append("answer_empty")
    for err in question_delivery_errors(current):
        rec["issues"].append(f"delivery:{err}")
    for err in question_quality_errors(current):
        rec["issues"].append(f"gate:{err}")

    choices = current.get("choices") or current.get("options") or []
    is_choice = bool(choices) or str(current.get("presentation_mode") or "") == "single_choice"
    if is_choice and isinstance(choices, list) and len(choices) != 4:
        rec["issues"].append(f"choice_count:{len(choices)}")

    mode = _check_mode(current)
    if _is_drawing(current) or mode in {"ai_judged_free_response", "visual_ai_checked", "handwriting_ai_checked", "review_mode"}:
        rec["self_check"] = "not_auto_checkable"
        return rec
    if canonical in (None, "", [], {}):
        return rec

    try:
        if is_choice:
            label = _correct_choice_label(practice, current)
            if not label:
                rec["issues"].append("choice_correct_label_unresolved")
                return rec
            good = _grade(app, practice, current, skill_id, label)
            wrong_label = next((x for x in _choice_labels(current) if x != label.upper()), None)
            bad = _grade(app, practice, current, skill_id, wrong_label) if wrong_label else {"correct": False}
        elif _multipart_answer(current) is not None:
            answers = _multipart_answer(current)
            good = _grade(app, practice, current, skill_id, answers)
            mutated = dict(answers)
            first = next(iter(mutated))
            mutated[first] = _mutate_scalar(mutated[first])
            bad = _grade(app, practice, current, skill_id, mutated)
        else:
            from core.checkers.math_input_normalization import latex_to_plain
            from core.gencode.question_quality_gate import is_inequality_solution_payload

            relational = is_inequality_solution_payload(current)
            good = _grade(app, practice, current, skill_id, str(canonical))
            bad = _grade(app, practice, current, skill_id, _mutate_scalar(canonical, relational=relational))
            display = current.get("display_answer")
            if isinstance(display, (str, int, float)) and str(display).strip() and str(display) != str(canonical):
                typed = latex_to_plain(str(display))
                shown = _grade(app, practice, current, skill_id, typed)
                if shown.get("correct") is not True:
                    rec["issues"].append(f"display_answer_rejected_by_checker:{str(display)[:80]}")
            for variant in _inequality_variants(current):
                verdict = _grade(app, practice, current, skill_id, variant)
                if verdict.get("correct") is not True:
                    rec["issues"].append(f"inequality_equivalent_rejected:{variant}")
            wrong_feedback = bad.get("correct_answer_display") or {}
            shown_value = str(wrong_feedback.get("value") or "") if isinstance(wrong_feedback, dict) else ""
            rec["feedback_display"] = shown_value or bad.get("result")
    except Exception as exc:
        rec["issues"].append(f"grading_exception:{type(exc).__name__}:{str(exc)[:160]}")
        rec["trace"] = traceback.format_exc()[-600:]
        return rec

    if good.get("correct") is not True:
        rec["issues"].append(f"authoritative_answer_fails_checker:{good.get('status')}:{str(good.get('result'))[:80]}")
    if bad.get("correct") is True:
        rec["issues"].append("obviously_wrong_answer_accepted")
    if not is_choice and not isinstance(canonical, dict):
        shown_value = str(rec.get("feedback_display") or "")
        if shown_value:
            from core.gencode.question_quality_gate import _INTERVAL_NOTATION_RE, natural_inequality_display

            if _INTERVAL_NOTATION_RE.search(shown_value) and natural_inequality_display(current):
                rec["issues"].append(f"feedback_shows_internal_interval_form:{shown_value[:60]}")
    return rec


def _components_for(module: Any, skill_id: str, seeds: int) -> list[tuple[str | None, str | None, list[int]]]:
    comps = _spec_components(module)
    seed_list = [SEED_BASE + 7 * i for i in range(seeds)]
    if comps:
        return [(cid, None, seed_list) for cid in comps]
    discovered: dict[str, list[int]] = {}
    for probe in range(1, 61):
        try:
            payload = module.generate(level=1, seed=probe)
        except Exception:
            continue
        pt = str((payload or {}).get("problem_type_id") or "")
        discovered.setdefault(pt, []).append(probe)
    out = []
    for pt, probes in discovered.items():
        if _accepts(module.generate, "problem_type_id"):
            out.append((None, pt, seed_list))
        else:
            out.append((None, pt, probes[:seeds]))
    return out


def classify(records: list[dict[str, Any]]) -> str:
    issues = [issue for rec in records for issue in rec["issues"]]
    if not records:
        return "BLOCKED"
    if all(any(i.startswith("generate_exception") for i in rec["issues"]) for rec in records):
        return "BLOCKED"
    if not issues:
        return "PASS"
    if any(i.startswith(("inequality_equivalent_rejected", "display_answer_rejected", "gate:display_answer", "feedback_shows_internal")) for i in issues):
        return "NEEDS_SHARED_REPAIR"
    return "NEEDS_GENERATOR_REPAIR"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--books", default=",".join(BOOKS))
    parser.add_argument("--only", default="", help="comma list of skill or skill:component")
    parser.add_argument("--out", default=str(ROOT / "tmp" / "quality_scan" / "scan_results.json"))
    args = parser.parse_args()

    app, practice = _load_app()
    books = tuple(b.strip() for b in args.books.split(",") if b.strip())
    only = [x.strip() for x in args.only.split(",") if x.strip()]
    results: dict[str, Any] = {}
    started = time.time()
    skills = _skill_ids(books)
    if only:
        skills = [s for s in skills if any(o.split(":")[0] == s for o in only)]
    for n, skill_id in enumerate(skills, 1):
        try:
            module = importlib.import_module(f"skills.{skill_id}")
        except Exception as exc:
            results[skill_id] = {"_import_error": f"{type(exc).__name__}:{exc}"}
            continue
        comp_rows = _components_for(module, skill_id, args.seeds)
        skill_out: dict[str, Any] = {}
        for cid, pt, seed_list in comp_rows:
            key = cid or pt or "default"
            if only and not any(o == skill_id or o == f"{skill_id}:{key}" for o in only):
                continue
            recs = []
            with app.app_context():
                for seed in seed_list:
                    recs.append(audit_sample(app, practice, module, skill_id, cid, pt, seed))
            skill_out[key] = {"status": classify(recs), "samples": recs}
        results[skill_id] = skill_out
        bad = sum(1 for v in skill_out.values() if v["status"] != "PASS")
        print(f"[{n}/{len(skills)}] {skill_id} components={len(skill_out)} non_pass={bad} t={time.time()-started:.0f}s", flush=True)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
