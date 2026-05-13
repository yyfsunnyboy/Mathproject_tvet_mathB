# B1 Phase 3A-1D 資料與 UI 一致性整理報告

## 1. 問題摘要
在 B1 教材匯入初期，由於 `skill_id` 前綴規則不一（`vh_mathB1_` vs `vh_數學B1_`）以及章節卡片顯示邏輯未與管理後台同步，導致系統中出現資料碎片化與 UI 顯示衝突。本輪任務已完成全量資料同步與 UI 規則統一。

## 2. B1 Chapter 1 資料盤點
| table/model | old_prefix_count vh_mathB1_* | new_prefix_count vh_數學B1_* | notes |
|---|---|---|---|
| skills_info | 0 | 10 | 已完全同步 |
| skill_curriculum | 0 | 10 | 已完全同步 |
| textbook_examples | 0 | 35 | 已完全同步 |
| 其他關聯表 | 0 | 0 | 無殘留 |

## 3. skill_id 同步修正
使用更新後的 `scripts/fix_b1_skill_id_volume_prefix.py` 執行修正：
- **Dry-run 影響筆數**: 34 筆
- **Apply 影響筆數**: 34 筆 (包含 skills_info, skill_curriculum, textbook_examples 等)
- **結果**: 成功將所有 `vh_mathB1_` 轉換為 `vh_數學B1_`，並自動處理重複 ID 合併。

## 4. SkillInfo / SkillCurriculum / TextbookExample 對應檢查
- **一致性檢查結果**: PASS
- **所有例題與課綱條目** 均已正確對應到 `vh_數學B1_` 系列技能。
- **無 Missing SkillInfo 情況**。

## 5. UI 顯示邏輯修正
- **共用 Helper**: 建立 `core/utils.py -> format_vocational_b_section_display`。
- **統一範圍**: 
    - 課程首頁 (Dashboard) 章節卡片
    - 技能管理中心 章節下拉選單
    - 例題管理中心 章節下拉選單 (經由 `_filter_sidebar.html`)
- **顯示規則**: 
    - 1-1 -> 1
    - 1-2 -> 2
    - review -> 【複習】
    - 已自動移除 Chapter 標題中的重複數字前導。

## 6. 修正前後對照
| page | before | after |
|---|---|---|
| 課程首頁 | 1 坐標系與函數 | 2 坐標系與函數 |
| 技能管理中心章下拉 | 1 坐標系與函數 | 2 坐標系與函數 |
| 例題管理中心 | vh_mathB1_LinearFunctions | vh_數學B1_LinearFunctions |

## 7. B4 影響檢查
- **B4 skill_id**: 維持 `vh_數學B4_`，未受影響。
- **B4 Dashboard**: 符合 `X-Y` 模式，自動套用新規則顯示正確編號，且標題正確。

## 8. 尚待處理
- **公式缺失**: 部分 B1 1-2 例題在匯入時標註為 `needs_review`，需在後續 Phase 進行人工核對或重新匯入。
- **Source Type**: 部分例題來源標記為 `docx`，需確認是否需要標準化。

## 9. 下一步建議
1. **繼續匯入 B1 Chapter 1 剩餘檔案**: 資料一致性已達成，可放心繼續匯入。
2. **全章完整性盤點**: 待 B1 第一章所有小節匯入完成後，生成 Agent Skill v2 規格包。

---
**核對人**: Antigravity AI
**日期**: 2026-05-13
