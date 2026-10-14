from pathlib import Path
import json,sys,re,sqlite3,hashlib,zipfile
from lxml import etree
ROOT=Path.cwd();sys.path.insert(0,str(ROOT))
from config import Config
from core.textbook_processor_v2 import _sanitize_db_latex_delimiters,clean_problem_leading_title
from core.textbook_mathtype_converter import extract_equation_native,wrap_latex_for_v2
from core.mtef import equation_native_to_latex
from core.textbook_importer_v3_orchestrate import find_b2_11_source_pair
OUT=ROOT/'reports/b2_1_1_ingestion_dryrun'
def read(n):return json.loads((OUT/n).read_text(encoding='utf-8'))
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
meta=read('phase2_meta.json');vs=read('phase2_visuals.json');lines=read('phase1_lines.json')
pair=find_b2_11_source_pair(ROOT)
prod=Path(Config.db_path)
with sqlite3.connect(prod.as_uri()+'?mode=ro',uri=True) as con:
 con.row_factory=sqlite3.Row
 skills=[dict(r) for r in con.execute('SELECT skill_id,chapter,section,paragraph FROM skill_curriculum WHERE curriculum=? AND volume=? AND section=?',('vocational','數學B2','1-1 角度的基本性質'))]
 refs=[dict(r) for r in con.execute('SELECT id,source_description,skill_id,notes FROM textbook_examples WHERE source_curriculum=? AND source_volume=? AND source_section=?',('vocational','數學B2','1-1 角度的基本性質'))]
checks=[];questions=[]
for (label,m),v in zip(meta.items(),vs):
 q=dict(m)
 q['source_description']=label
 q['problem_text']=_sanitize_db_latex_delimiters(clean_problem_leading_title(m['problem_text']))
 q['detailed_solution']=_sanitize_db_latex_delimiters(m['detailed_solution'])
 q['skill_mapping_state']='verified_existing_heading_skill' if m['formal_skill_id'] and any(s['skill_id']==m['formal_skill_id'] for s in skills) else 'unresolved_requires_phase3_or_phase4_AI'
 q['visual_reference']=v
 q['existing_visual_notes']=[r for r in refs if r['source_description'].replace(' ','')==label.replace(' ','')]
 questions.append(q)
 assert 'MATH_PARSE_FAILED' not in q['problem_text']+q['detailed_solution']
 assert re.findall(r'\([1-9]\)',q['problem_text'])==re.findall(r'\([1-9]\)',m['problem_text'])
for label,indices,subitems in [('例1',[32],[1,2]),('隨堂練習1',[37,38],[1,2]),('1-1習題 基礎題 2',[129,130],[1,2]),('1-1習題 基礎題 3',[131,132,133,134],[1,2,3])]:
 q=next(q for q in questions if q['source_description']==label)
 fchecks=[]
 with zipfile.ZipFile(pair.original_docx) as z:
  for index in indices:
   native,_=extract_equation_native(z.read(f'word/embeddings/oleObject{index}.bin'))
   latex,info=equation_native_to_latex(native)
   wrapped=_sanitize_db_latex_delimiters(wrap_latex_for_v2(latex))
   assert wrapped in q['problem_text'],(label,index,wrapped)
   fchecks.append(dict(formula_index=index,latex=wrapped,present=True))
 assert re.findall(r'\(([1-9])\)',q['problem_text'])==[str(i) for i in subitems]
 checks.append(dict(label=label,formulas=fchecks,subitem_order=subitems,problem_text=q['problem_text'],pdf_page={'例1':5,'隨堂練習1':6}.get(label,13),result='PASS at Phase2/prewrite text normalization; final Phase3 not available'))
expected=['例1','隨堂練習1','例2','隨堂練習2','例3','隨堂練習3','例4','隨堂練習4','108統測B']+[f'1-1習題 基礎題 {i}' for i in range(1,9)]+[f'1-1習題 進階題 {i}' for i in (9,10)]
assert list(meta)==expected
low=[v['source_description'] for v in vs if v.get('visual_classification')=='skipped_low_confidence']
issues={
 'segmentation':[{'label':'SDG 14 保育海洋生態—扇形計算','evidence':'DOCX Phase1 has the salt-worker problem, (2), and solution; PDF page 8 has (1)/(2). No Phase2 anchor captures this problem group. Existing scope exclusion may be intentional; not changed.','pdf_page':8}],
 'ordering':[{'label':'1-1習題 基礎題 1','evidence':'DOCX/PDF table contains 11 degree columns and blank answer cells. Phase1/2 emits all degrees then only four nonempty radian cells, losing blank-cell positions and column correspondence. Question and subquestion order otherwise matches source.','pdf_page':13}],
 'visual':[{'label':name,'evidence':'Existing matcher reports unmatched or match_score=0.88, below mount threshold; no automatic image reference. This is a reference warning, not necessarily a missing required diagram.'} for name in low]+[
 {'label':'例2','evidence':'Existing crop includes the following 隨堂練習2 problem, outside the example.','artifact':'crop_3.png','pdf_page':7},
 {'label':'1-1習題 基礎題 1','evidence':'Table classified text_and_formula_only; no visual fallback preserves missing blank-cell/column correspondence.','pdf_page':13},
 {'label':'1-1習題 基礎題 5','evidence':'Crop retains clock photo but cuts off most of the pendulum sector diagram.','artifact':'crop_14.png','pdf_page':13},
 {'label':'1-1習題 進階題 10','evidence':'Crop includes unrelated 熟習度自評表 below bridge photo and sector diagram.','artifact':'crop_19.png','pdf_page':14}],
 'pipeline_blocker':read('pipeline_report.json')['error'],
 'phase3_blocker':'External AI call did not return; stopped. Endpoint connectivity probe returned ConnectionError, environment credential does not have expected key shape. No fabricated/cached AI metadata used.',
 'mapping':{'heading_skills_verified':sum(q['skill_mapping_state']=='verified_existing_heading_skill' for q in questions),'unresolved':sum(q['skill_mapping_state']!='verified_existing_heading_skill' for q in questions)},
 'solutions':{'source_solution_present':sum(bool(q['detailed_solution']) for q in questions),'source_solution_absent':sum(not q['detailed_solution'] for q in questions),'note':'Four examples contain source solutions; exam item contains KEY hints. Other 14 source blocks have no solution; Phase3 fallback unverified.'}
}
save('questions_review.json',questions);save('known_broken_checks.json',checks);save('evidence.json',issues)
safety=read('safety.json');safety['production_sha256_after']=hashlib.sha256(prod.read_bytes()).hexdigest();safety['unchanged']=safety['production_sha256_before']==safety['production_sha256_after'];assert safety['unchanged'];save('safety.json',safety)
print({'phase2_examples_total':len(questions),'math_parse_failed':0,'segmentation_issues':len(issues['segmentation']),'ordering_issues':len(issues['ordering']),'visual_issues':len(issues['visual']),'known_broken_checks':'4 passed','mapping':issues['mapping'],'production_unchanged':safety['unchanged']})
