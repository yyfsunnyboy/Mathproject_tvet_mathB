import json, sqlite3, sys, re
sys.stdout.reconfigure(encoding='utf-8')
c=sqlite3.connect('file:instance/kumon_math.db?mode=ro',uri=True);c.row_factory=sqlite3.Row
rows=[dict(r) for r in c.execute("select * from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元3 計數原理' order by id")]
old=[r for r in rows if r['id']<12744];new=[r for r in rows if r['id']>=12744]
print('OLD',len(old),[r['id'] for r in old])
for r in new:
 n=json.loads(r['notes'] or '{}')
 print(r['id'],r['source_description'].split(' [')[0],r['skill_id'],'order',n.get('question_anchor',{}).get('source_order'),'needs',n.get('needs_review'),'solution_fail',r['detailed_solution'].count('MATH_PARSE_FAILED') if r['detailed_solution'] else 0,'stem_fail',r['problem_text'].count('MATH_PARSE_FAILED'),'visual',n.get('pdf_visual_status'),'note_keys',','.join(k for k in n if 'eq' in k.lower()))
for t in c.execute("select name from sqlite_master where type='table'"):
 name=t[0]; cols=[x[1] for x in c.execute('pragma table_info('+name+')')]
 keys=[k for k in cols if 'example' in k.lower() or 'textbook' in k.lower()]
 if keys:
  for key in keys:
   if key=='id' or name=='textbook_examples': continue
   try:
    q='select count(*) from "'+name+'" where "'+key+'" between 1362 and 1381'
    n=c.execute(q).fetchone()[0]
    if n: print('OLD_REF',name,key,n)
   except Exception as e: print('ERR',name,key,str(e))
for r in new:
 for field in ('problem_text','detailed_solution'):
  tokens=re.findall(r'\[MATH_PARSE_FAILED:[^]]+\]',r[field] or '')
  if tokens: print('FAIL_TOKENS',r['id'],field,tokens)
for table, in c.execute("select name from sqlite_master where type='table'"):
 if any(k in table.lower() for k in ('student','answer','record','tracker','question','practice','asset','gencode')):
  cols=[x[1] for x in c.execute(f'pragma table_info("{table}")')]
  print('TABLE',table,','.join(x for x in cols if any(k in x.lower() for k in ('example','question','skill','source','record'))))
for rid in (1362,1366,1374,1375,1377,1379,1380):
 for r in c.execute('select id,question_uid,source,question_text from practice_attempts where question_uid like ?',(f'%{rid}%',)):
  print('ATTEMPT_REF',rid,*r[:3],str(r[3])[:90])
for r in c.execute('select source,count(*),min(question_uid),max(question_uid) from practice_attempts group by source'):
 print('ATTEMPT_SOURCE',*r)
