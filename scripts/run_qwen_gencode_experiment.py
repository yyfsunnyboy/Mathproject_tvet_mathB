#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI: isolated Qwen3.5 9B Gencode experiment (dryrun-only).

Does NOT switch global AI mode, does NOT write tracker verified/published,
does NOT touch agent_skills_v3 production, and does NOT fall back to Gemini.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.qwen_experiment.constants import (
    DEFAULT_MAX_REPAIR_ROUNDS,
    DEFAULT_MODEL_PRESET,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_PROMPT_MODE,
    DEFAULT_SEED,
    DEFAULT_TIMEOUT_SECONDS,
)
from core.gencode.qwen_experiment.orchestrator import run_qwen_gencode_experiment


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Isolated Qwen Gencode experiment runner")
    p.add_argument("--example-id", type=int, required=True, help="textbook_examples.id")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--model-preset", type=str, default=DEFAULT_MODEL_PRESET)
    p.add_argument("--max-repair-rounds", type=int, default=DEFAULT_MAX_REPAIR_ROUNDS)
    p.add_argument("--output-root", type=str, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--resume", action="store_true", help="Resume latest/incomplete job")
    p.add_argument("--job-id", type=str, default="", help="Explicit job id (with --resume)")
    p.add_argument("--prompt-mode", type=str, default=DEFAULT_PROMPT_MODE, choices=["full", "compact"])
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    p.add_argument("--db-path", type=str, default="", help="Optional readonly sqlite path")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_qwen_gencode_experiment(
        example_id=int(args.example_id),
        seed=int(args.seed),
        model_preset=str(args.model_preset),
        max_repair_rounds=int(args.max_repair_rounds),
        output_root=str(args.output_root),
        resume=bool(args.resume),
        job_id=str(args.job_id or "").strip() or None,
        prompt_mode=str(args.prompt_mode),
        timeout=float(args.timeout),
        db_path=str(args.db_path or "").strip() or None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    status = str(result.get("status") or "FAIL")
    if status == "PASS":
        return 0
    if status == "BLOCKED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
