# -*- coding: utf-8 -*-
import pandas as pd
from pathlib import Path

xlsx = Path(r"C:\Users\Owner\Downloads\kumon_math_backup_20260731_1511.xlsx")
xls = pd.read_excel(xlsx, sheet_name=None, engine="openpyxl")

def ids(s):
    out=set()
    for v in s.dropna():
        if hasattr(v,'item'): v=v.item()
        if isinstance(v,float) and float(v).is_integer(): v=int(v)
        out.add(int(v) if isinstance(v,(int,float)) else v)
    return out

uids = ids(xls['users']['id'])
aids = ids(xls['adaptive_learning_logs']['student_id'])
print('intersection adaptive', sorted(aids & uids))
print('adaptive rows for those', len(xls['adaptive_learning_logs'][xls['adaptive_learning_logs']['student_id'].isin(list(aids & uids))]))

pids = ids(xls['progress']['user_id'])
print('intersection progress', sorted(pids & uids))
print('progress rows matching', len(xls['progress'][xls['progress']['user_id'].isin(list(pids & uids))]))

# users id=1 details
print(xls['users'][xls['users']['id']==1].to_dict('records'))
print('users dtypes', xls['users'].dtypes.to_dict())
print('adaptive student_id dtype', xls['adaptive_learning_logs']['student_id'].dtype)
print('progress user_id dtype', xls['progress']['user_id'].dtype)

# skill orphans - are they missing from skills_info entirely?
si = set(xls['skills_info']['skill_id'].astype(str))
orph = sorted({str(s) for s in xls['skill_curriculum']['skill_id'] if str(s) not in si})
print('orphan skills', orph)
# any near-match?
for o in orph[:5]:
    near = [s for s in si if o.split('_')[-1] in s or s.endswith(o.split('_')[-1])]
    print(' near', o, '->', near[:3])
