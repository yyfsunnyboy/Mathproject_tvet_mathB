import sys, zipfile
sys.path.insert(0, '.')
from core.mtef import MTEF

DOCX = 'textbook_import/uploaded_sources/general/數學2/327f295a06d7_單元04-排列.docx'
z = zipfile.ZipFile(DOCX)
for n in sys.argv[1:]:
    eqn, err = MTEF.OpenBytes(z.read('word/embeddings/oleObject%s.bin' % n))
    print('==', n, repr(eqn.Translate()))
    for node in eqn.nodes:
        v = node.value
        if hasattr(v, 'mtcode'):
            print('  CHAR  U+%04X typeface=%s(face=%s) bits8=%s bits16=%s opts=%s' % (
                v.mtcode or 0, v.typeface, (v.typeface or 0) - 128, getattr(v, 'bits8', None), getattr(v, 'bits16', None), getattr(v, 'options', None)))
        elif hasattr(v, 'embellType'):
            print('  EMBELL type=%s' % v.embellType)
        elif hasattr(v, 'selector'):
            print('  TMPL selector=%s variation=%s' % (v.selector, getattr(v, 'variation', None)))
        else:
            print('  ', node.tag, type(v).__name__)
