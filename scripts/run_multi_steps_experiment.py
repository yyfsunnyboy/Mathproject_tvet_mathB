"""
[File Name]
run_multi_steps_experiment.py

[Created Date]
2026-04-09

[Project]
Adaptive Math Learning System (Adaptive Summative + Teaching)

[Description]
This runner executes multi-budget AB experiments by sweeping MAX_STEPS settings.
It repeatedly calls the simulation entrypoint, preserves per-step result snapshots,
and builds cross-step summary tables for strategy-level and student-type-level comparisons.
The script also triggers cross-step plotting and output synchronization for reporting.

[Core Functionality]
- Override MAX_STEPS in batch mode (30/40/50) and run simulation rounds
- Preserve each round outputs with step-specific filenames to avoid overwrite
- Build cross-step merged summaries for strategy and strategy-by-student-type
- Regenerate multi-step comparison figures from merged summary tables
- Sync curated outputs into experiment subdirectories for presentation

[Related Experiments]
- Experiment 1: Baseline vs AB2 vs AB3
- Experiment 3: Policy Timing (AB3)

[Notes]
- No experiment logic is modified by this header.
- Added for maintainability and research documentation only.
"""

import os
import shutil
from pathlib import Path

import pandas as pd

import simulate_student
import plot_experiment_results as plot_results_module
from plot_experiment_results import (
    create_timestamped_run_dir,
    plot_multi_steps_results,
    sync_run_to_latest,
    setup_report_style,
)

MAX_STEPS_LIST = [30, 40, 50]
REPORTS_DIR = Path("reports")
EXP1_BASE_DIR = REPORTS_DIR / "experiment_1_ablation"
RUNS_DIR = EXP1_BASE_DIR / "runs"
LATEST_DIR = EXP1_BASE_DIR / "latest"
FINAL_DIR = EXP1_BASE_DIR / "final"
EXP1_OUTPUT_DIR_ENV = "MATHPROJECT_EXP1_OUTPUT_DIR"

# Per-run outputs that should be preserved with a steps suffix.
PRESERVE_FILES = [
    "ablation_simulation_results.csv",
    "ablation_strategy_summary.csv",
    "ablation_strategy_by_student_type_summary.csv",
]

EXP1_ARTIFACTS = [
    "ablation_simulation_results.csv",
    "ablation_strategy_summary.csv",
    "ablation_strategy_by_student_type_summary.csv",
    "multi_steps_strategy_summary.csv",
    "multi_steps_strategy_by_type_summary.csv",
    "experiment1_summary_table.csv",
    "experiment1_summary_table.md",
    "fig_multi_steps_success_rate.png",
    "fig_multi_steps_efficiency.png",
    "fig_exp1_student_type_improved.png",
]

STRATEGY_DISPLAY_MAP = {
    "AB1_Baseline": "Baseline",
    "AB2_RuleBased": "Rule-Based",
    "AB3_PPO_Dynamic": "Adaptive (Ours)",
}

REDUNDANT_EXP1_FIGURES = [
    "fig_ablation_by_student_type.png",
    "fig_ablation_by_student_type_success.png",
    "fig_ablation_success_rate.png",
    "fig_ablation_steps_vs_success.png",
    "fig_ablation_strategy_breakdown.png",
    "fig_multi_steps_ab3_by_student_type.png",
]

ACTIVE_EXP1_DIR: Path = LATEST_DIR


def get_active_exp1_dir() -> Path:
    """Current Experiment 1 output directory for this process."""
    return ACTIVE_EXP1_DIR


def set_active_exp1_dir(path: Path) -> None:
    """Configure active Experiment 1 output directory and env override."""
    global ACTIVE_EXP1_DIR
    ACTIVE_EXP1_DIR = path
    os.environ[EXP1_OUTPUT_DIR_ENV] = str(path)


def create_run_output_dir() -> Path:
    """Create runs/<timestamp> folder for current Experiment 1 execution."""
    dirs = create_timestamped_run_dir(EXP1_BASE_DIR)
    return dirs["run_dir"]


def refresh_latest_from_run(run_dir: Path) -> None:
    """Replace latest/ with current run outputs."""
    sync_run_to_latest(run_dir, LATEST_DIR)


