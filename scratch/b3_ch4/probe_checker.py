import os
import sys

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from core.gencode.runtime_skill_wrapper import check_answer

ac = {"answer_type": "expression", "checker": "expression_checker", "answer_equivalence": "algebraic_equivalent"}
cases = [
    ("a^(5/12)", "a^(5/12)"),
    ("a**(5/12)", "a^(5/12)"),
    ("a^7/b", "a^7*b^(-1)"),
    ("a^7 b^-1", "a^7*b^(-1)"),
    ("a^7b^(-1)", "a^7*b^(-1)"),
    ("0.125", "1/8"),
    ("1/8", "1/8"),
    ("2/8", "1/8"),
    (".6875", "0.6875"),
    ("0.68750", "0.6875"),
    ("0.6876", "0.6875"),
    ("(2a+b)/(a+b)", "(2*a+b)/(a+b)"),
    ("1+b+2a", "2*a+b+1"),
    ("3a+b", "2*a+b+1"),
    ("a<b<c", "a<b<c"),
    ("c>b>a", "a<b<c"),
    ("b<a<c", "a<b<c"),
    ("-4", "-4"),
    ("x=5", "5"),
    ("5", "5"),
    ("2950", "2950"),
    ("2.95*10^3", "2950"),
    ("1/a^12", "a^(-12)"),
    ("a^-12", "a^(-12)"),
    ("\\frac{1}{8}", "1/8"),
    ("27/4", "27/4"),
    ("sqrt(2)", "2^(1/2)"),
    ("5", "sqrt(5)"),
]
for u, c in cases:
    try:
        r = check_answer(u, c, payload={"answer_contract": ac}, answer_contract=ac)
    except Exception as e:
        r = f"ERR {e}"
    print(f"{u!r:22} vs {c!r:18} -> {r}")

ac2 = {"answer_type": "text", "checker": "text_checker", "answer_equivalence": "normalized_text_equivalence"}
for u, c in [("遞增", "遞增"), ("遞 增", "遞增")]:
    print(u, c, check_answer(u, c, payload={"answer_contract": ac2}, answer_contract=ac2))
