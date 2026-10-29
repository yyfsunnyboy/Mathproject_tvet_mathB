"""Apply or roll back the authorised 數學2 單元5「組合」Stage 1 change set (28 old rows -> 37 verified rows).

Same procedure as reports/gh_math2_unit4_stage1/apply_unit4.py, plus deleting the stale Unit 5 binding of the shared
gh_ComprehensiveExercises skill (skill_curriculum 360; the skill and its other units are untouched).
Default is a read-only preflight.  Production writes require --apply --production.  Never imports `app`.
"""
import argparse, hashlib, json, os, re, shutil, sqlite3, sys, uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from core.textbook_stage1_gate import evaluate_stage1_gate  # noqa: E402

CS = json.loads((HERE / 'production_change_set.json').read_text(encoding='utf-8'))
SCOPE = tuple(CS['unit'].values())
PROD = (ROOT / 'instance/kumon_math.db').resolve()
OLD_IDS = [r['id'] for r in CS['old_rows']]
NEW_IDS = [r['id'] for r in CS['new_rows']]
CUR_IDS = tuple([u['id'] for u in CS['curriculum_updates']] + [c['id'] for c in CS['curriculum_deletes']])
UNIT_SKILLS = tuple(CS['expected']['skills'])
PUA = re.compile('[\ue000-\uf8ff]')
SCOPE_SQL = 'source_curriculum=? and source_volume=? and source_chapter=?'
SCOPED = {
    'textbook_examples': (SCOPE_SQL, SCOPE),
    'skill_curriculum': (f'id in ({",".join("?" * len(CUR_IDS))})', CUR_IDS),
    'skill_family_bridge': None,  # re-seeded from the catalog by create_app(); not part of this change set
}


def sha(data): return hashlib.sha256(data).hexdigest()
def rowdict(row): return dict(row) if row is not None else None


def digest(con, sql, args=()):
    h = hashlib.sha256()
    for row in con.execute(sql, args):
        h.update(json.dumps(tuple(row), ensure_ascii=False, default=str).encode('utf-8')); h.update(b'\n')
    return h.hexdigest()


def outside_digests(con):
    out = {}
    for (table,) in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name").fetchall():
        if table in SCOPED:
            if SCOPED[table] is None:
                continue
            where, args = SCOPED[table]
            out[table] = digest(con, f'select * from "{table}" where not ({where}) order by rowid', args)
        else:
            out[table] = digest(con, f'select * from "{table}" order by rowid')
    return out


def scope_rows(con):
    return [rowdict(r) for r in con.execute(f'select * from textbook_examples where {SCOPE_SQL} order by id', SCOPE)]


