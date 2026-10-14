from pathlib import Path
import json,sys
ROOT=Path.cwd(); sys.path.insert(0,str(ROOT))
OUT=ROOT/'reports/b2_1_1_ingestion_dryrun'
from core.textbook_importer_v3_orchestrate import find_b2_11_source_pair
from core.textbook_pdf_visual import build_page_index,match_questions_to_pdf,assign_question_regions,classify_and_detect_visuals
import fitz
meta=json.loads((OUT/'phase2_meta.json').read_text(encoding='utf-8'))
pair=find_b2_11_source_pair(ROOT)
items=[dict(m,id=i+1,source_order=i+1,source_description=k,problem_type=m['source_type']) for i,(k,m) in enumerate(meta.items())]
with fitz.open(pair.pdf) as pdf:
 pages=build_page_index(pdf)
 print('PDF',pair.pdf,'pages',len(pages))
 for i,p in enumerate(pdf):
  p.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(str(OUT/f'page_{i+1}.png'))
  print('PAGE',i+1,p.get_text()[:130])
visuals=classify_and_detect_visuals(assign_question_regions(match_questions_to_pdf(items,pages),pages),pages)
(OUT/'phase2_visuals.json').write_text(json.dumps(visuals,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'pdf_pages.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
print('VISUALS')
for r in visuals:
 print(r['source_description'],{k:r.get(k) for k in ['pdf_match','match_score','visual_classification','should_mount','visual_reason','visual_page','visual_bbox']})
