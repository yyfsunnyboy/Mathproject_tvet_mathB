# -*- coding: utf-8 -*-
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
out_lines = []

def p(*a):
    out_lines.append(" ".join(str(x) for x in a))

conn = sqlite3.connect(ROOT / "instance" / "kumon_math.db")
conn.row_factory = sqlite3.Row
ids = [4628, 4718, 4719, 4720, 4627, 4612, 4609]
for eid in ids:
    r = conn.execute(
        "SELECT id, skill_id, problem_type, source_description, substr(problem_text,1,200) AS t FROM textbook_examples WHERE id=?",
        (eid,),
    ).fetchone()
    p("---", eid)
    p("type", r["problem_type"])
    p("src", r["source_description"])
    p("text", (r["t"] or "").replace("\n", " "))

from core.gencode.skill_fixed_domain_authority import resolve_domain_authority

for pt in [
    "polynomial_add_sub",
    "polynomial_remainder_param_solve",
    "polynomial_long_division",
]:
    res = resolve_domain_authority(
        skill_id="vh_數學B1_PolynomialArithmeticOperations",
        problem_type_id=pt,
    )
    p(
        "resolve",
        pt,
        "domain=",
        res.fixed_domain_key,
        "selected=",
        res.selected_operation,
        "entry=",
        res.entrypoint,
    )

from core.registry.domain_operation_registry import get_operation_spec

spec = get_operation_spec("algebra.polynomial", "polynomial_add_sub")
p(
    "op_spec",
    getattr(spec, "handler", None),
    getattr(spec, "supported_presentation_modes", None),
    getattr(spec, "supported_answer_types", None),
)

from agent_skills_v3.vh_數學B1_PolynomialArithmeticOperations.components.src_4627 import generate as g

pl = g.generate(seed=1)
ans = pl.get("answer")
p("smoke4627 answer", type(ans).__name__, repr(ans)[:200])
p("presentation", pl.get("presentation_mode"), pl.get("answer_type"))

# also smoke add_sub which might be multi-part
from agent_skills_v3.vh_數學B1_PolynomialArithmeticOperations.components.src_4612 import generate as g2
pl2 = g2.generate(seed=1)
p("smoke4612 answer", type(pl2.get("answer")).__name__, repr(pl2.get("answer"))[:200])
p("smoke4612 modes", pl2.get("presentation_mode"), pl2.get("answer_type"))

data = json.loads((ROOT / "scratch/_b1_3_1_report_data.json").read_text(encoding="utf-8"))
p("TABLE")
for r in data["rows"]:
    p(
        r["example_id"],
        r["problem_type_id"],
        r["component_status"],
        r["prod_exists"],
        r["manifest_status"],
        r["metadata_readiness"],
    )

text = "\n".join(out_lines)
(ROOT / "scratch/_b1_3_1_final_checks_out.txt").write_text(text, encoding="utf-8")
print("wrote", len(out_lines), "lines")
