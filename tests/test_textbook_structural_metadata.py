import hashlib
import json
import sqlite3
from pathlib import Path

import pytest
from flask import Flask

from core.textbook_structural_metadata import canonical_heading_identity, align_structural_metadata


def test_identity_is_stable_and_scoped():
    info = dict(curriculum='vocational', volume='數學B2')
    first = canonical_heading_identity(info, '2-4.1', '測試概念')
    assert first == canonical_heading_identity(info, '2-4.1', ' 測試概念 ')
    variants = [canonical_heading_identity(info, '2-4.2', '測試概念'),
                canonical_heading_identity(dict(info, volume='數學B3'), '2-4.1', '測試概念')]
    assert len({first[0], *(v[0] for v in variants)}) == 3
    assert first == ('vh_數學B2_SubSection_2_4_1', 'SubSection_2_4_1')
    assert first == canonical_heading_identity(info, '2-4.1', '不同概念')
    with pytest.raises(ValueError, match='namespace'):
        canonical_heading_identity(dict(info, curriculum='other'), '2-4.1', '測試概念')


def test_alignment_preserves_order_and_uses_outline_fallback():
    from models import db, SkillCurriculum, SkillInfo
    app = Flask('outline_fallback_test')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.add(SkillInfo(skill_id='outline_test', skill_en_name='OutlineTest',
                                 skill_ch_name='測試', description='測試', gemini_prompt=''))
        db.session.add(SkillInfo(skill_id='vh_test', skill_en_name='TestConcept',
                                 skill_ch_name='概念', description='概念', gemini_prompt=''))
        db.session.add(SkillCurriculum(skill_id='outline_test', curriculum='vocational',
                                      grade=10, volume='數學B2', chapter='第2章',
                                      section='2-4 測試'))
        db.session.add(SkillCurriculum(skill_id='vh_test', curriculum='vocational', grade=10,
                                      volume='數學B2', chapter='第2章', section='2-4 測試',
                                      paragraph='概念'))
        db.session.flush()
        _assert_alignment_outline_fallback()
        from core.textbook_processor_v2 import _phase4_resolve_mathb_formal_binding
        bound = _phase4_resolve_mathb_formal_binding(
            block_meta={'concept_code': '2-4.1', 'concept_name': '概念'},
            source_type='textbook_example', db_problem_text='測試題目文字',
            curriculum_info={'curriculum': 'vocational', 'volume': '數學B2',
                             'chapter': '第2章', 'section': '2-4 測試',
                             'section_code': '2-4'},
            item_sec_code='2-4', coords={'volume': '數學B2'},
            requested_skill_id='vh_test', mapping_status='structurally_bound')
        assert bound and bound[1] == 'vh_test'


def _assert_alignment_outline_fallback():
    info = dict(chapter='第2章', section='2-4 測試', section_code='2-4',
                curriculum='vocational', volume='數學B2',
                structural_skill_candidates=[dict(concept_code='2-4.1', concept_name='概念')])
    blocks = {'例2': dict(concept_code='2-4.1', concept_name='概念', formal_skill_id='vh_test',
                          source_type='textbook_example', detailed_solution='來源詳解'),
              '習題1': dict(source_type='exercise')}
    out = align_structural_metadata(list(reversed(blocks)), blocks, info)
    concepts = out['chapters'][0]['sections'][0]['concepts']
    assert concepts[0]['examples'][0]['title'] == '例2'
    assert concepts[0]['examples'][0]['detailed_solution'] == '來源詳解'
    assert concepts[0]['examples'][0]['correct_answer'] == ''
    assert out['unresolved_skill_bindings'] == []
    assert out['needs_skill_resolution'] == ['習題1']
    assert out['section_outline_fallback_count'] == 1
    exercise = concepts[1]['practice_questions'][0]
    assert exercise['skill_id'] == 'outline_test'
    assert exercise['mapping_status'] == 'section_outline_fallback'
    assert exercise['needs_skill_resolution'] is True
    with pytest.raises(ValueError):
        align_structural_metadata(['例2'], blocks, info)


