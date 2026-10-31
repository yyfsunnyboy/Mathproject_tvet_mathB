"""Isolated Unit 6 student-runtime check (NOT the formal 5000 / 5001 services).

* Facades / V3 packages: the sandbox project written by ``rehearse_unit6.py`` (tmp/gh_math2u6_rehearsal/run/project),
  prepended to ``skills.__path__`` in this process only; the real skills/ and agent_skills_v3/ are not touched.
* Domain: the reviewed candidate registered in memory (no promoted-capability config is written).
* DB: an online-backup copy of instance/kumon_math.db under tmp/; two throw-away accounts exist in that copy only.

    python reports/gh_math2_unit6_bundle/isolated_server.py prepare
    python reports/gh_math2_unit6_bundle/isolated_server.py api      # Flask test client, 42 components
    python reports/gh_math2_unit6_bundle/isolated_server.py serve    # http://127.0.0.1:5058 , stop with Ctrl+C
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "tmp/gh_math2u6_rehearsal/run"
PROJECT = RUN / "project"
ISO = ROOT / "tmp/gh_math2u6_rehearsal/isolated"
DB = ISO / "unit6_preview.db"
REPORT = Path(__file__).resolve().parent / "runtime_api_report.json"
PORT = 5058
USERS = {"u6preview_student": "student"}
PASSWORD = "u6preview-only"
SKILLS = ("gh_SampleSpace", "gh_Event", "gh_DefinitionOfClassicalProbability", "gh_PropertiesOfProbability")
LOAD_ERROR = "模組載入錯誤"


def prepare():
    from werkzeug.security import generate_password_hash

    ISO.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(f"file:{(ROOT / 'instance/kumon_math.db').as_posix()}?mode=ro", uri=True)
    dst = sqlite3.connect(DB)
    src.backup(dst)
    src.close()
    for name, role in USERS.items():
        dst.execute("delete from users where username=?", (name,))
        dst.execute("insert into users (username, password_hash, role, created_at) values (?,?,?,datetime('now'))",
                    (name, generate_password_hash(PASSWORD, method="pbkdf2:sha256"), role))
    dst.commit()
    dst.close()
    print("prepared", DB)


def _boot():
    assert DB.exists() and (PROJECT / "skills/gh_SampleSpace.py").exists(), "run rehearse_unit6.py and prepare first"
    os.environ["MATHPROJECT_DATABASE_URI"] = f"sqlite:///{DB.as_posix()}"
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    sys.path.append(str(PROJECT))  # namespace package `skills`: real skills/ stays first, only the 4 Unit 6 facades are added
    from agent_domains_candidate.classical_probability.sandbox_harness import register_candidate_in_memory

    register_candidate_in_memory()
    from app import app

    assert app.config["SQLALCHEMY_DATABASE_URI"].endswith("isolated/unit6_preview.db"), app.config["SQLALCHEMY_DATABASE_URI"]
    return app


def _wrong(value):
    text = str(value)
    return {"A": "B", "B": "A", "是": "否", "否": "是", "○": "×", "×": "○"}.get(text, text + "1" if text[-1:].isdigit() else "{99}")


def api():
    app = _boot()
    from core.gencode.multipart_answer_arity import expected_answer_field_count, rendered_answer_field_count
    from core.routes.practice import get_question_by_uid

    client = app.test_client()
    login = client.post("/login", data={"username": "u6preview_student", "password": PASSWORD})
    assert login.status_code in (302, 303), login.status_code
    report, failures = {}, []
    for skill in SKILLS:
        facade = __import__(f"skills.{skill}", fromlist=["GENERATOR_KEYS"])
        assert str(PROJECT) in facade.__file__, facade.__file__
        rows = report.setdefault(skill, {})
        for component in facade.GENERATOR_KEYS:
            q = client.get(f"/get_next_question?skill={skill}&component_id={component}")
            data = q.get_json() or {}
            uid = data.get("question_uid", "")
            with client.session_transaction() as sess:
                snapshot = dict(sess)
            with app.test_request_context():
                from flask import session

                session.update(snapshot)
                stored = get_question_by_uid(uid, skill_id=skill) or {}
            contract = data.get("answer_contract") or {}
            parts = contract.get("parts") or []
            stem = (data.get("metadata") or {}).get("stem_structure") or data.get("stem_structure") or {}
            row = {
                "status": q.status_code, "served_component": data.get("component_id") or data.get("problem_type_id"),
                "answer_type": contract.get("answer_type"), "route_mode": data.get("route_mode") or data.get("runtime_route_mode"),
                "expected_fields": expected_answer_field_count(data), "rendered_fields": rendered_answer_field_count(data),
                "stem_items": len(stem.get("items") or []), "group_labels": [p.get("group_label") for p in parts],
                "select_parts": [p.get("key") for p in parts if p.get("input_type") == "select"],
            }
            correct = stored.get("correct_answer")
            examples = [data.get("answer_format_example"), contract.get("answer_format_example")] + [
                p.get("answer_format_example") for p in parts]
            canon = [str(v) for v in (correct.values() if isinstance(correct, dict) else [correct])]
            row["leaks_answer"] = any(e and str(e) in canon for e in examples)
            if contract.get("answer_type") == "multi_part":
                answer = {p["key"]: str(correct[p["key"]]) for p in parts}
                if any(p.get("input_type") == "select" for p in parts):
                    for p in parts:
                        if p.get("input_type") == "select":
                            answer[p["key"]] = next(c["value"] for c in p["choices"] if c["label"] == correct[p["key"]])
                wrong = dict(answer)
                last = parts[-1]["key"]
                wrong[last] = _wrong(wrong[last])
                bad = client.post("/check_answer", json={"skill_id": skill, "question_uid": uid, "answers": wrong, "answer": wrong}).get_json()
                ok = client.post("/check_answer", json={"skill_id": skill, "question_uid": uid, "answers": answer, "answer": answer}).get_json()
            else:
                answer = str(correct)
                bad = client.post("/check_answer", json={"skill_id": skill, "question_uid": uid, "answer": _wrong(answer)}).get_json()
                ok = client.post("/check_answer", json={"skill_id": skill, "question_uid": uid, "answer": answer}).get_json()
            bad = bad or {}
            ok = ok or {}
            row.update(correct_accepted=bool(ok.get("correct")), wrong_rejected=bad.get("correct") is False,
                       wrong_failed_parts=[str(x.get("key", x) if isinstance(x, dict) else x) for x in bad.get("failed_parts") or []],
                       load_error=LOAD_ERROR in json.dumps([ok, bad], ensure_ascii=False))
            rows[component] = row
            n = row["expected_fields"]
            multi = row["answer_type"] == "multi_part"
            if (q.status_code != 200 or row["served_component"] != component or not row["correct_accepted"]
                    or not row["wrong_rejected"] or row["load_error"] or row["leaks_answer"]
                    or row["rendered_fields"] != n
                    or (multi and (row["stem_items"] != n or row["group_labels"] != [f"({i})" for i in range(1, n + 1)]
                                   or row["wrong_failed_parts"] != [parts[-1]["key"]]))):
                failures.append((skill, component, row, ok, bad))
    REPORT.write_text(json.dumps({"failures": len(failures), "skills": report}, ensure_ascii=False, indent=1, default=str),
                      encoding="utf-8")
    summary = {s: len(r) for s, r in report.items()}
    print("components", summary, "total", sum(summary.values()), "failures", len(failures))
    for f in failures[:5]:
        print(json.dumps(f, ensure_ascii=False, default=str)[:1500])


def serve():
    app = _boot()
    print(f"ISOLATED Unit 6 preview on http://127.0.0.1:{PORT} db={DB}", flush=True)
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    {"prepare": prepare, "api": api, "serve": serve}[sys.argv[1]]()
