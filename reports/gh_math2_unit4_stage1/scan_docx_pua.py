import re, sys, zipfile, collections
from pathlib import Path
p = Path(sys.argv[1])
pat = re.compile('[\ue000-\uf8ff]')
z = zipfile.ZipFile(p)
doc = z.read('word/document.xml').decode('utf8')
print(p.name, 'document.xml PUA:', collections.Counter('U+%04X' % ord(c) for c in pat.findall(doc)))
for m in list(pat.finditer(doc))[:40]:
    print('   ', repr(re.sub(r'<[^>]+>', '|', doc[max(0, m.start() - 200):m.end() + 100])[-160:]))
print([n for n in z.namelist() if 'embed' in n.lower() or 'ole' in n.lower()][:10], len([n for n in z.namelist() if n.endswith('.bin')]))
