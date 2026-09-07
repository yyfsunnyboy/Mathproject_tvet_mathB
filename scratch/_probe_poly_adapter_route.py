# -*- coding: utf-8 -*-
import inspect
import sys

sys.stdout.reconfigure(encoding="utf-8")

from core.domain.polynomial_domain import build_polynomial_matrix
from core.gencode.domain_matrix_adapter import convert_domain_matrix_to_question_payload
import core.gencode.domain_matrix_adapter as am

src = inspect.getsource(am.convert_domain_matrix_to_question_payload)

def probe(op: str) -> None:
    m = build_polynomial_matrix(seed=7, domain_operation=op)
    p = convert_domain_matrix_to_question_payload(
        m,
        presentation_mode="short_answer",
        answer_type="expression",
        problem_type_id=op,
        domain_operation=op,
    )
    q = (p.get("question_text") or p.get("question") or "")[:80]
    print(op, "OK", type(p.get("answer")).__name__, "q=", q.replace("\n", " "))
    print("  old_string_match", ("'" + op + "'" in src) or ('"' + op + '"' in src))

for op in ["polynomial_long_division", "polynomial_add_sub", "polynomial_multiply"]:
    probe(op)
