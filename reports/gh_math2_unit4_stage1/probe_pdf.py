import sys
try:
    import fitz
except ImportError:
    print('no fitz'); sys.exit()
doc = fitz.open('textbook_import/uploaded_sources/general/數學2/bf39d447345e_單元04-排列.pdf')
print(len(doc), 'pages')
import re
shown = 0
for pno, page in enumerate(doc):
    d = page.get_text('rawdict')
    for b in d['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                chars = s['chars']
                txt = ''.join(c['c'] for c in chars)
                if any(0xE000 <= ord(c['c']) <= 0xF8FF for c in chars):
                    print('PUA span page', pno + 1, s['font'], repr(txt), [hex(ord(c['c'])) for c in chars if 0xE000 <= ord(c['c']) <= 0xF8FF])
                if txt.strip() == 'P' and shown < 6:
                    # print the neighbours on the same line
                    shown += 1
                    print('--- page', pno + 1, 'line spans:')
                    for s2 in l['spans']:
                        print('   ', s2['font'], round(s2['size'], 1), [(c['c'], round(c['bbox'][0], 2), round(c['bbox'][2], 2)) for c in s2['chars']])
