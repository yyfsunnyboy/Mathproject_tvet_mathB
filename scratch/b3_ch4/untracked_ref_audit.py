"""Does any tracked file reference an untracked path (by basename or module name)?"""
import subprocess
from pathlib import Path

ROOT = Path.cwd()
git = lambda *a: subprocess.run(["git", "-c", "core.quotepath=false", *a], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
untracked = [p for p in git("ls-files", "--others", "--exclude-standard") if p]
tracked = [p for p in git("ls-files") if p.endswith((".py", ".js", ".html", ".json", ".md", ".ini", ".toml", ".cfg", ".yml", ".yaml", ".txt"))]
tracked_text = {}
for p in tracked:
    try:
        tracked_text[p] = (ROOT / p).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        pass
print("untracked files", len(untracked))
hits = {}
for u in untracked:
    stem = Path(u).stem
    needles = {Path(u).name}
    if u.endswith(".py"):
        needles.add(u[:-3].replace("/", "."))
        needles.add(stem if len(stem) > 12 else Path(u).name)
    for p, text in tracked_text.items():
        if any(n in text for n in needles):
            hits.setdefault(u, []).append(p)
for u, ps in sorted(hits.items()):
    print("REF", u, "<-", ps[:5])
print("untracked referenced by tracked files:", len(hits))
