"""Read-only scan of the same defect classes found in 數學2 單元1 across all 普高 (general) textbook rows.

    python reports/gh_math2_unit1_stage1/scan_common_defects.py [--db <path>]

Heuristic and diagnostic only — nothing is written to any DB. Output: scan_common_defects.json (+ stdout summary).
"""
import json, re, sqlite3, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.stdout.reconfigure(encoding="utf-8")
args = sys.argv[1:]
DB = Path(args[args.index("--db") + 1]) if "--db" in args else ROOT / "instance" / "kumon_math.db"
con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True); con.row_factory = sqlite3.Row
strip_math = lambda t: re.sub(r"\\(.*?\\)|\\[.*?\\]", "", t, flags=re.S)
out = defaultdict(lambda: defaultdict(list))
for r in con.execute("select id,source_volume,source_chapter,problem_type,problem_text,detailed_solution,source_description,notes from textbook_examples where source_curriculum='general' order by id"):
    key = f"{r['source_volume']}|{r['source_chapter']}"
    t, s = r["problem_text"] or "", r["detailed_solution"] or ""
    try: n = json.loads(r["notes"] or "{}")
    except Exception: n = {}
    d = out[key]; d["rows"].append(r["id"])
    if re.match(r"^\s*[，。、：；中的之裡]", t): d["H1_fragment_stem(pseudo item)"].append(r["id"])
    if re.search(r"[A-Za-z0-9\)]\s{2,}[A-Za-z0-9]", t + "\n" + s): d["H2_lost_symbol_gap"].append(r["id"])
    if re.search(r"(?<![A-Za-z0-9])[a-zA-Z]\d(?![\d])", strip_math(t)) and r["problem_type"] != "textbook_example": d["H3_possible_lost_superscript"].append(r["id"])
    if r["problem_type"] in ("in_class_practice", "basic_exercise", "advanced_exercise", "chapter_exercise") and re.search(r"(如下圖所示|依序數數字|如右圖所示|如圖所示)[：。]?\s*$", t) and "(1)" not in t and "求" not in t: d["H4_stem_ends_at_figure_leadin"].append(r["id"])
    if "證明" in t and t.strip().endswith(r"\)") and not re.search("恆|成立|倍數|整除", strip_math(t).split("證明")[-1]): d["H5_proof_without_claim"].append(r["id"])
    if n.get("needs_review"): d["F1_needs_review"].append(r["id"])
    if n.get("visual_required_missing") or n.get("pdf_visual_status") == "VISUAL_REQUIRED_MISSING": d["F2_visual_required_missing"].append(r["id"])
    if n.get("review_required_by_confidence"): d["F3_low_confidence"].append(r["id"])
    if "needs_review=true" in (r["source_description"] or ""): d["F4_needs_review_in_description"].append(r["id"])
# practice numbering continuity per chapter
for key in list(out):
    nums = sorted(int(re.search(r"隨堂練習(\d+)", c["source_description"]).group(1)) for c in con.execute(
        "select source_description from textbook_examples where source_curriculum='general' and source_volume=? and source_chapter=? and problem_type='in_class_practice'", tuple(key.split("|"))) if re.search(r"隨堂練習(\d+)", c["source_description"]))
    if nums and nums != list(range(1, len(nums) + 1)): out[key]["H6_practice_numbering_gap"].append(nums)
summary = {k: {h: (v if h == "rows" and False else (len(v) if h == "rows" else v)) for h, v in d.items()} for k, d in out.items()}
(HERE / "scan_common_defects.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
for k, d in sorted(summary.items()):
    flags = {h: v for h, v in d.items() if h != "rows"}
    print(f"{k:45s} rows={d['rows']:3d}", ({h: (len(v) if isinstance(v, list) and v and not isinstance(v[0], list) else v) for h, v in flags.items()} or "clean"))
