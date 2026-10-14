"""Run exactly one Waitress process against an isolated B1 load-test database."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5011)
    parser.add_argument("--threads", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.threads <= 16:
        raise SystemExit("--threads must be between 1 and 16")

    database = Path(args.database).resolve()
    if not database.is_file():
        raise SystemExit(f"Load-test database does not exist: {database}")
    os.environ["MATHPROJECT_DATABASE_URI"] = "sqlite:///" + database.as_posix()
    os.environ["MATHPROJECT_ENV"] = "production"
    os.environ["SEED_DB_ONLY"] = "1"
    os.environ.setdefault("SECRET_KEY", "b1-phase2-load-test-secret-key-only")

    from app import app
    from waitress import serve

    serve(app, host=args.host, port=args.port, threads=args.threads)


if __name__ == "__main__":
    main()
