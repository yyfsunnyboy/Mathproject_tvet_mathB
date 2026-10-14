import json
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix
from core.gencode.choice_contract_validator import validate_choice_answer_shapes, infer_choice_answer_shape
from core.gencode.vocational_choice_contract import __file__ as vcc

print(vcc)
bad = {}
for eid, spec in sorted(SOURCE_SPECS.items()):
    if spec["presentation"] != "single_choice":
        continue
    for seed in range(40):
        mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
        p = adapt_exponential_logarithmic_matrix(mat, domain_operation=spec["op"], presentation_mode="single_choice", component_id=f"src_{eid}", textbook_example_id=eid, seed=seed)
        errs = validate_choice_answer_shapes(p)
        if errs:
            bad.setdefault(eid, []).append(seed)
            if len(bad[eid]) == 1:
                print(eid, spec["op"], "semantic=", p.get("semantic_answer"), "display=", p.get("display_answer"))
                for c in p["choices"]:
                    print("   ", infer_choice_answer_shape(c.get("value") or c.get("text")), c.get("value"))
print({k: len(v) for k, v in bad.items()})
