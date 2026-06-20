import json
from pathlib import Path

transcript_path = Path("C:/Users/yehiv/.gemini/antigravity/brain/a83fefd5-4be0-4fbb-b6ae-5966666a7c0a/.system_generated/logs/transcript_full.jsonl")

if not transcript_path.exists():
    print("Transcript not found.")
    exit(1)

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            tool_calls = data.get("tool_calls", []) or []
            # Check if tool_calls is a list
            if not isinstance(tool_calls, list):
                continue
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args") or {}
                target_file = str(args.get("TargetFile") or "")
                if "line_equation_domain.py" in target_file:
                    print("="*80)
                    print(f"Step {data.get('step_index')} Tool {name}")
                    print("="*80)
                    if "ReplacementContent" in args:
                        print("--- TargetContent ---")
                        print(args.get("TargetContent"))
                        print("--- ReplacementContent ---")
                        print(args.get("ReplacementContent"))
                    elif "ReplacementChunks" in args:
                        for idx, chunk in enumerate(args["ReplacementChunks"]):
                            print(f"--- Chunk {idx} TargetContent ---")
                            print(chunk.get("TargetContent"))
                            print(f"--- Chunk {idx} ReplacementContent ---")
                            print(chunk.get("ReplacementContent"))
                    elif "CodeContent" in args:
                        print("--- CodeContent ---")
                        print(args.get("CodeContent"))
        except Exception as e:
            print("Error parsing line:", e)
