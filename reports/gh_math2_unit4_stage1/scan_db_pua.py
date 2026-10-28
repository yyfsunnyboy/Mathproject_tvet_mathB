import re, sqlite3, sys, collections
db = sys.argv[1]
pat = re.compile('[\ue000-\uf8ff]')
con = sqlite3.connect('file:%s?mode=ro' % db.replace('\\', '/'), uri=True)
cur = con.execute("select id, source_curriculum, source_volume, source_chapter, source_description, problem_text, detailed_solution from textbook_examples")
agg = collections.Counter()
detail = []
for rid, cu, vol, ch, desc, pt, ds in cur:
    for name, x in (('problem', pt), ('solution', ds)):
        m = pat.findall(x or '')
        if m:
            agg[(cu, vol, ch, name)] += 1
            detail.append((rid, desc.split(' [')[0], name, sorted(set('U+%04X' % ord(c) for c in m))))
for k, v in sorted(agg.items()):
    print(k, v)
if len(sys.argv) > 2:
    for d in detail:
        print(d)
