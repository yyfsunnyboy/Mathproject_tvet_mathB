import importlib, json, sys

eid = int(sys.argv[1]) if len(sys.argv) > 1 else 12127
import glob
path = glob.glob(f"agent_skills_v3/vh_數學B3_SubSection_4_*/components/src_{eid}/generate.py")[0].replace("\\", "/").split("/")
mod = importlib.import_module(f"agent_skills_v3.{path[1]}.components.{path[3]}.generate")
p = mod.generate(seed=11)
print("Q:", p["question_text"])
print("stem_structure:", json.dumps(p.get("stem_structure"), ensure_ascii=False)[:600])
c = p.get("answer_contract") or {}
for part in c.get("parts") or []:
    print("PART", json.dumps({k: part.get(k) for k in ("key", "label", "prompt", "display_label", "field_label", "placeholder", "input_type", "choices")}, ensure_ascii=False))
for k in ("subquestions", "answer_fields", "fields", "input_fields"):
    if p.get(k):
        print(k, json.dumps(p[k], ensure_ascii=False)[:800])
ui = p.get("ui_contract") or {}
print("ui", json.dumps(ui, ensure_ascii=False)[:800])
print("keys", sorted(p.keys()))
