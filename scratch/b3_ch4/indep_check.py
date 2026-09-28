import sys
import os
from collections import Counter

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
import sympy as sp  # noqa: E402

from _b3_ch4_tex import math_segments, tex_to_sympy, numeric, log_arguments_positive  # noqa: E402
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix  # noqa: E402

EVAL_OPS = {
    "exp_integer_power_eval", "exp_zero_negative_eval", "exp_rational_power_eval", "exp_rational_power_combo",
    "log_definition_eval", "log_basic_property_eval", "log_rational_value_eval", "log_product_quotient_eval",
    "log_linear_combination_eval", "log_change_base_chain_eval", "log_change_base_product_eval",
    "exp_integer_exponent_simplify", "exp_rational_exponent_simplify",
}
EQ_OPS = {
    "exp_equation_same_base", "exp_equation_convert_base", "exp_equation_quadratic_sub", "exp_equation_factor_common",
    "log_equation_linear_arg", "log_equation_product_quadratic", "log_equation_quadratic_arg", "log_equation_solve_base",
}
SUBS = {sp.Symbol("a"): sp.Rational(17, 10), sp.Symbol("b"): sp.Rational(23, 10), sp.Symbol("c"): sp.Rational(13, 10)}


def answer_expr(text):
    return sp.sympify(str(text).replace("^", "**"), locals={"a": sp.Symbol("a"), "b": sp.Symbol("b")})


def target_expression(matrix):
    segs = math_segments(matrix["question_text"])
    seg = max(segs, key=len)
    if seg.endswith("="):
        return seg[:-1]
    if "=" in seg:
        return seg.split("=", 1)[1]
    return seg


def items(matrix):
    return [row["text"] for row in (matrix.get("stem_structure") or {}).get("items") or []]


def close(u, v):
    return abs(u - v) < 1e-9 * max(1, abs(v))


problems = Counter()
checked = Counter()
seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for eid, spec in sorted(SOURCE_SPECS.items()):
    op = spec["op"]
    if op not in EVAL_OPS | EQ_OPS:
        continue
    for seed in range(seeds):
        mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
        value = mat["answer"]["value"]
        try:
            if isinstance(value, dict):
                pairs = list(zip(items(mat), value.values()))
                if op == "log_equation_quadratic_arg":
                    eq = max(math_segments(mat["question_text"]), key=len)
                    pairs = [(r"\(" + eq + r"\)", v) for v in value.values()]
            else:
                pairs = [(None, value)]
            for item, ans in pairs:
                if op in EVAL_OPS:
                    tex = target_expression(mat) if item is None else math_segments(item)[0]
                    got = numeric(tex_to_sympy(tex), SUBS)
                    want = numeric(answer_expr(ans), SUBS)
                    if not close(got, want):
                        problems[f"{eid}:{op}:value"] += 1
                        if problems[f"{eid}:{op}:value"] == 1:
                            print("VALUE", eid, seed, tex, ans, got, want)
                else:
                    segs = math_segments(item) if item else math_segments(mat["question_text"])
                    eqs = [s for s in segs if "=" in s and not s.endswith("=")]
                    eq = max(eqs, key=len)
                    left, right = eq.split("=", 1)
                    syms = {}
                    lhs = tex_to_sympy(left, syms)
                    rhs = tex_to_sympy(right, syms)
                    var = syms.get("x") or syms.get("a")
                    sub = {var: answer_expr(ans)}
                    if not close(numeric(lhs, sub), numeric(rhs, sub)):
                        problems[f"{eid}:{op}:not_root"] += 1
                        if problems[f"{eid}:{op}:not_root"] == 1:
                            print("ROOT", eid, seed, eq, ans)
                    if not (log_arguments_positive(lhs, sub) and log_arguments_positive(rhs, sub)):
                        problems[f"{eid}:{op}:domain"] += 1
                    if op == "log_equation_product_quadratic":
                        rej = {var: sp.Integer(mat["params"]["rejected"])}
                        if log_arguments_positive(lhs, rej) and log_arguments_positive(rhs, rej):
                            problems[f"{eid}:{op}:rejected_legal"] += 1
                checked[op] += 1
        except Exception as exc:  # noqa: BLE001
            problems[f"{eid}:{op}:{type(exc).__name__}:{str(exc)[:60]}"] += 1
            if problems[f"{eid}:{op}:{type(exc).__name__}:{str(exc)[:60]}"] == 1:
                print("ERR", eid, seed, mat["question_text"][:200], exc)
for k, v in sorted(problems.items()):
    print(k, v)
print("checked:", dict(checked))
print("problem keys:", len(problems))
