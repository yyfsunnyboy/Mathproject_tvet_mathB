"""Student-side acceptance of the published 數學2 Unit 1 skills through the real practice routes, on an ISOLATED database copy.

* Fresh process, Flask test client (no server is started, nothing listens on a port); MATHPROJECT_DATABASE_URI points at a copy of the
  formal DB, so check_answer / practice records can never reach the formal database (asserted before and after).
* For every published component and several seeds it records what the browser receives (question text, input prompts, choices, figure
  fields) and submits a wrong and a correct answer exactly as the UI would (every box a string).
* Writes live_acceptance_payloads.json (text for the MathJax render check) and live_acceptance_result.json.
"""
import collections
import hashlib
import json
import logging
import os
import sqlite3
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
PROD = ROOT / "instance" / "kumon_math.db"
SEEDS_PER_COMPONENT = 6


def sha_state() -> dict:
    con = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
    try:
        return {t: con.execute(f"select count(*) from {t}").fetchone()[0] for t in ("practice_attempts", "adaptive_learning_logs", "progress", "mistake_notebook_entries", "student_abilities")}
    finally:
        con.close()


before = sha_state()
work = HERE / "live_acceptance_tmp"
work.mkdir(exist_ok=True)
copy = work / "kumon_math_live_acceptance.db"
for p in work.glob("kumon_math_live_acceptance.db*"):
    p.unlink()
src = sqlite3.connect(f"file:{PROD.as_posix()}?mode=ro", uri=True)
dst = sqlite3.connect(copy)
src.backup(dst)
student = dst.execute("select id from users where role='student' order by id limit 1").fetchone()
dst.close()
src.close()
os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{copy.as_posix()}"

from agent_domains_candidate.sequence_progression import verification as V  # noqa: E402
from agent_domains_candidate.sequence_progression.sequence_progression_specs import COMPONENTS, SKILLS  # noqa: E402
from app import app  # noqa: E402
from core import practice_question_store as QS  # noqa: E402

errors: list[str] = []


class Capture(logging.Handler):
    def emit(self, record):
        msg = record.getMessage()
        if any(k in msg for k in ("DOMAIN_CAPABILITY_UNRESOLVED", "domain_binding_mismatch", "QUESTION DELIVERY REJECTED", "Traceback")):
            errors.append(msg[:300])


for name in ("", "app", "core"):
    logging.getLogger(name).addHandler(Capture())
app.config["WTF_CSRF_ENABLED"] = False
assert app.config["SQLALCHEMY_DATABASE_URI"].endswith("kumon_math_live_acceptance.db"), app.config["SQLALCHEMY_DATABASE_URI"]


def stored(uid: str) -> dict:
    for bucket in QS._STORE.values():
        if uid in bucket:
            return bucket[uid]
    return {}


def as_typed(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return {k: as_typed(v) for k, v in value.items()}
    return value


def submit(client, skill, body, answer):
    answer = as_typed(answer)
    res = client.post("/check_answer", json={"skill_id": skill, "question_uid": body.get("question_uid", ""), "problem_type_id": body.get("problem_type_id", ""),
                                             "answer": answer, **({"answers": answer} if isinstance(answer, dict) else {})})
    data = res.get_json(silent=True) or {}
    return (data.get("correct") if res.status_code == 200 else None), data


payloads, result = [], {"skills": {}, "db_copy": str(copy.relative_to(ROOT)), "student_id": student[0] if student else None}
NOT_PUBLISHED = {12668, 12673}  # patch-round components: sandbox only until the next Promotion
PUBLISHED = {c: v for c, v in COMPONENTS.items() if c not in NOT_PUBLISHED}
published = sorted({SKILLS[spec[0]] for spec in PUBLISHED.values()})
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["_user_id"] = str(student[0])
        sess["_fresh"] = True
    for skill in published:
        page = client.get(f"/practice/{skill}")
        rep = {"practice_page": page.status_code, "mathjax_in_page": b"mathjax" in page.data.lower(), "served": collections.Counter(), "http_errors": [],
               "grading_problems": [], "figure_fields": 0, "image_fields": 0, "multi_part": 0}
        for cid in sorted(c for c in PUBLISHED if SKILLS[PUBLISHED[c][0]] == skill):
            seen = set()
            for attempt in range(SEEDS_PER_COMPONENT * 6):
                if len(seen) >= SEEDS_PER_COMPONENT:
                    break
                res = client.get(f"/get_next_question?skill={skill}&level=1&component_id=src_{cid}")
                body = res.get_json(silent=True) or {}
                if res.status_code != 200 or not body.get("question_uid"):
                    rep["http_errors"].append(f"{cid}:{res.status_code}:{str(body)[:120]}")
                    break
                payload = stored(body["question_uid"]) or body
                text = body.get("question_text") or payload.get("question_text")
                if text in seen:
                    continue
                seen.add(text)
                rep["served"][payload.get("textbook_example_id")] += 1
                rep["figure_fields"] += bool(body.get("visual_spec") or payload.get("visual_spec"))
                rep["image_fields"] += bool(body.get("image_assets") or body.get("image_url") or payload.get("image_assets"))
                contract = payload.get("answer_contract") or {}
                parts = V.parts_of(payload)
                multi = contract.get("answer_type") == "multi_part"
                rep["multi_part"] += multi
                expected = payload.get("correct_answer")
                wrong = {**expected, parts[0]["key"]: V.wrong_value(parts[0])} if multi else V.wrong_value(parts[0])
                got_wrong, _ = submit(client, skill, body, wrong)
                got_right, data = submit(client, skill, body, expected)
                if got_wrong is not False:
                    rep["grading_problems"].append(f"{cid}:wrong->{got_wrong}")
                if got_right is not True:
                    rep["grading_problems"].append(f"{cid}:correct->{got_right}")
                texts = [text] + [str(p.get("prompt") or p.get("label") or "") for p in parts] + [str(c.get("value") or c.get("text") or "") for c in (payload.get("choices") or [])]
                feedback = [str(x) for k, x in data.items() if isinstance(x, str) and k in ("explanation", "correct_answer_display", "display_answer", "feedback", "message")]
                feedback += [str(s) for s in payload.get("explanation_steps") or []] + [str(payload.get("display_answer") or "")]
                payloads.append({"skill": skill, "cid": cid, "texts": [t for t in texts if t], "feedback": [t for t in feedback if t]})
        rep["served"] = dict(sorted(rep["served"].items(), key=lambda kv: str(kv[0])))
        result["skills"][skill] = rep

after = sha_state()
result.update(runtime_errors=errors[:20], formal_db_counts_before=before, formal_db_counts_after=after, formal_db_unchanged=before == after,
              components_served=sum(len(r["served"]) for r in result["skills"].values()), payload_count=len(payloads))
result["passed"] = (before == after and not errors and all(r["practice_page"] == 200 and not r["http_errors"] and not r["grading_problems"] for r in result["skills"].values()))
(HERE / "live_acceptance_payloads.json").write_text(json.dumps(payloads, ensure_ascii=False), encoding="utf-8")
(HERE / "live_acceptance_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: (v if k != "skills" else {s: {a: b for a, b in r.items() if a != "served"} | {"components": len(r["served"]), "min_served": min(r["served"].values())} for s, r in v.items()}) for k, v in result.items()}, ensure_ascii=False, indent=1, default=str))
