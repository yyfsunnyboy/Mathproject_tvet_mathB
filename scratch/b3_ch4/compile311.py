import glob
import py_compile
import sys

files = (
    glob.glob("core/domain/exponential_logarithmic_*.py")
    + ["core/gencode/exponential_logarithmic_capability_adapter.py", "core/registry/domain_operation_registry.py",
       "scripts/scaffold_b3_ch4_packages.py", "tests/test_b3_ch4_package_gate.py", "tests/_b3_ch4_tex.py"]
    + glob.glob("agent_skills_v3/vh_數學B3_SubSection_4_*/**/*.py", recursive=True)
    + glob.glob("skills/vh_數學B3_SubSection_4_*.py")
)
bad = []
for path in files:
    try:
        with open(path, encoding="utf-8") as fh:
            compile(fh.read(), path, "exec")
    except SyntaxError as exc:
        bad.append((path, str(exc)[:200]))
print(sys.version.split()[0], "compiled", len(files), "bad", bad)
