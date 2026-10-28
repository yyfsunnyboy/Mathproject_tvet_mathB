import fitz
doc = fitz.open('textbook_import/uploaded_sources/general/數學2/bf39d447345e_單元04-排列.pdf')
page = doc[3]
d = page.get_text('rawdict')
chars = []
for b in d['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            for c in s['chars']:
                chars.append((c['c'], c['bbox'], s['font'], s['size']))
# group by baseline row around P
for i, (c, bb, f, sz) in enumerate(chars):
    if c == 'P' and f.startswith('MMTimes') and sz > 11:
        row = [x for x in chars if abs(x[1][3] - bb[3]) < 7 and x[1][0] >= bb[0] - 1 and x[1][0] < bb[0] + 150]
        row.sort(key=lambda x: x[1][0])
        print('P at', round(bb[0], 1), round(bb[3], 1))
        print('   ', [(x[0], round(x[1][0], 1), round(x[1][2], 1), round(x[3], 1)) for x in row][:20])
