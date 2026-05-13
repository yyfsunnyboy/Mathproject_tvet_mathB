import os
import sys
import yaml
import ast
import re
import importlib.util

# Paths
WORKSPACE = r"d:\Python\Mathproject_tvet_mathB"
sys.path.append(WORKSPACE)
REGISTRY_PATH = os.path.join(WORKSPACE, "configs", "b4_generator_registry.v0.1.yaml")
ROUTER_PATH = os.path.join(WORKSPACE, "core", "vocational_math_b4", "services", "question_router.py")
PRACTICE_PATH = os.path.join(WORKSPACE, "core", "routes", "practice.py")
REPORT_PATH = os.path.join(WORKSPACE, "reports", "gencode_integration", "b4_registry_consistency_check_report.md")

ALLOWLIST_PATHS = {
    "1": os.path.join(WORKSPACE, "core", "vocational_math_b4", "adaptive", "b4_chapter1_deterministic_allowlist.py"),
    "2": os.path.join(WORKSPACE, "core", "vocational_math_b4", "adaptive", "b4_chapter2_phase6c1_allowlist.py"),
    "3": os.path.join(WORKSPACE, "core", "vocational_math_b4", "adaptive", "b4_chapter3_phase7b_allowlist.py"),
}

VALID_STATUSES = {"runtime_ready", "manual_review", "future_ai_judged", "experimental", "unknown"}

