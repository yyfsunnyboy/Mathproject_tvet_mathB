"""Measure vocational dashboard SQL statements with and without the old N+1 path."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from sqlalchemy import event


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--username", default="b1load_001")
    args = parser.parse_args()
    database = Path(args.database).resolve()
    os.environ["MATHPROJECT_DATABASE_URI"] = "sqlite:///" + database.as_posix()
    os.environ["SEED_DB_ONLY"] = "1"

    from app import app
    import core.vocational_student_home as home
    from models import User, db

    with app.app_context():
        user = User.query.filter_by(username=args.username).one()
        engine = db.engine

        def measure(*, simulate_old_n_plus_one: bool) -> int:
            original = home._skill_meta_map
            if simulate_old_n_plus_one:
                home._skill_meta_map = lambda _ids: {}
            count = 0

            def before_cursor(*_args):
                nonlocal count
                count += 1

            db.session.remove()
            event.listen(engine, "before_cursor_execute", before_cursor)
            try:
                home.build_vocational_home_context(user)
            finally:
                event.remove(engine, "before_cursor_execute", before_cursor)
                home._skill_meta_map = original
                db.session.remove()
            return count

        baseline = measure(simulate_old_n_plus_one=True)
        optimized = measure(simulate_old_n_plus_one=False)
        print(json.dumps({"baseline_queries": baseline, "optimized_queries": optimized}))


if __name__ == "__main__":
    main()
