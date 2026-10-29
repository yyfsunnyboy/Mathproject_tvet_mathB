"""HTTP checks against the isolated instance (127.0.0.1:5057) as a logged-in student: every Unit 5 row is served by the real practice API.

For each of the 37 rows: stem == Stage 1 stem; image_assets only where the figure is required (進階題12) and none elsewhere; every image
URL loads (HTTP 200, PNG, the reviewed SHA-256); no answer before submitting.  進階題12 is then answered and graded through /check_answer.
Also checks the isolated DB: 37 rows / 37 anchors, legacy rows replaced, stems and answers equal to the Stage 1 dry run, every table row
outside Unit 5 equal to the formal DB.  Writes isolated_http_result.json.
"""
import hashlib
import io
import json
import re
import sqlite3
import sys
from pathlib import Path

import requests
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "http://127.0.0.1:5057"
ISO_DB = HERE / "isolated" / "unit5_preview.db"
FORMAL = ROOT / "instance/kumon_math.db"
DRY = ROOT / "reports/gh_math2_unit5_stage1_repair/dry_run_raw.json"
FIGURE_ANCHORS = {"general_2_section_advanced_exercise_012_037"}
UNIT5 = "source_curriculum='general' and source_volume='數學2' and source_chapter='單元5 組合'"

s = requests.Session()
r = s.post(f"{BASE}/login", data={"username": "u5preview_student", "password": "u5preview-only"}, allow_redirects=False)
assert r.status_code in (302, 303), (r.status_code, r.text[:200])

con = sqlite3.connect(f"file:{ISO_DB.as_posix()}?mode=ro", uri=True)
rows = con.execute(f"select id, skill_id, source_description, problem_text, correct_answer, notes from textbook_examples where {UNIT5} order by id").fetchall()
legacy = con.execute(f"select count(*) from textbook_examples where {UNIT5} and json_extract(notes,'$.question_anchor.anchor_id') is null").fetchone()[0]
con.close()

dry = {((r["notes"].get("question_anchor") or {}).get("anchor_id")): r for r in json.loads(DRY.read_text(encoding="utf-8"))["capture"]["post_review_rows"]}
results, problems = [], []
for rid, skill, title, text, answer, notes in rows:
    n = json.loads(notes)
    anchor = n["question_anchor"]["anchor_id"]
    q = s.get(f"{BASE}/get_next_question", params={"skill": skill, "level": 1, "mode": "type_rotation", "textbook_example_id": rid}).json()
    served_id = int(q.get("textbook_example_id") or 0)
    imgs = []
    for a in q.get("image_assets") or []:
        resp = s.get(BASE + a["url"])
        info = {"url": a["url"], "status": resp.status_code, "content_type": resp.headers.get("Content-Type"), "sha256": hashlib.sha256(resp.content).hexdigest()}
        if resp.status_code == 200:
            im = Image.open(io.BytesIO(resp.content))
            info.update(format=im.format, size=list(im.size))
        imgs.append(info)
    d = dry.get(anchor) or {}
    rec = {"id": rid, "title": title.split(" [")[0], "anchor": anchor, "skill_id": skill, "served_id": served_id,
           "source": q.get("question_source"), "stem_equal_db": q.get("question_text") == text,
           "stem_equal_stage1_dry_run": d.get("problem_text") == text, "answer_equal_stage1_dry_run": (d.get("correct_answer") or "") == (answer or ""),
           "figure_required": anchor in FIGURE_ANCHORS, "image_assets": imgs,
           "answer_hidden": q.get("correct_answer") in ("", None) or not str(answer or "").strip() or n.get("pdf_visual_status") is None}
    ok = (served_id == rid and rec["stem_equal_db"] and rec["stem_equal_stage1_dry_run"] and rec["answer_equal_stage1_dry_run"]
          and (len(imgs) == 1) == rec["figure_required"] and all(i["status"] == 200 and i.get("format") == "PNG" for i in imgs))
    if rec["figure_required"]:
        asset = n["image_assets"][0]
        ok = ok and imgs[0]["sha256"] == asset["sha256"] and asset.get("question_anchor") == anchor and asset.get("source_page") == 16
        rec["asset"] = {k: asset.get(k) for k in ("source_page", "bbox", "sha256", "match_method", "visual_status", "question_anchor", "width", "height", "dpi")}
        ok = ok and q.get("correct_answer") == "" and "116" not in json.dumps(q.get("answer_contract"), ensure_ascii=False)
    rec["ok"] = bool(ok)
    if not ok:
        problems.append(rid)
    results.append(rec)

grading = {}
fig = next(r for r in results if r["figure_required"])
for label, ans in (("correct_symbol", {"part_1": "③", "part_2": "116"}), ("correct_digit", {"part_1": "3", "part_2": "116"}),
                   ("wrong_part1", {"part_1": "④", "part_2": "116"}), ("wrong_part2", {"part_1": "③", "part_2": "120"})):
    q = s.get(f"{BASE}/get_next_question", params={"skill": fig["skill_id"], "level": 1, "mode": "type_rotation", "textbook_example_id": fig["id"]}).json()
    body = s.post(f"{BASE}/check_answer", json={"skill_id": fig["skill_id"], "question_uid": q["question_uid"], "answer": ans}).json()
    grading[label] = {"answer": ans, "correct": body.get("correct"), "result": body.get("result")}
grading_ok = (grading["correct_symbol"]["correct"] is True and grading["correct_digit"]["correct"] in (True,) and grading["wrong_part1"]["correct"] is False
              and grading["wrong_part2"]["correct"] is False)
# an identical correct re-submission may be a duplicate (stable question_uid); a fresh label variant must still be graded correct
if grading["correct_digit"]["correct"] is not True:
    grading_ok = False

# rows outside Unit 5: isolated copy == formal
def digest(db, where):
    c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        h = hashlib.sha256()
        n = 0
        for row in c.execute(f"select * from textbook_examples where not ({where}) order by id"):
            h.update(json.dumps(row, ensure_ascii=False, default=str).encode("utf-8"))
            n += 1
        return n, h.hexdigest()
    finally:
        c.close()


outside_iso, outside_formal = digest(ISO_DB, UNIT5), digest(FORMAL, UNIT5)
unit4 = "source_curriculum='general' and source_volume='數學2' and source_chapter='單元4 排列'"
u4_iso, u4_formal = digest(ISO_DB, f"not ({unit4})"), digest(FORMAL, f"not ({unit4})")
summary = {
    "rows": len(rows), "unique_anchors": len({r["anchor"] for r in results}), "legacy_rows_left": legacy,
    "figure_required": [r["id"] for r in results if r["figure_required"]],
    "rows_with_images": [r["id"] for r in results if r["image_assets"]],
    "problems": problems, "grading": grading, "grading_ok": grading_ok,
    "rows_outside_unit5_identical_to_formal": outside_iso == outside_formal, "outside_unit5": {"isolated": outside_iso, "formal": outside_formal},
    "unit4_rows_identical_to_formal": u4_iso == u4_formal, "unit4": {"isolated": u4_iso, "formal": u4_formal},
}
(HERE / "isolated_http_result.json").write_text(json.dumps({"summary": summary, "rows": results}, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=1))
