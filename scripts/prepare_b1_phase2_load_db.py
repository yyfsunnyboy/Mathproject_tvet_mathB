"""Create an isolated, minimal B1 database for repeatable load tests."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from werkzeug.security import generate_password_hash


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _published_skills() -> list[str]:
    result: list[str] = []
    for path in sorted((ROOT / "agent_skills_v3").glob("vh_數學B1_*/component_manifest.json")):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if payload.get("publish_status") == "production_manifest_compiled":
            result.append(str(payload["skill_id"]))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--users", type=int, default=30)
    parser.add_argument("--password", default="b1-load-test")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    target = Path(args.database).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if not args.replace:
            raise SystemExit(f"Refusing to overwrite {target}; pass --replace")
        target.unlink()
    for suffix in ("-wal", "-shm"):
        Path(str(target) + suffix).unlink(missing_ok=True)

    os.environ["MATHPROJECT_DATABASE_URI"] = "sqlite:///" + target.as_posix()
    os.environ["SEED_DB_ONLY"] = "1"
    from app import app
    from models import SkillCurriculum, SkillInfo, User, db

    skills = _published_skills()
    with app.app_context():
        for index, skill_id in enumerate(skills, start=1):
            if db.session.get(SkillInfo, skill_id) is None:
                db.session.add(
                    SkillInfo(
                        skill_id=skill_id,
                        skill_en_name=skill_id.removeprefix("vh_數學B1_"),
                        skill_ch_name=skill_id.removeprefix("vh_數學B1_"),
                        description="B1 Phase 2 load test",
                        gemini_prompt="deterministic runtime",
                        is_active=True,
                    )
                )
                db.session.add(
                    SkillCurriculum(
                        skill_id=skill_id,
                        curriculum="vocational",
                        grade=10,
                        volume="數學B1",
                        chapter="B1 load test",
                        section=f"load-{index:02d}",
                        display_order=index,
                    )
                )
        password_hash = generate_password_hash(args.password, method="pbkdf2:sha256")
        for index in range(1, args.users + 1):
            db.session.add(
                User(
                    username=f"b1load_{index:03d}",
                    password_hash=password_hash,
                    role="student",
                    curriculum_code="vocational",
                )
            )
        db.session.commit()

    print(json.dumps({"database": str(target), "users": args.users, "skills": len(skills)}))


if __name__ == "__main__":
    main()
