# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.checkers.expression_equivalence_checker import (
    check_equation_equivalence_answer,
    check_expression_equivalence_answer,
    check_expression_equivalence_debug,
)
from core.gencode.answer_payload import grade_numeric_contract_answer
from core.gencode.runtime_skill_wrapper import check_answer

rows = [
    ("(x-1)(x-2)", "(x-2)(x-1)", "PASS", "expr"),
    ("(x-1)(x-2)", "(x - 1) (x - 2)", "PASS", "expr"),
    ("(x-1)(x-2)", "(x+1)(x-2)", "FAIL", "expr"),
    ("2*x+2", "2(x+1)", "PASS", "expr"),
    ("1/2", "2/4", "PASS", "frac"),
    ("1/2", "3/6", "PASS", "frac"),
    ("2", "+2", "PASS", "int"),
    ("2", "2.0", "PASS", "int"),
    ("2", "3", "FAIL", "int"),
    ("x=3", "3=x", "PASS", "eq"),
    ("x=3", "2x=6", "PASS", "eq"),
    ("x=3", "x-3=0", "PASS", "eq"),
    ("x=3", "x=4", "FAIL", "eq"),
]

int_ac = {"answer_type": "integer", "checker": "integer_checker", "equivalence_type": "numeric_equivalence"}
frac_ac = {"answer_type": "rational", "checker": "rational_checker", "equivalence_type": "rational_equivalent"}

print("canonical | student | expected | actual")
for canonical, student, expected, kind in rows:
    if kind == "expr":
        actual = "PASS" if check_expression_equivalence_answer(student, canonical) else "FAIL"
    elif kind == "eq":
        actual = "PASS" if check_equation_equivalence_answer(student, canonical) else "FAIL"
    elif kind == "frac":
        actual = "PASS" if grade_numeric_contract_answer(student, canonical, frac_ac, checker="rational_checker").get("correct") else "FAIL"
    else:
        actual = "PASS" if grade_numeric_contract_answer(student, canonical, int_ac, checker="integer_checker").get("correct") else "FAIL"
    print(f"{canonical} | {student} | {expected} | {actual}")

form = {
    "required_form": "factorized",
    "answer_type": "expression",
    "checker": "expression_checker",
}
dbg = check_expression_equivalence_debug("x^2-3x+2", "(x-1)(x-2)", answer_contract=form)
print("required_form expanded", dbg["correct"], dbg.get("required_form_failed"), dbg.get("simplify_result"))
print(
    "required_form swapped",
    check_expression_equivalence_answer("(x-2)(x-1)", "(x-1)(x-2)", answer_contract=form),
)
