import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
from _b3_ch4_tex import math_segments, tex_to_sympy  # noqa: E402
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix  # noqa: E402

for eid, spec in sorted(SOURCE_SPECS.items()):
    if spec["op"] != "exp_rational_exponent_simplify":
        continue
    for seed in range(12):
        m = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
        texts = [i["text"] for i in (m.get("stem_structure") or {}).get("items") or []] or [m["question_text"]]
        for text in texts:
            segs = math_segments(text)
            seg = max(segs, key=len)
            try:
                expr = tex_to_sympy(seg.split("=", 1)[-1] if not seg.endswith("=") else seg[:-1])
            except Exception as exc:  # noqa: BLE001
                print("PARSE", eid, seed, seg, exc)
                break
            item = {"text": text}
            syms = {str(s) for s in expr.free_symbols} - {"a", "b"}
            if syms:
                print("SYM", eid, seed, syms, item["text"])
                break

for eid, spec in sorted(SOURCE_SPECS.items()):
    m = build_exponential_logarithmic_matrix(3, {"textbook_example_id": eid})
    for key, value in (m["validation_facts"].get("given_approximations") or {}).items():
        if key.startswith("log ") and str(value) not in m["question_text"]:
            print("GIVEN", eid, spec["op"], key, repr(value), m["question_text"][:160])

for eid, spec in sorted(SOURCE_SPECS.items()):
    if spec["op"] == "common_log_table_lookup":
        m = build_exponential_logarithmic_matrix(3, {"textbook_example_id": eid})
        print("TABLE", eid, json.dumps(m["stem_structure"], ensure_ascii=False)[-400:], m["answer"]["value"])
