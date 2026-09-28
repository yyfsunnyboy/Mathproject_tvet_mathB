import json
from core.domain.exponential_logarithmic_domain import build_exponential_logarithmic_matrix
from core.gencode import domain_matrix_adapter as dma
from core.gencode import single_choice_payload_normalizer as scn

ctx = {"skill_id": "vh_數學B3_SubSection_4_1_3", "problem_type_id": "exp_growth_decay_model_choice",
       "textbook_example_id": 12135, "presentation": "single_choice"}
matrix = build_exponential_logarithmic_matrix(11, ctx)
print("MATRIX", json.dumps(matrix.get("choices") or matrix.get("answer", {}).get("choices"), ensure_ascii=False)[:400])
for k in ("choices", "distractors"):
    if k in matrix:
        print(k, json.dumps(matrix[k], ensure_ascii=False)[:300])
print(json.dumps({k: (v if k != "choices" else None) for k, v in matrix.get("answer", {}).items()}, ensure_ascii=False)[:600])

orig = scn.normalize_single_choice_payload
def traced(payload):
    print("PRE-NORMALIZE", json.dumps(payload.get("choices"), ensure_ascii=False)[:300])
    out = orig(payload)
    print("POST-NORMALIZE", json.dumps(out.get("choices"), ensure_ascii=False)[:300])
    return out
scn.normalize_single_choice_payload = traced
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix
p = adapt_exponential_logarithmic_matrix(matrix, domain_operation="exp_growth_decay_model_choice",
    presentation_mode="single_choice", answer_type="single_choice", component_id="src_12135",
    textbook_example_id=12135, seed=11)
print("FINAL", json.dumps(p["choices"][0], ensure_ascii=False))
