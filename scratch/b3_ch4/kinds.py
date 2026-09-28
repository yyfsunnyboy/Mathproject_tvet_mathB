import json
from collections import Counter

rows = json.load(open("scratch/b3_ch4/corpus.json", encoding="utf-8"))
print(Counter(r["ptype"] for r in rows))
print(Counter(r["skill"] for r in rows))
line = []
for r in rows:
    line.append(f"{r['id']}:{r['skill'].split('SubSection_')[-1]}:{r['ptype']}")
print(" ".join(line))
