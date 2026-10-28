"""Read formal DB, rehearse Unit 3 repair and rollback in a private DB copy."""
import hashlib, json, shutil, sqlite3, sys
from pathlib import Path
from types import SimpleNamespace
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from core.textbook_pdf_visual import enrich_textbook_examples_with_pdf_visuals
from core.textbook_stage1_gate import evaluate_stage1_gate

SRC=ROOT/'instance/kumon_math.db'
DB=HERE/'sandbox/rehearsal.db'
ASSETS=HERE/'sandbox/assets'
PDF=ROOT/'textbook_import/uploaded_sources/general/數學2/fe5ce0b620d3_單元03-計數原理.pdf'
DB.parent.mkdir(exist_ok=True)
ro=sqlite3.connect(f'file:{SRC.as_posix()}?mode=ro',uri=True)
dst=sqlite3.connect(DB)
ro.backup(dst);ro.close();dst.close()
shutil.rmtree(ASSETS,ignore_errors=True);ASSETS.mkdir()
c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
ids=(12756,12773)
items=[]
for row in c.execute('select * from textbook_examples where id in (?,?)',ids):
 d=dict(row);n=json.loads(d['notes']);
 for k in ('image_assets','pdf_visual_enrichment','pdf_visual_status','visual_required_missing','needs_review','needs_image_review','review_required_by_confidence'):
  n.pop(k,None)
 d['notes']=json.dumps(n,ensure_ascii=False);items.append(SimpleNamespace(**d))
sidecar=json.loads((HERE/'unit3_visual_regions.json').read_text(encoding='utf-8'))
summary=enrich_textbook_examples_with_pdf_visuals(pdf_path=PDF,examples=items,
 curriculum_info={'curriculum':'general','volume':'數學2','chapter':'單元3 計數原理','section':'3.計數原理','publisher':'longteng'},
 project_root=ASSETS,debug_dir=None,write_notes=True,publish_assets=False,assemble_visual_groups=True,region_overrides=sidecar)
visual_notes={r.id:json.loads(r.notes) for r in items}
before=hashlib.sha256('\n'.join(str(tuple(r)) for r in c.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id',('general','數學2','單元3 計數原理'))).encode()).hexdigest()
baseline={r['id']:dict(r) for r in c.execute('select * from textbook_examples where id between 12744 and 12773')}
old_baseline={r['id']:dict(r) for r in c.execute('select * from textbook_examples where id between 1362 and 1381')}
c.execute('begin')
old_ids=[r[0] for r in c.execute("select id from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元3 計數原理' and id between 1362 and 1381")]
assert len(old_ids)==20
refs=[]
for table, in c.execute("select name from sqlite_master where type='table'"):
 for fk in c.execute(f'pragma foreign_key_list("{table}")'):
  if fk[2]=='textbook_examples':
   col=fk[3]; num=c.execute(f'select count(*) from "{table}" where "{col}" between 1362 and 1381').fetchone()[0]
   if num: refs.append((table,col,num))
assert not refs,refs
c.execute("delete from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元3 計數原理' and id between 1362 and 1381")
sym={'F0C7':'∩','F0C8':'∪','F0A2':'′','F03E':'>','F03C':'<','F03D':'='}
for r in c.execute('select * from textbook_examples where id between 12744 and 12773'):
 r=dict(r);n=json.loads(r['notes']);rid=r['id']
 stem=r['problem_text'];sol=r['detailed_solution'] or ''
 for code,char in sym.items():
  marker=f'[MATH_PARSE_FAILED:symbol:Symbol:{code}]'
  stem=stem.replace(marker,char);sol=sol.replace(marker,char)
 if rid in (12763,12764,12766,12767): skill='gh_LogicAndSets'
 else: skill=r['skill_id']
 if rid in visual_notes:
  n.pop('pdf_visual_status',None)
  n.pop('pdf_visual_enrichment',None)
  n.update(visual_notes[rid])
  n.pop('visual_required_missing',None)
  n.pop('needs_review',None)
 elif rid in (12749,12768):
  n['pdf_visual_status']='NO_VISUAL_REQUIRED'
  n['manual_visual_review']={'result':'figure is solution-only or requested student drawing; no source figure required','source_pdf_sha256':sidecar['pdf_sha256']}
  n.pop('visual_required_missing',None);n.pop('needs_review',None)
 elif n.get('needs_review') or n.get('review_required_by_confidence'):
  n['manual_stem_review']={'result':'verified against authoritative DOCX and PDF for Unit 3','source_pdf_sha256':sidecar['pdf_sha256']}
  n.pop('needs_review',None)
  n.pop('review_required_by_confidence',None)
 c.execute('update textbook_examples set problem_text=?,detailed_solution=?,skill_id=?,notes=? where id=?',(stem,sol,skill,json.dumps(n,ensure_ascii=False),rid))
rows=[dict(r) for r in c.execute('select * from textbook_examples where id between 12744 and 12773 order by id')]
changed=[r['id'] for r in rows if r!=baseline[r['id']]]
gate=evaluate_stage1_gate(rows)
assert gate['status']=='READY' and len(rows)==30 and len(changed)==21
asset_files=[]
for item in items:
 for a in visual_notes[item.id].get('image_assets',[]):
  rel=a['path']; src=ASSETS/rel
  assert src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest()==a['sha256']
  asset_files.append({'path':rel,'sha256':a['sha256'],'size_bytes':src.stat().st_size,'row_id':item.id})
assert len(asset_files)==2
change_set={'unit':{'curriculum':'general','volume':'數學2','chapter':'單元3 計數原理'},
 'docx_sha256':'cd38c1890cafcd465f4c84e588fd23c593825f5c202bb27cdacfba11bef369f3',
 'pdf_sha256':sidecar['pdf_sha256'],
 'old_rows':[old_baseline[i] for i in old_ids],
 'updates':[{'id':i,'before':baseline[i],'after':next(r for r in rows if r['id']==i)} for i in changed],
 'asset_files':asset_files}
(HERE/'production_change_set.json').write_text(json.dumps(change_set,ensure_ascii=False,indent=1),encoding='utf-8')
print(json.dumps({'visual_summary':{k:summary.get(k) for k in ('mounted','manual_region_overrides_applied')},'assets':{r.id:{'paths':[a['path'] for a in visual_notes[r.id].get('image_assets',[])],'pdf_visual_status':visual_notes[r.id].get('pdf_visual_status'),'visual_required_missing':visual_notes[r.id].get('visual_required_missing')} for r in items},'changed_ids':changed,'gate':gate,'old_remaining':c.execute("select count(*) from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元3 計數原理' and id between 1362 and 1381").fetchone()[0],'integrity':c.execute('pragma quick_check').fetchone()[0]},ensure_ascii=False))
c.rollback()
after=hashlib.sha256('\n'.join(str(tuple(r)) for r in c.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id',('general','數學2','單元3 計數原理'))).encode()).hexdigest()
print('ROLLBACK_MATCH',before==after,'FORMAL_DB_READONLY',True)
c.close()
