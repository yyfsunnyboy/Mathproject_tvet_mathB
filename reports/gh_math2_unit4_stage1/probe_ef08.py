import sys, zipfile
sys.path.insert(0, '.')
from core.mtef import mtef_bytes_to_latex, MTEF

DOCX = 'textbook_import/uploaded_sources/general/數學2/327f295a06d7_單元04-排列.docx'
z = zipfile.ZipFile(DOCX)
names = sorted([n for n in z.namelist() if n.startswith('word/embeddings/oleObject')],
               key=lambda s: int(''.join(c for c in s if c.isdigit())))
hits = []
for n in names:
    b = z.read(n)
    latex, meta = mtef_bytes_to_latex(b)
    if '\uef08' in latex:
        hits.append(n)
print(len(names), 'ole;', len(hits), 'with EF08:', hits[:50])


def dump(ast, depth=0):
    tag = ast.tag
    v = ast.value
    extra = ''
    if tag.name == 'CHAR' if hasattr(tag, 'name') else False:
        extra = 'mtcode=U+%04X typeface=%s emb=%s opts=%s' % (v.mtcode or 0, v.typeface, getattr(v, 'embellishments', None), getattr(v, 'options', None))
    elif hasattr(v, 'selector'):
        extra = 'selector=%s' % v.selector
    print('  ' * depth, tag, extra)
    for c in ast.children or []:
        dump(c, depth + 1)


if len(sys.argv) > 1:
    n = sys.argv[1]
    eqn, err = MTEF.OpenBytes(z.read(n))
    print(eqn.Translate())
    ast = eqn.makeAST() if hasattr(eqn, 'makeAST') else None
    print('ast', type(ast))
    if ast is not None:
        dump(ast if hasattr(ast, 'tag') else ast[0])
