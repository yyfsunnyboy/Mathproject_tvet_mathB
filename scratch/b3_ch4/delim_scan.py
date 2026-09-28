import importlib, json, re
from collections import Counter
import glob, os

bad = Counter()
examples = {}
n = 0


def wellformed(text):
    if not isinstance(text, str):
        return True
    for seg in re.findall(r"\$(.*?)\$", text, flags=re.S):
        if "\\(" in seg or "\\)" in seg:
            return False
    stripped = re.sub(r"\$.*?\$", "", text, flags=re.S)
    depth = 0
    for tok in re.findall(r"\\\(|\\\)", stripped):
        depth += 1 if tok == "\\(" else -1
        if depth not in (0, 1):
            return False
    return depth == 0 and stripped.count("$") == 0


for comp in sorted(glob.glob("agent_skills_v3/vh_數學B3_SubSection_4_*/components/src_*/generate.py")):
    parts = comp.replace("\\", "/").split("/")
    mod = importlib.import_module(f"agent_skills_v3.{parts[1]}.components.{parts[3]}.generate")
    for seed in range(20):
        p = mod.generate(seed=seed)
        n += 1
        fields = {"question_text": p.get("question_text")}
        for i, c in enumerate(p.get("choices") or []):
            fields[f"c{i}.text"] = c.get("text")
            fields[f"c{i}.display"] = c.get("display")
        for i, o in enumerate(p.get("options") or []):
            fields[f"o{i}"] = o
        for k in ("correct_answer_display", "display_answer", "answer_display"):
            if k in p:
                fields[k] = p.get(k)
        for k, v in fields.items():
            if not wellformed(v):
                key = (parts[3], k.split(".")[0][:1] + k.split(".")[-1] if k.startswith(("c", "o")) and k[1:2].isdigit() else k)
                bad[(parts[3], mod.PROBLEM_TYPE_ID)] += 1
                examples.setdefault((parts[3], mod.PROBLEM_TYPE_ID), (k, v))
print("payloads", n, "bad", sum(bad.values()))
for k, c in bad.most_common():
    print(k, c, examples[k])
