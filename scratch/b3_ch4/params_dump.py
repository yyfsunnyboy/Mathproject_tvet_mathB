import json
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix

seen = {}
for eid, spec in sorted(SOURCE_SPECS.items()):
    key = (spec["op"], spec["presentation"])
    if key in seen:
        continue
    seen[key] = eid
out = []
for (op, pres), eid in sorted(seen.items()):
    mat = build_exponential_logarithmic_matrix(5, {"textbook_example_id": eid})
    out.append(f"## {op} [{pres}] eid={eid}")
    out.append("Q: " + mat["question_text"].replace("\n", " / ")[:400])
    out.append("A: " + json.dumps(mat["answer"]["value"], ensure_ascii=False))
    out.append("P: " + json.dumps(mat.get("params"), ensure_ascii=False, default=str)[:400])
    out.append("G: " + json.dumps(mat["validation_facts"].get("given_approximations"), ensure_ascii=False, default=str)[:200])
with open("scratch/b3_ch4/params_out.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))
print(len(seen))
