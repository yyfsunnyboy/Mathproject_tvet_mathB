"""Safe project-local environment secret persistence."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


def _without_key(lines: list[str], key: str) -> list[str]:
    prefix = f"{key}="
    return [line for line in lines if not line.lstrip().startswith(prefix)]


def update_gemini_api_key(value: str | None, *, env_path: Path = ENV_PATH) -> bool:
    """Atomically set or clear GEMINI_API_KEY while retaining other .env entries."""
    key = "GEMINI_API_KEY"
    new_value = str(value or "").strip()
    existing = env_path.read_text(encoding="utf-8").splitlines() if env_path.exists() else []
    lines = _without_key(existing, key)
    if new_value:
        lines.append(f"{key}={new_value}")
    payload = "\n".join(lines) + ("\n" if lines else "")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".env.", suffix=".tmp", dir=str(env_path.parent), text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        os.replace(temp_name, env_path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    if new_value:
        os.environ[key] = new_value
    else:
        os.environ.pop(key, None)
    return bool(new_value)
