"""Read-only: every image referenced by production DB rows must exist and be git-tracked."""
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path.cwd()
con = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
tracked = set(
    subprocess.run(["git", "-c", "core.quotepath=false", "ls-files", "static"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
)
refs = {}
cols = [r[1] for r in con.execute("PRAGMA table_info(textbook_examples)")]
text_cols = [c for c in cols if c in ("notes", "image_assets", "problem_text", "detailed_solution", "metadata_json", "visual_assets")]
for row in con.execute(f"SELECT id, skill_id, {', '.join(text_cols)} FROM textbook_examples"):
    eid, skill = row[0], row[1]
    blob = " ".join(str(v or "") for v in row[2:])
    for m in re.findall(r"(?:/?static/)?(question_assets/[^\s\"'\\)>,]+?\.(?:png|jpe?g|gif|svg|webp))", blob, flags=re.I):
        refs.setdefault(m, set()).add((eid, skill))
missing, untracked = [], []
for rel, owners in sorted(refs.items()):
    path = "static/" + rel
    if not (ROOT / path).is_file():
        missing.append((path, sorted(owners)[:3]))
    elif path not in tracked:
        untracked.append((path, sorted(owners)[:3]))
b3 = [r for r, o in refs.items() if any("B3" in s for _, s in o)]
print("columns scanned", text_cols)
print("referenced images", len(refs), "b3", len(b3))
print("missing", len(missing), missing[:10])
print("untracked", len(untracked), untracked[:10])
print("tracked ok", len(refs) - len(missing) - len(untracked))
from collections import Counter
print("missing by volume", Counter(re.search(r"數學B\d", p).group(0) if re.search(r"數學B\d", p) else "?" for p, _ in missing))
names = {}
for f in (ROOT / "static" / "question_assets").rglob("*"):
    if f.is_file():
        names.setdefault(f.name, []).append(f.relative_to(ROOT).as_posix())
alt = [(p, names.get(Path(p).name)) for p, _ in missing]
print("missing with same-name file elsewhere", sum(1 for _, a in alt if a))
print("missing with no copy anywhere", sum(1 for _, a in alt if not a))
print("B3 missing", [p for p, _ in missing if "數學B3" in p])
print("B3 referenced", sorted(p for p in refs if "數學B3" in p))

