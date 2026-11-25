# B2 第 3 章全 Skill 工程封板報告

**日期**：2026-11-23  
**基準 HEAD（階段 A 後）**：`dc21df72`  
**審計**：`scripts/_b2_ch3_full_quality_audit.py` → `AUDIT_REPORT.json`（stamp `20261123_134714`）  
**結論**：**PASS_ENGINEERING**  
**本階段 B 產物：先不 Commit／Push**（待教師驗收）

非宣稱：真人瀏覽器／iPad／Canvas 佈局／AI Tutor／Domain Evidence／Promotion Gate 全部通過。

---

## 1. 15 Skill 稽核表

章名：`第3章 向 量`；無另立具名 Skill；15 SubSection 皆 active、皆在掌握制 allowlist。

| Skill | 名稱 | TE | Y | Generator／Checker | 掌握 | status |
|---|---|---:|---:|---|---|---|
| `3_1_1` | 向量定義 | 3 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_1_2` | 向量的加法作圖 | 3 | 1 | SAMPLED／PASS | X/Y | PASS |
| `3_1_3` | 向量的減法作圖 | 7 | 1 | SAMPLED／PASS | X/Y | PASS |
| `3_1_4` | 向量的實數積作圖 | 14 | 6 | SAMPLED／PASS | X/Y | PASS |
| `3_2_1` | 向量的坐標表示法 | 11 | 6 | SAMPLED／PASS | X/Y | PASS |
| `3_2_2` | 向量加減的坐標表示法 | 15 | 6 | SAMPLED／PASS | X/Y | PASS |
| `3_2_3` | 向量實數積的坐標表示法 | 2 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_2_4` | 向量實數積的基本性質 | 3 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_2_5` | 向量的平行 | 4 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_2_6` | 單位向量 | 5 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_3_1` | 向量的夾角 | 4 | 3 | SAMPLED／PASS | X/Y | PASS |
| `3_3_2` | 向量內積的定義 | 5 | 3 | SAMPLED／PASS | X/Y | PASS |
| `3_3_3` | 向量內積的坐標表示法 | 9 | 5 | SAMPLED／PASS | X/Y | PASS |
| `3_3_4` | 兩向量的垂直 | 4 | 2 | SAMPLED／PASS | X/Y | PASS |
| `3_3_5` | 向量內積的性質 | 6 | 4 | SAMPLED／PASS | X/Y | PASS |

前綴：`vh_數學B2_SubSection_`。

---

## 2. TE／Y／Generator／Checker

| 指標 | 值 |
|---|---|
| Skill 數 | 15（皆 active） |
| TE 總數 | 95 |
| **Y 合計（各 Skill 加總，非去重）** | **47** |
| 全章去重 `problem_type_id` | **42** |
| 抽樣 | 每型 10 seed；LIMITED 擴至 30 |
| 生成失敗 | 0 |
| Checker 正答 PASS／錯答 FAIL | 全部 PASS |
| 簡易等價變體拒收 | 0（本輪測得） |
| 模糊 display_label | 0 |
| payload `skill_id` 錯掛 | 0 |

---

## 3. 參數變化統計（摘要）

- 多數題型 `HAS_VARIATION`（stems／params 足夠）。
- **12** 題型擴至 30 seed 後仍 `LIMITED_VARIATION`（題幹模板固定、參數仍有變化）→ **P2**，見 `P2_notes.md`。
- 未出現「僅 question_uid 不同」的假變化判定為通過條件。

---

## 4. 數學正確性／多解

- 隔離抽樣下無 Generator 崩潰、無 Checker 正／錯顛倒。
- 未做真人逐題「教學級多解／無解」深度驗收 → 深度項 **NOT_TESTED**。
- 未發現需 P0／P1 修復的數學契約錯誤。

---

## 5. 圖文與 Skill 歸屬

- 抽樣 payload 未出現跨 Skill `skill_id` 錯掛。
- 部分題型帶 `visual_spec`／圖；部分純坐標題無圖（合理）。
- 瀏覽器圖文配對、Canvas 大圖位置、crop 保真：**NOT_TESTED**。

跨 Skill 共用 type（掌握仍 `(user, skill, type)`，不自動計入；腳本已回歸）：

| type | Skills |
|---|---|
| `simplify_vector_path_expression` | `3_1_2`, `3_1_3` |
| `solve_parallelogram_fourth_vertex` | `3_2_1`, `3_2_2` |
| `compute_vector_linear_combination` | `3_2_2`, `3_2_4` |
| `compute_cosine_of_angle_from_dot` | `3_3_1`, `3_3_3` |
| `compute_dot_product_from_magnitudes_angle` | `3_3_2`, `3_3_5` |

---

## 6. 學生端標籤／MathJax／Canvas

| 項目 | 狀態 |
|---|---|
| display_label 抽樣（無 sum／sin／小題1…） | PASS（自動化） |
| MathJax 根號橫線／分數 DOM | **NOT_TESTED** |
| 桌面／1180×820／390 版面 | **NOT_TESTED** |
| 大圖僅在繪圖區 | **NOT_TESTED** |

---

## 7. Mastery／MsgBox／導航

| 測試 | 結果 |
|---|---|
| `test_b2_ch3_type_mastery_pilot.py` | **59/59 PASS**（稽核後再跑） |
| 舊連對不換算／同型一次／assisted／跨 type 不計入 | PASS |
| 同章導航 | PASS |

MsgBox 真人點擊、跨 Session 瀏覽器：**NOT_TESTED**（契約與自動化覆蓋）。

---

## 8. 已修復 P0／P1

**無。** 本輪未改 Generator／Checker／正式 DB。

---

## 9. 保留 P2 與人工待驗收

見 `P2_notes.md`（12 個 LIMITED 題型）。  
人工：瀏覽器標籤、Canvas、響應式、AI Tutor／OCR。

---

## 10. SOP 修改（階段 B）

**無新增。** 沿用已提交的 §12.8／`AGENTS.md`／共用掌握制；未建平行 SOP。

---

## 11. 最終結論

**B2 第 3 章工程封板：PASS_ENGINEERING。**

- 正式 DB：未異動。  
- Flask 5000／Cloudflare／5001：未動。  
- 停止線：不進第 4 章／B3／B4；階段 B 產物待驗收後再提交。
