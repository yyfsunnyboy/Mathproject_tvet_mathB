"""Stage 1 驗證（隔離 DB 複本）：普高數學2 單元1「數列與遞迴關係」。

    python reports/gh_math2_unit1_stage1/verify_stage1.py [--db <path>] [--label before|after]

預設驗證 sandbox 複本；`--db` 可指向任何 DB 檔（唯讀開啟）。以 PASS/FAIL 逐項輸出並寫 verify_<label>.json，
有 FAIL 時結束碼為 1。本腳本不寫任何 DB。
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")
from core.textbook_pdf_visual import fingerprint_file  # noqa: E402

args = sys.argv[1:]
DB = Path(args[args.index("--db") + 1]) if "--db" in args else HERE / "sandbox" / "kumon_math_copy.db"
LABEL = args[args.index("--label") + 1] if "--label" in args else "after"
ASSET_ROOT = DB.parent  # sandbox/uploads/... ; for a prod-DB check the paths resolve under ROOT instead
if not (ASSET_ROOT / "uploads").exists():
    ASSET_ROOT = ROOT
DOCX = ROOT / "textbook_import/uploaded_sources/general/數學2/742ea24d3d43_單元01-數列與遞迴關係.docx"
PDF = ROOT / "textbook_import/uploaded_sources/general/數學2/f2bef2bd0e2b_單元01-數列與遞迴關係.pdf"
DOCX_SHA = "742ea24d3d43c759b659f2390e36871a781c34405fe86176ae7d494076146b38"
PDF_SHA = "f2bef2bd0e2bf87494da3b9777a41f2a2ed894ee73ee182746db3d33f81e1789"
CHAPTER = "單元1 數列與遞迴關係"
EXPECT_TOTAL = {"textbook_example": 11, "in_class_practice": 11, "exercise": 17}
EXERCISE_SKILL = {  # 習題逐題依數學內容核對（稽核報告 §2）；key = 習題標籤
    "觀念澄清1": "gh_Sequence", "觀念澄清2": "gh_Sequence", "觀念澄清3": "gh_Sequence", "觀念澄清4": "gh_RecursiveRelation",
    "觀念澄清5": "gh_Sequence", "基礎題1": "gh_Sequence", "基礎題2": "gh_Sequence", "基礎題3": "gh_Sequence",
    "基礎題4": "gh_Sequence", "基礎題5": "gh_RecursiveRelation", "基礎題6": "gh_RecursiveRelation",
    "基礎題7": "gh_RecursiveRelation", "基礎題8": "gh_RecursiveRelation", "進階題9": "gh_RecursiveRelation",
    "進階題10": "gh_Sequence", "進階題11": "gh_MathematicalInduction", "進階題12": "gh_RecursiveRelation",
}
SPAN_SKILL = {"甲": "gh_Sequence", "乙": "gh_RecursiveRelation", "丙": "gh_MathematicalInduction"}

results: list[dict] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append({"check": name, "result": "PASS" if ok else "FAIL", "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def cjk(s: str) -> str:
    s = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", "", s, flags=re.S)
    return "".join(ch for ch in s if "一" <= ch <= "鿿")


# ---------------------------------------------------------------- DOCX structure
def docx_paragraphs() -> list[str]:
    x = zipfile.ZipFile(DOCX).read("word/document.xml").decode("utf8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S):
        out.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)).strip())
    return out


paras = docx_paragraphs()
seq: list[tuple[str, int, str, str]] = []  # (type, number, linked_example, span_skill)
span, ex_no, pr_no, last_ex = "", 0, 0, ""
for t in paras:
    m = re.match(r"^([甲乙丙])\s+\S", t)
    if m and len(t) < 16:
        span = SPAN_SKILL[m.group(1)]
    if re.fullmatch(r"例題\d+", t):
        ex_no = int(t[2:]); last_ex = t
        seq.append(("textbook_example", ex_no, "", span))
    elif t == "隨堂練習":
        pr_no += 1
        seq.append(("in_class_practice", pr_no, last_ex, span))
    elif t == "1習題":
        break

con = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute(
    "select * from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter=? order by id", (CHAPTER,))]
for r in rows:
    r["n"] = json.loads(r["notes"])
    r["label"] = r["source_description"].split(" [")[0].replace(" ", "")
    r["qa"] = r["n"]["question_anchor"]

# ---------------------------------------------------------------- 1 count / source
kinds = Counter("exercise" if r["qa"]["question_type"] in ("exercise", "advanced_exercise") or r["problem_type"].endswith("exercise") else r["problem_type"] for r in rows)
check("題目數量 = 39（11 例題 + 11 隨堂練習 + 17 習題）", len(rows) == 39 and dict(kinds) == EXPECT_TOTAL, f"rows={len(rows)} {dict(kinds)}")
check("範圍內無偽題（不含以句號外標點開頭的碎片）", not any(re.match(r"^[，。、：；中的之]", r["problem_text"]) for r in rows))
check("來源檔存在且完整 SHA-256 吻合", fingerprint_file(DOCX) == DOCX_SHA and fingerprint_file(PDF) == PDF_SHA)
prov_bad = [r["id"] for r in rows if r["n"].get("source_provenance", {}).get("primary", {}).get("sha256") != DOCX_SHA
            or r["n"]["source_provenance"].get("optional_enrich_pdf", {}).get("sha256") != PDF_SHA]
check("40→39 題 source_provenance 皆指向已驗證 DOCX/PDF 雜湊", not prov_bad, str(prov_bad))

# ---------------------------------------------------------------- 2 order / anchors / linked
doc_order = [(t, n) for t, n, _, _ in seq]
db_order = [(r["problem_type"], int(r["qa"]["question_number"])) for r in sorted(rows, key=lambda r: r["qa"]["source_order"]) if r["problem_type"] in ("textbook_example", "in_class_practice")]
check("例題/隨堂練習順序與 DOCX 標題順序一致", db_order == doc_order, f"db={len(db_order)} docx={len(doc_order)}")
practices = sorted(int(r["qa"]["question_number"]) for r in rows if r["problem_type"] == "in_class_practice")
check("隨堂練習編號連續 1..11", practices == list(range(1, 12)), str(practices))
lk = {(r["problem_type"], int(r["qa"]["question_number"])): (re.search(r"linked_example=(例題\d+)", r["source_description"]) or [None, ""])[1] for r in rows}
bad_link = [(n, lk.get(("in_class_practice", n)), e) for t, n, e, _ in seq if t == "in_class_practice" and lk.get((t, n)) != e]
check("隨堂練習 linked_example 與 DOCX 相鄰例題一致", not bad_link, str(bad_link))
lab_bad = [r["id"] for r in rows if r["problem_type"] in ("in_class_practice", "textbook_example")
           and r["qa"]["question_label"].replace("例", "例題") .replace("例題題", "例題") != r["label"]]
check("anchor_id 唯一、question_label 與 source_description 標籤一致", len({r["qa"]["anchor_id"] for r in rows}) == len(rows) and not lab_bad, str(lab_bad))
mism = [r["id"] for r in rows if r["problem_type"] in ("in_class_practice", "textbook_example")
        and f"_{int(r['qa']['question_number']):03d}_" not in r["qa"]["anchor_id"]]
check("anchor_id / anchor_key 內的題號與 question_number 一致", not mism, str(mism))

# ---------------------------------------------------------------- 3 skill binding
sk_bad = []
span_by = {(t, n): s for t, n, _, s in seq}
for r in rows:
    key = (r["problem_type"], int(r["qa"]["question_number"]))
    if key in span_by:
        exp = span_by[key]
    else:
        exp = EXERCISE_SKILL.get(re.sub(r"^1習題", "", r["label"]))
    if exp != r["skill_id"]:
        sk_bad.append((r["id"], r["label"], r["skill_id"], exp))
check("每題 Skill 綁定：例題/隨堂練習依 heading span、習題依內容核對", not sk_bad, str(sk_bad))
sc = [tuple(r) for r in con.execute("select skill_id,display_order from skill_curriculum where curriculum='general' and volume='數學2' and chapter=? order by display_order", (CHAPTER,))]
check("skill_curriculum 僅 3 筆且順序 甲乙丙", [s for s, _ in sc] == ["gh_Sequence", "gh_RecursiveRelation", "gh_MathematicalInduction"], str(sc))
act = [tuple(r) for r in con.execute("select skill_id,is_active from skills_info where skill_id in ('gh_Sequence','gh_RecursiveRelation','gh_MathematicalInduction')")]
check("3 個 Skill 於 skills_info 皆啟用", len(act) == 3 and all(a == 1 for _, a in act), str(act))
check("題目 skill 皆存在於 skill_curriculum 綁定", {r["skill_id"] for r in rows} <= {s for s, _ in sc})

# ---------------------------------------------------------------- 4 math / stem integrity
fmt_bad = []
for r in rows:
    for col in ("problem_text", "detailed_solution"):
        t = r[col] or ""
        if "MATH_PARSE_FAILED" in t or "[MATH" in t or t.count("\\(") != t.count("\\)") or "\\(\\)" in t:
            fmt_bad.append((r["id"], col, "parse/unbalanced"))
        if re.search(r"[A-Za-z0-9\)]\s{2,}[A-Za-z0-9]", t):
            fmt_bad.append((r["id"], col, "gap(lost symbol?)"))
        if re.sub(r"\\[{}]", "", t).count("{") != re.sub(r"\\[{}]", "", t).count("}"):
            fmt_bad.append((r["id"], col, "brace"))
    if r["n"].get("math_warnings"):
        fmt_bad.append((r["id"], "notes", "math_warnings"))
check("公式：無 MATH_PARSE_FAILED、括號/大括號平衡、無符號遺失空隙", not fmt_bad, str(fmt_bad))
sup_bad = [r["id"] for r in rows if re.search(r"(?<![A-Za-z0-9])r2(?!\d)", re.sub(r"\\\(.*?\\\)", "", r["problem_text"]))]
check("無 'r2' 型上標遺失", not sup_bad, str(sup_bad))

TERMINAL = ("。", "？", "！", "）", "」", ")", "?", "\\)", "…", "：")
trunc = []
for r in rows:
    t = r["problem_text"].rstrip()
    sub = re.findall(r"\((\d)\)", t)
    if not t.endswith(TERMINAL[:-1]):
        trunc.append((r["id"], "no terminal punctuation", t[-12:]))
    if sub and sub != [str(i) for i in range(1, len(sub) + 1)]:
        trunc.append((r["id"], "sub-question numbering", sub))
    if re.search(r"(如下圖所示|依序數數字|如右圖所示)[：。]?$", t) and r["problem_type"] != "textbook_example" and "(1)" not in t:
        trunc.append((r["id"], "stem ends at figure lead-in without question", t[-15:]))
    if re.search(r"證明：.*\n.*\\\)$", t, flags=re.S):
        trunc.append((r["id"], "proof stem lacks claim ('恆為…')", t[-15:]))
check("題幹完整性：結尾標點、小題編號連續、無『只剩引導句』、證明題含結論", not trunc, str(trunc))

# DOCX 文字覆蓋：DOCX 例題/隨堂練習/習題區的每個中文段落，須在 DB 題幹/詳解/備份中找到（略去敘述性教材）
corpus = "".join(cjk(r["problem_text"]) + cjk(r["detailed_solution"] or "") + cjk(r["n"].get("raw_problem_backup", "")) for r in rows)
start = next(i for i, t in enumerate(paras) if t == "例題1")
region = paras[start:]
unfound = []
for t in region:
    k = cjk(t)
    if len(k) >= 8 and k not in corpus:
        unfound.append(t[:60])
cov = 1 - len(unfound) / max(1, sum(1 for t in region if len(cjk(t)) >= 8))
check("DOCX 中文段落覆蓋（informational：未覆蓋者應為教材敘述，詳見 verify JSON）", True, f"coverage={cov:.2%} unfound={len(unfound)}")

# ---------------------------------------------------------------- 5 images
CUE = re.compile(r"如下圖|如右圖|右圖|下圖所示|如圖")
img_bad, evidence_bad = [], []
orig_review = {r["id"] for r in rows if r["n"].get("needs_review")}
for r in rows:
    n = r["n"]
    assets = n.get("image_assets") or []
    need = bool(CUE.search(r["problem_text"])) or n.get("image_role") == "required_diagram"
    if need and not assets:
        img_bad.append((r["id"], "required figure without asset"))
    if n.get("visual_required_missing") or n.get("needs_image_review") or n.get("image_warning"):
        img_bad.append((r["id"], "visual flags unresolved"))
    for a in assets:
        p = ASSET_ROOT / a["path"]
        if not p.exists():
            img_bad.append((r["id"], f"missing file {a['path'][-40:]}")); continue
        if fingerprint_file(p) != a["sha256"]:
            img_bad.append((r["id"], "sha mismatch"))
        if not (1 <= a["source_page"] <= 24) or a["width"] < 150 or a["height"] < 60:
            img_bad.append((r["id"], f"geometry {a['width']}x{a['height']}"))
        if a.get("question_anchor") != r["qa"]["anchor_id"]:
            img_bad.append((r["id"], "asset anchor != row anchor"))
    if re.search(r"（單選）\s*\n?\s*①[　 ]*②", r["problem_text"]) and r["problem_text"].count("①") and "大拇指" not in r["problem_text"] and len(assets) < 2:
        img_bad.append((r["id"], "image-option MCQ needs 2 assets"))
check("圖片：必要圖皆有資產、檔案存在、SHA 吻合、頁碼/尺寸合理、錨點一致、無未解旗標", not img_bad, str(img_bad))
check("needs_review：全數為 False（且曾被標記者皆有人工核對證據）",
      not any(r["n"].get("needs_review") for r in rows), "needs_review True ids=" + str([r["id"] for r in rows if r["n"].get("needs_review")]))
ev = [r["id"] for r in rows if r["id"] in (12668, 12673, 12686, 12687, 12688, 12690, 12694, 12695, 12698, 12699, 12702) and not r["n"].get("manual_visual_review")] \
    + [r["id"] for r in rows if r["id"] in (12692, 12705) and not r["n"].get("manual_stem_review")]
check("被標記過的 13 題皆保存 manual_visual_review / manual_stem_review 證據", not ev, str(ev))
check("12673 圖為完整的手指計數圖（非吉祥物誤裁）", (lambda a: bool(a) and a[0]["bbox"][0] >= 390 and a[0]["bbox"][3] - a[0]["bbox"][1] < 200)(
    [x for r in rows if r["id"] == 12673 for x in r["n"].get("image_assets", [])]))

# ---------------------------------------------------------------- 6 other chapters untouched (only meaningful on sandbox copy)
prod = ROOT / "instance" / "kumon_math.db"
if DB.resolve() != prod.resolve():
    pc = sqlite3.connect(f"file:{prod.as_posix()}?mode=ro", uri=True)
    q = "select id,skill_id,source_chapter,problem_text,notes from textbook_examples where not (id between 12667 and 12706) order by id"
    same = [tuple(r) for r in pc.execute(q)] == [tuple(r) for r in con.execute(q)]
    check("範圍外 textbook_examples 與正式庫逐列相同", same)
    for t in ("skill_curriculum", "skills_info", "gencode_component_tracker"):
        a = [tuple(r) for r in pc.execute(f"select * from {t}")]
        b = [tuple(r) for r in con.execute(f"select * from {t}")]
        check(f"{t} 與正式庫相同", a == b)
    pc.close()

fails = [r for r in results if r["result"] == "FAIL"]
print(f"\nSTAGE1 {'READY' if not fails else 'BLOCKED'}: {len(results) - len(fails)}/{len(results)} PASS")
(HERE / f"verify_{LABEL}.json").write_text(json.dumps({"db": str(DB.relative_to(ROOT)) if ROOT in DB.parents else str(DB), "rows": len(rows),
                                                     "results": results, "docx_unfound_paragraphs": unfound,
                                                     "verdict": "READY" if not fails else "BLOCKED"}, ensure_ascii=False, indent=1), encoding="utf-8")
sys.exit(1 if fails else 0)