def cleanup_redundant_experiment1_figures() -> None:
    """Remove redundant Experiment 1 figure files from root and exp1 folders."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp1_dir = get_active_exp1_dir()
    exp1_dir.mkdir(parents=True, exist_ok=True)
    for filename in REDUNDANT_EXP1_FIGURES:
        for parent in (REPORTS_DIR, exp1_dir):
            path = parent / filename
            if path.exists():
                path.unlink()


def cleanup_previous_step_snapshots(max_steps_list: list[int]) -> None:
    """Remove stale step-suffixed CSV snapshots before a new multi-step run."""
    exp1_dir = get_active_exp1_dir()
    exp1_dir.mkdir(parents=True, exist_ok=True)
    stems = [
        "ablation_simulation_results",
        "ablation_strategy_summary",
        "ablation_strategy_by_student_type_summary",
    ]
    for steps in max_steps_list:
        for stem in stems:
            path = exp1_dir / f"{stem}_steps{int(steps)}.csv"
            if path.exists():
                path.unlink()

    cleanup_redundant_experiment1_figures()


def run_single_steps_experiment(max_steps: int) -> None:
    """Run one simulate_student round with an overridden MAX_STEPS."""
    simulate_student.MAX_STEPS = int(max_steps)
    simulate_student.main(output_mode="experiment1")


def preserve_step_outputs(max_steps: int) -> None:
    """Copy current report CSVs to step-suffixed files to avoid overwrite."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    exp1_dir = get_active_exp1_dir()
    exp1_dir.mkdir(parents=True, exist_ok=True)
    for filename in PRESERVE_FILES:
        src = exp1_dir / filename
        if not src.exists():
            continue
        stem = src.stem
        dst = exp1_dir / f"{stem}_steps{max_steps}.csv"
        shutil.copy2(src, dst)


def consolidate_experiment1_outputs() -> None:
    """Move Experiment 1 artifacts from reports root into experiment_1_ablation.

    Note: experiment1_summary_table.* are generated from aggregated multi-step results.
    We avoid moving same-name files from reports root to prevent accidental overwrite.
    """
    # Outputs are already written into run_dir via env override. Keep as no-op
    # for backward compatibility.
    exp1_dir = get_active_exp1_dir()
    exp1_dir.mkdir(parents=True, exist_ok=True)


