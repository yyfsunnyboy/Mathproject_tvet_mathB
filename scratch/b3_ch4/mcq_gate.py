"""Every MCQ payload must pass validate_vocational_multiple_choice; record retry counts."""
import sys
from collections import Counter

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix
from core.gencode.exponential_logarithmic_capability_adapter import adapt_exponential_logarithmic_matrix
from core.gencode.choice_contract_validator import validate_vocational_multiple_choice
from core.gencode.vocational_choice_contract import normalize_legacy_vocational_choices

seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 100
bad = Counter()
attempts = Counter()
fails = Counter()
for eid, spec in sorted(SOURCE_SPECS.items()):
    if spec["presentation"] != "single_choice":
        continue
    for seed in range(seeds):
        try:
            mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
        except Exception as exc:  # noqa: BLE001
            fails[f"{eid}:{exc}"] += 1
            continue
        attempts[eid] += mat["givens"].get("generation_attempt", 0)
        p = adapt_exponential_logarithmic_matrix(mat, domain_operation=spec["op"], presentation_mode="single_choice", component_id=f"src_{eid}", textbook_example_id=eid, seed=seed)
        p["skill_id"] = spec["skill_id"]
        p["curriculum_profile"] = "vocational_high_b"
        errs = validate_vocational_multiple_choice(p, spec["skill_id"])
        if errs:
            bad[f"{eid}:{spec['op']}:{','.join(errs)}"] += 1
        normalize_legacy_vocational_choices(p, skill_id=spec["skill_id"])
print("invalid:", dict(bad))
print("build failures:", dict(fails))
print("avg retries >0.5:", {k: round(v / seeds, 2) for k, v in attempts.items() if v / seeds > 0.5})
