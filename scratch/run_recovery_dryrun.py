import sys
import json
from pathlib import Path

PROJECT_ROOT = Path("c:/Python/Mathproject_tvet_mathB")
sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.services.failed_component_recovery_service import recover_failed_components

def main():
    print("Running Failed Component Recovery Orchestrator (Dry Run)...")
    report = recover_failed_components(
        skill_id="vh_數學B1_LinearFunction",
        dry_run=True
    )
    
    # Safe dump for Windows console encoding
    output_str = json.dumps(report, indent=2, ensure_ascii=False)
    print(output_str.encode('cp950', errors='replace').decode('cp950'))

if __name__ == "__main__":
    main()
