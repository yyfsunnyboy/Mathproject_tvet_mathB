import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
rows = json.load(open("scratch/b3_ch4/corpus.json", encoding="utf-8"))
lines = []
keys = set()
for r in rows:
    n = r["notes"] if isinstance(r["notes"], dict) else {}
    keys.update(n.keys())
    extra = {k: n[k] for k in n if any(t in k for t in ("image", "visual", "calc", "skip", "gencode", "exclude"))}
    lines.append(f"### {r['id']} [{r['skill'].replace('SubSection_', '')}] {r['desc']} ({r['ptype']})")
    lines.append("Q: " + (r["q"] or "").replace("\n", " ⏎ "))
    lines.append("A: " + str(r["a"]))
    if extra:
        lines.append("X: " + json.dumps(extra, ensure_ascii=False)[:400])
open("scratch/b3_ch4/compact.txt", "w", encoding="utf-8").write("\n".join(lines))
print(sorted(keys))
