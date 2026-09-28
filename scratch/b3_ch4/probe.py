import importlib.util
import json
import os
import sys

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")


def load(skill, eid):
    p = f"agent_skills_v3/{skill}/components/src_{eid}/generate.py"
    spec = importlib.util.spec_from_file_location(f"m{eid}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


for skill, eid in [("vh_數學B3_SubSection_3_1_2", 12046), ("vh_數學B3_SubSection_3_1_3", 12050)]:
    p = load(skill, eid).generate(seed=3)
    p.pop("domain_matrix", None)
    keep = {k: p.get(k) for k in ("question_text", "answer", "correct_answer", "semantic_answer", "answer_type", "presentation_mode", "choices", "answer_contract", "stem_structure", "input_fields", "answer_fields", "multi_answer")}
    print(json.dumps(keep, ensure_ascii=False, indent=1, default=str)[:4000])
    print(sorted(p.keys()))
