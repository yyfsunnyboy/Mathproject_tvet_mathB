import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

os.environ.setdefault("ADV_RAG_EAGER_INIT", "0")

import config
from werkzeug.security import generate_password_hash

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS

tmp = Path(tempfile.mkdtemp()) / "rt.db"
config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(tmp).replace("\\", "/")
from app import create_app  # noqa: E402
from models import User, db  # noqa: E402

app = create_app()
app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
with app.app_context():
    db.session.add(User(username="ch4rt", password_hash=generate_password_hash("pass1234"), role="student"))
    db.session.commit()
client = app.test_client()
assert client.post("/login", data={"username": "ch4rt", "password": "pass1234"}).status_code in {302, 303}


def student_answer(q):
    parts = (q.get("answer_contract") or {}).get("parts") or []
    if len(parts) >= 2:
        return {str(p.get("key")): p.get("expected_answer") for p in parts}
    if q.get("answer_type") == "single_choice" or q.get("presentation_mode") == "single_choice":
        return q.get("correct_answer")
    return q.get("semantic_answer")


def wrong_answer(q, ans):
    if isinstance(ans, dict):
        bad = dict(ans)
        k = next(iter(bad))
        bad[k] = "12345"
        return bad
    if q.get("presentation_mode") == "single_choice":
        return next(c["label"] for c in q.get("choices") if c["label"] != ans)
    return "12345"


def post(q, ans):
    body = {"skill_id": q.get("skill_id"), "question_uid": q.get("question_uid"),
            "problem_type_id": q.get("problem_type_id") or "", "answer": ans}
    if isinstance(ans, dict):
        body["answers"] = ans
        body["user_answer"] = ans
    r = client.post("/check_answer", data=json.dumps(body), content_type="application/json")
    return r.status_code, (r.get_json(silent=True) or {})


seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 1
problems = Counter()
keys_seen = Counter()
for eid, spec in sorted(SOURCE_SPECS.items()):
    for seed in range(seeds):
        r = client.get("/get_next_question", query_string={"skill": spec["skill_id"], "level": 1, "component_id": f"src_{eid}", "gen_seed": seed + 11})
        if r.status_code != 200:
            problems[f"{eid}:get:{r.status_code}"] += 1
            continue
        q = r.get_json()
        keys_seen.update(q.keys())
        if q.get("component_id") != f"src_{eid}":
            problems[f"{eid}:component_mismatch:{q.get('component_id')}"] += 1
        if q.get("textbook_example_id") not in (eid, str(eid), None):
            problems[f"{eid}:teid:{q.get('textbook_example_id')}"] += 1
        ans = student_answer(q)
        code, res = post(q, ans)
        if code != 200 or res.get("correct") is not True:
            problems[f"{eid}:{spec['op']}:correct_rejected"] += 1
            if problems[f"{eid}:{spec['op']}:correct_rejected"] == 1:
                print("REJ", eid, json.dumps(ans, ensure_ascii=False)[:200], json.dumps(res, ensure_ascii=False)[:300])
        r = client.get("/get_next_question", query_string={"skill": spec["skill_id"], "level": 1, "component_id": f"src_{eid}", "gen_seed": seed + 11})
        q = r.get_json()
        code, res = post(q, wrong_answer(q, student_answer(q)))
        if res.get("correct") is True:
            problems[f"{eid}:{spec['op']}:wrong_accepted"] += 1

# deeplink: textbook_example_id picks that source first
for eid in (12127, 12219, 12241, 12272):
    spec = SOURCE_SPECS[eid]
    r = client.get("/get_next_question", query_string={"skill": spec["skill_id"], "level": 1, "textbook_example_id": eid})
    q = r.get_json() or {}
    print("deeplink", eid, r.status_code, q.get("component_id"), q.get("textbook_example_id"))

for k, v in sorted(problems.items()):
    print(k, v)
print("problems:", len(problems))
print("sample keys:", sorted(keys_seen)[:80])
