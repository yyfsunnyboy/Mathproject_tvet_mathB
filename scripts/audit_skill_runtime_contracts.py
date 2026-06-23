import os
import sys
import importlib
import inspect
import json
from app import create_app
from core.legacy_generator_adapter import invoke_skill_generate, normalize_runtime_value

def audit_skills():
    app = create_app()
    with app.app_context():
        skills_dir = os.path.join(app.root_path, 'skills')
        if not os.path.exists(skills_dir):
            print(f"Skills directory not found: {skills_dir}")
            return

        py_files = sorted([f[:-3] for f in os.listdir(skills_dir) if f.endswith('.py') and f != '__init__.py'])
        
        stats = {
            "scanned": 0,
            "import_success": 0,
            "smoke_success": 0,
            "sig_incompatible": 0, # count cases where adapter is needed to prevent crash
            "fraction_risk": 0,
            "wrapper_missing": 0,
        }

        print(f"Auditing {len(py_files)} skill modules...")
        audit_results = []

        for skill_id in py_files:
            stats["scanned"] += 1
            result = {
                "skill_id": skill_id,
                "module_exists": True,
                "import_success": False,
                "generate_exists": False,
                "generate_signature": None,
                "accepts_component_id": False,
                "accepts_level": False,
                "smoke_result": "failed",
                "fraction_formatting_risk": False,
                "result_contract_valid": False,
                "error_type": None,
                "category": None
            }

            # 1. Import
            try:
                module = importlib.import_module(f"skills.{skill_id}")
                result["import_success"] = True
                stats["import_success"] += 1
            except Exception as e:
                result["error_type"] = f"import_error: {str(e)}"
                result["category"] = "C" # wrapper missing / load error
                stats["wrapper_missing"] += 1
                audit_results.append(result)
                continue

            # 2. Check generate
            generate_fn = getattr(module, "generate", None)
            if not generate_fn or not callable(generate_fn):
                result["error_type"] = "generate_missing"
                result["category"] = "D" # logic/missing error
                audit_results.append(result)
                continue
            
            result["generate_exists"] = True

            # 3. Signature inspect
            try:
                sig = inspect.signature(generate_fn)
                result["generate_signature"] = str(sig)
                params = sig.parameters
                accepts_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
                
                result["accepts_level"] = accepts_var_kw or ("level" in params)
                result["accepts_component_id"] = accepts_var_kw or ("component_id" in params)
                
                # If it doesn't accept component_id but we would have sent it, it's incompatible without adapter
                if not result["accepts_component_id"]:
                    stats["sig_incompatible"] += 1

            except Exception as e:
                result["error_type"] = f"signature_inspect_error: {str(e)}"
                result["category"] = "D"

            # 4. Check formatting risk (source scan for :.2f / :.1f on Fraction)
            try:
                src_path = inspect.getsourcefile(module)
                if src_path and os.path.exists(src_path):
                    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                        src_content = f.read()
                        if "Fraction" in src_content and (".2f" in src_content or ".1f" in src_content):
                            result["fraction_formatting_risk"] = True
                            stats["fraction_risk"] += 1
            except Exception:
                pass

            # 5. Smoke Run via Adapter
            try:
                # Call with all kwargs; adapter will filter them safely
                pld = invoke_skill_generate(
                    module,
                    level=1,
                    component_id="comp_smoke_test_123",
                    seed=42,
                    skill_id=skill_id
                )
                result["smoke_result"] = "success"
                stats["smoke_success"] += 1

                # Normalize to test serialization
                norm_pld = normalize_runtime_value(pld)

                # Validate result contract
                if isinstance(norm_pld, dict) and ("question_text" in norm_pld or "new_question_text" in norm_pld) and "answer" in norm_pld:
                    result["result_contract_valid"] = True
                else:
                    result["error_type"] = "invalid_result_keys"
                    result["category"] = "E"
            except Exception as e:
                result["error_type"] = f"smoke_execution_error: {str(e)}"
                result["category"] = "A" if "unexpected keyword argument" in str(e) else "D"

            audit_results.append(result)

        # Print audit report
        print("\n=== RUNTIME AUDIT STATISTICS ===")
        print(f"Total skills scanned:       {stats['scanned']}")
        print(f"Import success:            {stats['import_success']}")
        print(f"Smoke run success:         {stats['smoke_success']}")
        print(f"Incompatible signatures:    {stats['sig_incompatible']} (prevented from crashing by adapter)")
        print(f"Fraction formatting risks: {stats['fraction_risk']}")
        print(f"Wrapper missing / broken:   {stats['wrapper_missing']}")
        print("=================================\n")

        print("Sample incompatibilities or issues:")
        for r in audit_results:
            if not r["result_contract_valid"] or r["error_type"]:
                print(f"- Skill: {r['skill_id']} | Category: {r['category']} | Error: {r['error_type']}")

if __name__ == '__main__':
    audit_skills()
