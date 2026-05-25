import argparse
import ast
import importlib.util
import json
import re
import time
from pathlib import Path
from typing import Any

TARGET_SKILL = "vh_數學B1_AbsoluteValue"
PLACEHOLDERS = ("[BLANK]", "[FORMULA_MISSING]", "TODO", "placeholder")

PT_SPECS: dict[str, dict[str, Any]] = {
    "absolute_value_numeric_evaluation": {
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "candidate_subdir": "absolute_value_numeric_evaluation",
        "subskill_id": "absolute_value_numeric_evaluation",
    },
    "absolute_value_equation_basic": {
        "answer_type": "text",
        "checker_type": "exact_string_checker",
        "candidate_subdir": "absolute_value_equation_basic",
        "subskill_id": "absolute_value_equation_basic",
    },
    "absolute_value_distance_from_zero": {
        "answer_type": "choice",
        "checker_type": "choice_checker",
        "candidate_subdir": "absolute_value_distance_from_zero",
        "subskill_id": "absolute_value_distance_from_zero",
    },
    "absolute_value_distance_between_two_points": {
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "candidate_subdir": "absolute_value_distance_between_two_points",
        "subskill_id": "absolute_value_distance_between_two_points",
    },
}


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


def _candidate_code(skill_id: str, problem_type_id: str) -> str:
    if problem_type_id == "absolute_value_numeric_evaluation":
        return f'''import random
PROBLEM_TYPE_ID = "{problem_type_id}"
SKILL_ID = "{skill_id}"
SUBSKILL_ID = "{problem_type_id}"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = ((int(seed) % 41) - 20) if seed is not None else rng.randint(-20, 20)
    answer = abs(n)
    question_text = f"求 $|{{n}}|$ 的值。"
    solution_steps = ["絕對值表示與 0 的距離。", f"$|{{n}}|={{answer}}$。"]
    metadata = {{
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{{rng.randint(1, 9)}}",
        "parameter_signature": f"absolute_value_numeric_evaluation:n={{n}}:difficulty={{difficulty}}",
        "question_pattern_id": f"p{{rng.randint(1, 4)}}",
        "diagnosis_tags": ["absolute_value_definition", "sign_error"],
        "prerequisite_subskills": [],
    }}
    return {{
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
'''
    if problem_type_id == "absolute_value_equation_basic":
        return f'''import random
PROBLEM_TYPE_ID = "{problem_type_id}"
SKILL_ID = "{skill_id}"
SUBSKILL_ID = "{problem_type_id}"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = ((int(seed) % 20) + 1) if seed is not None else rng.randint(1, 20)
    question_text = f"解方程式 $|x|={{n}}$。"
    answer = f"x=-{{n}} 或 x={{n}}"
    solution_steps = [f"$|x|={{n}}$ 表示 $x$ 到 $0$ 的距離為 ${{n}}$。", f"因此 $x=-{{n}}$ 或 $x={{n}}$。"]
    metadata = {{
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{{rng.randint(1, 9)}}",
        "parameter_signature": f"absolute_value_equation_basic:n={{n}}:difficulty={{difficulty}}",
        "question_pattern_id": f"p{{rng.randint(1, 4)}}",
        "diagnosis_tags": ["absolute_value_equation", "two_solutions"],
        "prerequisite_subskills": ["absolute_value_numeric_evaluation"],
    }}
    return {{
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": answer,
        "answer_type": "text",
        "checker_type": "exact_string_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": answer,
        "explanation": "\\n".join(solution_steps),
        "choices": [],
    }}
'''
    if problem_type_id == "absolute_value_distance_from_zero":
        return f'''import random
PROBLEM_TYPE_ID = "{problem_type_id}"
SKILL_ID = "{skill_id}"
SUBSKILL_ID = "{problem_type_id}"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    n = -(((int(seed) % 20) + 1)) if seed is not None else -rng.randint(1, 20)
    question_text = f"下列哪一項是 $|{{n}}|$ 的正確意義？"
    correct = f"數線上 ${{n}}$ 到 $0$ 的距離"
    choices = [correct, f"數線上 ${{abs(n)}}$ 到 ${{n}}$ 的距離", f"${{n}}$ 本身", "一個負數"]
    solution_steps = ["絕對值表示數線上該數到 $0$ 的距離。", f"因此 $|{{n}}|$ 表示 ${{n}}$ 到 $0$ 的距離。"]
    metadata = {{
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{{rng.randint(1, 9)}}",
        "parameter_signature": f"absolute_value_distance_from_zero:n={{n}}:pattern=meaning",
        "question_pattern_id": f"p{{rng.randint(1, 4)}}",
        "diagnosis_tags": ["absolute_value_meaning", "distance_from_zero"],
        "prerequisite_subskills": ["number_line_basic_position"],
    }}
    return {{
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "choices": choices,
        "answer": correct,
        "answer_type": "choice",
        "checker_type": "choice_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": correct,
        "explanation": "\\n".join(solution_steps),
    }}
'''
    if problem_type_id == "absolute_value_distance_between_two_points":
        return f'''import random
PROBLEM_TYPE_ID = "{problem_type_id}"
SKILL_ID = "{skill_id}"
SUBSKILL_ID = "{problem_type_id}"
def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    if seed is not None:
        a = (int(seed) % 21) - 10
        b = ((int(seed) * 3 + 5) % 21) - 10
        if a == b:
            b = 10 if a != 10 else -10
    else:
        a = rng.randint(-10, 10)
        b = rng.randint(-10, 10)
        while b == a:
            b = rng.randint(-10, 10)
    dist = abs(b - a)
    question_text = f"已知數線上兩點 $A({{a}})$、$B({{b}})$，試求 A、B 兩點的距離。"
    solution_steps = [
        "數線上兩點距離等於兩坐標差的絕對值。",
        f"$|{{b}}-({{a}})|=|{{b-a}}|={{dist}}$。",
        f"所以 A、B 兩點的距離為 ${{dist}}$。",
    ]
    metadata = {{
        "scenario_family": PROBLEM_TYPE_ID,
        "scenario_id": f"s{{rng.randint(1, 9)}}",
        "parameter_signature": f"absolute_value_distance_between_two_points:a={{a}}:b={{b}}:difficulty={{difficulty}}",
        "question_pattern_id": f"p{{rng.randint(1, 4)}}",
        "diagnosis_tags": ["absolute_value_distance", "number_line_distance", "coordinate_difference"],
        "prerequisite_subskills": ["number_line_basic_position", "absolute_value_numeric_evaluation"],
    }}
    return {{
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "subskill_id": SUBSKILL_ID,
        "question_text": question_text,
        "answer": dist,
        "answer_type": "integer",
        "checker_type": "integer_checker",
        "solution_steps": solution_steps,
        "metadata": metadata,
        "question": question_text,
        "correct_answer": dist,
        "explanation": "\\n".join(solution_steps),
        "choices": [],
    }}
'''
    raise RuntimeError("closed_loop_generator_not_implemented")


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("import spec failed")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _exact_string_checker(expected: str, given: str) -> bool:
    return str(expected).strip() == str(given).strip()


