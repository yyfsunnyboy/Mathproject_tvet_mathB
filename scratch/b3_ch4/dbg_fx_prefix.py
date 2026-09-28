import importlib, glob
from core.gencode.runtime_skill_wrapper import check_answer

path = glob.glob("agent_skills_v3/vh_數學B3_SubSection_4_2_1/components/src_12152/generate.py")[0].replace("\\", "/").split("/")
mod = importlib.import_module(f"agent_skills_v3.{path[1]}.components.{path[3]}.generate")
for seed in range(3):
    p = mod.generate(seed=seed)
    ans = dict(p["correct_answer"])
    k1 = next(iter(ans))
    print(ans)
    for variant in (ans[k1], "f(x)=" + str(ans[k1]), "y=" + str(ans[k1])):
        trial = dict(ans)
        trial[k1] = variant
        print("  ", repr(variant), check_answer(trial, p["correct_answer"], payload=p))
