# B3 Gencode Domain — Architecture + Gap Analysis

**Scope evidence:** `instance/kumon_math.db` textbook_examples with `skill_id LIKE 'vh_數學B3%'`  
**Curriculum / Publisher / Volume (from notes.question_anchor):** vocational / longteng / 數學B3  
**Imported coverage now:** Chapter 1 only — sections `1-1`, `1-2` (74 examples, 9 structural skills)  
**Not in DB yet:** B3 Ch2–Ch4 (equations / inequalities / exp-log) — out of this round  

Legacy Excel skill ids (`arithmetic_seq_term`, …) are **not** the runtime skill surface; authoritative skills are `vh_數學B3_SubSection_*`.

---

## A. B3 Skill Inventory

| skill_id | chapter | section | subsection (structural) | inferred topic | example_count |
|---|---|---|---|---|---|
| `vh_數學B3_SubSection_1_1_1` | 1 數列與級數 | 1-1 等差數列與等差級數 | 1-1.1 | 通項公式展開前 n 項 | 3 |
| `vh_數學B3_SubSection_1_1_2` | 1 | 1-1 | 1-1.2 | 等差數列第 n 項／由兩項反推 | 13 |
| `vh_數學B3_SubSection_1_1_3` | 1 | 1-1 | 1-1.3 | 等差中項 | 2 |
| `vh_數學B3_SubSection_1_1_4` | 1 | 1-1 | 1-1.4 | 等差遞迴 → 一般項 | 5 |
| `vh_數學B3_SubSection_1_1_5` | 1 | 1-1 | 1-1.5 | 等差級數前 n 項和 | 14 |
| `vh_數學B3_SubSection_1_2_1` | 1 | 1-2 等比數列與等比級數 | 1-2.1 | 等比數列第 n 項／由兩項反推 | 19 |
| `vh_數學B3_SubSection_1_2_2` | 1 | 1-2 | 1-2.2 | 等比中項 | 4 |
| `vh_數學B3_SubSection_1_2_3` | 1 | 1-2 | 1-2.3 | 等比遞迴 → 一般項 | 3 |
| `vh_數學B3_SubSection_1_2_4` | 1 | 1-2 | 1-2.4 | 等比級數前 n 項和 | 11 |

**Totals:** chapters=1 · sections=2 · skills=9 · textbook_examples=74  

Representative dumps: `scratch/_b3_corpus_inventory.json`, `scratch/_b3_all_problem_texts.txt`

---

## B. B3 Problem Family Inventory

Families are derived from **mathematical solve structure**, not skill name alone.

