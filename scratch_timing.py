import time
SKILL = 'vh_數學B4_ConditionalProbability'

print('Step 1: import')
t0=time.time()
from core.vocational_math_b4.generators.chap2_conditional_probability import (
    conditional_probability_basic, without_replacement_conditional_probability
)
print(f'  import done: {time.time()-t0:.3f}s')

for seed in [1, 2, 3, 4, 5, 10, 20]:
    t0=time.time()
    p = conditional_probability_basic(skill_id=SKILL, subskill_id='x', seed=seed)
    elapsed = time.time()-t0
    print(f'  cond_basic seed={seed}: {elapsed:.4f}s ans={p["answer"]}')

for seed in [1, 2, 3, 4, 5, 10, 20]:
    t0=time.time()
    p = without_replacement_conditional_probability(skill_id=SKILL, subskill_id='x', seed=seed)
    elapsed = time.time()-t0
    print(f'  wor seed={seed}: {elapsed:.4f}s ans={p["answer"]}')

print('DONE')
