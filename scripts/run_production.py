"""Windows production entry point for MathProject."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PRODUCTION_HOST = "127.0.0.1"
PRODUCTION_PORT = 5000
DEFAULT_THREADS = 10


def _thread_count() -> int:
    raw = str(os.environ.get("WAITRESS_THREADS") or DEFAULT_THREADS).strip()
    try:
        threads = int(raw)
    except ValueError as exc:
        raise RuntimeError("WAITRESS_THREADS must be an integer.") from exc
    if not 1 <= threads <= 16:
        raise RuntimeError("WAITRESS_THREADS must be between 1 and 16.")
    return threads


def build_production_app():
    load_dotenv(PROJECT_ROOT / ".env")

    from config import Config

    Config.resolve_secret_key(production=True)
    os.environ["MATHPROJECT_ENV"] = "production"
    from app import app

    if app.debug or app.config.get("ENV") == "development":
        raise RuntimeError("Production application must run with debug disabled.")
    return app


def main() -> None:
    from waitress import serve

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    threads = _thread_count()
    application = build_production_app()
    logging.getLogger("mathproject.production").info(
        "MathProject production startup host=%s port=%s threads=%s",
        PRODUCTION_HOST,
        PRODUCTION_PORT,
        threads,
    )
    serve(
        application,
        host=PRODUCTION_HOST,
        port=PRODUCTION_PORT,
        threads=threads,
    )


if __name__ == "__main__":
    main()