| family_id | family_name | skill_ids | problem_type | inputs | operation | answer type | domain needed | existing reusable | new domain | multipart | diagram | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `expand_general_term_first_n` | 通項展開前 n 項 | 1_1_1 | short multipart | formula `a(n)`, n | eval a(1)..a(n) | expression list | Y | sympy/Fraction | **Y** | Y | N | |
| `arithmetic_nth_from_a1_d` | 已知 a1,d 求 an | 1_1_2 | short/MCQ | a1,d,n | a1+(n-1)d | number/expr | Y | — | **Y** | N | N | |
| `arithmetic_d_from_a1_an` | 已知 a1,an 求 d | 1_1_2 | MCQ | a1,an,n | (an-a1)/(n-1) | number | Y | — | **Y** | N | N | |
| `arithmetic_from_two_terms` | 已知 ai,aj 求 d 與/或 ak | 1_1_2 | multipart | ai,i,aj,j,k | recover d, ak | multi | Y | — | **Y** | Y | N | 含 11923 |
| `arithmetic_insert_terms` | 兩端插入成等差 | 1_1_2 | short | A,B,k,which | d=(B-A)/(k+1); term/sum | number | Y | — | **Y** | N | N | 可求插入項或插入項和 |
| `arithmetic_word_nth` | 文字情境 → 等差項 | 1_1_2 | short/MCQ | context params | model→an / first negative | number | Y | — | **Y** | N | N | 體重／悠遊卡等 |
| `arithmetic_mean_solve` | 等差中項求 x | 1_1_3 | short | linear forms, mean | (p+q)/2=m | number | Y | — | **Y** | N | N | |
| `arithmetic_recurrence_general` | 等差遞迴→一般項+ak | 1_1_4 | multipart | a1,d,k | an=a1+(n-1)d | expr+number | Y | — | **Y** | Y | N | |
| `arithmetic_recurrence_diagram` | 圖形規律→遞迴 | 1_1_4 | multipart | diagram pattern | invent recurrence | expr+number | Y | — | partial | Y | **Y** | 11922 manual/diagram |
| `arithmetic_series_sum_given` | 已知級數求 Sn | 1_1_5 | short/MCQ | a1,d,n or listed | Sn=n(2a1+(n-1)d)/2 | number | Y | — | **Y** | N | N | |
| `arithmetic_series_recover_param` | 已知 Sn 反推 a1 或 d | 1_1_5 | short | Sn + (a1\|d) + n | solve linear | number | Y | — | **Y** | N | N | |
| `arithmetic_series_from_two_terms` | 已知兩項求 Sn | 1_1_5 | short | ai,aj,n | recover→Sn | number | Y | — | **Y** | N | N | |
| `arithmetic_sum_multiples_range` | 區間倍數總和 | 1_1_5 | MCQ | L,R,step | AP sum in range | number | Y | — | **Y** | N | N | 1..153 之 4 倍數 |
| `arithmetic_odd_count_mid_total` | 奇數項中項→總和 | 1_1_5 | MCQ | mid, count | total=mid*count | number | Y | — | **Y** | N | N | 統測體適能分組 |
| `arithmetic_word_series` | 文字等差求和／求排 | 1_1_5 | short multipart | seats/shots… | an + Sn | multi | Y | — | **Y** | often | sometimes | 疊杯圖→diagram |
| `geometric_nth_from_a1_r` | 已知 a1,r 求 an | 1_2_1 | short/MCQ | a1,r,n | a1*r^(n-1) | number/expr | Y | — | **Y** | N | N | |
| `geometric_r_from_a1_an` | 已知 a1,an 求 r | 1_2_1 | short | a1,an,n | (an/a1)^(1/(n-1)) | number | Y | — | **Y** | exact root | N | |
| `geometric_from_two_terms` | 已知 bi,bj 求 bk | 1_2_1 | short/MCQ | bi,i,bj,j,k | recover r, bk | number/expr | Y | — | **Y** | N | N | |
| `geometric_insert_terms` | 兩端插入成等比 | 1_2_1 | short | A,B,k,which | r=(B/A)^(1/(k+1)) | number/expr | Y | — | **Y** | N | N | |
| `geometric_r_from_pair_sums` | a+b,c+d→r | 1_2_1 | short/MCQ | pair sums | r^2=(c+d)/(a+b) | number | Y | — | **Y** | N | N | 正數假設 |
| `geometric_r_from_cd_over_ab` | cd/ab→r | 1_2_1 | short | ratio | r^2=… | number | Y | — | **Y** | N | N | |
| `geometric_word_nth` | 細菌／人口／傳染／賽程 | 1_2_1,1_2_4 | short/MCQ | growth model | GP term / rounds | number/expr | Y | — | **Y** | N | N | 部分 log/ineq 求輪數 |
| `geometric_mean_value` | 求等比中項 | 1_2_2 | short | a,b | ±√(ab) | multi/expr | Y | — | **Y** | often ± | N | |
| `geometric_mean_solve_x` | 中項已知求 x | 1_2_2 | short | a,x,mean | x=mean²/a | number/expr | Y | — | **Y** | N | N | |
| `ap_gp_mixed_mean` | 等差＋等比中項聯立 | 1_2_2 | MCQ | AP + GP mean | solve system | number | Y | — | **Y** | N | N | 11970 |
| `geometric_recurrence_general` | 等比遞迴→一般項+ak | 1_2_3 | multipart | a1,r,k | an=a1*r^(n-1) | expr+number | Y | — | **Y** | Y | N | |
| `geometric_series_sum_given` | 已知級數求 Sn | 1_2_4 | short/MCQ | a1,r,n | a1(1-r^n)/(1-r) | number/expr | Y | — | **Y** | N | N | r=±1 special |
| `geometric_series_recover_param` | 已知 Sn 反推 n 或 a1 | 1_2_4 | short | Sn+(a1\|r) | solve | number | Y | — | **Y** | N | N | |
| `geometric_series_from_a1_ak` | 已知 a1,ak 求 S_m | 1_2_4 | MCQ | a1,ak,m | recover r→Sm | number | Y | — | **Y** | N | N | |

### Corpus quality flags (manual review / not generator-faithful yet)

| id | issue |
|---|---|
| 11901 | stem truncated（例3 投球） |
| 11950 | OCR/importer garbage fragment |
| 11952 | stem truncated（分期付款） |
| 11918 | diagram required（疊杯） |
| 11922 | diagram required（地磚規律） |

---

## C. Existing Domain Reuse Matrix

| capability | existing location | reuse for B3? |
|---|---|---|
| exact Fraction / sympy | stdlib + sympy | **reuse** |
| expression / equation / multipart / single-choice checkers | `core/gencode/*`, checkers | **reuse** |
| `stem_structure` multipart | `multipart_stem_contract` | **reuse** |
| vocational MCQ 4-choice | `single_choice_contract` | **reuse** |
| `runtime_skill_wrapper` / V3 components | `agent_skills_v3` + `skills/` facade | **reuse** |
| `domain_operation_registry` + capability adapter | B2 circle/vector pattern | **reuse pattern** |
| statistics `arithmetic_mean_from_raw` | float stats | **do not reuse** (not exact AP mean) |
| integer/fraction/polynomial/radical ops | old JH libs | optional formatting only |
| circle / vector / trig domains | B2 | **no** |
| any sequence/series domain | — | **missing** |

Verdict: **almost all B3 Ch1 math truth is NEW domain**; runtime/checkers/wrapper are fully reusable.

---

## D. Missing Domain Capability Matrix (NEW_DOMAIN_FUNCTIONS_REQUIRED)

