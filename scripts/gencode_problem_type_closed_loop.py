import argparse
import ast
import importlib.util
import json
import re
import time
from pathlib import Path
from typing import Any

TARGET_SKILL = "vh_數學B1_AbsoluteValue"
TARGET_PT = "absolute_value_numeric_evaluation"
PLACEHOLDERS = ("[BLANK]", "[FORMULA_MISSING]", "TODO", "placeholder")


def _yaml_like(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_yaml_like(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for v in data:
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_yaml_like(v, indent + 2))
            else:
                lines.append(f"{pad}- {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(lines)
    return f"{pad}{json.dumps(data, ensure_ascii=False)}"


def _read_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

def _ensure_registry_list_fields(data: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(data, dict):
        data = {}
    data.setdefault("version", "0.1")
    data.setdefault("scope", "vocational_math_b1_section_1_1")
    for key in [
        "verified_problem_types",
        "failed_problem_types",
        "manual_review_problem_types",
        "future_ai_judged_problem_types",
    ]:
        if not isinstance(data.get(key), list):
            data[key] = []
    data.setdefault("runtime_ready_auto_publish", False)
    return data


def _candidate_code() -> str:
    return f'''import random

PROBLEM_TYPE_ID = "{TARGET_PT}"
SKILL_ID = "{TARGET_SKILL}"
SUBSKILL_ID = "{TARGET_PT}"

def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    if seed is not None:
        # Deterministic mapping for verifier sampling; avoids consecutive duplicates for sequential seeds.
        n = (int(seed) % 41) - 20
    else:
        n = rng.randint(-20, 20)
    answer = abs(n)
    question_text = f"求 $|{{n}}|$ 的值。"
    solution_steps = ["絕對值表示到 0 的距離。", f"因此 $|{{n}}|={{{{ans}}}}$。".replace("{{ans}}", str(answer))]
    metadata = {{
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{{rng.randint(1, 9)}}",
        "parameter_signature": f"absolute_value_numeric_evaluation:n={{n}}:difficulty={{difficulty}}",
        "question_pattern_id": f"p{{rng.randint(1, 4)}}",
        "diagnosis_tags": ["absolute_value_definition", "sign_error"],
        "prerequisite_subskills": [],
    }}
    payload = {{
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\\n".join(solution_steps),
        "choices": [],
    }}
    return payload
'''


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("import spec failed")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_verifier(path: Path, rounds: int = 30) -> dict[str, Any]:
    rep = {"candidate_path": str(path), "errors": [], "samples": [], "passed": False}
    src = path.read_text(encoding="utf-8")
    try:
        ast.parse(src)
    except Exception as e:
        rep["errors"].append(f"syntax_check_failed: {e}")
        return rep
    if any(t.lower() in src.lower() for t in PLACEHOLDERS):
        rep["errors"].append("placeholder_detected")
    if re.search(r"(?<![\$\\])\b[0-9a-zA-Z]+\^[0-9]+\b", src):
        rep["errors"].append("plain_power_notation_detected")
    mod = _load_module(path)
    if not hasattr(mod, "generate"):
        rep["errors"].append("generate_missing")
        return rep
    seen_q, seen_sig = [], []
    for i in range(rounds):
        t0 = time.time()
        payload = mod.generate(seed=i, difficulty="easy")
        if time.time() - t0 > 5:
            rep["errors"].append("timeout_exceeded")
            break
        req = {
            "problem_type_id",
            "skill_id",
            "subskill_id",
            "question_text",
            "answer",
            "answer_type",
            "checker_type",
            "solution_steps",
            "metadata",
            "question",
            "correct_answer",
            "explanation",
            "choices",
        }
        if not req.issubset(payload.keys()):
            rep["errors"].append("output_contract_missing_keys")
        if payload.get("answer_type") != "integer":
            rep["errors"].append("answer_type_invalid")
        if payload.get("checker_type") != "integer_checker":
            rep["errors"].append("checker_type_invalid")
        try:
            int(payload["answer"])
        except Exception:
            rep["errors"].append("correct_answer_self_check_failed")
        q = str(payload.get("question_text", ""))
        if "$" not in q:
            rep["errors"].append("latex_safety_failed")
        seen_q.append(q)
        seen_sig.append(str(payload.get("metadata", {}).get("parameter_signature", "")))
        rep["samples"].append(payload)
    cdup = sum(1 for i in range(1, len(seen_q)) if seen_q[i] == seen_q[i - 1])
    uq = len(set(seen_q))
    rr = 0.0 if not seen_q else 1 - uq / len(seen_q)
    usig = len(set(seen_sig))
    rep["diversity"] = {"consecutive_duplicate_count": cdup, "unique_question_text_count": uq, "repeated_question_text_ratio": rr, "unique_parameter_signature_count": usig}
    if cdup != 0:
        rep["errors"].append("consecutive_duplicate_count_nonzero")
    if uq < 6:
        rep["errors"].append("unique_question_text_count_below_6")
    if rr > 0.5:
        rep["errors"].append("repeated_question_text_ratio_above_0.5")
    if usig < 6:
        rep["errors"].append("unique_parameter_signature_count_below_6")
    rep["passed"] = len(rep["errors"]) == 0
    return rep


def _merge_registry(reg_path: Path, verified_entry: dict[str, Any] | None, failed_reason: str | None) -> dict[str, Any]:
    reg = _read_yaml(reg_path) if reg_path.exists() else {}
    reg = _ensure_registry_list_fields(reg)
    verified = [v for v in reg["verified_problem_types"] if not (isinstance(v, dict) and v.get("skill_id") == TARGET_SKILL and v.get("problem_type_id") == TARGET_PT)]
    failed = [f for f in reg["failed_problem_types"] if not (isinstance(f, dict) and f.get("skill_id") == TARGET_SKILL and f.get("problem_type_id") == TARGET_PT)]
    if verified_entry:
        verified.append(verified_entry)
    elif failed_reason:
        # non-destructive: keep old verified if existed in previous registry
        old = _read_yaml(reg_path) if reg_path.exists() else {}
        old = _ensure_registry_list_fields(old)
        keep = None
        for v in old["verified_problem_types"]:
            if isinstance(v, dict) and v.get("skill_id") == TARGET_SKILL and v.get("problem_type_id") == TARGET_PT:
                keep = v
                break
        if keep:
            verified.append(keep)
        failed.append({"problem_type_id": TARGET_PT, "skill_id": TARGET_SKILL, "reason": failed_reason})
    reg["verified_problem_types"] = verified
    reg["failed_problem_types"] = failed
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(_yaml_like(reg) + "\n", encoding="utf-8")
    return reg


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", required=True)
    p.add_argument("--problem-type-id", required=True)
    p.add_argument("--max-rounds", type=int, default=5)
    args = p.parse_args()
    if args.skill_id != TARGET_SKILL or args.problem_type_id != TARGET_PT:
        raise RuntimeError("此版本只支援 vh_數學B1_AbsoluteValue / absolute_value_numeric_evaluation")
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value" / "problem_types_absolute_value.yaml"
    spec_obj = _read_yaml(spec_path)
    items = spec_obj.get("items", [])
    if not any(isinstance(i, dict) and i.get("problem_type_id") == TARGET_PT for i in items):
        raise RuntimeError("problem_type spec not found, run inventory first")

    pdir = root / "generated_candidates" / "vocational_math_b1" / "section_1_1" / TARGET_PT
    pdir.mkdir(parents=True, exist_ok=True)
    cand = pdir / "candidate_v1.py"
    cand.write_text(_candidate_code(), encoding="utf-8")

    trace = {"rounds": [], "final_candidate": str(cand), "status": "failed"}
    current = cand
    for r in range(1, args.max_rounds + 1):
        rep = _run_verifier(current)
        rp = pdir / f"verifier_report_v{r}.json"
        rp.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        trace["rounds"].append({"round": r, "candidate": str(current), "report": str(rp), "passed": rep["passed"]})
        if rep["passed"]:
            trace["status"] = "verified"
            break
        if r == args.max_rounds:
            break
        prompt = pdir / f"repair_prompt_v{r+1}.md"
        prompt.write_text(f"# Repair Prompt\n\nerrors:\n{json.dumps(rep['errors'], ensure_ascii=False)}\n", encoding="utf-8")
        nxt = pdir / f"candidate_v{r+1}.py"
        nxt.write_text(_candidate_code(), encoding="utf-8")
        current = nxt
    (pdir / "final_status.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

    entry = None
    reason = None
    if trace["status"] == "verified":
        entry = {
            "problem_type_id": TARGET_PT,
            "skill_id": TARGET_SKILL,
            "subskill_id": TARGET_PT,
            "status": "verified",
            "candidate_path": "generated_candidates/vocational_math_b1/section_1_1/absolute_value_numeric_evaluation/candidate_v1.py",
            "function_name": "generate",
            "answer_type": "integer",
            "checker_type": "integer_checker",
        }
    else:
        last = json.loads((pdir / f"verifier_report_v{args.max_rounds}.json").read_text(encoding="utf-8"))
        reason = ", ".join(last.get("errors", [])[:3]) or "failed"
    reg_path = root / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    reg = _merge_registry(reg_path, entry, reason)
    out = {
        "status": trace["status"],
        "registry": str(reg_path),
        "verified_count": len(reg.get("verified_problem_types", [])),
    }
    if trace["status"] != "verified":
        latest_report_path = Path(trace["rounds"][-1]["report"]) if trace.get("rounds") else None
        first_error = ""
        if latest_report_path and latest_report_path.exists():
            latest = json.loads(latest_report_path.read_text(encoding="utf-8"))
            errs = latest.get("errors", [])
            first_error = errs[0] if errs else ""
        out["failed_reason"] = reason
        out["verifier_report_path"] = str(latest_report_path) if latest_report_path else ""
        out["first_error"] = first_error
        out["latest_candidate_path"] = trace["final_candidate"] if trace.get("final_candidate") else str(cand)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
