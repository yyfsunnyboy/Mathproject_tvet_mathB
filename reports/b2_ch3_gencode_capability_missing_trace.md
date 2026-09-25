# B2 Ch3 GenCode — CAPABILITY_MATCH missing Root-Cause Trace

## Failed Job

| Field | Value |
|---|---|
| job_id | `c3a832274e9f46bcb37e0fa2cd296377` |
| DB row id | 1 |
| skill_id | `vh_數學B2_SubSection_3_2_1` |
| skill_ch_name | 向量的坐標表示法 |
| category / section | `3-2 向量的坐標表示法` |
| curriculum | vocational B2（技高） |
| volume / chapter | 數學B2 / 第3章 向量 |
| examples | 11 |
| stage | FINALIZE |
| status (before fix) | `failed` |
| capability_status | `missing` |
| domain_key | `""` |
| missing_layers | `domain_registry_binding` |
| wiring_error | `skill_domain_not_registered: 'vh_數學B2_SubSection_3_2_1'` |
| production_preserved | `true` |
| published | 0 |
| COMPONENT_BUILD…PUBLISH | never started (`pending`) |

Evidence: `gencode_v3_orchestrator_jobs` payload (`scratch/_b2_ch3_gencode_job1_payload.json`).

---

## Call chain (UI → Finalize)

| Stage | Function | File | Input | Output / Decision | Evidence |
|---|---|---|---|---|---|
| UI 建立 V3 | admin skill action | admin gencode routes | skill_id | enqueue / run orchestrator | skill card for 3-2-1 |
| Orchestrator entry | `run_v3_build_orchestrator` | `core/gencode/services/v3_build_orchestrator_service.py` | skill_id, conn | durable job row | job_id above |
| LOAD_EXAMPLES | SQL `textbook_examples WHERE skill_id=?` | same | skill_id | 11 ids | counts.example_count=11 |
| PREFLIGHT | `evaluate_skill_v3_capability(..., probe_examples=True)` | `v3_skill_capability_preflight_service.py` | skill_id | capability_status=`missing` | payload.capability |
| Domain resolve | `resolve_domain_for_skill` | `core/registry/taxonomy_registry.py` | skill_id | raises `SkillDomainNotRegisteredError` | wiring_error |
| CAPABILITY_MATCH (preflight) | `_check_domain_wiring` → not registered | preflight service | — | probes **skipped**; all 11 tagged `domain_registry_missing` | evaluate() return |
| CAPABILITY_MATCH (orchestrator bug) | `summarize_dispositions([])` from empty `example_probes` | orchestrator | empty probes | needs_capability_count=**0** (wrong) | old payload counts |
| FINALIZE fail path | `if capability_status != READY` | orchestrator ~690 | status=`missing` | error `CAPABILITY_NOT_READY` / message `missing` | errors[] |
| Publish | skipped | — | — | production preserved | production_preserved=true |

---

## Exact meaning of `CAPABILITY_MATCH: missing`

Code (preflight):

```python
if not wiring.get("registered"):
    status = CAPABILITY_MISSING  # "missing"
```

`missing` **does mean**:

**A. skill capability metadata / domain registry binding does not exist**

Specifically: `taxonomy_registry.resolve_domain_for_skill(skill_id)` raises `SkillDomainNotRegisteredError`.

It is **not**:

- B probe not run because of crash (probe intentionally skipped when unregistered)
- C no compatible generator after probe (probes never ran)
- E/F component/package/staging issues (never reached COMPONENT_BUILD)
- H resume leak (fresh job; all early stages same second)

Secondary **orchestration bug** (now fixed): empty probes → disposition summary zeros → Finalize treated `missing` as hard `failed` instead of soft `needs_capability`, so UI showed `CAPABILITY_MATCH: missing` with published/skip/needs_capability all 0 even though preflight knew 11× `domain_registry_missing`.

---

## First divergence vs known-good

Known-good example: `vh_數學B2_SubSection_2_1_1` (law of sines) / other B2 Ch1–Ch2 packages under `agent_skills_v3/vh_數學B2_*`.

| Artifact | Known-good B2 | Failing 3-2-1 | Same? |
|---|---|---|---|
| textbook examples | present | 11 present | Yes |
| `taxonomy_registry` skill profile | yes (`trigonometry.*`) | **absent** | **NO — first divergence** |
| `fixed_domain_key` | set | empty | No |
| domain module / entrypoint | importable | none | No |
| example Phase1 probes | run | skipped | consequence of registry miss |
| component package | may exist | none | later |
| publish | possible when READY | blocked | later |

**First missing artifact:** skill → domain registry binding in `core/registry/taxonomy_registry.py`.
There is also **no** `core/domain/*vector*` module and no vector keys in domain inventory — so this is not “registry forgot an existing domain”; the domain itself is absent.

---

## Root cause classification

1. **Primary: missing real capability / registry**
   - No `vector.*` / 向量 domain in registry or `core/domain`.
   - Skill `vh_數學B2_SubSection_3_2_1` not onboarded like Ch1/Ch2 trig SubSections.

2. **Secondary: orchestration reporting bug** (minimal fix applied)
   - Unregistered skills produced empty probes → zeroed needs_capability counts → hard fail `CAPABILITY_MATCH: missing` instead of soft `needs_capability` with the 11 reasons.

---

## 11 example capability analysis

| example_id | source | Topology (needed capability) |
|---|---|---|
| 11754 | 例1 | vector at origin: draw + components + magnitude |
| 11755 | 隨堂1 | same |
| 11756 | 例2 | equal vectors → solve coordinates |
| 11757 | 隨堂2 | same |
| 11758 | 例3 | directed segment \(\overrightarrow{AB}\) + magnitude |
| 11759 | 隨堂3 | same |
| 11760 | 例4 | parallelogram fourth vertex from 3 points |
| 11761 | 隨堂4 | same |
| 11775 | 基礎1 | multi-part AB / magnitude |
| 11783 | 進階9 | application \(\overrightarrow{AB}\) + magnitude (has figure) |
| 11822 | 自我評量8 | two vectors → triangle perimeter (MCQ) |

**Not a single generator family.** Minimum new domain families likely include at least:

1. `vector.coordinate_representation` (components / magnitude / equal vectors / directed segment) — **first necessary**
2. `vector.parallelogram_vertex` (or compose from segment ops)
3. choice/perimeter compose for 11822

Existing `coordinate_geometry.*` domains do **not** cover \(\vec{a}=(x,y)\) vector algebra; reuse is limited to plane point helpers at most.

---

## Minimal fix applied (this round)

Orchestrator only — **no** fake capability, **no** registry hardcode for Ch3, **no** publish bypass.

- Prefer preflight needs_capability summary when probes are empty
- Soft-stop `missing` / `invalid` / `needs_capability` as `JOB_STATUS_NEEDS_CAPABILITY` with `production_preserved=True`
- Regression: `test_unregistered_domain_soft_stops_as_needs_capability_not_failed_missing`

**Not built this round:** vector domain / generators (real capability work = next stage).
