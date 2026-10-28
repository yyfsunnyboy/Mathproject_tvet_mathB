"""Apply or roll back the authorized Unit 3 Stage 1 change set.

Default is read-only preflight. Production writes require --apply --production.
"""
import argparse, hashlib, json, os, shutil, sqlite3, sys
from datetime import datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from core.textbook_stage1_gate import evaluate_stage1_gate

CS=json.loads((HERE/'production_change_set.json').read_text(encoding='utf-8'))
SCOPE=CS['unit']
PROD=(ROOT/'instance/kumon_math.db').resolve()
SOURCE_ASSETS=HERE/'sandbox/assets'
COLS=('problem_text','detailed_solution','skill_id','notes')

def sha(data): return hashlib.sha256(data).hexdigest()
def rowdict(row): return dict(row) if row else None
def dg_rows(con,sql,args=()):
 h=hashlib.sha256()
 for row in con.execute(sql,args):
  h.update(json.dumps(tuple(row),ensure_ascii=False,default=str).encode('utf-8'))
  h.update(b'\n')
 return h.hexdigest()
def outside_digests(con):
 out={'textbook_outside':dg_rows(con,"select * from textbook_examples where not (source_curriculum=? and source_volume=? and source_chapter=?) order by id",tuple(SCOPE.values()))}
 for table, in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name"):
  if table=='textbook_examples': continue
  out[table]=dg_rows(con,f'select * from "{table}" order by rowid')
 return out
