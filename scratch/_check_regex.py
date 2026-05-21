import re
from pathlib import Path

PERM_COMB_RE = r"(?:\bP\s*\(|\bC\s*\(|\bP\s*\^|\bC\s*\^|\bP_|\bC_)"
re.compile(PERM_COMB_RE)

lines = Path(r"c:\Python\Mathproject_tvet_mathB\core\textbook_processor.py").read_text(
    encoding="utf-8-sig"
).splitlines()
for ln in (5258, 5645):
    assert PERM_COMB_RE in lines[ln - 1]
    assert "兜嗽" not in lines[ln - 1]
print("L5258/L5645 OK")

m = re.search(r"re\.sub\((r'[^']+')", lines[4730])
pat = eval(m.group(1))
re.compile(pat)
print("L4731 OK:", pat)

re.compile(r"[|｜、，,;]")
print("L2981 table_re OK")
print("done")
