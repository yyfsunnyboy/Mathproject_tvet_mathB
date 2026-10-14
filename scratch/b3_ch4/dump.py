import json
import sys

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
ids = [int(x) for x in sys.argv[2:]] or sorted(SOURCE_SPECS)
out = []
for eid in ids:
    spec = SOURCE_SPECS[eid]
    mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
    out.append(f"### {eid} {spec['op']} {spec['presentation']}")
    out.append("Q: " + mat["question_text"].replace("\n", " ⏎ "))
    out.append("A: " + json.dumps(mat["answer"]["value"], ensure_ascii=False))
    if mat.get("part_checkers"):
        out.append("CHK: " + json.dumps(mat["part_checkers"], ensure_ascii=False))
    if mat.get("answer", {}).get("part_labels"):
        out.append("LBL: " + json.dumps(mat["answer"]["part_labels"], ensure_ascii=False))
    for ch in mat.get("choices") or []:
        mark = "*" if ch["label"] == mat.get("correct_label") else " "
        out.append(f"  {mark}{ch['label']} {ch['text']}  [{ch['value']}]")
    facts = mat["validation_facts"]
    if facts.get("given_approximations"):
        out.append("GIVEN: " + json.dumps(facts["given_approximations"], ensure_ascii=False))
    if mat.get("visual_spec", {}).get("kind") != "none":
        vs = mat["visual_spec"]
        out.append(f"VISUAL: curves={len(vs.get('curves') or [])} points={vs.get('points')}")
open("scratch/b3_ch4/dump_out.txt", "w", encoding="utf-8").write("\n".join(out))
print(len(ids))