Proposed domain: `sequence.series`  
Module: `core/domain/sequence_series_domain.py`  
Entrypoint: `build_sequence_series_matrix`  
Adapter: `core/gencode/sequence_series_capability_adapter.py`

### Pure math primitives (single source of truth)

| API | purpose |
|---|---|
| `eval_term_expression(expr, n)` | evaluate closed-form a(n) exactly |
| `expand_first_terms(expr, n)` | list a(1)..a(n) |
| `arithmetic_nth(a1, d, n)` | a_n |
| `arithmetic_diff_from_two(ai, i, aj, j)` | d |
| `arithmetic_term_from_two(ai, i, aj, j, k)` | a_k |
| `arithmetic_insert_diff(A, B, inserted)` | d |
| `arithmetic_inserted_term(A, B, inserted, which)` | term |
| `arithmetic_inserted_sum(A, B, inserted)` | sum of inserted only |
| `arithmetic_mean(a, b)` | (a+b)/2 exact |
| `solve_linear_arithmetic_mean(p_coeff, p0, q_coeff, q0, mean)` | solve x |
| `arithmetic_partial_sum(a1, d, n)` | S_n |
| `arithmetic_recover_a1_from_sum(Sn, d, n)` | a1 |
| `arithmetic_recover_d_from_sum(Sn, a1, n)` | d |
| `sum_multiples_in_range(lo, hi, step)` | AP sum of multiples |
| `geometric_nth(a1, r, n)` | a_n |
| `geometric_ratio_from_two(ai, i, aj, j)` | r (exact when possible) |
| `geometric_term_from_two(...)` | a_k |
| `geometric_insert_ratio(A, B, inserted)` | r |
| `geometric_inserted_term(...)` | term |
| `geometric_means(a, b)` | ±√(ab) exact |
| `geometric_mean_solve_other(a, mean)` | other endpoint |
| `geometric_partial_sum(a1, r, n)` | S_n (r≠1 / r=1) |
| `geometric_recover_a1_from_sum(Sn, r, n)` | a1 |
| `geometric_recover_n_from_sum(Sn, a1, r)` | n (exact integer when solvable) |

Randomization / stem Chinese stay in matrix builder / generators — **not** in primitives.

---

## E. Proposed Files

| file | role |
|---|---|
| `core/domain/sequence_series_domain.py` | primitives + `build_sequence_series_matrix` |
| `core/gencode/sequence_series_capability_adapter.py` | payload contracts |
| `core/registry/domain_operation_registry.py` | register `sequence.series` ops |
| `tests/test_sequence_series_domain.py` | unit + round-trip |
| `tests/test_b3_sequence_series_sampling.py` | 50-sample / family (phased) |
| `skills/vh_數學B3_SubSection_*.py` | thin facades (like B2) |
| `agent_skills_v3/vh_數學B3_SubSection_*/...` | per-source components |
| `reports/b3_gencode_domain_architecture.md` | this doc |

**Do not touch:** textbook_examples, importer, DOCX/PDF, DB schema, practice frontend contract.

---

## F. Proposed API Contract (sketch)

```python
def arithmetic_nth(a1: RationalLike, d: RationalLike, n: int) -> Fraction:
    """a_n = a1 + (n-1)d. Requires n >= 1."""

def arithmetic_diff_from_two(ai, i, aj, j) -> Fraction:
    """d = (aj-ai)/(j-i). Requires i != j, indices >= 1."""

def geometric_partial_sum(a1, r, n) -> Fraction | sp.Expr:
    """S_n = n*a1 if r==1 else a1*(1-r**n)/(1-r). n>=1."""
```

Invalid: n<1, i==j, r with non-unique root when corpus assumes uniqueness, division by zero, inconsistent GP signs for real even roots → raise `ValueError` with stable code.

---

## G. Test Plan

1. **Domain unit tests** — every primitive: normal / negative / zero / fraction / invalid / exactness; AP/GP forward↔inverse round-trip.
2. **Matrix builder smoke** — one op per family → valid matrix + checker accepts oracle.
3. **50-sample / family** — phased: core AP/GP term+sum first, then insert/mean/recover, then word/MCQ.
4. **Multipart** — field count + `stem_structure` invariants (reuse B2 tests patterns).
5. **B1/B2 regression** — existing domain tests + `test_global_practice_bootstrap_gate` + representative B2 skills.
6. **Acceptance** — fill `B3_DOMAIN_ACCEPTANCE` stub as coverage grows.

### Implementation order (minimal increments)

1. Domain primitives + unit tests  
2. Registry + adapter + matrix builder for core ops  
3. Generators for high-coverage families (1_1_2, 1_1_5, 1_2_1, 1_2_4)  
4. Remaining families  
5. Sampling + B1/B2 regression  
6. Flag diagram / truncated sources as unsupported  

---

## Ambiguity / Scope Notes

- Only **imported** Ch1 corpus is in scope; do not invent Ch2–4 generators from Excel alone.
- Student `correct_answer=NULL` is expected; generators own parameterized answers via domain.
- Truncated/garbage/diagram rows → `unsupported / manual-review`, not fake coverage.
- Legacy Excel skill ids are documentation only; do not revive as runtime skills.
