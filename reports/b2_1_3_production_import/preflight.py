import sys, json, sqlite3, hashlib, os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')
if '--offline' in sys.argv:
    # Isolated parsing only; exercise the importer's built-in ID fallback in memory.
    os.environ.pop('GEMINI_API_KEY', None)
    os.environ.pop('GOOGLE_API_KEY', None)
from flask import Flask
from config import Config
from models import db
from core import textbook_processor_v2 as tp
from core import textbook_importer_v3_pipeline as pipeline
from core.textbook_question_anchor import build_anchors_from_block_meta

OUT = Path(__file__).resolve().parent
SOURCE = next((ROOT/'textbook_import/source/vocational/math_B2').glob('*1-3*課本.docx'))
LATEX = OUT / (SOURCE.stem+'_Latex.docx')
PROD = ROOT/'instance/kumon_math.db'
app = Flask('preflight',root_path=str(ROOT))
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'
db.init_app(app)
with app.app_context():
    raw=db.engine.raw_connection()
    with sqlite3.connect(PROD.as_uri()+'?mode=ro',uri=True) as ro:
        ro.backup(raw.driver_connection)
    raw.close()
    info=pipeline.build_curriculum_info_for_v3_import(latex_docx_path=LATEX,original_docx_filename=SOURCE.name)
    lines=tp.phase1_extract_docx_lines(str(LATEX),curriculum_info=info)
    info=tp._resolve_import_source_metadata(parse_filename=SOURCE.name,lines=lines,curriculum_info=info)['curriculum_info']
    audit=pipeline.audit_v3_skill_extraction(SOURCE,info,lines)
    assert audit['curriculum_binding']=='PASS'
    info=audit['curriculum_info']
    blocks=tp.phase2_deterministic_block_slice(lines,source_scope='section_textbook',curriculum_info=info)
    meta=dict(tp._DOCX_BLOCK_META)
    anchors=build_anchors_from_block_meta(meta,info)
    result=dict(audit=audit,info=info,meta=meta,anchors=anchors,blocks=blocks)
    (OUT/'preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    failures=[k for k,v in meta.items() if 'MATH_PARSE_FAILED' in str(v)]
    print('PREFLIGHT',len(blocks),'failures',failures,flush=True)
    assert not failures
    db.session.rollback()
