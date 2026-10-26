"""Read-only audit of the gh_Sequence bundle before any human approval.

A. Promotion preflight on the real workspace (no writes; expected blockers: only the pending human approval).
B. Cross-validation of the overlapping primitives against the existing static ``sequence.series`` domain (vocational B3).
C. Static safety scan of the package files (imports, I/O, randomness, eval) and byte-identity with the sandbox candidate.
D. Variation-audit comparison: the same 2-choice rule on the 4 ○× components and on an already published ○× skill.
Nothing is written to the database, uploads, configs, core/domain/promoted or the production skill tree.
"""
import ast
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the production skill tree free of .pyc files while auditing it
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
report: dict = {}

# ---------------------------------------------------------------- A. preflight
from core.gencode.reviewed_capability_promotion import preflight_reviewed_bundle  # noqa: E402

workspace = next((ROOT / "reports" / "domain_operation_workspaces").glob("capability_sequence_progression_*")) / "revision_0001"
pre = preflight_reviewed_bundle(workspace)
report["A_preflight"] = {"passed": pre["passed"], "blockers": pre["blockers"], "bundle_sha256": pre["bundle_sha256"]}
print("A preflight blockers (approval is the only expected one):", pre["blockers"])

# ---------------------------------------------------------------- C. package safety
SRC = ROOT / "agent_domains_candidate" / "sequence_progression"
bundle = pre["bundle"]
BANNED_CALLS = {"open", "eval", "exec", "compile", "__import__", "input", "print"}
BANNED_MODULES = {"os", "sys", "subprocess", "socket", "requests", "urllib", "http", "random", "time", "datetime", "pathlib", "shutil", "sqlite3", "importlib"}
findings, identical = [], {}
for name, digest in bundle["files"].items():
    src_path, pkg_path = SRC / name, workspace / "production_package" / name
    identical[name] = hashlib.sha256(src_path.read_bytes()).hexdigest() == digest == hashlib.sha256(pkg_path.read_bytes()).hexdigest()
    tree = ast.parse(pkg_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            findings += [f"{name}: import {a.name}" for a in node.names if a.name.split(".")[0] in BANNED_MODULES]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0 and node.module.split(".")[0] in BANNED_MODULES:
            findings.append(f"{name}: from {node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BANNED_CALLS:
            findings.append(f"{name}: call {node.func.id}")
        elif isinstance(node, (ast.Try,)):
            for h in node.handlers:
                if h.type is None:
                    findings.append(f"{name}: bare except line {h.lineno}")
        elif isinstance(node, ast.FunctionDef):
            body = [n for n in node.body if not isinstance(n, ast.Expr)]
            if not body or (len(body) == 1 and isinstance(body[0], (ast.Pass,))):
                findings.append(f"{name}: empty function {node.name}")
        elif isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call) and getattr(node.exc.func, "id", "") == "NotImplementedError":
            findings.append(f"{name}: NotImplementedError")
imports = sorted({n.module.split(".")[0] if isinstance(n, ast.ImportFrom) and n.module and n.level == 0 else (n.names[0].name.split(".")[0] if isinstance(n, ast.Import) else "")
                  for p in bundle["files"] for n in ast.walk(ast.parse((workspace / "production_package" / p).read_text(encoding="utf-8")))
                  if isinstance(n, (ast.Import, ast.ImportFrom))} - {""})
report["C_safety"] = {"byte_identical_to_sandbox_candidate_and_bundle_hash": identical, "banned_findings": findings, "third_party_or_core_imports": imports}
print("C package identical to reviewed hashes:", identical, "| banned findings:", findings, "| imports:", imports)

# ---------------------------------------------------------------- B. cross-validation vs core/domain/sequence_series_*
from agent_domains_candidate.sequence_progression import build_sandbox as B  # noqa: E402
from agent_domains_candidate.sequence_progression import sequence_progression_domain as D  # noqa: E402
from agent_domains_candidate.sequence_progression.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.sequence_progression.sequence_progression_specs import COMPONENTS  # noqa: E402
from core.domain import sequence_series_domain as OLD  # noqa: E402
from core.domain import sequence_series_extended as OLDX  # noqa: E402
import sympy as sp  # noqa: E402

register_candidate_in_memory()
cross = {"terms": [0, 0], "arith_two_terms": [0, 0], "arith_first_negative": [0, 0], "geo_ratio_two_terms": [0, 0],
         "geo_nth": [0, 0], "geo_shifted_pair_sums": [0, 0, 0], "not_covered_by_existing_domain": []}  # [agree, total(, not applicable)]


def agree(key: str, ok: bool) -> None:
    cross[key][1] += 1
    cross[key][0] += 1 if ok else 0


for cid, (_s, op, source, sampler) in sorted(COMPONENTS.items()):
    for variant in B.collect_variants(cid, op, source, sampler):
        m = D.build_sequence_progression_matrix(domain_operation=op, constraints=dict(variant))
        a = m["answer"]
        if op == "sequence_terms_from_formula":
            for item, rec in zip(variant["items"], a["items"]):
                agree("terms", [sp.nsimplify(t) for t in rec["terms"]] == [sp.nsimplify(OLD.eval_term_expression(D.formula_expr(item), k)) for k in range(1, 6)])
        elif op == "arithmetic_from_terms":
            d = OLD.arithmetic_diff_from_two(variant["A"], variant["m"], variant["B"], variant["n"])
            a1 = OLD.arithmetic_term_from_two(variant["A"], variant["m"], variant["B"], variant["n"], 1)
            agree("arith_two_terms", D.num(a["d"]) == sp.Rational(d.numerator, d.denominator) and D.num(a["a1"]) == sp.Rational(a1.numerator, a1.denominator))
            agree("arith_first_negative", OLD_k(a1, d) + 1 == a["first_negative"] if (OLD_k := lambda s, st: OLDX.first_arithmetic_index_crossing_threshold(s, st, 0, compare="lt")) else False)
        elif op == "geometric_from_terms":
            r = OLD.geometric_ratio_from_two(variant["terms"][0], 1, variant["terms"][1], 2)
            agree("geo_ratio_two_terms", sp.simplify(r - D.num(a["r"])) == 0)
            agree("geo_nth", sp.simplify(OLD.geometric_nth(variant["terms"][0], r, a["k"]) - D.num(a["a_k"])) == 0)
        elif op == "geometric_from_relations" and a["kind"] == "two_terms":
            r = OLD.geometric_ratio_from_two(variant["A"], variant["m"], variant["B"], variant["n"])
            agree("geo_ratio_two_terms", sp.simplify(r - D.num(a["r"])) == 0)
        elif op == "geometric_from_relations" and a["kind"] == "sum_pairs":
            cross["geo_shifted_pair_sums"][1] += 1
            try:  # the existing helper only accepts positive pair sums / positive ratios
                r = OLDX.geometric_ratio_from_shifted_pair_sums(variant["S13"], variant["S24"], 1)
            except ValueError:
                cross["geo_shifted_pair_sums"][2] += 1
                continue
            cross["geo_shifted_pair_sums"][0] += 1 if sp.Rational(r.numerator, r.denominator) == D.num(a["r"]) else 0
cross["not_covered_by_existing_domain"] = ["geometric_from_relations/product_positive,diff_sum", "progression_three_numbers (4 kinds)", "sequence_statements (4 kinds)",
                                           "radical ratios in geometric_from_terms index search"]
report["B_cross_validation"] = cross
print("B cross-validation [agree, total(, not applicable)]:", {k: v for k, v in cross.items() if k != "not_covered_by_existing_domain"})

# ---------------------------------------------------------------- D. variation audit rule on a published 2-choice skill
con = sqlite3.connect(f"file:{(ROOT / 'instance' / 'kumon_math.db').as_posix()}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
from core.gencode.services.v3_variation_audit_service import audit_skill_variation  # noqa: E402

res = audit_skill_variation("gh_PolynomialInequalities", seeds=list(range(1, 21)), source="production", project_root=str(ROOT), conn=con)
by = res.get("variation_status_by_component") or {}
bad = {k: (v.get("error") if isinstance(v, dict) else v) for k, v in by.items() if (v.get("variation_status") if isinstance(v, dict) else v) != "dynamic"}
report["D_published_two_choice_skill"] = {"skill": "gh_PolynomialInequalities", "status": res.get("status"), "non_dynamic": bad}
print("D published Unit 11 skill:", res.get("status"), bad)

(HERE / "audit_before_approval.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
