# B2 第4章：題型分類、Generator 品質與 X/Y 掌握制導入報告

**日期**：2026-11-23  
**狀態**：`PASS_ENGINEERING`（掌握制＋MCQ 必修；部分參數變化／響應式為 P2／NOT_TESTED）  
**本輪**：不 commit／不 push；正式 DB 唯讀；Flask 5001 已重載 allowlist

---

## 1. 第4章完整 Skill 清單

皆為 active 練習 SubSection（無另立具名 Skill）：

| Skill ID | 名稱 | Section | TE | Y | 制度 |
|---|---|---|---:|---:|---|
| `vh_數學B2_SubSection_4_1_1` | 圓的標準式 | 4-1 | 16 | 9 | X/Y（已導入） |
| `vh_數學B2_SubSection_4_1_2` | 圓的一般式 | 4-1 | 19 | 10 | X/Y（已導入） |
| `vh_數學B2_SubSection_4_2_1` | 點與圓的關係 | 4-2 | 5 | 3 | X/Y（已導入） |
| `vh_數學B2_SubSection_4_2_2` | 圓與直線的關係 | 4-2 | 17 | 12 | X/Y（已導入） |
| `vh_數學B2_SubSection_4_2_3` | 圓的切線方程式 | 4-2 | 8 | 5 | X/Y（已導入） |
| `vh_數學B2_SubSection_4_2_4` | 切線段長 | 4-2 | 5 | 3 | X/Y（已導入） |

合計 Runtime 可用題型 **42**（去重 per Skill）。證據：`ch4_inventory.json`。

---

## 2. 分類矩陣

完整 42 列矩陣：

- `reports/b2_ch4_intro/ch4_classification_matrix.md`
- `reports/b2_ch4_intro/ch4_classification_matrix.json`

欄位：Skill／Source ID／題型名稱／problem_type_id／Generator／Checker／Y／狀態。  
**未虛構** problem_type；皆來自 facade `GENERATOR_SPECS`＋Runtime inventory。

統計：PASS 31／LIMITED（低變化 P2）11／CHECKER|MCQ 問題 0。

---

## 3. Y 與 X/Y 導入狀態

6／6 Skill 已加入 `B2_TYPE_MASTERY_PILOT_SKILL_IDS`。  
Pilot：**31/31 PASS**（`b2_ch4_type_mastery_pilot_latest.json`）。  
Live 5001：`4_1_1` 顯示「已掌握題型 **0/9**」。

---

## 4. 教材覆蓋與缺口

- 6 Skill 皆有 TE＋facade＋V3 components＋Y≥1。  
- **缺口／P2**：11 個題型 10-seed 抽樣 `unique_stems≤2`（LOW_VARIATION），數學仍可作答，列改善清單，不為湊數破壞保真。  
- 無 NO_COMPONENT／CHECKER_ISSUES／MCQ_ISSUES（本次 10-seed 抽樣）。

---

## 5. Generator 參數變化統計

`ch4_variation_sample.json`：

| 狀態 | 題型數 |
|---|---:|
| PASS（≥3 unique stems／10 seeds） | 31 |
| LOW_VARIATION（P2） | 11 |
| MCQ／Checker 問題 | 0 |

`circle_same_center_scaled_area` 屬可變化 MCQ（面積因子→r²）。

---

## 6. 數學／Checker／MCQ 回歸

| 項目 | 結果 |
|---|---|
| `src_11887` 30 seed：4 選項、唯一、正確選項存在、正答／錯答 | **PASS** |
| Ch4 mastery pilot | **31/31 PASS** |
| Ch3 mastery 回歸（更新 not_gated） | **58/58 PASS** |
| Ch1／Ch2 全套 | **NOT_TESTED**（僅確認 allowlist 仍含既有 ID） |

---

## 7. `4_1_1` 選項缺漏 — Root Cause 與修復

**Root Cause（證據）：**

1. Generator（`circle_same_center_scaled_area`／TE **11887**）**始終產出完整 A–D**，正確答案（例：`=8`）在選項中；Checker 以 `choice_label` 判分 PASS。  
2. 教師「只看到 A、C」較符合 **前端 2×2 網格＋長方程式選項** 在中寬視窗被裁切／擠出可視區的顯示問題，而非 payload 缺 B／D。  
3. Facade 曾誤標 `checker_key=expression_checker`（已改 `choice_label_checker`）。

**修復：**

- `templates/index.html`：長方程式選項強制 **單欄**，禁止 compact／2×2。  
- `skills/vh_數學B2_SubSection_4_1_1.py`：11886／11887／11890 checker 對齊 choice_label。  
- Live 驗收：四選項全部可見；正確 D=`=8`；版面 `display:flex` 單欄。

證據：`evidence_4_1_1_mcq_xy_after.png`。

---

## 8. 學生端驗收

| 項目 | 結果 |
|---|---|
| X/Y 顯示 | **PASS**（0/9） |
| MCQ 四選完整 | **PASS** |
| Canvas／題幹位置 | **PASS**（截圖） |
| 390px／iPad | **NOT_TESTED** |
| 全章含圖題逐題 | **NOT_TESTED**（本輪優先 MCQ＋掌握制） |

---

## 9. SOP 更新

`VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §12.8：第4章 6 SubSection 納入 allowlist；長方程式 MCQ 單欄可見性 Gate。  
§9.2／§9.3 既有規範已涵蓋參數變化、uid≠多樣性、複合分式（前輪）。

---

## 10. 狀態清單

| 代碼 | 項目 |
|---|---|
| **PASS** | Skill 盤點、題型 inventory、X/Y 導入、11887 MCQ 完整、掌握制 pilot、Ch3 回歸 |
| **FIXED** | MCQ 長式 2×2 裁切風險；4_1_1 MCQ checker metadata |
| **P2／LIMITED** | 11 低變化題型 |
| **NOT_TESTED** | 390／iPad；Ch1／Ch2 全測；全章圖片巡檢 |
| **BLOCKED** | 無（無需正式 DB 寫入） |
| **NEEDS_DECISION** | 無 |

---

## 11. PASS_ENGINEERING？

**是（工程層）**：6 Skill 分類可追溯、Y≥1、掌握制實測、P0 MCQ 顯示／契約已修。  
**非人工全章封板**：響應式與全圖巡檢未做；低變化列 P2。

---

## 12. Git 工作樹（本輪相關）

修改／新增（未 commit）：

- `core/practice_type_mastery.py`
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md`
- `templates/index.html`
- `skills/vh_數學B2_SubSection_4_1_1.py`
- `scripts/test_b2_ch4_type_mastery_pilot.py`
- `scripts/test_b2_ch3_type_mastery_pilot.py`（not_gated 調整）
- `reports/b2_ch4_intro/*`

並保留其他 Agent 既有未提交成果（Ch3 P1、銳角參數化、特別角分式等）。

---

## 13. 後續建議

1. 教師目視驗收第4章 X/Y 與 11887 四選項。  
2. P2：對 11 個低變化題型做有限度參數池（不整冊重建）。  
3. 補 390／iPad 與含圖題抽樣後再人工封板。  
4. **停止於此；不自動進 B3／B4。**
