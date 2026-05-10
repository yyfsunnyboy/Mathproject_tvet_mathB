# B4 Chapter 4 Phase 8A：Textbook Evidence and Skill Inventory Planning

## 1. Scope and Guardrails

本階段 (Phase 8A) 專司進行教材證據盤點與 Deterministic Coverage 規劃。嚴格遵循以下限制：
- 不改 code
- 不改 tests
- 不改 DB
- 不寫 generator
- 不接 adaptive
- 不新增 SOP

---

## 2. Chap4 Textbook Evidence Summary

經過針對 `b4_skill_source_summary.csv` 與系統既有 Textbook Examples / Skills 的盤點，**確認 B4 教材（高職數學B第四冊）僅存在三個章節：1. 排列組合、2. 機率、3. 統計。完全找不到任何屬於 Chapter 4 的教材資料。**

- source_chapter: Missing
- source_section: Missing
- skill_id: Missing
- skill_name: Missing
- source_type: Missing
- textbook_example count: 0
- in_class_practice count: 0
- self_assessment count: 0
- **Risk 摘要**：**BLOCK**（找不到 Chap4 教材資料）

---

## 3. Chap4 Skill Inventory

因查無章節，無從建立 Inventory。

| section | skill_id | skill_name | textbook evidence count | likely problem families | deterministic suitability | notes |
|---|---|---|---|---|---|---|
| N/A | N/A | N/A | 0 | N/A | not_suitable_now | 教材範圍不存在 |

---

## 4. Skill-level Textbook Family Coverage

| skill_id | textbook_example families | in_class_practice families | self_assessment families | deterministic-safe families | reserved families | notes |
|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | 無教材資料 |

---

## 5. Problem Type Candidate Taxonomy

| skill_id | problem_type_candidate | scenario_family | answer_type | checker_candidate | deterministic_ready | risk | notes |
|---|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | no | HIGH | BLOCK |

---

## 6. Reserved / Future AI-judged 題型

因不存在 Chapter 4，故無從分類。
（若系統未來擴增教材範圍，應遵循 SOP 預設將圖表、畫圖、完整填表等排除於 Deterministic 之外。）

---

## 7. First Runtime-ready Batch Proposal

無法建立 Implementation Batch Proposal。

| proposed_phase | skill_id | problem_type | scenario_family | reason | risk |
|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | 無教材資料 | HIGH (BLOCK) |

---

## 8. Testing / Smoke Gate Plan

暫不適用。

---

## 9. Relation to Adaptive Practice

本輪不接 adaptive_practice。由於 Chap4 教材範圍不存在，亦無法在未來進行 chapter mode adaptive integration。

---

## 10. Recommended Next Phase

**決策：BLOCK**

由於符合 SOP 中「找不到 Chap4 教材資料 / textbook evidence insufficient」的強制暫停條件，**本流程即刻 BLOCK，不啟動 Phase 8B**。

**建議下一步**：
- 退回檢視整個 B4 專案進度，因 B4 全三章皆已完成 Deterministic Mainline Coverage（Phase 7G）。
- 建議轉換任務目標，例如啟動下一冊 (B5) 的前期規劃，或是回頭進行 B1~B3 / 國中先備知識的補強 (Prerequisite Content Planning)。

---

## 11. Final Confirmation

- 是否只新增 planning report：**是**
- 是否修改 production code：**否**
- 是否修改 tests：**否**
- 是否修改 DB：**否**
- 是否新增 generator：**否**
- 是否修改 adaptive scoring / mastery / APR / PPO：**否**
- 是否接 adaptive_practice：**否**
- 是否啟動 implementation：**否**
- 是否新增 SOP：**否**
