import codecs

with codecs.open('core/routes/practice.py', 'r', 'utf-8') as f:
    content = f.read()

target = """        module_path = f"skills.{skill_id}"
        if module_path in sys.modules:
            mod = importlib.reload(sys.modules[module_path])
        else:
            mod = importlib.import_module(module_path)"""

replacement = """        module_path = f"skills.{skill_id}"
        if skill_id != "vh_數學B4_TreeDiagramCounting":
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)
        else:
            mod = None"""

if target in content:
    content = content.replace(target, replacement)
    with codecs.open('core/routes/practice.py', 'w', 'utf-8') as f:
        f.write(content)
    print("Replaced import successfully in get_next_question")
else:
    print("Target not found for get_next_question import")

target2 = """        module_path = f"skills.{skill_id_for_generate}"
        if module_path in sys.modules:
            mod = importlib.reload(sys.modules[module_path])
        else:
            mod = importlib.import_module(module_path)"""

replacement2 = """        module_path = f"skills.{skill_id_for_generate}"
        if skill_id_for_generate != "vh_數學B4_TreeDiagramCounting":
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)
        else:
            mod = None"""

if target2 in content:
    content = content.replace(target2, replacement2)
    with codecs.open('core/routes/practice.py', 'w', 'utf-8') as f:
        f.write(content)
    print("Replaced import successfully in get_adaptive_question")
else:
    print("Target not found for get_adaptive_question import")
