import json, sqlite3, re, pathlib, fitz, difflib, sys
sys.stdout.reconfigure(encoding='utf-8')
c=sqlite3.connect('file:instance/kumon_math.db?mode=ro',uri=True);c.row_factory=sqlite3.Row
pdf=fitz.open(next(pathlib.Path('textbook_import/uploaded_sources/general/數學2').glob('*單元03*.pdf')))
for r in c.execute('select id,problem_text,notes from textbook_examples where id between 12744 and 12773'):
 n=json.loads(r['notes']);pg=(n.get('pdf_visual_enrichment') or {}).get('page')
 s=''.join(re.findall(r'[\u4e00-\u9fff]',r['problem_text']))
 t=''.join(re.findall(r'[\u4e00-\u9fff]',pdf[pg-1].get_text()))
 m=difflib.SequenceMatcher(None,s,t,autojunk=False).get_matching_blocks()
 cov=sum(x.size for x in m)/max(1,len(s))
 print(r['id'],pg,len(s),round(cov,3),''.join(s[x.a:x.a+x.size]+'|' for x in m if x.size>=4)[:130])
