import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill_id", required=True)
    parser.add_argument("--phase", required=True)
    args = parser.parse_args()
    
    skill_id = args.skill_id
    phase = str(args.phase).strip()
    
    if phase == "1":
        cmd = [sys.executable, "scripts/gencode_pipeline_phase1_audit.py", "--skill-id", skill_id]
    elif phase == "2":
        cmd = [sys.executable, "scripts/gencode_pipeline_phase2_build.py", "--skill-id", skill_id]
    elif phase == "3":
        cmd = [sys.executable, "scripts/gencode_pipeline_phase3_publish_gate.py", "--skill-id", skill_id]
    else:
        cmd = [sys.executable, "scripts/run_skill_gencode_pipeline.py", "--skill-id", skill_id]
        
    print(f"Executing: {' '.join(cmd)}")
    proc = subprocess.run(cmd)
    sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