def _run_verifier(path: Path, problem_type_id: str, rounds: int = 30) -> dict[str, Any]:
    spec = PT_SPECS[problem_type_id]
    rep = {"candidate_path": str(path), "errors": [], "samples": [], "passed": False}
    src = path.read_text(encoding="utf-8")
    try:
        ast.parse(src)
    except Exception as e:
        rep["errors"].append(f"syntax_check_failed: {e}")
        return rep
    if any(t.lower() in src.lower() for t in PLACEHOLDERS):
        rep["errors"].append("placeholder_detected")

    mod = _load_module(path)
    if not hasattr(mod, "generate"):
        rep["errors"].append("generate_missing")
        return rep

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
    }
    seen_q, seen_sig = [], []
    for i in range(rounds):
        t0 = time.time()
        payload = mod.generate(seed=i, difficulty="easy")
        if time.time() - t0 > 5:
            rep["errors"].append("timeout_exceeded")
            break
        if not isinstance(payload, dict):
            rep["errors"].append("payload_not_dict")
            continue
        if not req.issubset(payload.keys()):
            rep["errors"].append("output_contract_missing_keys")
        if payload.get("answer_type") != spec["answer_type"]:
            rep["errors"].append("answer_type_invalid")
        if payload.get("checker_type") != spec["checker_type"]:
            rep["errors"].append("checker_type_invalid")

        q = str(payload.get("question_text", ""))
        if "$" not in q:
            rep["errors"].append("latex_safety_failed")

        if problem_type_id in {"absolute_value_numeric_evaluation", "absolute_value_distance_between_two_points"}:
            try:
                a = int(payload["answer"])
                c = int(payload["correct_answer"])
                if a != c:
                    rep["errors"].append("correct_answer_self_check_failed")
                if str(payload["correct_answer"]).strip() == "__wrong__":
                    rep["errors"].append("wrong_answer_rejection_failed")
            except Exception:
                rep["errors"].append("correct_answer_self_check_failed")
        elif problem_type_id == "absolute_value_equation_basic":
            ans = str(payload.get("answer", ""))
            cor = str(payload.get("correct_answer", ""))
            if not _exact_string_checker(ans, cor):
                rep["errors"].append("correct_answer_self_check_failed")
            if _exact_string_checker(cor, "__wrong__"):
                rep["errors"].append("wrong_answer_rejection_failed")
            if not re.match(r"^x=-\d+\s或\sx=\d+$", cor.strip()):
                rep["errors"].append("answer_format_invalid")
        elif problem_type_id == "absolute_value_distance_from_zero":
            choices = payload.get("choices")
            ans = str(payload.get("answer", ""))
            cor = str(payload.get("correct_answer", ""))
            if not isinstance(choices, list):
                rep["errors"].append("choices_type_invalid")
                choices = []
            if len(choices) < 4:
                rep["errors"].append("choices_count_below_4")
            if len(set(str(c) for c in choices)) != len(choices):
                rep["errors"].append("choices_duplicate_detected")
            if ans not in [str(c) for c in choices]:
                rep["errors"].append("answer_not_in_choices")
            if not _exact_string_checker(ans, cor):
                rep["errors"].append("correct_answer_self_check_failed")
            if _exact_string_checker(cor, "__wrong__"):
                rep["errors"].append("wrong_answer_rejection_failed")

        sig = str(payload.get("metadata", {}).get("parameter_signature", ""))
        seen_q.append(q)
        seen_sig.append(sig)
        rep["samples"].append(payload)

    cdup = sum(1 for i in range(1, len(seen_q)) if seen_q[i] == seen_q[i - 1])
    uq = len(set(seen_q))
    rr = 0.0 if not seen_q else 1 - uq / len(seen_q)
    usig = len(set(seen_sig))
    rep["diversity"] = {
        "consecutive_duplicate_count": cdup,
        "unique_question_text_count": uq,
        "repeated_question_text_ratio": rr,
        "unique_parameter_signature_count": usig,
    }
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


