import json, re, sys
f = sys.argv[1] if len(sys.argv) > 1 else 'reports/gh_math2_unit4_stage1/formal_replay_with_regions.json'
d = json.load(open(f, encoding='utf8'))
rows = d['attempts'][-1]['rows']
print(len(rows))
pat = re.compile('[\ue000-\uf8ff]')
for r in rows:
    t = r['problem_text']
    n = r['notes']
    fields = {'problem': t}
    for k, v in n.items():
        if isinstance(v, str):
            fields['notes.' + k] = v
    for name, x in fields.items():
        m = pat.findall(x)
        if m:
            print(r['label'], name, sorted(set('U+%04X' % ord(c) for c in m)), len(m))
            for mm in list(pat.finditer(x))[:2]:
                print('    ', repr(x[max(0, mm.start() - 30):mm.end() + 30]))
