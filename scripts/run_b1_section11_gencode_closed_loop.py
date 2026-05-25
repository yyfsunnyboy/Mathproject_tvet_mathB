import argparse
import json
import subprocess
import sys
from pathlib import Path

TARGET_SKILL = "vh_數學B1_AbsoluteValue"
TARGET_PT = "absolute_value_numeric_evaluation"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--skill-id", default=None)
    p.add_argument("--max-rounds", type=int, default=5)
    args = p.parse_args()

    if args.skill_id and args.skill_id != TARGET_SKILL:
        raise RuntimeError("此穩定版僅支援 vh_數學B1_AbsoluteValue")

    root = Path(__file__).resolve().parents[1]
    skill = args.skill_id or TARGET_SKILL
    cmds = [
        [sys.executable, "scripts/gencode_skill_inventory.py", "--skill-id", skill],
        [sys.executable, "scripts/gencode_problem_type_closed_loop.py", "--skill-id", skill, "--problem-type-id", TARGET_PT, "--max-rounds", str(args.max_rounds)],
    ]
    steps = []
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, timeout=180)
        steps.append({"cmd": cmd, "exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
        if r.returncode != 0:
            print(json.dumps({"success": False, "failed_step": cmd, "steps": steps}, ensure_ascii=False, indent=2))
            raise SystemExit(r.returncode)
    print(json.dumps({"success": True, "steps": steps}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
