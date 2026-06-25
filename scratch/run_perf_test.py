import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.gencode.test_skills_performance import test_status_map_does_not_audit_variation_by_default

def main():
    try:
        test_status_map_does_not_audit_variation_by_default()
        print("Test SUCCESS")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Test FAILED: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
