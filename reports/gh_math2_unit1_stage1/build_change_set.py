"""Diff the sandbox copy against production (read-only) -> production_change_set.json + row_diff.md.

Describes the exact minimal change set a future, explicitly authorised production apply must contain.
Nothing here writes to any database.
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.stdout.reconfigure(encoding="utf-8")
P = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
P.row_factory = sqlite3.Row
S = sqlite3.connect(f"file:{(HERE / 'sandbox' / 'kumon_math_copy.db').as_posix()}?mode=ro", uri=True)
S.row_factory = sqlite3.Row
Q = "select * from textbook_examples where id between 12667 and 12706"
pr = {r["id"]: dict(r) for r in P.execute(Q)}
sr = {r["id"]: dict(r) for r in S.execute(Q)}


def _fp(row, cols):
    """Fingerprint of the production values this op replaces; an apply refuses to run when they have drifted."""
    return hashlib.sha256(json.dumps({c: row[c] for c in cols}, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def short(t, n=70):
    t = (t or "").replace("\n", " ⏎ ")
    return t if len(t) <= n else t[:n] + "…"


ops, md = [], ["| id | 題目 | 變更欄位 | 修復前 → 修復後 |", "|---|---|---|---|"]
for i in sorted(pr):
    a, b = pr[i], sr.get(i)
    label = a["source_description"].split(" [")[0]
    if b is None:
        ops.append({"op": "delete", "table": "textbook_examples", "id": i, "expected_before_sha256": _fp(a, ("problem_text", "detailed_solution", "source_description", "notes"))})
        md.append(f"| {i} | {label} | 刪除偽題 | {short(a['problem_text'])} → （移除） |")
        continue
    na, nb = json.loads(a["notes"]), json.loads(b["notes"])
    ch = [c for c in ("problem_text", "detailed_solution", "source_description", "notes") if a[c] != b[c]]
    if not ch:
        continue
    desc = []
    if a["problem_text"] != b["problem_text"]:
        desc.append(f"題幹：{short(a['problem_text'], 40)} → {short(b['problem_text'], 60)}")
    if a["detailed_solution"] != b["detailed_solution"]:
        desc.append("詳解符號 `b␣1` → `b-1`")
    if a["source_description"] != b["source_description"]:
        desc.append(f"標籤：{a['source_description'].split(' [')[0]} → {b['source_description'].split(' [')[0]}；"
                    f"{short(a['source_description'].split(' [')[1], 45)} → {short(b['source_description'].split(' [')[1], 45)}")
    if na.get("image_assets") != nb.get("image_assets"):
        desc.append(f"圖片 {len(na.get('image_assets') or [])} → {len(nb.get('image_assets') or [])}")
    if na.get("needs_review") != nb.get("needs_review"):
        desc.append(f"needs_review {na.get('needs_review')} → {nb.get('needs_review')}（附人工核對證據）")
    ops.append({"op": "update", "table": "textbook_examples", "id": i, "columns": ch, "new": {c: b[c] for c in ch},
                "expected_before_sha256": _fp(a, ch)})
    md.append(f"| {i} | {label} | {', '.join(ch)} | {'；'.join(desc)} |")

files = []
for p in sorted((HERE / "sandbox" / "uploads").rglob("*.png")):
    files.append({"copy_to": p.relative_to(HERE / "sandbox").as_posix(),
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
(HERE / "production_change_set.json").write_text(json.dumps({
    "scope": "textbook_examples id 12667-12706 only (source_chapter = 單元1 數列與遞迴關係)",
    "db_ops": ops,
    "asset_files": files,
    "obsolete_prod_assets": [
        "uploads/question_assets/.../in_class_practice_隨堂練習2_...fig1.png (mis-cropped hand/sloth; replaced at a new path)",
        "…_隨堂練習9_…_needs_reviewtrue_…fig1.png and …_隨堂練習12_…_needs_reviewtrue_…fig1.png (renamed to 隨堂練習8 / 隨堂練習11)",
    ],
}, ensure_ascii=False, indent=1), encoding="utf-8")
(HERE / "row_diff.md").write_text("\n".join(md), encoding="utf-8")
print(len(ops), "db ops;", len(files), "asset files;",
      sum(o["op"] == "delete" for o in ops), "delete;", sum(o["op"] == "update" for o in ops), "update")
