"""Existing skills (vocational B3 sequence domain, vocational B1, junior high, earlier general-high units) and the unpublished
gh_MathematicalInduction behave as before, through the real routes of a production-configured app on an ISOLATED database copy.
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
PROD = ROOT / "instance" / "kumon_math.db"
work = HERE / "live_acceptance_tmp"
work.mkdir(exist_ok=True)
copy = work / "kumon_math_live_regression.db"
for p in work.glob("kumon_math_live_regression.db*"):
    p.unlink()
src = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
dst = sqlite3.connect(copy)
src.backup(dst)
student = dst.execute("select id from users where role='student' order by id limit 1").fetchone()
dst.close()
src.close()
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{copy.as_posix()}"
os.environ["MATHPROJECT_ENV"] = "production"

from app import app  # noqa: E402
from core import practice_question_store as QS  # noqa: E402

SAMPLE = ["vh_數學B3_SubSection_1_1_2", "vh_數學B3_SubSection_1_2_1", "vh_數學B1_AbsoluteValue", "jh_數學2下_ArithmeticSequences",
          "gh_PolynomialInequalities", "gh_EquationOfALine", "gh_GraphsOfCubicFunctions", "gh_MathematicalInduction"]
app.config["WTF_CSRF_ENABLED"] = False
assert app.config["SQLALCHEMY_DATABASE_URI"].endswith("kumon_math_live_regression.db")


def stored(uid):
    for bucket in QS._STORE.values():
        if uid in bucket:
            return bucket[uid]
    return {}


def typed(v):
    if isinstance(v, list):
        return ", ".join(map(str, v))
    return {k: typed(x) for k, x in v.items()} if isinstance(v, dict) else v


out = {"app_debug": app.debug, "skills": {}}
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(student[0])
        sess["_fresh"] = True
    for skill in SAMPLE:
        rep = {"in_skills_dir": (ROOT / "skills" / f"{skill}.py").exists(), "page": client.get(f"/practice/{skill}").status_code, "questions": 0, "graded_correct": 0, "graded_total": 0, "statuses": []}
        for _ in range(4):
            res = client.get(f"/get_next_question?skill={skill}&level=1")
            body = res.get_json(silent=True) or {}
            rep["statuses"].append(res.status_code)
            if res.status_code != 200 or not body.get("question_uid"):
                rep["last_error"] = str(body)[:160]
                continue
            rep["questions"] += 1
            payload = stored(body["question_uid"]) or body
            expected = payload.get("correct_answer")
            if expected is None:
                continue
            ans = typed(expected)
            r = client.post("/check_answer", json={"skill_id": skill, "question_uid": body["question_uid"], "problem_type_id": body.get("problem_type_id", ""),
                                                     "answer": ans, **({"answers": ans} if isinstance(ans, dict) else {})})
            data = r.get_json(silent=True) or {}
            rep["graded_total"] += 1
            rep["graded_correct"] += bool(r.status_code == 200 and data.get("correct") is True)
        out["skills"][skill] = rep
(HERE / "live_regression_existing_result.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
