# B2 第 3 章題型掌握制導入報告

**日期**：2026-11-23  
**前置**：第 2 章工程封板 `PASS_ENGINEERING`（`reports/b2_ch2_quality_seal/`）  
**基準 HEAD**：`8f0ae5b3`（本輪**不 commit／不 push**；工作樹含本輪未提交變更）  
**證據**：`ch3_runtime_inventory.json`、`ch3_quality_sample.json`、`b2_ch3_type_mastery_pilot_latest.json`

---

## 1. 完整 Skill 盤點

章名：`第3章 向 量`。**無另立具名 Skill**；curriculum 共 **15** 個 SubSection，**全部 active**，皆有 TE＋facade＋Runtime Y≥1。

| Skill | 名稱 | section | TE | Y | 抽樣 |
|---|---|---|---:|---:|---|
| `3_1_1` | 向量定義 | 3-1 | 3 | 2 | PASS |
| `3_1_2` | 向量的加法作圖 | 3-1 | 3 | 1 | PASS |
| `3_1_3` | 向量的減法作圖 | 3-1 | 7 | 1 | PASS |
| `3_1_4` | 向量的實數積作圖 | 3-1 | 14 | 6 | PASS |
| `3_2_1` | 向量的坐標表示法 | 3-2 | 11 | 6 | PASS |
| `3_2_2` | 向量加減的坐標表示法 | 3-2 | 15 | 6 | PASS |
| `3_2_3` | 向量實數積的坐標表示法 | 3-2 | 2 | 2 | PASS |
| `3_2_4` | 向量實數積的基本性質 | 3-2 | 3 | 2 | PASS |
| `3_2_5` | 向量的平行 | 3-2 | 4 | 2 | PASS |
| `3_2_6` | 單位向量 | 3-2 | 5 | 2 | PASS |
| `3_3_1` | 向量的夾角 | 3-3 | 4 | 3 | PASS |
| `3_3_2` | 向量內積的定義 | 3-3 | 5 | 3 | PASS |
| `3_3_3` | 向量內積的坐標表示法 | 3-3 | 9 | 5 | PASS |
| `3_3_4` | 兩向量的垂直 | 3-3 | 4 | 2 | PASS |
| `3_3_5` | 向量內積的性質 | 3-3 | 6 | 4 | PASS |

前綴皆為 `vh_數學B2_SubSection_`。

---

## 2. 實際納入 X/Y 的 Skill

**本批 15／15 全部納入** `B2_TYPE_MASTERY_PILOT_SKILL_IDS`（沿用共用 `core/practice_type_mastery.py`，未新造 Service）。

未納入：第 4 章、inactive、B3／B4（維持連對）。

---

## 3. 各 Skill 的 Y

見上表；Y 合計 **47**（Runtime 去重 `problem_type_id`）。

---

## 4. Source／Generator／Checker／Runtime

- 每 Skill：10 seed 抽樣生成；正答／錯答 Checker 契約 `check(user, correct, question_payload=…)`。
- 結果：15 Skill **PASS_BATCH**；無 P0／P1。
- 模糊標籤：無。
- 若干 MCQ／固定模板題型列 **P2 低變化**（見 `P2_notes.md`）；數學正確，不重建 Generator。

---

## 5. 題型掌握與導航測試

| 測試 | 結果 |
|---|---|
| `scripts/test_b2_ch3_type_mastery_pilot.py` | **59/59 PASS** |
| 舊連對不換算 | PASS |
| 同型一次／答錯保留／assisted | PASS |
| 完成後同章導航（`3_1_1`→`3_1_2`） | PASS |
| 跨 Skill 共用 type 不自動計入（`simplify_vector_path_expression`） | PASS |
| 第1章回歸 `test_b2_ch1_type_mastery_pilot` | **13/13 PASS** |
| 第1章 runtime accept | **32/32 PASS** |
| 第2章 mastery pilot | **27/27 PASS** |

真人瀏覽器／iPad／Canvas／AI Tutor：**NOT_TESTED**。

---

## 6. DB 異動與備份

- **正式 DB：無 schema／資料異動**（僅程式 allowlist）。
- 測試寫入皆在隔離 `VACUUM INTO` 副本。
- 未轉換舊 `Progress.consecutive_correct` → MASTERED；未刪學生歷程。

---

## 7. 需人工決策／關注

跨 Skill 共用 `problem_type_id`（掌握仍按 `(user, skill, type)`，不自動計入）：

| problem_type_id | Skills |
|---|---|
| `simplify_vector_path_expression` | `3_1_2`, `3_1_3` |
| `solve_parallelogram_fourth_vertex` | `3_2_1`, `3_2_2` |
| `compute_vector_linear_combination` | `3_2_2`, `3_2_4` |
| `compute_cosine_of_angle_from_dot` | `3_3_1`, `3_3_3` |
| `compute_dot_product_from_magnitudes_angle` | `3_3_2`, `3_3_5` |

教學上若認為加法／減法作圖不應各自過關，可再決策是否合併或調整 Y；**本輪不強行切換、不標記 MASTERED**。

---

## 8. SOP 修改（最小）

- `core/practice_type_mastery.py`：allowlist ＋第3章 15 Skill  
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §12.8：補第3章範圍；第4章仍連對  
- `AGENTS.md`：B2 試點含第2／第3章合格 SubSection  
- 測試：`scripts/test_b2_ch3_type_mastery_pilot.py`；對齊 `test_b2_ch2_type_mastery_pilot.py` 對第1章 A 類／第4章的斷言  

未另建平行 SOP；未改數學答案檢核原則／AI Tutor Contract（無契約缺口）。

---

## 9. 待完成與下一批建議

1. 第3章代表題瀏覽器煙霧（標籤、X/Y、Canvas、390／1180）。  
2. P2 低變化題型參數擴充（非阻擋）。  
3. 共用 type 教學治理（可選）。  
4. **停止線**：不進第4章／B3／B4；驗收後再統一 Commit／Push。
