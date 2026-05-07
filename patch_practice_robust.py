import re
import codecs

with codecs.open('core/routes/practice.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 1: MANUAL_REVIEW_SKILLS
regex1 = r"(\"vh_數學B4_TreeDiagramCounting\":\s*\{.*?\},\s*)\"vh_數學B4_PascalTriangle\""
if re.search(regex1, content, re.DOTALL):
    content = re.sub(regex1, '\"vh_數學B4_PascalTriangle\"', content, count=1, flags=re.DOTALL)
    print("Replaced target1 successfully")
else:
    print("Regex 1 not found")

# Replace 2: get_adaptive_question grading_mode
regex2 = r"(\"answer_type\": \"text\",\s*\})\s*if request\.args\.get\(\"adaptive_audit\"\)"
replacement2 = """"answer_type": "text",
            "grading_mode": "ai_judged_free_response" if (skill_id_for_generate == "vh_數學B4_TreeDiagramCounting" or data.get("problem_type") == "tree_diagram_listing") else "deterministic_int",
            "variant": data.get("variant"),
            "problem_type": data.get("problem_type")
        }
        if request.args.get("adaptive_audit")"""
if re.search(regex2, content, re.DOTALL):
    content = re.sub(regex2, replacement2, content, count=1, flags=re.DOTALL)
    print("Replaced target2 successfully")
else:
    print("Regex 2 not found")

# Replace 3: get_next_question grading_mode
regex3 = r"(\"answer_type\": skill_info\.get\(\"input_type\", \"text\"\)\s*\})\s*except Exception as e:"
replacement3 = """"answer_type": skill_info.get("input_type", "text"),
            "grading_mode": "ai_judged_free_response" if (skill_id == "vh_數學B4_TreeDiagramCounting" or data.get("problem_type") == "tree_diagram_listing") else "deterministic_int",
            "variant": data.get("variant"),
            "problem_type": data.get("problem_type")
        })
    except Exception as e:"""
if re.search(regex3, content, re.DOTALL):
    content = re.sub(regex3, replacement3, content, count=1, flags=re.DOTALL)
    print("Replaced target3 successfully")
else:
    print("Regex 3 not found")

with codecs.open('core/routes/practice.py', 'w', encoding='utf-8') as f:
    f.write(content)
