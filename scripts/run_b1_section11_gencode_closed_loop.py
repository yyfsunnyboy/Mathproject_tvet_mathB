import argparse
import ast
import importlib.util
import json
import random
import re
import sqlite3
import time
from pathlib import Path
from typing import Any


FORMAL_SKILLS = {
    "vh_數學B1_NumberLine",
    "vh_數學B1_AbsoluteValue",
    "vh_數學B1_AbsoluteValueInequality",
    "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning",
}
OUTLINE_SKILL = "outline_vocational_數學B1_11"
PLACEHOLDER_TOKENS = ("[BLANK]", "[FORMULA_MISSING]", "TODO", "placeholder")
MANUAL_KEYWORDS = ("說明理由", "證明", "解釋")
VISUAL_KEYWORDS = ("畫出", "作圖", "在數線上表示", "圖示", "幾何意義")


def _dump_yaml_like(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_dump_yaml_like(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {json.dumps(v, ensure_ascii=False)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(_dump_yaml_like(item, indent + 2))
            else:
                lines.append(f"{pad}- {json.dumps(item, ensure_ascii=False)}")
        return "\n".join(lines)
    return f"{pad}{json.dumps(data, ensure_ascii=False)}"


def load_section_context(db_path: Path) -> dict[str, Any]:
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    sql = """
    SELECT
      sc.skill_id,
      sc.curriculum,
      sc.grade,
      sc.volume,
      sc.chapter,
      sc.section,
      sc.paragraph,
      si.skill_ch_name,
      si.skill_en_name,
      si.category,
      si.is_active
    FROM skill_curriculum sc
    LEFT JOIN skills_info si ON si.skill_id = sc.skill_id
    WHERE sc.volume = ? AND sc.section LIKE ?
    ORDER BY sc.skill_id
    """
    skill_rows = [dict(r) for r in cur.execute(sql, ("數學B1", "1-1%")).fetchall()]
    skills_filtered = [
        r for r in skill_rows if r["skill_id"] in FORMAL_SKILLS and r["skill_id"] != OUTLINE_SKILL
    ]
    te_cols = [r[1] for r in cur.execute("PRAGMA table_info(textbook_examples)").fetchall()]
    order_key = "te.id" if "id" in te_cols else "te.rowid"
    sql_examples = f"""
    SELECT te.*
    FROM textbook_examples te
    JOIN skill_curriculum sc ON sc.skill_id = te.skill_id
    WHERE sc.volume = ? AND sc.section LIKE ?
    ORDER BY {order_key}
    """
    examples = [dict(r) for r in cur.execute(sql_examples, ("數學B1", "1-1%")).fetchall()]
    con.close()
    examples = [e for e in examples if e.get("skill_id") in FORMAL_SKILLS]
    return {"skills_all": skill_rows, "skills": skills_filtered, "examples": examples}


def _example_text(ex: dict[str, Any]) -> str:
    parts = []
    for key in ("problem", "question", "prompt", "stem", "content"):
        v = ex.get(key)
        if isinstance(v, str):
            parts.append(v)
    return " ".join(parts).strip()


def classify_examples(examples: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out = {
        "deterministic_numeric": [],
        "deterministic_expression": [],
        "deterministic_choice": [],
        "visual_reading_short_answer": [],
        "handwriting_free_response": [],
        "proof_or_explanation": [],
        "teacher_review": [],
        "future_ai_judged": [],
    }
    for ex in examples:
        text = _example_text(ex)
        if any(k in text for k in MANUAL_KEYWORDS):
            out["teacher_review"].append(ex)
            continue
        if any(k in text for k in VISUAL_KEYWORDS):
            if "幾何意義" in text:
                out["future_ai_judged"].append(ex)
            else:
                out["visual_reading_short_answer"].append(ex)
            continue
        if any(k in text for k in ("選擇", "下列何者", "A.", "B.", "C.", "D.")):
            out["deterministic_choice"].append(ex)
            continue
        if any(k in text for k in ("不等式", "區間", "x", "|")):
            out["deterministic_expression"].append(ex)
            continue
        out["deterministic_numeric"].append(ex)
    return out


def _select_problem_type(skill_id: str, text: str, category: str) -> str | None:
    if category.startswith("deterministic"):
        if skill_id == "vh_數學B1_NumberLine":
            if any(k in text for k in ("大小", "排列", "由小到大", "由大到小")):
                return "number_line_integer_ordering"
            return "number_line_point_value_reading"
        if skill_id == "vh_數學B1_AbsoluteValue":
            if any(k in text for k in ("方程", "= ", "＝")):
                return "absolute_value_equation_basic"
            if "距離" in text:
                return "absolute_value_distance_interpretation"
            return "absolute_value_numeric_evaluation"
        if skill_id == "vh_數學B1_AbsoluteValueInequality":
            if "<" in text or "小於" in text:
                return "absolute_value_inequality_less_than_basic"
            return "absolute_value_inequality_greater_than_basic"
        if skill_id == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning":
            return "absolute_value_inequality_interval_interpretation"
    return None


def build_problem_type_specs(classified: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    for category, rows in classified.items():
        for ex in rows:
            skill_id = ex.get("skill_id", "")
            text = _example_text(ex)
            pt = _select_problem_type(skill_id, text, category)
            if pt is None:
                continue
            runtime = "deterministic" if category.startswith("deterministic") else "manual"
            answer_type = "choice" if category == "deterministic_choice" else "numeric_or_expression"
            checker_type = "deterministic_checker" if runtime == "deterministic" else "manual_review"
            specs.setdefault(
                pt,
                {
                    "problem_type_id": pt,
                    "skill_id": skill_id,
                    "display_name": pt.replace("_", " "),
                    "runtime_category": runtime,
                    "answer_type": answer_type,
                    "checker_type": checker_type,
                    "examples_refs": [],
                    "output_contract": {
                        "required_keys": [
                            "problem_type_id",
                            "skill_id",
                            "question_text",
                            "answer",
                            "answer_type",
                            "checker_type",
                            "solution_steps",
                            "metadata",
                        ]
                    },
                    "difficulty_policy": "easy_only_v1",
                    "status": "draft",
                },
            )
            specs[pt]["examples_refs"].append(ex.get("id"))
    return list(specs.values())


def _candidate_code(spec: dict[str, Any]) -> str:
    pt = spec["problem_type_id"]
    sid = spec["skill_id"]
    return f'''import random

PROBLEM_TYPE_ID = "{pt}"
SKILL_ID = "{sid}"

def generate(seed: int | None = None, difficulty: str = "easy") -> dict:
    rng = random.Random(seed)
    scenario_id = rng.randint(1, 5)
    if PROBLEM_TYPE_ID == "number_line_integer_ordering":
        nums = rng.sample(range(-20, 21), 4)
        q = f"將下列整數由小到大排列：$" + ", ".join(str(n) for n in nums) + "$"
        answer = ",".join(str(n) for n in sorted(nums))
        steps = ["比較正負與絕對值大小。", "依序排列得到答案。"]
    elif PROBLEM_TYPE_ID == "number_line_point_value_reading":
        x = rng.randint(-15, 15)
        q = f"數線上點 $P$ 對應到整數 ${{x}}$，已知 $P$ 在 ${{x}}$，求其數值。".replace("{{x}}", str(x))
        answer = str(x)
        steps = ["直接讀取數線上點的對應整數。"]
    elif PROBLEM_TYPE_ID == "absolute_value_numeric_evaluation":
        a = rng.randint(-20, 20)
        q = f"求 $|{{a}}|$ 的值。".replace("{{a}}", str(a))
        answer = str(abs(a))
        steps = ["絕對值表示到 0 的距離。", f"因此 $|{{a}}|={{{{ans}}}}$。".replace("{{a}}", str(a)).replace("{{ans}}", str(abs(a)))]
    elif PROBLEM_TYPE_ID == "absolute_value_distance_interpretation":
        a = rng.randint(-15, 15)
        b = rng.randint(-15, 15)
        q = f"在數線上，${{a}}$ 與 ${{b}}$ 的距離為多少？".replace("{{a}}", str(a)).replace("{{b}}", str(b))
        answer = str(abs(a - b))
        steps = ["兩點距離為差的絕對值。", f"$|{{a}}-{{b}}|={{{{ans}}}}$".replace("{{a}}", str(a)).replace("{{b}}", str(b)).replace("{{ans}}", str(abs(a-b)))]
    elif PROBLEM_TYPE_ID == "absolute_value_equation_basic":
        n = rng.randint(1, 12)
        q = f"解方程式：$|x|={{{{n}}}}$".replace("{{n}}", str(n))
        answer = f"x={n} 或 x={-n}"
        steps = ["絕對值方程有兩個對稱解。", f"$x={{{{n}}}}$ 或 $x=-{{{{n}}}}$".replace("{{n}}", str(n))]
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_less_than_basic":
        n = rng.randint(1, 12)
        q = f"解不等式：$|x|<{{{{n}}}}$".replace("{{n}}", str(n))
        answer = f"-{n}<x<{n}"
        steps = ["由絕對值小於型態得雙邊不等式。"]
    elif PROBLEM_TYPE_ID == "absolute_value_inequality_greater_than_basic":
        n = rng.randint(1, 12)
        q = f"解不等式：$|x|>{{{{n}}}}$".replace("{{n}}", str(n))
        answer = f"x<-{n} 或 x>{n}"
        steps = ["由絕對值大於型態得兩側區間聯集。"]
    else:
        n = rng.randint(1, 12)
        q = f"將解集寫成區間：$|x|\\leq {{{{n}}}}$".replace("{{n}}", str(n))
        answer = f"[{-n},{n}]"
        steps = ["絕對值小於等於轉成閉區間。"]

    payload = {{
        "problem_type_id": PROBLEM_TYPE_ID,
        "skill_id": SKILL_ID,
        "question_text": q,
        "answer": answer,
        "answer_type": "choice" if "選擇" in q else "numeric_or_expression",
        "checker_type": "deterministic_checker",
        "solution_steps": steps,
        "metadata": {{
            "scenario_family": PROBLEM_TYPE_ID,
            "scenario_id": scenario_id,
            "parameter_signature": f"{{PROBLEM_TYPE_ID}}:{{scenario_id}}:{{difficulty}}",
            "question_pattern_id": f"p{{scenario_id}}",
        }},
    }}
    return payload
'''


def generate_candidate(spec: dict[str, Any], base_dir: Path) -> Path:
    pdir = base_dir / spec["problem_type_id"]
    pdir.mkdir(parents=True, exist_ok=True)
    p = pdir / "candidate_v1.py"
    p.write_text(_candidate_code(spec), encoding="utf-8")
    return p


def _load_module(candidate_path: Path):
    spec = importlib.util.spec_from_file_location(candidate_path.stem, candidate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("import spec failed")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_verifier(candidate_path: Path, rounds: int = 30) -> dict[str, Any]:
    report = {"candidate_path": str(candidate_path), "errors": [], "samples": [], "passed": False}
    src = candidate_path.read_text(encoding="utf-8")
    try:
        ast.parse(src)
    except Exception as e:
        report["errors"].append(f"syntax_check_failed: {e}")
        return report
    if any(tok.lower() in src.lower() for tok in PLACEHOLDER_TOKENS):
        report["errors"].append("placeholder_detected")
    if re.search(r"(?<![\\$])\\b[0-9a-zA-Z]+\\^[0-9]+\\b", src):
        report["errors"].append("plain_power_notation_detected")
    try:
        mod = _load_module(candidate_path)
    except Exception as e:
        report["errors"].append(f"import_check_failed: {e}")
        return report
    if not hasattr(mod, "generate"):
        report["errors"].append("generate_missing")
        return report
    seen_q = []
    seen_sig = []
    for i in range(rounds):
        t0 = time.time()
        payload = mod.generate(seed=i, difficulty="easy")
        dt = time.time() - t0
        if dt > 5:
            report["errors"].append("timeout_exceeded")
            break
        keys = {
            "problem_type_id",
            "skill_id",
            "question_text",
            "answer",
            "answer_type",
            "checker_type",
            "solution_steps",
            "metadata",
        }
        if not keys.issubset(payload.keys()):
            report["errors"].append("output_contract_missing_keys")
        if payload.get("checker_type") != "deterministic_checker":
            report["errors"].append("checker_type_invalid")
        if payload.get("answer_type") not in ("choice", "numeric_or_expression"):
            report["errors"].append("answer_type_invalid")
        q = str(payload.get("question_text", ""))
        if any(tok.lower() in q.lower() for tok in PLACEHOLDER_TOKENS):
            report["errors"].append("question_placeholder_detected")
        seen_q.append(q)
        seen_sig.append(str(payload.get("metadata", {}).get("parameter_signature", "")))
        report["samples"].append(payload)
    consecutive_duplicate_count = sum(1 for i in range(1, len(seen_q)) if seen_q[i] == seen_q[i - 1])
    unique_question_text_count = len(set(seen_q))
    repeated_question_text_ratio = 0.0 if not seen_q else 1 - (unique_question_text_count / len(seen_q))
    unique_parameter_signature_count = len(set(seen_sig))
    diversity = {
        "consecutive_duplicate_count": consecutive_duplicate_count,
        "unique_question_text_count": unique_question_text_count,
        "repeated_question_text_ratio": repeated_question_text_ratio,
        "unique_parameter_signature_count": unique_parameter_signature_count,
    }
    report["diversity"] = diversity
    if consecutive_duplicate_count != 0:
        report["errors"].append("consecutive_duplicate_count_nonzero")
    if unique_question_text_count < 6:
        report["errors"].append("unique_question_text_count_below_6")
    if repeated_question_text_ratio > 0.5:
        report["errors"].append("repeated_question_text_ratio_above_0.5")
    if unique_parameter_signature_count < 6:
        report["errors"].append("unique_parameter_signature_count_below_6")
    report["passed"] = not report["errors"]
    return report


def healer_repair_loop(spec: dict[str, Any], candidate_path: Path, max_rounds: int) -> dict[str, Any]:
    trace = {"rounds": [], "final_candidate": str(candidate_path), "status": "failed"}
    current = candidate_path
    for r in range(1, max_rounds + 1):
        rep = run_verifier(current, rounds=30)
        rpt_path = current.parent / f"verifier_report_v{r}.json"
        rpt_path.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        trace["rounds"].append({"round": r, "candidate": str(current), "report": str(rpt_path), "passed": rep["passed"]})
        if rep["passed"]:
            trace["status"] = "verified"
            trace["final_candidate"] = str(current)
            break
        if r == max_rounds:
            break
        next_idx = r + 1
        repair_prompt = {
            "problem_type_spec": spec,
            "candidate_path": str(current),
            "verifier_errors": rep["errors"],
            "failed_samples": rep["samples"][:3],
            "instruction": "Keep deterministic logic; fix verifier errors only.",
        }
        (current.parent / f"repair_prompt_v{next_idx}.md").write_text(
            "# Repair Prompt\n\n```json\n" + json.dumps(repair_prompt, ensure_ascii=False, indent=2) + "\n```\n",
            encoding="utf-8",
        )
        current = current.parent / f"candidate_v{next_idx}.py"
        current.write_text(_candidate_code(spec), encoding="utf-8")
    (Path(trace["final_candidate"]).parent / "final_status.json").write_text(
        json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return trace


def write_section_files(base: Path, specs: list[dict[str, Any]], examples: list[dict[str, Any]]) -> None:
    base.mkdir(parents=True, exist_ok=True)
    skill_yaml = {
        "scope": "vocational_math_b1_section_1_1",
        "chapter_anchor_skill": OUTLINE_SKILL,
        "formal_skills": sorted(FORMAL_SKILLS),
        "status": "draft",
        "note": "prototype only, no runtime publish",
    }
    (base / "skill.yaml").write_text(_dump_yaml_like(skill_yaml) + "\n", encoding="utf-8")
    (base / "problem_types.yaml").write_text(_dump_yaml_like({"items": specs}) + "\n", encoding="utf-8")
    ex_map = []
    for ex in examples:
        ex_map.append({"example_id": ex.get("id"), "skill_id": ex.get("skill_id"), "ref": ex.get("source", "db_textbook_examples")})
    (base / "examples_map.yaml").write_text(_dump_yaml_like({"examples": ex_map}) + "\n", encoding="utf-8")
    domain_functions = {
        "allowed_imports": ["math", "random"],
        "forbidden_functions": ["eval", "exec", "input", "os.system"],
        "checker": "deterministic_checker",
    }
    (base / "domain_functions.yaml").write_text(_dump_yaml_like(domain_functions) + "\n", encoding="utf-8")
    evals = {"gates": ["syntax", "import", "contract", "sampling>=30", "diversity", "timeout<=5s"], "status": "draft"}
    (base / "evals.yaml").write_text(_dump_yaml_like(evals) + "\n", encoding="utf-8")


def write_registry(path: Path, verified: list[str], failed: list[str], manual: list[str], future: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "0.1",
        "scope": "vocational_math_b1_section_1_1",
        "verified_problem_types": verified,
        "failed_problem_types": failed,
        "manual_review_problem_types": manual,
        "future_ai_judged_problem_types": future,
        "runtime_ready_auto_publish": False,
    }
    path.write_text(_dump_yaml_like(payload) + "\n", encoding="utf-8")


def write_report(
    report_path: Path,
    context: dict[str, Any],
    classified: dict[str, list[dict[str, Any]]],
    specs: list[dict[str, Any]],
    traces: dict[str, dict[str, Any]],
    registry_path: Path,
) -> None:
    skills = sorted({s["skill_id"] for s in context["skills"]})
    verified = sorted([k for k, v in traces.items() if v["status"] == "verified"])
    failed = sorted([k for k, v in traces.items() if v["status"] != "verified"])
    manual = sorted([s["problem_type_id"] for s in specs if s["runtime_category"] != "deterministic"])
    deterministic = sorted([s["problem_type_id"] for s in specs if s["runtime_category"] == "deterministic"])
    lines = [
        "# B1 1-1 Gencode Closed Loop Report",
        "",
        "## 1) DB 讀到的 B1 1-1 skills",
        *(f"- {s}" for s in skills),
        "",
        f"## 2) textbook_examples 數量\n- {len(context['examples'])}",
        "",
        "## 3) examples 分流結果",
        f"- deterministic: {len(classified['deterministic_numeric']) + len(classified['deterministic_expression'])}",
        f"- choice: {len(classified['deterministic_choice'])}",
        f"- manual_review: {len(classified['teacher_review']) + len(classified['proof_or_explanation']) + len(classified['visual_reading_short_answer'])}",
        f"- future_ai_judged: {len(classified['future_ai_judged'])}",
        "",
        "## 4) problem_type 清單",
        *(f"- {s['problem_type_id']}" for s in specs),
        "",
        "## 5) 每個 problem_type candidate rounds",
    ]
    for pt, tr in traces.items():
        lines.append(f"- {pt}: {len(tr['rounds'])} rounds, status={tr['status']}")
    lines.extend(["", "## 6) verifier pass/fail 摘要"])
    for pt, tr in traces.items():
        lines.append(f"- {pt}: {tr['status']}")
    lines.extend(["", "## 7) healer 修復紀錄"])
    for pt, tr in traces.items():
        logs = ", ".join(f"v{r['round']}:{'pass' if r['passed'] else 'fail'}" for r in tr["rounds"])
        lines.append(f"- {pt}: {logs}")
    lines.extend(["", "## 8) verified 清單"])
    if verified:
        lines.extend(f"- {x}" for x in verified)
    else:
        lines.append("- (none)")
    lines.extend(["", "## 9) failed/manual_review 清單"])
    if failed:
        lines.extend(f"- failed: {x}" for x in failed)
    else:
        lines.append("- failed: (none)")
    if manual:
        lines.extend(f"- manual_review: {x}" for x in manual)
    else:
        lines.append("- manual_review: (none)")
    lines.extend(["", "## 10) sample generated questions"])
    for pt, tr in traces.items():
        if tr["rounds"]:
            rep = json.loads(Path(tr["rounds"][0]["report"]).read_text(encoding="utf-8"))
            for sample in rep.get("samples", [])[:1]:
                lines.append(f"- {pt}: {sample.get('question_text', '')}")
    lines.extend(
        [
            "",
            "## 11) registry path",
            f"- {registry_path}",
            "",
            "## 12) 確認未修改 DB / production router / templates",
            "- DB: not modified by this script (read-only sqlite queries).",
            "- Production router/practice/templates: not touched.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-rounds", type=int, default=5)
    parser.add_argument("--db-path", default="instance/kumon_math.db")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    context = load_section_context(root / args.db_path)
    found = {s["skill_id"] for s in context["skills"]}
    missing = sorted(FORMAL_SKILLS - found)

    classified = classify_examples(context["examples"])
    specs = build_problem_type_specs(classified)
    safe_specs = [s for s in specs if s["runtime_category"] == "deterministic"]

    section_dir = root / "agent_skills_v2" / "vocational_math_b1" / "chapter_1" / "section_1_1_number_line_absolute_value"
    write_section_files(section_dir, specs, context["examples"])

    gen_base = root / "generated_candidates" / "vocational_math_b1" / "section_1_1"
    traces = {}
    for spec in safe_specs:
        cp = generate_candidate(spec, gen_base)
        traces[spec["problem_type_id"]] = healer_repair_loop(spec, cp, max_rounds=args.max_rounds)

    verified = sorted([k for k, v in traces.items() if v["status"] == "verified"])
    failed = sorted([k for k, v in traces.items() if v["status"] != "verified"])
    manual = sorted([s["problem_type_id"] for s in specs if s["runtime_category"] != "deterministic"])
    future = sorted([s["problem_type_id"] for s in specs if s["runtime_category"] != "deterministic" and "geometric" in s["problem_type_id"]])

    registry_path = root / "configs" / "generated_registry" / "b1_section_1_1_verified_registry.v0.1.yaml"
    write_registry(registry_path, verified, failed, manual, future)

    report_path = root / "reports" / "gencode_closed_loop" / "b1_section_1_1_closed_loop_report.md"
    write_report(report_path, context, classified, specs, traces, registry_path)

    print(json.dumps({"missing_formal_skills": missing, "report": str(report_path), "registry": str(registry_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