def preflight(con, uploads_root):
    problems = []
    for kind in ('docx', 'pdf'):
        f = ROOT / CS[kind]['path']
        if not f.is_file() or sha(f.read_bytes()) != CS[kind]['sha256']: problems.append(f'{kind} source hash mismatch')
    record = json.loads((ROOT / CS['source_record']).read_text(encoding='utf-8'))['sources']
    for kind in ('docx', 'pdf'):
        if record[kind]['sha256'] != CS[kind]['sha256'] or record[kind]['stored_path'] != CS[kind]['path']: problems.append(f'{kind} import record mismatch')
    regions = json.loads((ROOT / CS['verified_region']['file']).read_text(encoding='utf-8'))['sources']
    hit = [s for s in regions if s['pdf_sha256'] == CS['pdf']['sha256'] and (s['curriculum'], s['volume'], s['chapter']) == SCOPE]
    if len(hit) != 1 or hit[0]['verified_by'] != 'teacher' or CS['verified_region']['label'] not in hit[0]['regions']: problems.append('verified region not in live catalog')
    current = scope_rows(con)
    if current != CS['old_rows']: problems.append('Unit 5 rows differ from the old 28 rows in the change set (ids/content drift)')
    if [r['id'] for r in current] != list(range(1413, 1441)): problems.append('old id range drift')
    if con.execute('select max(id) from textbook_examples').fetchone()[0] != NEW_IDS[0] - 1: problems.append('max(textbook_examples.id) changed since replay')
    if con.execute(f'select count(*) from textbook_examples where id between {NEW_IDS[0]} and {NEW_IDS[-1]}').fetchone()[0]: problems.append('new id range occupied')
    for u in CS['curriculum_updates']:
        if rowdict(con.execute('select * from skill_curriculum where id=?', (u['id'],)).fetchone()) != u['before']: problems.append(f"skill_curriculum {u['id']} drift")
    for c in CS['curriculum_deletes']:
        if rowdict(con.execute('select * from skill_curriculum where id=?', (c['id'],)).fetchone()) != c: problems.append(f"skill_curriculum {c['id']} drift")
    for (table,) in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall():
        if table in ('textbook_examples', 'skill_curriculum', 'skills_info', 'skill_family_bridge'):
            continue
        for c in [x[1] for x in con.execute(f'pragma table_info("{table}")')]:
            if c == 'skill_id' or c.endswith('_skill_id'):
                n = con.execute(f'select count(*) from "{table}" where "{c}" in ({",".join("?" * len(UNIT_SKILLS))})', UNIT_SKILLS).fetchone()[0]
                if n: problems.append(f'{table}.{c}: {n} rows reference the Unit 5 skills')
            if re.search(r'example_id|source_example|textbook_example|question_id|item_id', c, re.I):
                n = con.execute(f'select count(*) from "{table}" where cast("{c}" as text) in ({",".join("?" * len(OLD_IDS))})', [str(i) for i in OLD_IDS]).fetchone()[0]
                if n: problems.append(f'{table}.{c}: {n} old-row references')
    if con.execute("select 1 from sqlite_master where name='practice_attempts'").fetchone():
        old = {str(i) for i in OLD_IDS}
        for (uid,) in con.execute('select distinct question_uid from practice_attempts'):
            try: uuid.UUID(str(uid))
            except ValueError:
                if str(uid) in old: problems.append(f'non-UUID attempt references old row {uid}')
    for r in CS['old_rows']:
        n = json.loads(r['notes'] or '{}')
        if n.get('image_assets') or r.get('image_path'): problems.append(f"old row {r['id']} owns image assets (not handled)")
    for a in CS['asset_files']:
        src = HERE / a['source_file']; dst = uploads_root / a['path']
        if not src.is_file() or sha(src.read_bytes()) != a['sha256']: problems.append(f"asset source mismatch row {a['row_id']}")
        if dst.exists(): problems.append(f"asset destination already exists: {a['path']}")
    if con.execute('pragma quick_check').fetchone()[0] != 'ok': problems.append('db quick_check failed')
    return problems


def verify_unit(con, uploads_root):
    rows = scope_rows(con)
    assert len(rows) == 37 and [r['id'] for r in rows] == NEW_IDS, 'row set != 37 new rows'
    assert rows == CS['new_rows'], 'row content != verified change set'
    assert con.execute(f'select count(*) from textbook_examples where id in ({",".join("?" * len(OLD_IDS))})', OLD_IDS).fetchone()[0] == 0, 'old rows remain'
    skills = dict(Counter(r['skill_id'] for r in rows))
    assert skills == CS['expected']['skills'], skills
    for r in rows:
        for field in ('problem_text', 'detailed_solution', 'correct_answer'):
            v = r[field] or ''
            assert not PUA.search(v) and 'MATH_PARSE_FAILED' not in v, (r['id'], field)
    anchors = [json.loads(r['notes'])['question_anchor'] for r in rows]
    assert len({a['anchor_id'] for a in anchors}) == 37 and sorted(a['source_order'] for a in anchors) == list(range(1, 38))
    gate = evaluate_stage1_gate(rows)
    assert gate['status'] == 'READY' and gate['stage1_ready'] and not gate['blocked'] and not gate['needs_review'], gate
    figure_rows = [r['id'] for r in rows if json.loads(r['notes']).get('image_assets')]
    assert figure_rows == CS['expected']['figure_rows'], figure_rows
    for a in CS['asset_files']:
        f = uploads_root / a['path']
        assert f.is_file() and sha(f.read_bytes()) == a['sha256'], a['path']
        n = json.loads(next(r['notes'] for r in rows if r['id'] == a['row_id']))
        ok = [x for x in n.get('image_assets', []) if x['path'] == a['path'] and x['sha256'] == a['sha256']
              and x.get('visual_status') == 'accepted' and x.get('visual_classification') == 'required' and not x.get('needs_crop_review')]
        assert len(ok) == 1
    for u in CS['curriculum_updates']:
        assert rowdict(con.execute('select * from skill_curriculum where id=?', (u['id'],)).fetchone()) == u['after']
    for c in CS['curriculum_deletes']:
        assert con.execute('select count(*) from skill_curriculum where id=?', (c['id'],)).fetchone()[0] == 0
    assert con.execute("select count(*) from skill_curriculum where skill_id='gh_ComprehensiveExercises'").fetchone()[0] >= 1
    return {'rows': len(rows), 'ids': [NEW_IDS[0], NEW_IDS[-1]], 'skills': skills, 'old_remaining': 0, 'gate': gate['status'],
            'blocked': len(gate['blocked']), 'needs_review': len(gate['needs_review']), 'figure_rows': figure_rows, 'source_order': '1-37',
            'curriculum_updates': [(u['id'], u['after']['display_order']) for u in CS['curriculum_updates']],
            'curriculum_deleted': [c['id'] for c in CS['curriculum_deletes']], 'private_use_or_parse_failed': 0}


