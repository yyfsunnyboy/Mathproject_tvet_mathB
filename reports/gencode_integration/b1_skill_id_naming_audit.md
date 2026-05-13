# B1 Skill ID 命名規則稽核報告

## 1. 任務目的
盤點 B1 1-1 教材匯入後產生的 `skill_id` 命名規則，並與 B4 既有規範進行對比，評估一致性風險並提出修正方案。

## 2. B1 目前命名現況
目前 B1 1-1 匯入後產生的 `skill_id` 採用「全英文」前綴格式：
- `vh_mathB1_NumberLine`
- `vh_mathB1_AbsoluteValue`
- `vh_mathB1_AbsoluteValueInequalities`
- `vh_mathB1_AbsoluteValueInequalityExpansion`

## 3. B4 既有命名規則
B4 既有生產代碼與 Registry 採用「中英混合」前綴格式：
- `vh_數學B4_AdditionPrinciple`
- `vh_數學B4_VarianceAndStandardDeviation`
- `vh_數學B4_TreeDiagramCounting`

## 4. 命名規則來源盤點

| file_path | function / code area | observed behavior | notes |
|---|---|---|---|
| `core/textbook_processor.py` | `_determine_target_skill_id` (Line 4068-4069) | `if subject == 'B' and vol_num == 4: return f"vh_數學{subject}{vol_num}_{...}"` | 這裡明確針對 B4 做了特殊處理，其餘冊別則使用 `vh_math...`。 |
| `core/textbook_processor.py` | `_determine_target_skill_id` (Line 4069) | `return f"vh_math{subject}{vol_num}_{target_clean_en_id}"` | 這是 B1 產生全英文 ID 的直接來源。 |

### B4 命名規則使用位置
| file_path / data source | example skill_id | role | notes |
|---|---|---|---|
| `core/vocational_math_b4/services/question_router.py` | `vh_數學B4_CentralTendencyMeasures` | 路由註冊 Key | 生產環境硬編碼使用此格式。 |
| `configs/b4_generator_registry.v0.1.yaml` | `vh_數學B4_AdditionPrinciple` | Registry 唯一 ID | 與生產代碼保持一致。 |
| `core/vocational_math_b4/adaptive/allowlist.py` | `vh_數學B4_ProbabilityProperties` | Allowlist Key | 影響自適應練習的過濾。 |

## 5. 已匯入 B1 1-1 資料影響範圍
經腳本稽核，目前 DB 中受影響的資料如下：

| table/model | affected_rows | related_fields | notes |
|---|---|---|---|
| `SkillInfo` | 4 | `skill_id` | `vh_mathB1_...` 格式。 |
| `SkillCurriculum` | 4 | `skill_id` | 關聯課程對應表。 |
| `TextbookExample` | 13 | `skill_id` | 匯入的 13 題例題與隨堂練習。 |
| `SkillPrerequisites` | 0 | `skill_id`, `pre_skill_id` | 尚未定義先修關係。 |
| `ExperimentLog` | 0 | `skill_id` | 尚未對 B1 執行 gencode。 |
| `ExecutionSample` | 0 | `skill_id` | 尚未產生執行樣本。 |

## 6. 命名策略比較

| 策略 | 優點 | 缺點 | 風險 | 建議 |
|---|---|---|---|---|
| **策略 A**：B1-B3 沿用 `vh_mathB1_*` | 符合全英文變數命名慣例。 | 與 B4 不一致，造成跨冊搜尋或統計時的複雜度。 | 前端與報表系統需處理兩套前綴邏輯。 | 不建議。 |
| **策略 B**：B1-B3 改成 `vh_數學B1_*` | **與 B4 完全一致**，統一「高職數學B」系列規範。 | 代碼中包含中文字元。 | 若未來需要多國語系化可能需再調整（但目前專案為台灣本地化）。 | **強烈建議**。 |

## 7. 推薦修正方案
為了確保「高職數學B」系列 (B1-B4) 的架構一致性，建議將 B1-B3 的命名規則修正為與 B4 一致的 `vh_數學B{n}_` 格式。

### 執行步驟 (下一輪)：
1.  **修改匯入器邏輯**：
    *   修改 `core/textbook_processor.py` 中的 `_determine_target_skill_id` 函式。
    *   取消對 `vol_num == 4` 的特殊判斷，統一改為 `f"vh_數學{subject}{vol_num}_{...}"`。
2.  **同步更新資料庫 (針對已匯入的 B1 1-1)**：
    *   使用 SQL 或 Python 腳本將 `SkillInfo`, `SkillCurriculum`, `TextbookExample` 中所有 `vh_mathB1_` 前綴更新為 `vh_數學B1_`。

## 8. 下一步建議
1.  **核准策略 B**：確認是否同意將 B1-B3 命名格式統一為 `vh_數學B1_`。
2.  **執行修正腳本**：在 Phase 3A-1 執行上述兩項修正步驟。
3.  **重新執行 Consistency Check**：確保修改後 B1 的新命名能正確被系統識別。