def preflight(con,uploads_root):
 problems=[]
 old_ids=[r['id'] for r in CS['old_rows']]
 updated_ids=[x['id'] for x in CS['updates']]
 if len(old_ids)!=20 or old_ids!=list(range(1362,1382)) or len(updated_ids)!=21: problems.append('change-set count/id mismatch')
 current=[rowdict(r) for r in con.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id',tuple(SCOPE.values()))]
 if len(current)!=50 or {r['id'] for r in current}!={*old_ids,*range(12744,12774)}: problems.append('unit row scope drift')
 for rec in CS['old_rows']:
  if rowdict(con.execute('select * from textbook_examples where id=?',(rec['id'],)).fetchone())!=rec: problems.append(f"old row {rec['id']} drift")
 for op in CS['updates']:
  if rowdict(con.execute('select * from textbook_examples where id=?',(op['id'],)).fetchone())!=op['before']: problems.append(f"new row {op['id']} drift")
 for table, in con.execute("select name from sqlite_master where type='table'"):
  cols=[x[1] for x in con.execute(f'pragma table_info("{table}")')]
  keys=[x for x in cols if x in ('textbook_example_id','example_id','source_example_id')]
  for key in keys:
   n=con.execute(f'select count(*) from "{table}" where "{key}" between 1362 and 1381').fetchone()[0]
   if n: problems.append(f'{table}.{key}: {n} old-row references')
 # Attempts use UUID question_uid values and source categories; decimal substrings
 # inside UUIDs are not textbook example references.
 if con.execute("select 1 from sqlite_master where type='table' and name='practice_attempts'").fetchone():
  sources={r[0] for r in con.execute('select distinct source from practice_attempts')}
  if not sources.issubset({'general_practice','chapter_review'}): problems.append(f'unknown practice_attempt source categories: {sources}')
  import uuid
  for uid, in con.execute('select question_uid from practice_attempts'):
   try: uuid.UUID(uid)
   except (ValueError,TypeError):
    if any(str(i) in str(uid) for i in old_ids): problems.append(f'non-UUID practice attempt may reference old row: {uid}')
 source_record=ROOT/'textbook_import/uploaded_sources/general/數學2/80fe968ed2d3c218baf44e9d9782c1cb32cf4a708f543fbff754e970647819f6.json'
 record=json.loads(source_record.read_text(encoding='utf-8'))
 for kind,hash_key in (('docx','docx_sha256'),('pdf','pdf_sha256')):
  src=record['sources'][kind]; f=ROOT/src['stored_path']
  if not f.is_file() or f.stat().st_size!=src['size_bytes'] or sha(f.read_bytes())!=src['sha256'] or src['sha256']!=CS[hash_key]: problems.append(f'{kind} source hash/path mismatch')
 for asset in CS['asset_files']:
  src=SOURCE_ASSETS/asset['path']; dst=uploads_root/asset['path']
  if not src.is_file() or sha(src.read_bytes())!=asset['sha256']: problems.append(f"source asset mismatch {asset['row_id']}")
  if dst.exists(): problems.append(f"destination asset already exists {asset['row_id']}")
 if con.execute('pragma quick_check').fetchone()[0]!='ok': problems.append('db quick_check failed')
 return problems
def verify_unit(con,uploads_root):
 rows=[rowdict(r) for r in con.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id',tuple(SCOPE.values()))]
 assert len(rows)==30 and [r['id'] for r in rows]==list(range(12744,12774))
 from collections import Counter
 skills=dict(Counter(r['skill_id'] for r in rows))
 assert skills=={'gh_LogicAndSets':9,'gh_CountingPrinciples':21},skills
 assert all('MATH_PARSE_FAILED' not in (r['problem_text'] or '')+(r['detailed_solution'] or '') for r in rows)
 anchors=[json.loads(r['notes'])['question_anchor'] for r in rows]
 assert len({a['anchor_id'] for a in anchors})==30 and sorted(a['source_order'] for a in anchors)==list(range(1,31))
 gate=evaluate_stage1_gate(rows)
 assert gate['status']=='READY' and not gate['blocked'] and not gate['needs_review'],gate
 for asset in CS['asset_files']:
  f=uploads_root/asset['path']
  assert f.is_file() and sha(f.read_bytes())==asset['sha256']
  n=json.loads(next(r['notes'] for r in rows if r['id']==asset['row_id']))
  assert len([a for a in n.get('image_assets',[]) if a['path']==asset['path'] and a['sha256']==asset['sha256'] and a.get('visual_status')=='accepted'])==1
 return {'rows':len(rows),'skills':skills,'gate':gate['status'],'blocked':len(gate['blocked']),'needs_review':len(gate['needs_review']),'math_parse_failed':0,'assets':len(CS['asset_files'])}
def restore(con,manifest,uploads_root):
 # Used only when current rows still match this exact applied change set.
 for rec in CS['old_rows']:
  assert con.execute('select 1 from textbook_examples where id=?',(rec['id'],)).fetchone() is None
 for op in CS['updates']:
  assert rowdict(con.execute('select * from textbook_examples where id=?',(op['id'],)).fetchone())==op['after']
 con.execute('begin immediate')
 try:
  for rec in CS['old_rows']:
   cols=list(rec)
   con.execute(f"insert into textbook_examples ({','.join(cols)}) values ({','.join('?' for _ in cols)})",[rec[k] for k in cols])
  for op in CS['updates']:
   cols=[k for k in COLS if op['before'][k]!=op['after'][k]]
   con.execute('update textbook_examples set '+','.join(f'{k}=?' for k in cols)+' where id=?',[*[op['before'][k] for k in cols],op['id']])
  con.execute('commit')
 except Exception:
  con.execute('rollback');raise
 for asset in CS['asset_files']:
  dst=uploads_root/asset['path']
  if dst.is_file() and sha(dst.read_bytes())==asset['sha256']: dst.unlink()
def apply(con,db,uploads_root,backup_dir):
 problems=preflight(con,uploads_root)
 assert not problems,problems
 before_out=outside_digests(con)
 stamp=datetime.now().strftime('%Y%m%d_%H%M%S_%f')
 backup_dir.mkdir(parents=True,exist_ok=True)
 backup=backup_dir/f'kumon_math_before_math2_unit3_stage1_{stamp}.db'
 b=sqlite3.connect(backup);con.backup(b);assert b.execute('pragma integrity_check').fetchone()[0]=='ok';b.close()
 manifest=backup_dir/f'apply_manifest_unit3_{stamp}.json'
 m={'unit':SCOPE,'backup':str(backup),'backup_sha256':sha(backup.read_bytes()),'created_assets':CS['asset_files'],'change_set_sha256':sha((HERE/'production_change_set.json').read_bytes()),'status':'backed_up'}
 manifest.write_text(json.dumps(m,ensure_ascii=False,indent=1),encoding='utf-8')
 pending=[]
 try:
  for asset in CS['asset_files']:
   dst=uploads_root/asset['path'];dst.parent.mkdir(parents=True,exist_ok=True)
   tmp=dst.with_name(dst.name+f'.pending_{stamp}')
   shutil.copy2(SOURCE_ASSETS/asset['path'],tmp)
   assert sha(tmp.read_bytes())==asset['sha256'];pending.append((tmp,dst))
  con.execute('begin immediate')
  try:
   for rec in CS['old_rows']:
    result=con.execute('delete from textbook_examples where id=? and source_curriculum=? and source_volume=? and source_chapter=?',(rec['id'],*SCOPE.values()))
    assert result.rowcount==1
   for op in CS['updates']:
    cols=[k for k in COLS if op['before'][k]!=op['after'][k]]
    result=con.execute('update textbook_examples set '+','.join(f'{k}=?' for k in cols)+' where id=? and source_curriculum=? and source_volume=? and source_chapter=?',(*[op['after'][k] for k in cols],op['id'],*SCOPE.values()))
    assert result.rowcount==1
   assert con.execute('select count(*) from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=?',tuple(SCOPE.values())).fetchone()[0]==30
   assert outside_digests(con)==before_out
   con.execute('commit')
  except Exception:
   con.execute('rollback');raise
  for tmp,dst in pending: os.replace(tmp,dst)
  result=verify_unit(con,uploads_root)
  assert outside_digests(con)==before_out,'out-of-scope DB drift'
  assert con.execute('pragma integrity_check').fetchone()[0]=='ok'
  m.update(status='applied_verified',verification=result,outside_digests=before_out)
  manifest.write_text(json.dumps(m,ensure_ascii=False,indent=1),encoding='utf-8')
  return manifest,result
 except Exception:
  for tmp,dst in pending:
   if tmp.exists(): tmp.unlink()
  if con.execute('select count(*) from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=?',tuple(SCOPE.values())).fetchone()[0]==30:
   restore(con,m,uploads_root)
  m['status']='rolled_back_after_failure';manifest.write_text(json.dumps(m,ensure_ascii=False,indent=1),encoding='utf-8')
  raise
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--db',default=str(PROD));ap.add_argument('--uploads-root',default=str(ROOT));ap.add_argument('--backup-dir');ap.add_argument('--apply',action='store_true');ap.add_argument('--production',action='store_true');ap.add_argument('--rollback');a=ap.parse_args()
 db=Path(a.db).resolve();root=Path(a.uploads_root).resolve();prod=(db==PROD or root==ROOT)
 if prod and (a.apply or a.rollback) and not a.production: sys.exit('REFUSED: production write requires --production')
 if not prod and a.production: sys.exit('REFUSED: production flag with test paths')
 con=sqlite3.connect(db,isolation_level=None);con.row_factory=sqlite3.Row
 try:
  if a.rollback:
   m=json.loads(Path(a.rollback).read_text(encoding='utf-8'))
   assert m['unit']==SCOPE and m['status']=='applied_verified'
   restore(con,m,root);print('ROLLBACK PASS');return
  if not a.apply:
   problems=preflight(con,root);print('PREFLIGHT', 'PASS' if not problems else 'FAIL',problems);return
  manifest,result=apply(con,db,root,Path(a.backup_dir or (ROOT/'instance/backups')))
  print('APPLY PASS',json.dumps(result,ensure_ascii=False),'MANIFEST',manifest)
 finally: con.close()
if __name__=='__main__': main()
