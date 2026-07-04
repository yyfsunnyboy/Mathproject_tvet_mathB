import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.proposal_approval_service import review_capability_proposals

def main():
    print("Running Capability Proposal Approval Gate (Dry Run)...")
    report = review_capability_proposals(
        skill_id="vh_數學B1_LinearFunction",
        decisions={},  # Empty decisions as requested (no automatic decisions)
        dry_run=True
    )
    
    output_str = json.dumps(report, indent=2, ensure_ascii=False)
    print(output_str.encode('cp950', errors='replace').decode('cp950'))

if __name__ == "__main__":
    main()