def insert_row(con, table, rec):
    cols = list(rec)
    con.execute(f'insert into {table} ({",".join(cols)}) values ({",".join("?" * len(cols))})', [rec[k] for k in cols])


def restore(con, uploads_root):
    """Compensation: put the exact pre-change rows back (valid only while the change set is what is applied)."""
    con.execute('begin immediate')
    try:
        n = con.execute(f'delete from textbook_examples where {SCOPE_SQL} and id between ? and ?', (*SCOPE, NEW_IDS[0], NEW_IDS[-1])).rowcount
        assert n in (0, 37), n
        for rec in CS['old_rows']:
            if con.execute('select 1 from textbook_examples where id=?', (rec['id'],)).fetchone() is None:
                insert_row(con, 'textbook_examples', rec)
        for u in CS['curriculum_updates']:
            con.execute('update skill_curriculum set display_order=? where id=?', (u['before']['display_order'], u['id']))
        for c in CS['curriculum_deletes']:
            if con.execute('select 1 from skill_curriculum where id=?', (c['id'],)).fetchone() is None:
                insert_row(con, 'skill_curriculum', c)
        assert scope_rows(con) == CS['old_rows']
        con.execute('commit')
    except Exception:
        con.execute('rollback'); raise
    for a in CS['asset_files']:
        dst = uploads_root / a['path']
        if dst.is_file() and sha(dst.read_bytes()) == a['sha256']: dst.unlink()


