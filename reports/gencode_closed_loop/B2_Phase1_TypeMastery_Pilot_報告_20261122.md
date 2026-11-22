# B2 第一批：第1章具名 Skill 題型掌握試點

**日期**：2026-11-22  
**停止線**：本批完成即停；不進 B3／B4；不重建整冊 Generator／不重匯教材

## 盤點口徑（核對既有報告）

| 項目 | 數值 |
|---|---|
| Skills | 48（active 44／inactive 4） |
| textbook_examples | 321 |
| facade / v3 package | 42／42 |
| 接線缺口 | active 缺 facade／TE／v3：`SubSection_1_4_1`、`SubSection_1_4_2` |

## 試點範圍

`B2_TYPE_MASTERY_PILOT_SKILL_IDS`（第1章具名，不含 SubSection），共 8 個；各自 Runtime Y≥1。

導入：X/Y 掌握、完成 MsgBox、同章導航（沿用 §12 共用實作）。  
**不**把 `consecutive_correct` 換算為 MASTERED。  
其餘 B2（含 SubSection、第2～4章）維持連對語意。

## 測試

- `scripts/test_b2_ch1_type_mastery_pilot.py`：**10/10 PASS**
- B1 共用掌握腳本：15/15 PASS
- 有序多值 checker：31 PASS

## 下一批建議

1. 補 `SubSection_1_4_1/1_4_2` 接線或標 inactive（治理）。  
2. 第1章 SubSection 是否納入掌握制（需額外驗收）。  
3. 第2章具名／應用單元試點。  
4. Stage 1 B2 教材 provenance／SHA-256 封板核對。  
5. B1／B2 真人瀏覽器與 iPad 驗收。
