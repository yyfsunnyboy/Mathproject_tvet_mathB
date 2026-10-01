import codecs

with codecs.open('core/routes/practice.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '            "answer_type": skill_info.get("input_type", "text") \r\n        })\r\n    except Exception as e:'

replacement = """            "answer_type": skill_info.get("input_type", "text"),
            "grading_mode": "ai_judged_free_response" if (skill_id == "vh_數學B4_TreeDiagramCounting" or data.get("problem_type") == "tree_diagram_listing") else "deterministic_int",
            "variant": data.get("variant"),
            "problem_type": data.get("problem_type")
        })
    except Exception as e:"""

if target in content:
    content = content.replace(target, replacement)
    print("Replaced target using str.replace successfully")
else:
    print("Target string not found for str.replace")
    
    # Let's try to find ignoring whitespace
    import re
    regex = re.compile(r'"answer_type": skill_info\.get\("input_type", "text"\)\s*\}\)\s*except Exception as e:', re.DOTALL)
    if regex.search(content):
        content = regex.sub(replacement, content)
        print("Replaced target using regex successfully")
    else:
        print("Regex still failed")

with codecs.open('core/routes/practice.py', 'w', encoding='utf-8') as f:
    f.write(content)
