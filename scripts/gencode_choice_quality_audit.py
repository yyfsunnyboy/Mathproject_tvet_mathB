from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REPORT_DIR = PROJECT_ROOT / "reports" / "gencode_quality"
VALID_LABELS = {"A", "B", "C", "D"}


def _iter_skill_modules(skill_id: str | None) -> list[tuple[str, Path]]:
    skill_dir = PROJECT_ROOT / "skills"
    if not skill_dir.exists():
        return []
    out: list[tuple[str, Path]] = []
    if skill_id:
        p = skill_dir / f"{skill_id}.py"
        if p.exists():
            out.append((f"skills.{skill_id}", p))
        return out
    for p in sorted(skill_dir.glob("*.py")):
        if p.name.startswith("_"):
            continue
        out.append((f"skills.{p.stem}", p))
    return out


def _iter_candidate_modules() -> list[tuple[str, Path]]:
    base = PROJECT_ROOT / "generated_candidates"
    if not base.exists():
        return []
    out: list[tuple[str, Path]] = []
    for p in sorted(base.rglob("candidate_v*.py")):
        out.append((str(p.relative_to(PROJECT_ROOT)).replace("\\", "/"), p))
    return out


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if not spec or not spec.loader:
        raise RuntimeError("import_spec_invalid")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _is_choice_payload(q: dict[str, Any]) -> bool:
    if not isinstance(q, dict):
        return False
    eq = str(((q.get("answer_contract") or {}).get("equivalence_type") or "")).strip()
    ans_type = str(q.get("answer_type", "")).strip()
    return eq == "choice_label" or ans_type in {"choice", "choice_label"}


def _evaluate_choice_label_distribution(choice_question_count: int, label_counts: dict[str, int]) -> dict[str, Any]:
    warnings: list[str] = []
    issues: list[str] = []
    fixed_detected = False
    positive_labels = [k for k, v in (label_counts or {}).items() if v > 0]
    unique_label_count = len(positive_labels)
    if choice_question_count < 20:
        warnings.append("insufficient_choice_samples_for_label_distribution")
        return {"fixed_detected": False, "issues": issues, "warnings": warnings}
    if unique_label_count == 1:
        fixed_detected = True
        issues.append("choice_answer_fixed_label_detected")
    if choice_question_count >= 50 and unique_label_count < 2 and "choice_answer_fixed_label_detected" not in issues:
        fixed_detected = True
        issues.append("choice_answer_fixed_label_detected")
    return {"fixed_detected": fixed_detected, "issues": issues, "warnings": warnings}


