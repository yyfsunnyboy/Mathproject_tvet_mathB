# -*- coding: utf-8 -*-
"""Constants for the isolated Qwen Gencode experiment path."""

from __future__ import annotations

DEFAULT_MODEL_PRESET = "qwen3.5-9b"
DEFAULT_OUTPUT_ROOT = "reports/gencode_qwen_dryrun"
PROMPT_VERSION = "qwen_gencode_experiment_v1"
DEFAULT_MAX_REPAIR_ROUNDS = 3
DEFAULT_SEED = 7
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_OLLAMA_BASE = "http://localhost:11434"
DEFAULT_PROMPT_MODE = "full"

# Multi-seed sampling for variation / integrity (reuse shared integrity seeds).
from core.gencode.services.v3_question_integrity_validator import DEFAULT_INTEGRITY_SEEDS

VALIDATION_SEEDS: tuple[int, ...] = DEFAULT_INTEGRITY_SEEDS

FORBIDDEN_MODULE_NAMES: frozenset[str] = frozenset(
    {
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "http",
        "httplib",
        "ftplib",
        "pickle",
        "pathlib",
        "shutil",
        "ctypes",
        "multiprocessing",
        "asyncio",
    }
)

FORBIDDEN_CALL_NAMES: frozenset[str] = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "__import__",
        "system",
        "popen",
        "remove",
        "unlink",
        "rmtree",
        "rmdir",
    }
)

ALLOWED_TOP_LEVEL_IMPORT_PREFIXES: tuple[str, ...] = (
    "__future__",
    "core.gencode",
    "core.domain",
    "core.checkers",
    "core.registry",
    "typing",
    "math",
    "random",
    "fractions",
    "decimal",
    "dataclasses",
    "collections",
    "itertools",
    "functools",
    "re",
    "json",
    "copy",
    "hashlib",
)

GENERATE_INTERFACE_SPEC = """
Required Python module interface for generate.py:

```python
from __future__ import annotations
from typing import Any

def generate(level: int = 1, seed: int | None = None, **kwargs: Any) -> dict[str, Any]:
    \"\"\"Return one question payload dict. Must vary with seed.\"\"\"
    ...
```

Optional:
```python
def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    ...
```

Payload MUST include at least:
- question_text (str, non-placeholder)
- answer OR correct_answer
- answer_type OR answer_contract.answer_type
- presentation_mode
- problem_type_id
- metadata: {givens, target, derivation}
- choices: list (may be empty for short_answer; required for single_choice)
- answer_contract: {answer_type, checker_key or checker, equivalence_type or answer_equivalence}
- component_id (when provided via kwargs)
- seed (echo input seed)
""".strip()
