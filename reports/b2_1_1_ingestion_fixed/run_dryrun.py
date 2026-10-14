from pathlib import Path
import sys, sqlite3, json, hashlib, queue, copy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from flask import Flask
from config import Config
from models import db
import core.textbook_importer_v3_pipeline as pipeline
import core.textbook_processor_v2 as tp
from core.textbook_importer_v3_orchestrate import find_b2_11_source_pair
from core.textbook_importer_v3_phase3_dryrun import build_dryrun_questions
OUT=ROOT/'reports/b2_1_1_ingestion_fixed'
def save(name,data):
 (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
prod=Path(Config.db_path)
before=hashlib.sha256(prod.read_bytes()).hexdigest()
app=Flask('b2_11_isolated_dryrun',root_path=str(ROOT))
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'
db.init_app(app)
with app.app_context():
 raw=db.engine.raw_connection()
 with sqlite3.connect(prod.as_uri()+'?mode=ro',uri=True) as ro:
  ro.backup(raw.driver_connection)
 raw.close()
 before_skills={r[0] for r in db.session.execute(__import__('sqlalchemy').text('select skill_id from skills_info'))}
 before_examples=db.session.execute(__import__('sqlalchemy').text('select count(*) from textbook_examples')).scalar()
pair=find_b2_11_source_pair(ROOT)
captured={}
original_attach=pipeline._attach_anchor_notes_to_phase3
def capture(parsed,meta,info):
 result=original_attach(parsed,meta,info)
 captured.update(parsed=copy.deepcopy(parsed),meta=copy.deepcopy(meta),info=copy.deepcopy(info))
 save('phase3_capture.json',captured)
 return result
original_build=pipeline.build_curriculum_info_for_v3_import
def build(**kwargs):
 return original_build(**kwargs,apply_policy=False)
# No application startup, no production engine, no Phase4, fresh conversion in audit dir.
with patch.object(pipeline,'_latex_output_path',lambda p: OUT/(p.stem+'_Latex.docx')), patch.object(pipeline,'_attach_anchor_notes_to_phase3',capture), patch.object(pipeline,'build_curriculum_info_for_v3_import',build):
 report=pipeline.run_v3_pair_pipeline(project_root=ROOT,docx_path=pair.original_docx,pdf_path=pair.pdf,curriculum='vocational',volume='數學B2',allow_phase4=False,app=app)
save('pipeline_report.json',report)
print('PIPELINE',report.get('ok'),report.get('error'),flush=True)
if captured:
 joined=build_dryrun_questions(captured['meta'],captured['parsed'],captured['info'])
 with app.app_context():
  for q in joined['questions']:
   q['problem_text']=tp._sanitize_db_latex_delimiters(tp.clean_problem_leading_title(q['problem_text']))
   q['detailed_solution']=tp._sanitize_db_latex_delimiters(q['detailed_solution'])
   q['source_description']=q['anchor']
   resolved=tp._phase4_resolve_mathb_formal_binding(block_meta=captured['meta'][q['anchor']],source_type=q['source_type'],db_problem_text=q['problem_text'],curriculum_info=captured['info'],item_sec_code=q['section_code'],coords=tp._import_scope_coords(captured['info']),source_description=q['anchor'])
   q['resolved_skill_id']=resolved[1] if resolved else None
  db.session.rollback()
 save('questions.json',joined)
 import fitz
 from core.textbook_b2_11 import correct_pdf_regions
 from core.textbook_pdf_visual import build_page_index,match_questions_to_pdf,assign_question_regions,classify_and_detect_visuals
 with fitz.open(pair.pdf) as pdf:
  pages=build_page_index(pdf)
 items=[dict(q,id=i+1,problem_type=q['source_type']) for i,q in enumerate(joined['questions'])]
 visuals=classify_and_detect_visuals(assign_question_regions(match_questions_to_pdf(items,pages),pages),pages)
 visuals=correct_pdf_regions(visuals,pages,pair.pdf,captured['info'])
 save('visuals.json',visuals)
 save('pdf_pages.json',pages)
 print('QUESTIONS',joined['stats'],flush=True)
with app.app_context():
 assert before_skills=={r[0] for r in db.session.execute(__import__('sqlalchemy').text('select skill_id from skills_info'))}
 assert before_examples==db.session.execute(__import__('sqlalchemy').text('select count(*) from textbook_examples')).scalar()
after=hashlib.sha256(prod.read_bytes()).hexdigest()
save('safety.json',dict(production_sha256_before=before,production_sha256_after=after,unchanged=before==after,phase4_executed=False,database='in-memory snapshot',pdf=str(pair.pdf)))
assert before==after