def _merge_registry(reg_path: Path, skill_id: str, problem_type_id: str, verified_entry: dict[str, Any] | None, failed_reason: str | None) -> dict[str, Any]:
    reg = _read_yaml(reg_path) if reg_path.exists() else {}
    reg = _ensure_registry_list_fields(reg)
    verified = [
        v
        for v in reg["verified_problem_types"]
        if not (isinstance(v, dict) and v.get("skill_id") == skill_id and v.get("problem_type_id") == problem_type_id)
    ]
    failed = [
        f
        for f in reg["failed_problem_types"]
        if not (isinstance(f, dict) and f.get("skill_id") == skill_id and f.get("problem_type_id") == problem_type_id)
    ]
    if verified_entry:
        verified.append(verified_entry)
    elif failed_reason:
        old = _read_yaml(reg_path) if reg_path.exists() else {}
        old = _ensure_registry_list_fields(old)
        keep = None
        for v in old["verified_problem_types"]:
            if isinstance(v, dict) and v.get("skill_id") == skill_id and v.get("problem_type_id") == problem_type_id:
                keep = v
                break
        if keep:
            verified.append(keep)
        failed.append({"problem_type_id": problem_type_id, "skill_id": skill_id, "reason": failed_reason})
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

    if args.skill_id != TARGET_SKILL:
        raise RuntimeError("此版本只支援 vh_數學B1_AbsoluteValue")
    if args.problem_type_id not in PT_SPECS:
        raise RuntimeError("closed_loop_generator_not_implemented")

    root = Path(__file__).resolve().parents[1]
    spec_path = root / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value" / "problem_types_absolute_value.yaml"
    items = _read_yaml(spec_path).get("items", [])
    if not any(isinstance(i, dict) and i.get("problem_type_id") == args.problem_type_id for i in items):
        raise RuntimeError("problem_type spec not found, run inventory first")

    subdir = PT_SPECS[args.problem_type_id]["candidate_subdir"]
    pdir = root / "generated_candidates" / "vocational_math_b1" / "section_1_1" / subdir
    pdir.mkdir(parents=True, exist_ok=True)
    cand = pdir / "candidate_v1.py"
    cand.write_text(_candidate_code(args.skill_id, args.problem_type_id), encoding="utf-8")

    trace = {"rounds": [], "final_candidate": str(cand), "status": "failed"}
    current = cand
    for r in range(1, args.max_rounds + 1):
        rep = _run_verifier(current, problem_type_id=args.problem_type_id)
        rp = pdir / f"verifier_report_v{r}.json"
        rp.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        trace["rounds"].append({"round": r, "candidate": str(current), "report": str(rp), "passed": rep["passed"]})
        if rep["passed"]:
            trace["status"] = "verified"
            break
        if r == args.max_rounds:
            break
    (pdir / "final_status.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

    entry = None
    reason = None
    if trace["status"] == "verified":
        entry = {
            "problem_type_id": args.problem_type_id,
            "skill_id": args.skill_id,
            "subskill_id": PT_SPECS[args.problem_type_id]["subskill_id"],
            "status": "verified",
            "candidate_path": f"generated_candidates/vocational_math_b1/section_1_1/{subdir}/candidate_v1.py",
            "function_name": "generate",
            "answer_type": PT_SPECS[args.problem_type_id]["answer_type"],
            "checker_type": PT_SPECS[args.problem_type_id]["checker_type"],
        }
    else:
        last = json.loads((pdir / f"verifier_report_v{args.max_rounds}.json").read_text(encoding="utf-8"))
        reason = ", ".join(last.get("errors", [])[:3]) or "failed"

    reg_path = root / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    reg = _merge_registry(reg_path, args.skill_id, args.problem_type_id, entry, reason)
    out = {"status": trace["status"], "registry": str(reg_path), "verified_count": len(reg.get("verified_problem_types", []))}
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
