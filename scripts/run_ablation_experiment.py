# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from core.adaptive.ablation_experiment import ExperimentConfig, run_experiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run simulation-based ablation experiment for AB1/AB2/AB3.")
    parser.add_argument("--episodes", type=int, default=100, help="Episodes per prototype.")
    parser.add_argument("--max-steps", type=int, default=30, help="Max steps per episode.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Experiment output directory.")
    parser.add_argument(
        "--success-threshold",
        type=float,
        default=0.8,
        help="Polynomial ability threshold used to mark episode success.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ExperimentConfig(
        episodes_per_prototype=args.episodes,
        max_steps_per_episode=args.max_steps,
        random_seed=args.seed,
        output_dir=args.output_dir,
        success_polynomial_threshold=args.success_threshold,
    )
    outputs = run_experiment(config)
    for key, path in outputs.items():
        print(f"{key}={Path(path)}", flush=True)


if __name__ == "__main__":
    main()
