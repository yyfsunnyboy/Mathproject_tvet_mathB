"""Independent derivation of the reference solution for the one Unit 3 row that has no dynamic generator (12746, read-only).

12746 asks for the NEGATION of two compound propositions in free text.  Free text cannot be graded reliably by a rational/choice checker, so the
row is FIXED_UNGRADED (handwriting + verified reference).  The reference is verified here:

* De Morgan's laws are checked over the full truth table of the two atoms;
* the concrete truth values of the textbook statements are evaluated (2 is even, 2 is prime, pi = 3, pi > 0) and the proposed negations are shown
  to take the opposite truth value of the original statement.

Writes ``fixed_oracles.json`` next to this file.
"""
import itertools
import json
import sys
from pathlib import Path

import sympy as sp

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent

# De Morgan over the whole truth table
for p, q in itertools.product([True, False], repeat=2):
    assert (not (p and q)) == ((not p) or (not q))
    assert (not (p or q)) == ((not p) and (not q))
print("De Morgan: verified on 4 truth assignments each")

# concrete statements of 12746
two = sp.Integer(2)
even = bool(two % 2 == 0)
prime = bool(sp.isprime(two))
pi_eq_3 = bool(sp.simplify(sp.pi - 3) == 0)
pi_pos = bool(sp.pi.evalf() > 0)
assert (even, prime, pi_eq_3, pi_pos) == (True, True, False, True)

original_1 = even and prime
negation_1 = (not even) or (not prime)          # 2 不是偶數 或 2 不是質數
original_2 = pi_eq_3 or pi_pos
negation_2 = (not pi_eq_3) and (not pi_pos)     # pi != 3 且 pi 不是正數 (pi <= 0)
assert original_1 is True and negation_1 is False
assert original_2 is True and negation_2 is False
assert original_1 != negation_1 and original_2 != negation_2
print("(1) original", original_1, "negation", negation_1)
print("(2) original", original_2, "negation", negation_2)

result = {
    "12746": {
        "verified": {
            "de_morgan_truth_table": True,
            "atoms": {"2是偶數": even, "2是質數": prime, "pi=3": pi_eq_3, "pi是正數": pi_pos},
            "part_1": {"original": original_1, "negation": negation_1},
            "part_2": {"original": original_2, "negation": negation_2},
        }
    }
}
(HERE / "fixed_oracles.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
print("written", HERE / "fixed_oracles.json")
