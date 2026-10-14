# -*- coding: utf-8 -*-
import sqlite3, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from core.gencode.services.v3_publish_eligibility import component_publish_blockers
from core.gencode.skill_wrapper_compiler import _fetch_verified_components, _fetch_publish_eligible_components

conn=sqlite3.connect('instance/kumon_math.db')
conn.row_factory=sqlite3.Row
skill='vh_數學B1_PolynomialBasicConcepts'
verified=_fetch_verified_components(conn, skill)
print('verified', len(verified))
if verified:
    print('sample keys', list(verified[0]['induced_spec_payload'].keys())[:30])
    print('component_id field', verified[0].get('component_id'), verified[0]['induced_spec_payload'].get('component_id'))
    b=component_publish_blockers(skill_id=skill, component_skill_id=skill, component_status='verified', spec=verified[0]['induced_spec_payload'])
    print('blockers', b)
eligible=_fetch_publish_eligible_components(conn, skill)
print('eligible', len(eligible))

rows=conn.execute("select textbook_example_id, component_id, gencode_status from gencode_component_tracker where skill_id=? and gencode_status='verified'",(skill,)).fetchall()
print('db verified rows', [(r['textbook_example_id'], r['component_id']) for r in rows[:5]], 'count', len(rows))
