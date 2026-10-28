import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
c = sqlite3.connect('file:instance/kumon_math.db?mode=ro', uri=True)
print([x[1] for x in c.execute('pragma table_info(skill_curriculum)')])
print([x[1] for x in c.execute('pragma table_info(skills_info)')])
for r in c.execute("select * from skill_curriculum where curriculum='general' and volume='數學2' order by chapter, id"):
    print(r)
for r in c.execute("select * from skills_info where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation','gh_CountingPrinciples','gh_LogicAndSets')"):
    print([str(x)[:20] for x in r])