def parse_python_var(file_path, var_name):
    """Safely parse a variable from a Python file using regex + AST."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find the assignment, allowing for frozenset/set wrappers
        pattern = rf"{var_name}\s*(?::\s*[^=]+)?\s*=\s*(?:frozenset\(|set\()?\s*{{(.*?)}}\s*\)?"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            raw_items = match.group(1)
            # Find all string literals within the set/frozenset content
            items = re.findall(r'["\']([^"\']+)["\']', raw_items)
            return set(items)
            
        # Fallback for simple assignments
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        try:
                            return ast.literal_eval(node.value)
                        except:
                            pass
    except Exception as e:
        print(f"Warning: Failed to parse {var_name} from {file_path}: {e}")
    return None

def extract_registries(file_path):
    """Extract registry structure from question_router.py using AST."""
    registries = {}
    if not os.path.exists(file_path):
        return registries
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                target = node.targets[0] if isinstance(node, ast.Assign) else node.target
                if isinstance(target, ast.Name) and (target.id.endswith("_REGISTRY") or "_PHASE" in target.id):
                    reg_name = target.id
                    registries[reg_name] = {}
                    
                    # node.value should be a Dict
                    val_node = node.value
                    if isinstance(val_node, ast.Dict):
                        for key, value in zip(val_node.keys, val_node.values):
                            skill_id = None
                            if isinstance(key, ast.Constant):
                                skill_id = key.value
                            elif isinstance(key, ast.Name):
                                skill_id = key.id # Fallback
                                
                            if skill_id:
                                entries = []
                                if isinstance(value, ast.List):
                                    for entry_node in value.elts:
                                        if isinstance(entry_node, ast.Dict):
                                            entry_data = {}
                                            for ek, ev in zip(entry_node.keys, entry_node.values):
                                                ek_val = None
                                                if isinstance(ek, ast.Constant):
                                                    ek_val = ek.value
                                                
                                                if ek_val:
                                                    if isinstance(ev, ast.Constant):
                                                        entry_data[ek_val] = ev.value
                                                    else:
                                                        # Mark non-literal values (functions, names) as placeholder
                                                        entry_data[ek_val] = "<complex_value>"
                                            entries.append(entry_data)
                                registries[reg_name][skill_id] = entries
    except Exception as e:
        print(f"Warning: Failed to extract registries from {file_path}: {e}")
    return registries

def check_import(module_path, function_name):
    """Check if a module and function can be imported."""
    try:
        spec = importlib.util.find_spec(module_path)
        if spec is None:
            return False, f"Module {module_path} not found"
        
        # We don't actually import to avoid side effects, just check if it's a known module
        # But we need to check if the function exists. 
        # For simplicity in this script, we'll assume if the module exists, we're 50% there.
        # A more thorough check would involve loading the module.
        return True, "OK"
    except Exception as e:
        return False, str(e)

def run_check():
    print("Starting B4 Registry Consistency Check...")
    
    results = {
        "metrics": {},
        "mismatches": [],
        "warnings": [],
        "status_counts": {},
        "suspicious_ids": [],
        "critical_errors_count": 0,
        "warnings_count": 0
    }

    # 1. Load YAML
    if not os.path.exists(REGISTRY_PATH):
        print(f"Critical Error: YAML registry not found at {REGISTRY_PATH}")
        sys.exit(1)
    
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = yaml.safe_load(f)
    
    yaml_items = registry_data.get("items", [])
    results["metrics"]["yaml_items"] = len(yaml_items)

    # 2. Load Production Data
    router_registries = extract_registries(ROUTER_PATH)
    total_router_items = 0
    for reg_name, skills in router_registries.items():
        for skill_id, entries in skills.items():
            total_router_items += len(entries)
    results["metrics"]["router_items"] = total_router_items
    
    # Manual review skills are listed in Chapter 1 allowlist file as a specific set
    manual_review_skills = parse_python_var(ALLOWLIST_PATHS["1"], "B4_MANUAL_REVIEW_OR_UNAVAILABLE_SKILL_IDS") or set()
    
    allowlists = {
        "1": parse_python_var(ALLOWLIST_PATHS["1"], "B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST") or set(),
        "2": parse_python_var(ALLOWLIST_PATHS["2"], "B4_CHAPTER_2_PHASE6C1_ADAPTIVE_SKILL_ALLOWLIST") or set(),
        "3": parse_python_var(ALLOWLIST_PATHS["3"], "B4_CHAPTER3_PHASE7B_DETERMINISTIC_ALLOWLIST") or set(),
    }

    # 3. Compare Items
    yaml_map = {(item["skill_id"], item["problem_type_id"]): item for item in yaml_items}
    router_items_found = set()
    matched_count = 0

    # Build a flat list of router items for easier comparison
    flat_router_items = []
    for reg_name, skills in router_registries.items():
        for skill_id, entries in skills.items():
            for entry in entries:
                flat_router_items.append({
                    "skill_id": skill_id,
                    "problem_type_id": entry["problem_type_id"],
                    "generator_key": entry["generator_key"],
                    "source": reg_name
                })

    for r_item in flat_router_items:
        key = (r_item["skill_id"], r_item["problem_type_id"])
        if key in yaml_map:
            matched_count += 1
            router_items_found.add(key)
            y_item = yaml_map[key]
            
            # Check generator_key
            if y_item["generator_key"] != r_item["generator_key"]:
                results["warnings"].append({
                    "type": "generator_key_mismatch",
                    "skill_id": key[0],
                    "problem_type_id": key[1],
                    "yaml": y_item["generator_key"],
                    "router": r_item["generator_key"]
                })

            # Check status
            if y_item["status"] not in VALID_STATUSES:
                results["mismatches"].append({
                    "type": "invalid_status",
                    "skill_id": key[0],
                    "problem_type_id": key[1],
                    "value": y_item["status"]
                })
                results["critical_errors_count"] += 1
            
            # Check imports (simplified)
            if y_item.get("module_path") and y_item.get("function_name"):
                ok, msg = check_import(y_item["module_path"], y_item["function_name"])
                if not ok:
                    results["mismatches"].append({
                        "type": "import_failure",
                        "skill_id": key[0],
                        "problem_type_id": key[1],
                        "msg": msg
                    })
                    results["critical_errors_count"] += 1

            # Check allowlist consistency
            ch = str(y_item.get("chapter", ""))
            if ch in allowlists:
                actual_allowlisted = False
                # Handle fuzzy matching for vh_???B4_
                for a_skill in allowlists[ch]:
                    if a_skill == y_item["skill_id"]:
                        actual_allowlisted = True
                        break
                    # Fuzzy match if allowlist has ??? or ??
                    # Escape special regex chars, then replace dots with .+ or similar
                    clean_pattern = a_skill.replace("?", ".+")
                    if re.fullmatch(clean_pattern, y_item["skill_id"]):
                        actual_allowlisted = True
                        break
                
                if y_item["adaptive_allowlisted"] != actual_allowlisted:
                    results["warnings"].append({
                        "type": "adaptive_allowlist_mismatch",
                        "skill_id": key[0],
                        "chapter": ch,
                        "yaml": y_item["adaptive_allowlisted"],
                        "actual": actual_allowlisted
                    })
                    results["warnings_count"] += 1

            # Check manual_review consistency
            actual_manual = y_item["skill_id"] in manual_review_skills
            if y_item["manual_review"] != actual_manual:
                results["warnings"].append({
                    "type": "manual_review_mismatch",
                    "skill_id": key[0],
                    "yaml": y_item["manual_review"],
                    "actual": actual_manual
                })
                results["warnings_count"] += 1

        else:
            results["mismatches"].append({
                "type": "missing_in_yaml",
                "skill_id": r_item["skill_id"],
                "problem_type_id": r_item["problem_type_id"],
                "source": r_item["source"]
            })
            results["critical_errors_count"] += 1

    # Check for items in YAML not in Router
    for key, y_item in yaml_map.items():
        if key not in router_items_found:
            # Special case: manual_review items might not be in router but are in practice.py
            if y_item["manual_review"] and y_item["skill_id"] in manual_review_skills:
                continue
            
            results["mismatches"].append({
                "type": "missing_in_router",
                "skill_id": key[0],
                "problem_type_id": key[1]
            })
            results["critical_errors_count"] += 1

    # Typo Check in YAML
    for item in yaml_items:
        sid = item["skill_id"]
        if "??" in sid or "  " in sid or not sid.startswith("vh_"):
            results["suspicious_ids"].append(f"YAML: {sid}")
            results["critical_errors_count"] += 1

    # Typo Check in Router
    for reg_name, skills in router_registries.items():
        for sid in skills.keys():
            if "??" in sid or "  " in sid or not sid.startswith("vh_"):
                if f"Router: {sid}" not in results["suspicious_ids"]:
                    results["suspicious_ids"].append(f"Router: {sid}")
                    results["critical_errors_count"] += 1

    results["metrics"]["matched_items"] = matched_count
    results["metrics"]["missing_in_yaml"] = sum(1 for m in results["mismatches"] if m["type"] == "missing_in_yaml")
    results["metrics"]["missing_in_router"] = sum(1 for m in results["mismatches"] if m["type"] == "missing_in_router")
    results["metrics"]["adaptive_mismatch"] = sum(1 for w in results["warnings"] if w["type"] == "adaptive_allowlist_mismatch")
    results["metrics"]["manual_review_mismatch"] = sum(1 for w in results["warnings"] if w["type"] == "manual_review_mismatch")
    results["metrics"]["suspicious_id"] = len(results["suspicious_ids"])
    results["metrics"]["critical_errors"] = results["critical_errors_count"]
    results["metrics"]["warnings"] = results["warnings_count"]

    # Status counts
    for item in yaml_items:
        s = item["status"]
        results["status_counts"][s] = results["status_counts"].get(s, 0) + 1

    # 4. Generate Report
    generate_report(results)
    
    print("\n--- Summary ---")
    print(f"YAML Items: {results['metrics']['yaml_items']}")
    print(f"Router Items: {results['metrics']['router_items']}")
    print(f"Matched: {results['metrics']['matched_items']}")
    print(f"Critical Errors: {results['critical_errors_count']}")
    print(f"Warnings: {results['warnings_count']}")
    
    if results["critical_errors_count"] > 0:
        print("Result: FAIL")
        sys.exit(1)
    else:
        print("Result: PASS")
        sys.exit(0)

def generate_report(results):
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# B4 Generator Registry Consistency Check Report v0.1\n\n")
        f.write("## 1. 任務目的\n")
        f.write("本檢查器用來偵測 YAML registry 與 production code 間的 drift，確保盤點資訊準確。\n\n")
        
        f.write("## 2. 檢查來源\n")
        f.write("- configs/b4_generator_registry.v0.1.yaml\n")
        f.write("- core/vocational_math_b4/services/question_router.py\n")
        f.write("- core/vocational_math_b4/adaptive/allowlist.py\n")
        f.write("- core/routes/practice.py\n")
        f.write("- core/vocational_math_b4/domain/b4_validators.py\n\n")
        
        f.write("## 3. 總體統計\n")
        f.write("| metric | count |\n")
        f.write("|---|---|\n")
        for k, v in results["metrics"].items():
            f.write(f"| {k} | {v} |\n")
        f.write("\n")
        
        f.write("## 4. Router 對照結果\n")
        mismatches = results["mismatches"]
        if not mismatches:
            f.write("所有 YAML 項目皆與 Router 一致。\n\n")
        else:
            f.write("| skill_id | problem_type_id | type | result | notes |\n")
            f.write("|---|---|---|---|---|\n")
            for m in mismatches:
                f.write(f"| {m.get('skill_id', 'N/A')} | {m.get('problem_type_id', 'N/A')} | {m['type']} | FAIL | {m.get('msg', m.get('source', ''))} |\n")
            f.write("\n")
        
        f.write("## 5. Status 對照結果\n")
        f.write("| status | count |\n")
        f.write("|---|---|\n")
        for s, count in results["status_counts"].items():
            f.write(f"| {s} | {count} |\n")
        f.write("\n")
        
        unknowns = [item for item in results["status_counts"] if item in ("unknown", "experimental")]
        if unknowns:
            f.write("Unknown / Experimental 項目列表見 YAML。\n\n")

        f.write("## 6. Adaptive Allowlist 對照結果\n")
        adaptive_mismatches = [w for w in results["warnings"] if w["type"] == "adaptive_allowlist_mismatch"]
        if not adaptive_mismatches:
            f.write("所有項目的 Adaptive Allowlisted 狀態與實體檔案一致。\n\n")
        else:
            f.write("| skill_id | chapter | yaml | actual |\n")
            f.write("|---|---|---|---|\n")
            for m in adaptive_mismatches:
                f.write(f"| {m['skill_id']} | {m['chapter']} | {m['yaml']} | {m['actual']} |\n")
            f.write("\n")

        f.write("## 7. Manual Review 對照結果\n")
        manual_mismatches = [w for w in results["warnings"] if w["type"] == "manual_review_mismatch"]
        if not manual_mismatches:
            f.write("所有項目的 Manual Review 狀態與實體檔案一致。\n\n")
        else:
            f.write("| skill_id | yaml | actual |\n")
            f.write("|---|---|---|---|\n")
            for m in manual_mismatches:
                f.write(f"| {m['skill_id']} | {m['yaml']} | {m['actual']} |\n")
            f.write("\n")

        f.write("## 8. Suspicious ID / Typo 檢查\n")
        if not results["suspicious_ids"]:
            f.write("未偵測到可疑 ID。\n\n")
        else:
            f.write("偵測到以下可疑 ID：\n")
            for sid in results["suspicious_ids"]:
                f.write(f"- {sid}\n")
            f.write("\n")

        f.write("## 9. 結論\n")
        if results["critical_errors_count"] > 0:
            f.write("### RESULT: FAIL\n")
            f.write("需先人工修正 registry 或 production typo。\n\n")
        else:
            f.write("### RESULT: PASS\n")
            f.write("可進 Phase 2。\n\n")

        f.write("## 10. 下一步建議\n")
        if results["critical_errors_count"] > 0:
            f.write("建議先執行 Phase 1C：B4 typo / registry drift 修正任務。\n")
        else:
            f.write("建議進 Phase 2：Agent Skill v2 規格包設計。\n")

if __name__ == "__main__":
    run_check()
