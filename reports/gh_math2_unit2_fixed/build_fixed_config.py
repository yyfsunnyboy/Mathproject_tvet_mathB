"""Write configs/fixed_textbook_practice.json for the four Unit 2 rows without a Generator (formal DB opened read-only for the stem hashes).

Reference answers come from derive_fixed_oracles.py (vector measurement / symbolic induction check); the induction texts are the reviewed
reference proofs, verified by the same script.  Re-run both scripts after any change.
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from core.fixed_textbook_practice import CONFIG_PATH, stem_sha256  # noqa: E402

oracles = json.loads((HERE / "fixed_oracles.json").read_text(encoding="utf-8"))
RATIONAL = {"presentation_mode": "short_answer", "answer_type": "rational", "checker": "rational_checker", "checker_key": "rational_checker",
            "answer_equivalence": "rational_equivalent", "equivalence": "rational_equivalent", "equivalence_type": "rational_equivalent",
            "answer_shape": "fixed_textbook_rational"}
SCAFFOLD = ["驗證 n=1", "假設 n=k 成立", "推導 n=k+1 成立"]

SPEC = {
    12719: {"skill_id": "gh_Series", "label": "隨堂練習6（圖形題・自動判分）", "mode": "graded", "answer": oracles["12719"]["answer"], "answer_contract": RATIONAL,
            "reference_solution": [
                "正方形 ABCD 的邊長為 2，最大的黑色等腰直角三角形是半個正方形，面積為 $\\frac{1}{2}\\times 2\\times 2=2$。",
                "其餘黑色三角形沿著對角線的另一側依序縮小，每一個的直角邊長都是前一個的一半，所以面積是前一個的 $\\frac{1}{4}$。",
                "五個黑色三角形的面積依序為 $2,\\ \\frac{1}{2},\\ \\frac{1}{8},\\ \\frac{1}{32},\\ \\frac{1}{128}$，成首項 $2$、公比 $\\frac{1}{4}$ 的等比數列。",
                "面積總和 $S_{5}=\\frac{2\\left[1-\\left(\\frac{1}{4}\\right)^{5}\\right]}{1-\\frac{1}{4}}=\\frac{341}{128}$。"]},
    12727: {"skill_id": "gh_Series", "label": "習題基礎題6（圖形題・自動判分）", "mode": "graded", "answer": oracles["12727"]["answer"], "answer_contract": RATIONAL,
            "reference_solution": [
                "$T_{1}$ 是腰長 $AB=1$ 的等腰直角三角形，面積 $\\frac{1}{2}$。",
                "每個三角形的斜邊就是下一個三角形的腰，所以腰長依序是前一個的 $\\sqrt{2}$ 倍，面積是前一個的 $2$ 倍。",
                "五個三角形的面積依序為 $\\frac{1}{2},\\ 1,\\ 2,\\ 4,\\ 8$，成首項 $\\frac{1}{2}$、公比 $2$ 的等比數列。",
                "面積總和 $S_{5}=\\frac{\\frac{1}{2}\\left(2^{5}-1\\right)}{2-1}=\\frac{31}{2}$。"]},
    12731: {"skill_id": "gh_CommonSeriesSummationFormulas", "label": "例題8 平方和公式的歸納法證明（自評）", "mode": "ungraded", "practice_scaffold": SCAFFOLD,
            "reference_solution": [
                "【驗證 $n=1$】左式 $=1^{2}=1$，右式 $=\\frac{1\\times 2\\times 3}{6}=1$，等式成立。",
                "【假設 $n=k$ 成立】$1^{2}+2^{2}+\\cdots +k^{2}=\\frac{k(k+1)(2k+1)}{6}$。",
                "【推導 $n=k+1$ 成立】$1^{2}+2^{2}+\\cdots +k^{2}+(k+1)^{2}=\\frac{k(k+1)(2k+1)}{6}+(k+1)^{2}=\\frac{(k+1)\\left[k(2k+1)+6(k+1)\\right]}{6}=\\frac{(k+1)\\left(2k^{2}+7k+6\\right)}{6}=\\frac{(k+1)(k+2)(2k+3)}{6}$。",
                "這正是 $n=k+1$ 時的右式 $\\frac{(k+1)\\left[(k+1)+1\\right]\\left[2(k+1)+1\\right]}{6}$，所以 $n=k+1$ 也成立。",
                "由數學歸納法，對所有正整數 $n$，$1^{2}+2^{2}+\\cdots +n^{2}=\\frac{n(n+1)(2n+1)}{6}$ 恆成立。"]},
    12735: {"skill_id": "gh_CommonSeriesSummationFormulas", "label": "隨堂練習8 立方和公式的歸納法證明（自評）", "mode": "ungraded", "practice_scaffold": SCAFFOLD,
            "reference_solution": [
                "【驗證 $n=1$】左式 $=1^{3}=1$，右式 $=\\left(\\frac{1\\times 2}{2}\\right)^{2}=1$，等式成立。",
                "【假設 $n=k$ 成立】$1^{3}+2^{3}+\\cdots +k^{3}=\\left[\\frac{k(k+1)}{2}\\right]^{2}$。",
                "【推導 $n=k+1$ 成立】$1^{3}+2^{3}+\\cdots +k^{3}+(k+1)^{3}=\\frac{k^{2}(k+1)^{2}}{4}+(k+1)^{3}=\\frac{(k+1)^{2}\\left[k^{2}+4(k+1)\\right]}{4}=\\frac{(k+1)^{2}(k+2)^{2}}{4}$。",
                "這正是 $n=k+1$ 時的右式 $\\left[\\frac{(k+1)(k+2)}{2}\\right]^{2}$，所以 $n=k+1$ 也成立。",
                "由數學歸納法，對所有正整數 $n$，$1^{3}+2^{3}+\\cdots +n^{3}=\\left[\\frac{n(n+1)}{2}\\right]^{2}$ 恆成立。"]},
}

con = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
entries = {}
for rid, spec in SPEC.items():
    skill, text = con.execute("select skill_id, problem_text from textbook_examples where id=?", (rid,)).fetchone()
    assert skill == spec["skill_id"], (rid, skill)
    entry = {**spec, "problem_text_sha256": stem_sha256(text)}
    if spec["mode"] == "graded":
        entry["oracle"] = {k: oracles[str(rid)][k] for k in ("method", "areas", "page", "bbox")} | {"script": "reports/gh_math2_unit2_fixed/derive_fixed_oracles.py",
                                                                                                   "pdf_sha256": oracles["pdf_sha256"]}
    else:
        entry["oracle"] = {"verified": oracles[str(rid)]["verified"], "script": "reports/gh_math2_unit2_fixed/derive_fixed_oracles.py"}
    entries[str(rid)] = entry
CONFIG_PATH.write_text(json.dumps({"schema": "fixed_textbook_practice.v1", "reviewed": "2026-10-26", "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
print("written", CONFIG_PATH, sorted(entries))
