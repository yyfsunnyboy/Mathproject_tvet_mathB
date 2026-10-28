from pathlib import Path
import fitz, docx, zipfile, re, sys
from lxml import etree
sys.stdout.reconfigure(encoding='utf-8')
root=Path('textbook_import/uploaded_sources/general/數學2')
pdf=fitz.open(next(root.glob('*單元03*.pdf')))
print('PDF_PAGES',len(pdf))
for i in [1,3,5,8,16,17]:
 p=pdf[i]; print('PAGE',i+1,'images',len(p.get_images()),'drawings',len(p.get_drawings()))
 print(p.get_text()[:7500])
for i in [8,16,17]:
 pdf[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(f'reports/gh_math2_unit3_stage1/pdf_page_{i+1}.png')
file=next(root.glob('*單元03*.docx'))
d=docx.Document(file)
print('DOCX_PARAGRAPHS',len(d.paragraphs),'TABLES',len(d.tables))
for i,p in enumerate(d.paragraphs):
 t=p.text.strip()
 if re.search('例題|隨堂練習|觀念澄清|基礎題|進階題|習題|甲[.．]|乙[.．]',t) and len(t)<150:
  print('P',i,t[:140])
with zipfile.ZipFile(file) as z:
 xml=z.read('word/document.xml').decode()
 tree=etree.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 inst=[''.join(x.itertext()) for x in tree.xpath('//w:instrText',namespaces=ns)]
 syms=[(x.get('{'+ns['w']+'}font'),x.get('{'+ns['w']+'}char')) for x in tree.xpath('//w:sym',namespaces=ns)]
 print('EQ_FIELDS',sum('EQ ' in x for x in inst),'instr',inst,'syms',len(syms),'symbol_codes',sorted(set(syms)))