@pytest.mark.parametrize('api_key', ['invalid', None])
def test_real_section_pipeline_without_gemini(tmp_path, monkeypatch, api_key):
    import shutil
    from models import db, SkillCurriculum
    from core import textbook_importer_v3_pipeline as pipeline
    from core import textbook_processor_v2 as tp
    from core import ai_analyzer
    root = Path(__file__).resolve().parents[1]
    source = next((root/'textbook_import/source/vocational/math_B2').glob('*1-3*課本.docx'))
    prod = root/'instance/kumon_math.db'
    before = hashlib.sha256(prod.read_bytes()).hexdigest()
    shutil.copy2(source, tmp_path/source.name)
    monkeypatch.delenv('GOOGLE_API_KEY', raising=False)
    if api_key is None:
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    else:
        monkeypatch.setenv('GEMINI_API_KEY', api_key)
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(args)
        raise AssertionError('Unexpected Gemini dependency')
    monkeypatch.setattr(tp, 'get_model', forbidden)
    monkeypatch.setattr(ai_analyzer, 'get_model', forbidden)
    app = Flask('structural_test')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    with app.app_context():
        raw = db.engine.raw_connection()
        with sqlite3.connect(prod.as_uri()+'?mode=ro', uri=True) as ro:
            ro.backup(raw.driver_connection)
        raw.close()
        from sqlalchemy import text
        protected = {table: set(tuple(r) for r in db.session.execute(text(f'SELECT * FROM {table}')))
                     for table in ('skills_info', 'skill_curriculum', 'textbook_examples')}
        runs = []
        for _ in range(2):
            report = pipeline.run_v3_pair_pipeline(
                project_root=tmp_path, docx_path=tmp_path/source.name, pdf_path=None,
                curriculum='vocational', volume='數學B2', allow_phase4=False, app=app)
            assert report['ok'], report.get('error')
            assert report['metrics']['db_write']['skipped']
            assert report['metrics']['skill_extraction']['curriculum_binding'] == 'PASS'
            assert report['metrics']['ai_alignment']['phase3_questions'] == 29
            assert report['metrics']['ai_alignment']['metadata_alignment'] == 'PASS'
            assert report['metrics']['ai_alignment']['unresolved_skill_bindings'] == []
            assert len(report['metrics']['ai_alignment']['needs_skill_resolution']) == 10
            assert report['metrics']['ai_alignment']['section_outline_fallback_count'] == 10
            lines = tp.phase1_extract_docx_lines(str(tmp_path/(source.stem+'_Latex.docx')))
            assert any('−135°' in line for line in lines)
            assert any('−420°' in line for line in lines)
            assert 'MATH_PARSE_FAILED' not in json.dumps(tp._DOCX_BLOCK_META, ensure_ascii=False)
            assert '−135°' in json.dumps(tp._DOCX_BLOCK_META, ensure_ascii=False)
            assert '−420°' in json.dumps(tp._DOCX_BLOCK_META, ensure_ascii=False)
            rows = SkillCurriculum.query.filter_by(curriculum='vocational', volume='數學B2',
                                                  section='1-3 任意角的三角函數').all()
            ids = [(r.paragraph, r.skill_id) for r in rows if r.skill_id.startswith('vh_')]
            assert len(ids) == 7
            assert all(sid.startswith('vh_數學B2_SubSection_1_3_') for _, sid in ids)
            runs.append(ids)
        assert runs[0] == runs[1]
        assert calls == []
        for table, previous in protected.items():
            after = set(tuple(r) for r in db.session.execute(text(f'SELECT * FROM {table}')))
            assert previous <= after, f'Existing {table} records changed'
        from core.textbook_structural_metadata import resolve_heading_identity
        info = report['metrics']['skill_extraction']['curriculum_info']
        candidate = info['structural_skill_candidates'][0]
        duplicate = dict(candidate, concept_code='1-3.99')
        bad = dict(info, structural_skill_candidates=info['structural_skill_candidates'] + [duplicate])
        with pytest.raises(ValueError, match='Different heading codes'):
            resolve_heading_identity(bad, candidate['concept_code'], candidate['concept_name'])
        (tmp_path/'verification.json').write_text(json.dumps(dict(skills=runs[0], report=report),
                                                           ensure_ascii=False, indent=2), encoding='utf-8')
    assert hashlib.sha256(prod.read_bytes()).hexdigest() == before
