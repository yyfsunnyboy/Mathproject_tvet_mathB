import re
import codecs

with codecs.open('core/routes/practice.py', 'r', 'utf-8') as f:
    content = f.read()

regex = r"""    try:
        # \[.*?\] .*?
        module_path = f"skills\.\{skill_id\}"
        if module_path in sys\.modules:
            mod = importlib\.reload\(sys\.modules\[module_path\]\)
        else:
            mod = importlib\.import_module\(module_path\)"""

replacement = r"""    try:
        if skill_id != "vh_數學B4_TreeDiagramCounting":
            # [修正 2] 強制重新載入模組，解決「有修改沒更新」問題
            module_path = f"skills.{skill_id}"
            if module_path in sys.modules:
                mod = importlib.reload(sys.modules[module_path])
            else:
                mod = importlib.import_module(module_path)
        else:
            mod = None"""

content = re.sub(regex, replacement, content, count=1, flags=re.DOTALL)

with codecs.open('core/routes/practice.py', 'w', 'utf-8') as f:
    f.write(content)
