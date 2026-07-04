import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.proposal_draft_orchestrator_service import build_pending_domain_drafts

def main():
    print("Running Capability Proposal Draft Orchestrator (Dry Run)...")
    report = build_pending_domain_drafts(
        skill_id="vh_數學B1_LinearFunction",
        dry_run=True
    )
    
    output_str = json.dumps(report, indent=2, ensure_ascii=False)
    print(output_str.encode('cp950', errors='replace').decode('cp950'))

if __name__ == "__main__":
    main()
