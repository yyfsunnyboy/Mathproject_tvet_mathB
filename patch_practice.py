import re
import codecs

with codecs.open('core/routes/practice.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove vh_數學B4_TreeDiagramCounting from MANUAL_REVIEW_SKILLS
content = re.sub(r'\s*\"vh_數學B4_TreeDiagramCounting\":\s*\{.*?\},\n', '\n', content, flags=re.DOTALL)

# Add grading_mode to payload_out in get_adaptive_question
target1 = '''            "answer_type": "text",
        }
        if request.args.get("adaptive_audit") == "1":'''
replacement1 = '''            "answer_type": "text",
            "grading_mode": "ai_judged_free_response" if (skill_id_for_generate == "vh_數學B4_TreeDiagramCounting" or data.get("problem_type") == "tree_diagram_listing") else "deterministic_int",
            "variant": data.get("variant"),
            "problem_type": data.get("problem_type")
        }
        if request.args.get("adaptive_audit") == "1":'''
content = content.replace(target1, replacement1)

# Add grading_mode to return value of get_next_question
target2 = '''            "image_base64": data.get("image_base64", ""), 
            "visual_aids": data.get("visual_aids", []),
            "answer_type": skill_info.get("input_type", "text") 
        })
    except Exception as e:'''
replacement2 = '''            "image_base64": data.get("image_base64", ""), 
            "visual_aids": data.get("visual_aids", []),
            "answer_type": skill_info.get("input_type", "text"),
            "grading_mode": "ai_judged_free_response" if (skill_id == "vh_數學B4_TreeDiagramCounting" or data.get("problem_type") == "tree_diagram_listing") else "deterministic_int",
            "variant": data.get("variant"),
            "problem_type": data.get("problem_type")
        })
    except Exception as e:'''
content = content.replace(target2, replacement2)

with codecs.open('core/routes/practice.py', 'w', encoding='utf-8') as f:
    f.write(content)
