import json
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix
from core.gencode.runtime_skill_wrapper import check_answer
from core.checkers.choice_label_checker import check_choice_label, resolve_choice_semantic

eid = 12249
spec = SOURCE_SPECS[eid]
mat = build_exponential_logarithmic_matrix(0, {"textbook_example_id": eid})
p = adapt_exponential_logarithmic_matrix(mat, domain_operation=spec["op"], presentation_mode=spec["presentation"], component_id=f"src_{eid}", textbook_example_id=eid, seed=0)
print(json.dumps(mat["choices"], ensure_ascii=False))
print("label", mat["correct_label"], "correct_answer", p.get("correct_answer"))
print("payload choices", json.dumps(p.get("choices"), ensure_ascii=False)[:800])
print("contract", json.dumps(p["answer_contract"], ensure_ascii=False)[:800])
for c in mat["choices"]:
    print(c["label"], check_answer(c["label"], p.get("correct_answer"), payload=p),
          resolve_choice_semantic(c["label"], p.get("choices")),
          check_choice_label(c["label"], p.get("correct_answer"), p.get("choices")))
