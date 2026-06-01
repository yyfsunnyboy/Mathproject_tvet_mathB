from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gencode_pipeline_phase1_audit import ANSWER_CONTRACT_DEFAULTS

skill_id = "vh_數學B1_LinearFunction"
print("Input skill_id:", repr(skill_id))
print("Keys in ANSWER_CONTRACT_DEFAULTS:")
for k in ANSWER_CONTRACT_DEFAULTS.keys():
    print("-", repr(k), "Match:", k == skill_id)
