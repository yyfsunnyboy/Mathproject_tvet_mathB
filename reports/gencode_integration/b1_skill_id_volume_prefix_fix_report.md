# B1 Skill ID Volume Prefix 修正報告

## 1. 修正目的
本輪任務將技高數學B系列 (B1-B4) 的 `skill_id` prefix 統一改為依據教材匯入時的 `Volume` 欄位決定。確保 B1-B3 與 B4 既有規範一致，避免產生 `vh_mathB1_*` 與 `vh_數學B4_*` 並存的命名衝突，維持系統註冊表的一致性。

## 2. 問題來源
在 `core/textbook_processor.py` 的 `_determine_target_skill_id` 函式中，原本僅對 `vol_num == 4` 的 B4 教材進行了中文前綴處理，其餘冊別則 fallback 成英文前綴 `vh_mathB1_*`。這導致新匯入的 B1 1-1 資料產生的 ID 與 B4 格式不符。

## 3. 修改檔案
- `core/textbook_processor.py`: 修改 `skill_id` 產生邏輯，新增 `normalize_vocational_skill_prefix` helper。
- `scripts/fix_b1_skill_id_volume_prefix.py`: [NEW] 一次性資料同步修正腳本。
- `reports/gencode_integration/b1_skill_id_volume_prefix_fix_report.md`: [NEW] 本修正報告。

## 4. 新命名規則
| volume | prefix | 範例 |
|---|---|---|
| 數學B1 | vh_數學B1_ | vh_數學B1_NumberLine |
| 數學B2 | vh_數學B2_ | vh_數學B2_SkillName |
| 數學B3 | vh_數學B3_ | vh_數學B3_SkillName |
| 數學B4 | vh_數學B4_ | vh_數學B4_AdditionPrinciple |

## 5. 已同步修正的 B1 1-1 skill_id
| old_skill_id | new_skill_id |
|---|---|
| vh_mathB1_NumberLine | vh_數學B1_NumberLine |
| vh_mathB1_AbsoluteValue | vh_數學B1_AbsoluteValue |
| vh_mathB1_AbsoluteValueInequalities | vh_數學B1_AbsoluteValueInequalities |
| vh_mathB1_AbsoluteValueInequalityExpansion | vh_數學B1_AbsoluteValueInequalityExpansion |

## 6. DB 影響範圍
執行 `scripts/fix_b1_skill_id_volume_prefix.py --apply` 後的結果：

| table/model | affected_rows | action |
|---|---|---|
| `skills_info` | 4 | Updated `skill_id` |
| `skill_curriculum` | 4 | Updated `skill_id` |
| `textbook_examples` | 13 | Updated `skill_id` |
| `skill_prerequisites` | 0 | Checked |
| `skill_gencode_prompt` | 0 | Checked |
| `experiment_log` | 0 | Checked |
| `execution_samples` | 0 | Checked |
| `progress` | 0 | Checked |
| `skill_family_bridge` | 0 | Checked |

**總計影響筆數：21 筆**

## 7. 驗證結果
- **dry-run 結果**: 成功識別 21 筆需修正資料，未改動資料庫。
- **apply 結果**: 成功更新 21 筆資料。
- **殘留檢查**: 經查詢 DB，已無 `vh_mathB1_%` 開頭的 `skill_id`。
- **B4 影響檢查**: B4 的 `vh_數學B4_%` 資料完整，未受影響。
- **邏輯驗證**: 經 `scratch/test_prefix_logic.py` 驗證，輸入「數學B1」~「數學B4」均能正確產生「vh_數學B{N}_」前綴。

## 8. 風險與注意事項
由於 B1 目前僅匯入 1-1 且尚未執行 gencode，也沒有產生先修關係與實驗記錄，因此修正成本極低。本次修正已確保未來 B1-B3 匯入時會自動遵循 B4 的命名規範。

## 9. 下一步建議
進入 **Phase 3A-2：B1 1-1 匯入品質稽核與 Agent Skill v2 規格包生成**。利用已標準化的命名規則，為 B1 1-1 建立首批 Agent Skill v2 規格包。
