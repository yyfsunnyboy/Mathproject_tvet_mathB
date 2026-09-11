"""Deterministic metadata for imports backed by audited DOCX headings.

No model calls and no writes. Existing curriculum identities take precedence;
New vocational identities use volume and structural heading coordinates;
heading names remain authoritative binding evidence, not hash ID material.
"""
from __future__ import annotations

import re
import unicodedata
import json


def normalize_identity(value):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', str(value or ''))).strip()


def canonical_heading_identity(info, code, name):
    from core.textbook_formal_concept import build_formal_skill_id_from_en_id
    from core.textbook_processor_v2 import _fallback_en_id_from_concept_code

    values = [normalize_identity(info.get(k)) for k in ('curriculum', 'volume')]
    values += [normalize_identity(code), normalize_identity(name)]
    if not all(values) or not re.fullmatch(r'\d+-\d+\.\d+', values[2]):
        raise ValueError('Incomplete structural heading identity')
    # Use the existing formal DOCX coordinate naming contract, not a hash alias.
    # Name changes at the same coordinate are conflicts, not new identities.
    if values[0] != 'vocational' or not re.fullmatch(r'數學B\d+', values[1]):
        raise ValueError('Unsupported vocational heading namespace')
    en_id = _fallback_en_id_from_concept_code(values[2])
    return build_formal_skill_id_from_en_id(volume=values[1], concept_en_id=en_id), en_id


def resolve_heading_identity(info, code, name):
    from models import SkillCurriculum, SkillInfo, db

    candidates = info.get('structural_skill_candidates') or []
    evidence = [h for h in candidates if h['concept_code'] == code
                and normalize_identity(h['concept_name']) == normalize_identity(name)]
    if len(evidence) != 1:
        raise ValueError('Heading identity lacks unique DOCX evidence')
    if len({h['concept_code'] for h in candidates
            if normalize_identity(h['concept_name']) == normalize_identity(name)}) != 1:
        raise ValueError('Different heading codes share a display name; explicit reconciliation required')
    rows = SkillCurriculum.query.filter_by(
        curriculum=info['curriculum'], volume=info['volume'], section=info['section']).all()
    matches = {r.skill_id for r in rows if r.skill_id.startswith('vh_')
               and normalize_identity(r.paragraph) == normalize_identity(name)}
    if len(matches) > 1:
        raise ValueError('Ambiguous existing heading identities')
    if matches:
        sid = next(iter(matches))
        skill = db.session.get(SkillInfo, sid)
        if skill is None:
            raise ValueError('Existing curriculum skill record is missing')
        en_id = skill.skill_en_name
    else:
        sid, en_id = canonical_heading_identity(info, code, name)
        if db.session.get(SkillInfo, sid) is not None:
            raise ValueError('Canonical heading ID already exists outside this binding')
    return dict(concept_name=name, concept_en_id=en_id, formal_skill_id=sid,
                source='existing_registry' if matches else 'deterministic_docx_heading')


def align_structural_metadata(keys, block_meta, info):
    """Preserve blocks; structurally unbound exercises use the section outline."""
    from models import SkillCurriculum

    if len(keys) != len(set(keys)) or set(keys) != set(block_meta):
        raise ValueError('Metadata title inventory differs from DOCX blocks')
    concepts, unresolved, needs_resolution = [], [], []
    allowed = {h['concept_code']: h['concept_name'] for h in info['structural_skill_candidates']}
    section_rows = SkillCurriculum.query.filter_by(
        curriculum=info['curriculum'], volume=info['volume'], section=info['section']).all()
    outline_rows = [row for row in section_rows if row.skill_id.startswith('outline_')]
    if len(outline_rows) != 1:
        raise ValueError('Section outline identity is missing or ambiguous')
    outline_skill_id = outline_rows[0].skill_id
    formal_by_code = {}
    for heading in info['structural_skill_candidates']:
        matching = [row for row in section_rows
                    if row.skill_id.startswith('vh_')
                    and normalize_identity(row.paragraph) == normalize_identity(heading['concept_name'])]
        sid = heading.get('formal_skill_id') or (matching[0].skill_id if len(matching) == 1 else None)
        if sid:
            formal_by_code[heading['concept_code']] = (heading['concept_name'], sid)

    def classify_by_content(block):
        """Resolve an exercise only when content gives one deterministic scope."""
        text = normalize_identity(block.get('problem_text', '')).lower()
        candidates = list(formal_by_code.values())
        if not text or not candidates:
            return None
        # Candidate meanings come from authoritative DOCX headings; the
        # classifier does not inspect generator capability or solve the item.
        transform = next(((name, sid) for name, sid in candidates
                          if '變化' in name or ('週期' in name and not any(
                              fn in name for fn in ('正弦', '餘弦', '正切')))), None)
        transform_cues = ('平移', '伸縮', '係數', '虛線', '實線', '交點', '各三角函數', '最大值與最小值')
        functions = {
            '正弦': len(re.findall(r'(?<![a-z])sin', text)) + text.count('正弦'),
            '餘弦': len(re.findall(r'(?<![a-z])cos', text)) + text.count('餘弦'),
            '正切': len(re.findall(r'(?<![a-z])tan', text)) + text.count('正切'),
        }
        active = [name for name, count in functions.items() if count]
        if transform and (any(cue in text for cue in transform_cues) or len(active) > 1):
            return transform
        if len(active) == 1:
            fn = active[0]
            exact = [(name, sid) for name, sid in candidates if fn in name]
            if len(exact) == 1:
                return exact[0]
        return None
    for order, (title, block) in enumerate(block_meta.items(), 1):
        code, name = block.get('concept_code', ''), block.get('concept_name', '')
        sid = block.get('formal_skill_id', '')
        if code and (code not in allowed or allowed[code] != name):
            raise ValueError('Block heading differs from structural authority')
        structurally_bound = bool(code and sid)
        if not structurally_bound:
            if block.get('source_type') not in {'exercise', 'textbook_exercise', 'advanced_exercise'}:
                unresolved.append(title)
            else:
                classified = classify_by_content(block)
                if classified:
                    name, sid = classified
                else:
                    sid = outline_skill_id
                    name = info['section']
                    needs_resolution.append(title)
        resolution = {
            'source_order': order,
            'anchor': title,
            'needs_skill_resolution': bool(not structurally_bound and sid == outline_skill_id),
            'skill_assignment_status': ('structurally_bound' if structurally_bound else
                                        ('deterministic_content_classification'
                                         if sid != outline_skill_id else 'section_outline_fallback')),
            'section_outline_skill_id': outline_skill_id if sid == outline_skill_id else None,
        }
        item = dict(title=title, source_description=title, source_order=order,
                    source_type=block['source_type'], skill_id=sid,
                    correct_answer='', detailed_solution=block.get('detailed_solution', ''),
                    mapping_status=resolution['skill_assignment_status'],
                    needs_skill_resolution=resolution['needs_skill_resolution'],
                    notes=json.dumps(resolution, ensure_ascii=False, sort_keys=True))
        bucket = 'examples' if block['source_type'] == 'textbook_example' else 'practice_questions'
        concepts.append(dict(concept_name=name, concept_en_id=block.get('concept_en_id', ''),
                             **{bucket: [item]}))
    return dict(chapters=[dict(chapter_title=info['chapter'], sections=[dict(
        section_code=info['section_code'], section_title=info['section'], concepts=concepts)])],
        metadata_source='deterministic_docx_structure', metadata_alignment='PASS',
        unresolved_skill_bindings=unresolved,
        needs_skill_resolution=needs_resolution,
        section_outline_fallback_count=len(needs_resolution))