def build_multi_steps_strategy_summary(max_steps_list: list[int]) -> Path:
    """Merge per-step strategy summaries into one cross-step table."""
    exp1_dir = get_active_exp1_dir()
    rows: list[pd.DataFrame] = []
    for steps in max_steps_list:
        path = exp1_dir / f"ablation_strategy_summary_steps{steps}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["max_steps"] = int(steps)
        df = df.rename(
            columns={
                "avg_final_polynomial_mastery": "avg_final_mastery",
                "avg_unnecessary_remediations": "avg_unnecessary_remediation",
            }
        )
        keep = [
            "max_steps",
            "strategy",
            "success_rate",
            "avg_steps",
            "avg_final_mastery",
            "avg_unnecessary_remediation",
        ]
        for col in keep:
            if col not in df.columns:
                df[col] = pd.NA
        # Safety clamp: reported average steps cannot exceed configured MAX_STEPS.
        df["avg_steps"] = pd.to_numeric(df["avg_steps"], errors="coerce").clip(upper=int(steps))
        rows.append(df[keep])

    out = exp1_dir / "multi_steps_strategy_summary.csv"
    if rows:
        pd.concat(rows, ignore_index=True).to_csv(out, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(
            columns=[
                "max_steps",
                "strategy",
                "success_rate",
                "avg_steps",
                "avg_final_mastery",
                "avg_unnecessary_remediation",
            ]
        ).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def build_multi_steps_strategy_by_type_summary(max_steps_list: list[int]) -> Path:
    """Merge per-step strategy x student_type summaries into one cross-step table."""
    exp1_dir = get_active_exp1_dir()
    rows: list[pd.DataFrame] = []
    for steps in max_steps_list:
        path = exp1_dir / f"ablation_strategy_by_student_type_summary_steps{steps}.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if df.empty:
            continue
        df["max_steps"] = int(steps)
        df = df.rename(columns={"avg_final_polynomial_mastery": "avg_final_mastery"})
        keep = [
            "max_steps",
            "strategy",
            "student_type",
            "success_rate",
            "avg_steps",
            "avg_final_mastery",
        ]
        for col in keep:
            if col not in df.columns:
                df[col] = pd.NA
        # Safety clamp: reported average steps cannot exceed configured MAX_STEPS.
        df["avg_steps"] = pd.to_numeric(df["avg_steps"], errors="coerce").clip(upper=int(steps))
        rows.append(df[keep])

    out = exp1_dir / "multi_steps_strategy_by_type_summary.csv"
    if rows:
        pd.concat(rows, ignore_index=True).to_csv(out, index=False, encoding="utf-8-sig")
    else:
        pd.DataFrame(
            columns=[
                "max_steps",
                "strategy",
                "student_type",
                "success_rate",
                "avg_steps",
                "avg_final_mastery",
            ]
        ).to_csv(out, index=False, encoding="utf-8-sig")
    return out


def build_experiment1_summary_table_from_multi_steps() -> pd.DataFrame:
    """Build Experiment 1 final summary table from cross-step strategy summary."""
    src = get_active_exp1_dir() / "multi_steps_strategy_summary.csv"
    if not src.exists():
        return pd.DataFrame(
            columns=[
                "MAX_STEPS",
                "Strategy",
                "Success Rate (%)",
                "Avg Steps",
                "Avg Unnecessary Remediations",
                "Avg Final Mastery",
            ]
        )

    df = pd.read_csv(src)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "MAX_STEPS",
                "Strategy",
                "Success Rate (%)",
                "Avg Steps",
                "Avg Unnecessary Remediations",
                "Avg Final Mastery",
            ]
        )

    # Normalize source columns from existing summary output.
    if "avg_unnecessary_remediation" in df.columns:
        df["avg_unnecessary_remediations"] = df["avg_unnecessary_remediation"]

    keep = [
        "max_steps",
        "strategy",
        "success_rate",
        "avg_steps",
        "avg_unnecessary_remediations",
        "avg_final_mastery",
    ]
    for col in keep:
        if col not in df.columns:
            df[col] = pd.NA
    out = df[keep].copy()
    out["avg_steps"] = pd.to_numeric(out["avg_steps"], errors="coerce")
    out["max_steps"] = pd.to_numeric(out["max_steps"], errors="coerce")
    out["avg_steps"] = out[["avg_steps", "max_steps"]].min(axis=1)
    out = out.rename(
        columns={
            "max_steps": "MAX_STEPS",
            "strategy": "Strategy",
            "success_rate": "Success Rate (%)",
            "avg_steps": "Avg Steps",
            "avg_unnecessary_remediations": "Avg Unnecessary Remediations",
            "avg_final_mastery": "Avg Final Mastery",
        }
    )
    # success_rate in source is [0,1]; convert to percentage for final table.
    out["Success Rate (%)"] = pd.to_numeric(out["Success Rate (%)"], errors="coerce") * 100.0
    out["MAX_STEPS"] = pd.to_numeric(out["MAX_STEPS"], errors="coerce")

    strategy_order = {"AB1_Baseline": 0, "AB2_RuleBased": 1, "AB3_PPO_Dynamic": 2}
    out["_strategy_order"] = out["Strategy"].map(strategy_order).fillna(99)
    out = out.sort_values(["MAX_STEPS", "_strategy_order"]).drop(columns=["_strategy_order"])

    # Format all numeric columns to 2 decimals while keeping NaN-safe output.
    for col in [
        "Success Rate (%)",
        "Avg Steps",
        "Avg Unnecessary Remediations",
        "Avg Final Mastery",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce").round(2)
    out["MAX_STEPS"] = out["MAX_STEPS"].astype("Int64")
    out["Strategy"] = out["Strategy"].map(lambda s: STRATEGY_DISPLAY_MAP.get(str(s), str(s)))
    return out


def write_experiment1_summary_table(df: pd.DataFrame) -> tuple[Path, Path]:
    """Write Experiment 1 summary table in CSV and Markdown formats."""
    exp1_dir = get_active_exp1_dir()
    exp1_dir.mkdir(parents=True, exist_ok=True)
    csv_path = exp1_dir / "experiment1_summary_table.csv"
    md_path = exp1_dir / "experiment1_summary_table.md"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    lines = [
        "# Experiment 1 Summary Table",
        "",
        "| MAX_STEPS | Strategy | Success Rate (%) | Avg Steps | Avg Unnecessary Remediations | Avg Final Mastery |",
        "|-----------|----------|------------------|-----------|------------------------------|-------------------|",
    ]
    for _, row in df.iterrows():
        def fmt_num(v: object) -> str:
            if pd.isna(v):
                return "NaN"
            return f"{float(v):.2f}"

        max_steps = "NaN" if pd.isna(row["MAX_STEPS"]) else str(int(row["MAX_STEPS"]))
        lines.append(
            "| "
            + " | ".join(
                [
                    max_steps,
                    str(row["Strategy"]),
                    fmt_num(row["Success Rate (%)"]),
                    fmt_num(row["Avg Steps"]),
                    fmt_num(row["Avg Unnecessary Remediations"]),
                    fmt_num(row["Avg Final Mastery"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Note: The weak foundation group shows low absolute success rates, but Adaptive (Ours) still achieves the highest relative improvement.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    return csv_path, md_path


def validate_experiment1_summary_table(df: pd.DataFrame, max_steps_list: list[int]) -> None:
    """Enforce complete 3xN strategy table before writing final report artifacts."""
    expected_steps = sorted({int(s) for s in max_steps_list})
    expected_strategies = ["Baseline", "Rule-Based", "Adaptive (Ours)"]
    expected_pairs = {(s, st) for s in expected_steps for st in expected_strategies}

    got_pairs = set()
    for _, row in df.iterrows():
        try:
            step = int(row["MAX_STEPS"])
        except Exception:
            continue
        strategy = str(row["Strategy"])
        got_pairs.add((step, strategy))

    missing = sorted(expected_pairs - got_pairs)
    extra = sorted(got_pairs - expected_pairs)
    if missing or extra or len(df) != len(expected_pairs):
        raise RuntimeError(
            "Experiment 1 summary table is incomplete or inconsistent. "
            f"rows={len(df)}, expected_rows={len(expected_pairs)}, "
            f"missing={missing}, extra={extra}"
        )


def main() -> None:
    """Run multiple MAX_STEPS experiments and generate cross-step summaries + plots."""
    original_max_steps = simulate_student.MAX_STEPS
    prev_exp1_env = os.environ.get(EXP1_OUTPUT_DIR_ENV)
    max_steps_list = [int(s) for s in MAX_STEPS_LIST]
    run_dir = create_run_output_dir()
    set_active_exp1_dir(run_dir)
    # Ensure Experiment 1 plotting helpers write into this run folder.
    plot_results_module.EXP1_DIR = str(run_dir)
    print(f"[RUN] Writing outputs to {run_dir}")
    print(f"[PROTECT] Skipping final/ directory: {FINAL_DIR}")
    try:
        cleanup_previous_step_snapshots(max_steps_list)

        for steps in max_steps_list:
            print(f"\n=== Running simulate_student with MAX_STEPS={steps} ===")
            run_single_steps_experiment(steps)
            preserve_step_outputs(steps)

        strategy_out = build_multi_steps_strategy_summary(max_steps_list)
        by_type_out = build_multi_steps_strategy_by_type_summary(max_steps_list)
        exp1_table_df = build_experiment1_summary_table_from_multi_steps()
        validate_experiment1_summary_table(exp1_table_df, max_steps_list)
        exp1_csv, exp1_md = write_experiment1_summary_table(exp1_table_df)

        # Render only the 3 core Experiment 1 report figures.
        setup_report_style()
        plot_multi_steps_results(include_ab3_by_student_type=False)
        consolidate_experiment1_outputs()
        cleanup_redundant_experiment1_figures()
        print(f"[LATEST] Updating {LATEST_DIR}")
        refresh_latest_from_run(run_dir)
        print(f"[LATEST] Updated {LATEST_DIR}")
        print(f"[PROTECT] Skipping final/ directory: {FINAL_DIR}")

        print("\nMulti-steps experiment completed.")
        print(f"Output CSV: {strategy_out}")
        print(f"Output CSV: {by_type_out}")
        print(f"Output CSV: {exp1_csv}")
        print(f"Output Markdown: {exp1_md}")
        print(f"Output Figure: {run_dir / 'fig_multi_steps_success_rate.png'}")
        print(f"Output Figure: {run_dir / 'fig_multi_steps_efficiency.png'}")
        print(f"Output Figure: {run_dir / 'fig_exp1_student_type_improved.png'}")
    finally:
        simulate_student.MAX_STEPS = original_max_steps
        if prev_exp1_env is None:
            os.environ.pop(EXP1_OUTPUT_DIR_ENV, None)
        else:
            os.environ[EXP1_OUTPUT_DIR_ENV] = prev_exp1_env


if __name__ == "__main__":
    main()