def _run_choice_audit_on_module(name: str, path: Path, samples: int, filter_skill_id: str | None) -> dict[str, Any]:
    result = {
        "module": name,
        "path": str(path),
        "skill_id": "",
        "choice_question_count": 0,
        "choice_answer_label_counts": {},
        "fixed_label_detected": False,
        "warnings": [],
        "issues": [],
    }
    try:
        mod = _load_module(path, f"audit_{path.stem}_{abs(hash(str(path)))}")
    except Exception as e:
        result["issues"].append(f"import_failed:{e}")
        return result
    gen = getattr(mod, "generate", None)
    chk = getattr(mod, "check", None)
    if not callable(gen):
        result["issues"].append("missing_generate")
        return result

    label_counts: Counter[str] = Counter()
    has_choice = 0
    for i in range(samples):
        try:
            q = gen(level=1, seed=i)
        except Exception as e:
            result["issues"].append(f"generate_failed:{e}")
            break
        if not isinstance(q, dict):
            result["issues"].append("payload_not_dict")
            break
        sid = str(q.get("skill_id", "")).strip()
        if not result["skill_id"]:
            result["skill_id"] = sid
        if filter_skill_id and sid and sid != filter_skill_id:
            continue
        if not _is_choice_payload(q):
            continue
        has_choice += 1
        choices = list(q.get("choices", []) or [])
        if len(choices) != 4 or len(set(choices)) != len(choices):
            result["issues"].append("duplicate_choice_options")
        label = str(q.get("answer", "")).strip().upper()
        if label not in VALID_LABELS:
            result["issues"].append("invalid_choice_answer_label")
            continue
        label_counts[label] += 1
        idx = ord(label) - ord("A")
        if idx >= len(choices):
            result["issues"].append("choice_correct_answer_not_in_choices")
        if callable(chk):
            try:
                ok = chk(label, q.get("correct_answer"), choices)
                if isinstance(ok, dict):
                    ok = ok.get("correct")
                if not bool(ok):
                    result["issues"].append("check_label_failed")
            except TypeError:
                try:
                    ok = chk(label, q.get("correct_answer"), current_question=q)
                    if isinstance(ok, dict):
                        ok = ok.get("correct")
                    if not bool(ok):
                        result["issues"].append("check_label_failed")
                except Exception:
                    result["issues"].append("check_execution_failed")
            except Exception:
                result["issues"].append("check_execution_failed")

    result["choice_question_count"] = has_choice
    result["choice_answer_label_counts"] = dict(label_counts)
    dist_eval = _evaluate_choice_label_distribution(has_choice, dict(label_counts))
    result["fixed_label_detected"] = bool(dist_eval["fixed_detected"])
    result["issues"].extend(dist_eval["issues"])
    result["warnings"].extend(dist_eval["warnings"])
    return result


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Choice Quality Audit",
        "",
        f"- status: {payload.get('status', '')}",
        f"- samples: {payload.get('samples', 0)}",
        f"- audited_modules: {payload.get('audited_modules', 0)}",
        f"- modules_with_choice_questions: {payload.get('modules_with_choice_questions', 0)}",
        f"- blocking_reasons: {payload.get('blocking_reasons', [])}",
        "",
    ]
    for item in payload.get("results", []):
        lines.append(f"## {item.get('module')}")
        lines.append(f"- choice_question_count: {item.get('choice_question_count', 0)}")
        lines.append(f"- choice_answer_label_counts: {item.get('choice_answer_label_counts', {})}")
        lines.append(f"- fixed_label_detected: {item.get('fixed_label_detected', False)}")
        lines.append(f"- warnings: {item.get('warnings', [])}")
        lines.append(f"- issues: {item.get('issues', [])}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _summary(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "============================================================",
            "Gencode Choice 品質稽核摘要",
            "============================================================",
            f"status: {payload.get('status', '')}",
            f"samples: {payload.get('samples', 0)}",
            f"audited_modules: {payload.get('audited_modules', 0)}",
            f"modules_with_choice_questions: {payload.get('modules_with_choice_questions', 0)}",
            f"blocking_reasons: {payload.get('blocking_reasons', [])}",
            "============================================================",
        ]
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--samples", type=int, default=100)
    p.add_argument("--skill-id", default="")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    samples = max(1, int(args.samples))
    skill_id = args.skill_id.strip() or None

    targets = _iter_skill_modules(skill_id) + _iter_candidate_modules()
    results: list[dict[str, Any]] = []
    for name, path in targets:
        r = _run_choice_audit_on_module(name, path, samples, skill_id)
        if skill_id and r.get("skill_id") and r.get("skill_id") != skill_id:
            continue
        if r.get("choice_question_count", 0) <= 0 and not r.get("issues"):
            continue
        results.append(r)

    blocking = sorted(
        set(
            issue
            for r in results
            for issue in (r.get("issues") or [])
            if issue
            and any(
                key in issue
                for key in [
                    "choice_answer_fixed_label_detected",
                    "invalid_choice_answer_label",
                    "duplicate_choice_options",
                    "choice_correct_answer_not_in_choices",
                    "check_label_failed",
                    "check_execution_failed",
                ]
            )
        )
    )
    status = "PASS" if not blocking else "FAIL"
    payload = {
        "skill_id": skill_id or "",
        "samples": samples,
        "audited_modules": len(targets),
        "modules_with_choice_questions": len([r for r in results if r.get("choice_question_count", 0) > 0]),
        "status": status,
        "blocking_reasons": blocking,
        "warnings": sorted(set(w for r in results for w in (r.get("warnings") or []) if w)),
        "results": results,
    }

    if skill_id:
        out_json = REPORT_DIR / f"{skill_id}_choice_quality_audit.json"
        out_md = REPORT_DIR / f"{skill_id}_choice_quality_audit.md"
    else:
        out_json = REPORT_DIR / "choice_quality_audit.json"
        out_md = REPORT_DIR / "choice_quality_audit.md"
    _write_json(out_json, payload)
    _write_md(out_md, payload)
    print(json.dumps(payload, ensure_ascii=True) if args.json else _summary(payload))


if __name__ == "__main__":
    main()