def apply(con, uploads_root, backup_root):
    problems = preflight(con, uploads_root)
    assert not problems, problems
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bdir = backup_root / f'math2_unit5_stage1_{stamp}'
    bdir.mkdir(parents=True, exist_ok=False)
    backup = bdir / 'kumon_math_before_math2_unit5_stage1.db'
    dst = sqlite3.connect(backup); con.backup(dst)
    assert dst.execute('pragma integrity_check').fetchone()[0] == 'ok'
    backup_tables = outside_digests(dst); dst.close()
    for name in ('general_high_source_skill_map.json', 'fixed_textbook_practice.json', 'gencode_promoted_capabilities.json', 'stage1_verified_visual_regions.json'):
        if (ROOT / 'configs' / name).is_file(): shutil.copy2(ROOT / 'configs' / name, bdir / name)
    shutil.copy2(HERE / 'production_change_set.json', bdir / 'production_change_set.json')
    manifest = bdir / 'apply_manifest.json'
    m = {'unit': CS['unit'], 'status': 'backed_up', 'backup': str(backup), 'backup_sha256': sha(backup.read_bytes()),
         'source_fingerprints': {'docx': CS['docx'], 'pdf': CS['pdf']}, 'verified_region': CS['verified_region'],
         'pre_change_scope_summary': {'rows': len(CS['old_rows']), 'ids': [OLD_IDS[0], OLD_IDS[-1]],
                                      'skills': dict(Counter(r['skill_id'] for r in CS['old_rows'])),
                                      'row_digest': sha(json.dumps(CS['old_rows'], ensure_ascii=False, default=str).encode())},
         'pre_change_outside_digests': backup_tables, 'created_assets': CS['asset_files'],
         'change_set_sha256': sha((HERE / 'production_change_set.json').read_bytes())}
    manifest.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
    pending, published = [], []
    committed = False
    try:
        for a in CS['asset_files']:
            d = uploads_root / a['path']; d.parent.mkdir(parents=True, exist_ok=True)
            tmp = d.with_name(d.name + f'.pending_{stamp}')
            shutil.copy2(HERE / a['source_file'], tmp)
            assert sha(tmp.read_bytes()) == a['sha256']; pending.append((tmp, d))
        con.execute('begin immediate')
        try:
            before = outside_digests(con)
            assert before == backup_tables, 'formal DB drifted between backup and write lock: ' + str([k for k in before if before[k] != backup_tables.get(k)])
            assert scope_rows(con) == CS['old_rows']
            n = con.execute(f'delete from textbook_examples where {SCOPE_SQL} and id between ? and ?', (*SCOPE, OLD_IDS[0], OLD_IDS[-1])).rowcount
            assert n == 28, n
            for rec in CS['new_rows']: insert_row(con, 'textbook_examples', rec)
            for u in CS['curriculum_updates']:
                assert con.execute('update skill_curriculum set display_order=? where id=? and skill_id=?', (u['after']['display_order'], u['id'], u['before']['skill_id'])).rowcount == 1
            for c in CS['curriculum_deletes']:
                assert con.execute('delete from skill_curriculum where id=? and skill_id=? and chapter=?', (c['id'], c['skill_id'], c['chapter'])).rowcount == 1
            assert len(scope_rows(con)) == 37
            assert outside_digests(con) == before, 'out-of-scope drift inside transaction'
            con.execute('commit'); committed = True
        except Exception:
            con.execute('rollback'); raise
        for tmp, d in pending:
            os.replace(tmp, d); published.append(d)
        result = verify_unit(con, uploads_root)
        assert outside_digests(con) == backup_tables, 'out-of-scope DB drift after commit'
        assert con.execute('pragma integrity_check').fetchone()[0] == 'ok'
        m.update(status='applied_verified', verification=result, applied_at=datetime.now().isoformat(timespec='seconds'))
        manifest.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
        return manifest, result
    except Exception as exc:
        for tmp, _ in pending:
            if tmp.exists(): tmp.unlink()
        if committed:
            restore(con, uploads_root)
        else:
            for d in published:
                if d.exists(): d.unlink()
        m.update(status='rolled_back_after_failure', error=repr(exc)[:500])
        manifest.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=str(PROD)); ap.add_argument('--uploads-root', default=str(ROOT))
    ap.add_argument('--backup-dir'); ap.add_argument('--apply', action='store_true'); ap.add_argument('--production', action='store_true')
    ap.add_argument('--rollback'); ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    db, root = Path(a.db).resolve(), Path(a.uploads_root).resolve()
    prod = db == PROD or root == ROOT
    if prod and (a.apply or a.rollback) and not a.production: sys.exit('REFUSED: production write requires --production')
    if not prod and a.production: sys.exit('REFUSED: --production with test paths')
    if prod != (db == PROD and root == ROOT): sys.exit('REFUSED: mixed production/test paths')
    con = sqlite3.connect(db, isolation_level=None, timeout=30); con.row_factory = sqlite3.Row
    try:
        if a.rollback:
            m = json.loads(Path(a.rollback).read_text(encoding='utf-8'))
            assert m['unit'] == CS['unit'] and m['status'] == 'applied_verified'
            assert scope_rows(con) == CS['new_rows'], 'current rows are not exactly the applied change set'
            restore(con, root); print('ROLLBACK PASS', len(scope_rows(con)), 'rows restored'); return
        if a.verify:
            print('VERIFY PASS', json.dumps(verify_unit(con, root), ensure_ascii=False)); return
        if not a.apply:
            p = preflight(con, root); print('PREFLIGHT', 'PASS' if not p else 'FAIL', p); return
        manifest, result = apply(con, root, Path(a.backup_dir or (ROOT / 'instance/backups')))
        print('APPLY PASS', json.dumps(result, ensure_ascii=False), 'MANIFEST', manifest)
    finally:
        con.close()


if __name__ == '__main__':
    main()
