"""B1 student-flow and synchronized-submit Locust scenarios."""

from __future__ import annotations

import itertools
import json
import os
import random
from pathlib import Path

from gevent.lock import Semaphore
from locust import HttpUser, between, events, task


ROOT = Path(__file__).resolve().parents[2]
COMPONENTS: dict[str, str] = {}
for _path in (ROOT / "agent_skills_v3").glob("vh_數學B1_*/component_manifest.json"):
    _manifest = json.loads(_path.read_text(encoding="utf-8-sig"))
    if _manifest.get("publish_status") != "production_manifest_compiled":
        continue
    _candidate = next(
        (
            row for row in _manifest.get("components", [])
            if row.get("answer_type") != "drawing"
            and row.get("presentation_mode") != "drawing"
        ),
        None,
    )
    if _candidate:
        COMPONENTS[_path.parent.name] = str(_candidate["component_id"])
SKILLS = sorted(COMPONENTS)
PASSWORD = os.environ.get("B1_LOAD_PASSWORD", "b1-load-test")
MODE = os.environ.get("B1_LOAD_MODE", "normal").strip().lower()
_ids = itertools.count(1)
_id_lock = Semaphore()
_burst_lock = Semaphore()
_burst_ready = 0
_burst_completed = 0
_burst_event = None


@events.test_start.add_listener
def _reset_burst(environment, **_kwargs):
    global _ids, _burst_ready, _burst_completed, _burst_event
    from gevent.event import Event

    _ids = itertools.count(1)
    _burst_ready = 0
    _burst_completed = 0
    _burst_event = Event()


class B1Student(HttpUser):
    wait_time = between(1.0, 3.0)

    def on_start(self):
        with _id_lock:
            self.user_number = next(_ids)
        response = self.client.post(
            "/login",
            data={
                "username": f"b1load_{self.user_number:03d}",
                "password": PASSWORD,
                "role": "student",
            },
            name="POST /login",
        )
        if response.status_code not in (200, 302):
            response.failure(f"login status {response.status_code}")
        self.seed = self.user_number * 100_000
        self.burst_done = False

    def _question(self, skill_id: str) -> dict | None:
        self.seed += 1
        with self.client.get(
            "/get_next_question",
            params={
                "skill": skill_id,
                "level": 1,
                "gen_seed": self.seed,
                "component_id": COMPONENTS[skill_id],
            },
            name="GET /get_next_question",
            timeout=30,
            catch_response=True,
        ) as response:
            try:
                payload = response.json()
            except Exception:
                response.failure("non-JSON question response")
                return None
            if response.status_code != 200 or not payload.get("question_uid"):
                response.failure(f"question status={response.status_code} body={payload!r}")
                return None
            return payload

    def _submit(self, skill_id: str, question: dict) -> None:
        answer = question.get("correct_answer", question.get("answer"))
        with self.client.post(
            "/check_answer",
            json={"skill_id": skill_id, "question_uid": question["question_uid"], "answer": answer},
            name="POST /check_answer",
            timeout=30,
            catch_response=True,
        ) as response:
            try:
                payload = response.json()
            except Exception:
                response.failure("non-JSON submit response")
                return
            if response.status_code != 200 or payload.get("correct") is not True:
                response.failure(f"submit status={response.status_code} body={payload!r}")

    @task
    def student_flow(self):
        global _burst_ready, _burst_completed
        if MODE == "burst" and self.burst_done:
            return

        skill_id = SKILLS[(self.user_number - 1 + random.randrange(len(SKILLS))) % len(SKILLS)]
        self.client.get("/dashboard", name="GET /dashboard", timeout=30)
        self.client.get(f"/practice/{skill_id}", name="GET /practice/[skill]", timeout=30)
        question = self._question(skill_id)
        if question is None:
            return

        if MODE == "burst":
            with _burst_lock:
                _burst_ready += 1
                if _burst_ready >= int(os.environ.get("B1_LOAD_USERS", "30")):
                    _burst_event.set()
            _burst_event.wait(timeout=60)
            self._submit(skill_id, question)
            self.burst_done = True
            with _burst_lock:
                _burst_completed += 1
                if _burst_completed >= int(os.environ.get("B1_LOAD_USERS", "30")):
                    self.environment.runner.quit()
            return

        self._submit(skill_id, question)
