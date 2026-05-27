from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_closed_loop"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        f"# Web Runtime Audit: {payload.get('skill_id', '')}",
        "",
        f"- status: {payload.get('status', '')}",
        f"- samples: {payload.get('samples', 0)}",
        f"- expected_problem_types: {payload.get('expected_problem_types', [])}",
        f"- observed_problem_types: {payload.get('observed_problem_types', [])}",
        f"- missing_problem_types: {payload.get('missing_problem_types', [])}",
        f"- route_sources: {payload.get('route_sources', {})}",
        f"- wrapper_loaded_count: {payload.get('wrapper_loaded_count', 0)}",
        f"- db_fallback_count: {payload.get('db_fallback_count', 0)}",
        f"- legacy_count: {payload.get('legacy_count', 0)}",
        f"- blocking_reasons: {payload.get('blocking_reasons', [])}",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            "Gencode Web Runtime 稽核摘要",
            "============================================================",
            f"skill_id: {payload.get('skill_id', '')}",
            f"samples: {payload.get('samples', 0)}",
            f"status: {payload.get('status', '')}",
            f"expected_problem_types: {payload.get('expected_problem_types', [])}",
            f"observed_problem_types: {payload.get('observed_problem_types', [])}",
            f"distribution_counts: {payload.get('distribution_counts', {})}",
            f"missing_problem_types: {payload.get('missing_problem_types', [])}",
            f"route_sources: {payload.get('route_sources', {})}",
            f"wrapper_loaded_count: {payload.get('wrapper_loaded_count', 0)}",
            f"db_fallback_count: {payload.get('db_fallback_count', 0)}",
            f"legacy_count: {payload.get('legacy_count', 0)}",
            f"blocking_reasons: {payload.get('blocking_reasons', [])}",
            "============================================================",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    skill_id = str(args.skill_id).strip()
    samples = max(1, int(args.samples))

    phase2 = _read_json(REPORT_DIR / f"{skill_id}_phase2_build.json")
    expected_problem_types = sorted(set(phase2.get("verified_problem_types") or []))

    from app import create_app
    from models import User

    app = create_app()
    observed_counts: Counter[str] = Counter()
    route_sources: Counter[str] = Counter()
    answer_type_counts: Counter[str] = Counter()
    previews: list[dict[str, Any]] = []
    wrapper_loaded_count = 0
    db_fallback_count = 0
    legacy_count = 0
    choice_question_count = 0
    missing_problem_type_id_count = 0
    blocking_reasons: list[str] = []

    with app.app_context():
        user = User.query.order_by(User.id.asc()).first()
        if not user:
            payload = {
                "skill_id": skill_id,
                "samples": samples,
                "status": "FAIL",
                "blocking_reasons": ["no_test_user_for_login_required_route"],
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else _summary(payload))
            return
        user_id = str(user.id)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["_user_id"] = user_id
            sess["_fresh"] = True

        for _ in range(samples):
            resp = client.get(f"/get_next_question?skill={skill_id}&level=1")
            if resp.status_code != 200:
                blocking_reasons.append(f"web_runtime_http_{resp.status_code}")
                continue
            data = resp.get_json(silent=True) or {}
            pt = str(data.get("problem_type_id") or "").strip()
            if not pt:
                missing_problem_type_id_count += 1
            else:
                observed_counts[pt] += 1
            source = str(data.get("route_source") or data.get("source") or data.get("question_source") or "unknown").strip()
            route_sources[source] += 1
            if source == "gencode_wrapper":
                wrapper_loaded_count += 1
            elif source == "db_fallback":
                db_fallback_count += 1
            elif source == "legacy":
                legacy_count += 1
            answer_type = str(data.get("answer_type") or "").strip()
            if answer_type:
                answer_type_counts[answer_type] += 1
            if data.get("choices"):
                choice_question_count += 1
            if len(previews) < 10:
                previews.append(
                    {
                        "problem_type_id": pt,
                        "route_source": source,
                        "answer_type": answer_type,
                        "has_choices": bool(data.get("choices")),
                        "question_text_preview": str(data.get("new_question_text") or "")[:120],
                    }
                )

    observed_problem_types = sorted(observed_counts.keys())
    missing_problem_types = sorted(set(expected_problem_types) - set(observed_problem_types))
    unexpected_problem_types = sorted(set(observed_problem_types) - set(expected_problem_types))

    if missing_problem_types:
        blocking_reasons.append("web_runtime_distribution_missing_verified_problem_types")
    if wrapper_loaded_count == 0:
        blocking_reasons.append("web_runtime_not_using_gencode_wrapper")
    if missing_problem_type_id_count > 0:
        blocking_reasons.append("web_runtime_missing_problem_type_id")

    status = "PASS" if not blocking_reasons else "FAIL"
    payload = {
        "skill_id": skill_id,
        "samples": samples,
        "expected_problem_types": expected_problem_types,
        "observed_problem_types": observed_problem_types,
        "distribution_counts": dict(observed_counts),
        "missing_problem_types": missing_problem_types,
        "unexpected_problem_types": unexpected_problem_types,
        "route_sources": dict(route_sources),
        "wrapper_loaded_count": wrapper_loaded_count,
        "db_fallback_count": db_fallback_count,
        "legacy_count": legacy_count,
        "choice_question_count": choice_question_count,
        "missing_problem_type_id_count": missing_problem_type_id_count,
        "answer_type_counts": dict(answer_type_counts),
        "sample_previews": previews,
        "status": status,
        "blocking_reasons": sorted(set(blocking_reasons)),
    }

    out_json = REPORT_DIR / f"{skill_id}_web_runtime_audit.json"
    out_md = REPORT_DIR / f"{skill_id}_web_runtime_audit.md"
    _write_json(out_json, payload)
    _write_md(out_md, payload)
    print(json.dumps(payload, ensure_ascii=True) if args.json else _summary(payload))


if __name__ == "__main__":
    main()
