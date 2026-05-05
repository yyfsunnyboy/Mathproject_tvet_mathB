# B4 Phase 5B: Subskill Remediation Inventory Report

**File Path Checked:** `configs/adaptive/subskill_remediation.yaml`, `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`, `core/adaptive/session_engine.py`

This report provides a read-only inventory and extraction of the current remediation and subskill structures, focusing on how B4 Chapter 1 fits into the existing architecture.

## 1. YAML File Summary
- **File Checked:** `configs/adaptive/subskill_remediation.yaml`
- **Top-Level Keys:** `subskills`, `diagnosis_map`, `remediation_map`
- **Schema Structure:**
  - `subskills`: Defines a dictionary where keys are subskill IDs (e.g., `int.sign_handling`). Each contains `domain`, `display_name`, and optionally `depends_on`.
  - `diagnosis_map`: Maps specific error keys to target subskills.
  - `remediation_map`: Maps a source subskill to either a detailed domain/display_name or a `target` fallback subskill ID.
- **Main Skills Defined:** The current YAML structure only contains complete second-generation subskill analysis for four foundational algebraic domains: `integer_arithmetic`, `fraction_arithmetic`, `radical_arithmetic`, and `polynomial_arithmetic`.
- **Prerequisite/Remediation Relationships:** Existing logic relies heavily on `depends_on` and `remediation_map` to map complex polynomial algebra back down to basic integer/fraction arithmetic.

## 2. Distinction of Current Ecosystem

To accurately analyze the architecture, we must explicitly distinguish the following sets:

### A. Existing Complete YAML Subskill Domains
The system currently has fully modeled subskill trees and remediation mappings for foundational algebra:
- **`integer_arithmetic`** (12 subskills defined, e.g., `int.add_sub`, `int.bracket_scope`)
- **`fraction_arithmetic`** (7 subskills defined, e.g., `frac.divide`, `frac.same_base_multiplication_rule`)
- **`radical_arithmetic`** (Structure recognized by system, though implicitly mapped in B4/JH overlap)
- **`polynomial_arithmetic`** (8 subskills defined, e.g., `poly.expand_binomial`)

### B. B4 Chapter 1 Deterministic Adaptive Skills
These skills are generator-ready and explicitly allowlisted for production, but **are not yet backed by a complete B4-specific subskill remediation tree in the YAML**. They rely entirely on synthetic catalog entries.
1. `vh_數學B4_AdditionPrinciple`
2. `vh_數學B4_MultiplicationPrinciple`
3. `vh_數學B4_FactorialNotation`
4. `vh_數學B4_PermutationOfDistinctObjects`
5. `vh_數學B4_RepeatedPermutation`
6. `vh_數學B4_PermutationWithRepetition`
7. `vh_數學B4_PermutationOfNonDistinctObjects`
8. `vh_數學B4_CombinationDefinition`
9. `vh_數學B4_CombinationApplications`
10. `vh_數學B4_CombinationProperties`
11. `vh_數學B4_Combination`
12. `vh_數學B4_BinomialCoefficientIdentities`
13. `vh_數學B4_BinomialTheorem`

### C. Safe Minimal Remediation Bridge Candidates
Because the B4 Chapter 1 skills cover combinatorics and counting principles, the existing arithmetic subskills in the YAML cannot fully explain permutation/combination conceptual errors. 
- **Preferred Approach:** B4-to-B4 fallback remediation among the allowlisted deterministic skills (e.g., routing a failing Combination student back to Factorial Notation or Multiplication Principle).
- **Secondary Approach:** Only map to existing arithmetic YAML subskills (like `int.mul_div` or `frac.divide`) when the diagnostic error is *strictly* related to basic calculation or formula evaluation failures.

## 3. Current In-Code Remediation Bridge (B4-to-B4)
Extracted from `core/vocational_math_b4/adaptive/b4_chapter1_deterministic_allowlist.py`:

The code already provides an in-memory B4-to-B4 remediation bridge (`B4_CHAPTER_1_REMEDIATION_BRIDGE`) mapping advanced counting concepts back to foundational counting concepts.
*Examples:*
- `vh_數學B4_PermutationWithRepetition` -> routes to `PermutationOfDistinctObjects`, `MultiplicationPrinciple`
- `vh_數學B4_CombinationDefinition` -> routes to `MultiplicationPrinciple`, `AdditionPrinciple`
- `vh_數學B4_BinomialTheorem` -> routes to `BinomialCoefficientIdentities`, `CombinationDefinition`

## 4. Gap Analysis
- **Missing B4 YAML Ontology:** There are zero combinatorial, counting, or B4-specific subskills defined in `subskill_remediation.yaml`.
- **Conceptual Divergence:** We cannot pretend that existing algebraic subskills (like solving polynomials or dividing fractions) fully explain why a student fails to understand the difference between Permutation and Combination.
- **Synthetic Catalog Limitations:** Currently, `session_engine.py` assigns a placeholder `b4_chapter1_synthetic_bootstrap` to all B4 skills, lacking the specific granularity needed to traverse a real diagnostic subskill graph.

## 5. Two-Stage Recommendation Plan

To safely roll out B4 Chapter 1 adaptive remediation without polluting existing Junior High arithmetic pipelines, we recommend the following two-stage plan:

### Phase 5B-Fix-E1: Minimal B4-to-B4 Remediation Bridge
- **Goal:** Achieve pilot usability for B4 deterministic adaptive sessions immediately.
- **Action:** Wire the existing Python dictionary (`B4_CHAPTER_1_REMEDIATION_BRIDGE`) directly into the `session_engine.py` fallback routing loop.
- **Details:** If a student fails a B4 counting skill repeatedly, forcefully route them to the prerequisite B4 counting skill defined in the code bridge, entirely bypassing the YAML subskill evaluation. Do not add B4 to the YAML yet.

### Phase 5B-Fix-E2: Formal B4 Chapter 1 Subskill Tree Design
- **Goal:** Achieve deep, second-generation diagnostic capabilities for counting problems.
- **Action:** Design a true B4 Chapter 1 permutation/combination subskill tree and add it to `configs/adaptive/subskill_remediation.yaml` (or a dedicated B4 YAML).
- **Details:** This involves mapping out the exact conceptual barriers (e.g., "ordered vs unordered selection", "distinguishable vs indistinguishable items", "tree diagram exhaustive listing") and wiring generator micro-hints. This is a larger content-design task deferred to Phase 5B-Fix-E2.
