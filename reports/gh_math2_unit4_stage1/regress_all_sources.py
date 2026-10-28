import sys, zipfile, re, collections
from pathlib import Path
sys.path.insert(0, '.')
import core.mtef.chars as chars
from core.mtef import mtef_bytes_to_latex

PUA = re.compile('[\ue000-\uf8ff]')
files = sorted(Path('textbook_import').rglob('*.docx'))
files = [f for f in files if not f.name.startswith('~$')]
saved = dict(chars.SpaceTypefaceChars)
rows = []
for f in files:
    try:
        z = zipfile.ZipFile(f)
    except Exception:
        continue
    oles = [n for n in z.namelist() if n.startswith('word/embeddings/oleObject') and n.endswith('.bin')]
    if not oles:
        continue
    changed = other_diff = total = new_pua = 0
    pua_codes = collections.Counter()
    for n in oles:
        b = z.read(n)
        chars.SpaceTypefaceChars.clear(); chars.SpaceTypefaceChars.update(saved)
        # mtef.py imported the same dict object, so mutate in place
        new, _ = mtef_bytes_to_latex(b)
        chars.SpaceTypefaceChars.clear()
        old, _ = mtef_bytes_to_latex(b)
        chars.SpaceTypefaceChars.update(saved)
        total += 1
        if new != old:
            changed += 1
            if old.replace('\uef08', '') != new:
                other_diff += 1
        for c in PUA.findall(new):
            pua_codes['U+%04X' % ord(c)] += 1
    rows.append((str(f.relative_to('textbook_import')), total, changed, other_diff, dict(pua_codes)))
for r in rows:
    print(r)
