import sys
import traceback
from collections import Counter, defaultdict

from core.domain.exponential_logarithmic_domain import SOURCE_SPECS, build_exponential_logarithmic_matrix

seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20
only = set(int(x) for x in sys.argv[2:]) if len(sys.argv) > 2 else None
fails = defaultdict(Counter)
examples = {}
attempts = Counter()
for eid, spec in sorted(SOURCE_SPECS.items()):
    if only and eid not in only:
        continue
    for seed in range(seeds):
        try:
            mat = build_exponential_logarithmic_matrix(seed, {"textbook_example_id": eid})
            attempts[spec["op"]] += mat["generation_attempt"]
        except Exception as exc:  # noqa: BLE001
            key = f"{type(exc).__name__}:{str(exc)[:120]}"
            fails[(eid, spec["op"])][key] += 1
            if (eid, key) not in examples:
                examples[(eid, key)] = traceback.format_exc()
for (eid, op), c in sorted(fails.items()):
    print(eid, op, dict(c))
shown = set()
for (eid, key), tb in examples.items():
    if key in shown:
        continue
    shown.add(key)
    print("=" * 30, eid, key)
    print(tb[-1500:])
print("retries:", {k: v for k, v in attempts.items() if v})
print("fail ids:", len(fails))
