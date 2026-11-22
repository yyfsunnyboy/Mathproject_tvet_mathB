# B2 第二階段報告：第1章驗收、Registry 補缺、第2章掌握制導入

**日期**：2026-11-22  
**基準**：`d139243e`（本輪**不 commit／不 push**）  
**停止線**：本批完成即停；不進 B3／B4；不改 B1 Generator

---

## 1. B2 第1章試點驗收

代表 Skill（隔離 DB Runtime）：

| Skill | Y | 結果 |
|---|---|---|
| `vh_數學B2_RatioAndRatioValue` | 1 | PASS |
| `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` | 4 | PASS |
| `vh_數學B2_FundamentalTrigonometricIdentities` | 3 | PASS |

自動化：`scripts/test_b2_phase2_ch1_runtime_accept.py` → **27/27 PASS**  
（同型不重複、答錯保留、AI 後需獨立、導航同章、自由複習保留掌握、學生隔離、MsgBox markup）

| 項目 | 狀態 |
|---|---|
| 真人瀏覽器／iPad UI | **NOT_TESTED** |
| Multipart 正式 submit 畫面 | **NOT_TESTED**（本批代表題型未強制 multipart live） |

另：`test_b2_ch1_type_mastery_pilot.py` **10/10 PASS**（更新後仍涵蓋第1章具名 8 個）。

---

## 2. `SubSection_1_4_1`／`1_4_2` 根因與修復

| 項目 | 證據 |
|---|---|
| 名稱 | 正弦／餘弦函數的圖形與其週期現象的表徵 |
| TE | **0** |
| facade / v3 package | **無** |
| usable Y | **0** |
| 判定 | **尚未完成 Generator 的 active 空殼**（非接線遺漏；不可虛構 Source／假 facade） |

**安全修復**：`skills_info.is_active=False`（保留 curriculum／不刪歷史）。  
腳本：`scripts/_b2_deactivate_empty_1_4_shells.py`  
證據：`b2_deactivate_1_4_shells_20261122_025548.json`  
備份：`instance/backups/kumon_math_pre_b2_phase2_20261122_105325.db`

若日後要恢復為練習 Skill，需完整 Source → Domain Evidence → Generator → Gate，**非本輪範圍**。

---

## 3. 第1章 SubSection 分類

| 類別 | Skill | 說明 |
|---|---|---|
| **A 實際練習** | `1_3_1`、`1_3_2`、`1_3_4`～`1_3_7`、`1_4_3`、`1_4_4`（8） | 有 TE＋facade＋Y≥1 |
| **B 空殼／未完成** | `1_4_1`、`1_4_2`（已 inactive） | 無 TE／facade／Y |

**人工決策（未自動納入掌握制）**：第1章 A 類 SubSection 是否併入 `B2_TYPE_MASTERY_PILOT_SKILL_IDS`。  
本輪維持 Phase-1 行為：第1章僅具名 8 個啟用掌握制，避免改變已驗收試點範圍。

---

## 4. 第2章導入清單與 Y

第2章**無另立具名 Skill**；合格練習節點皆為 SubSection。

| Skill | 名稱 | Runtime Y |
|---|---|---|
| `vh_數學B2_SubSection_2_1_1` | 正弦定理 | **6** |
| `vh_數學B2_SubSection_2_1_2` | 餘弦定理 | **5** |
| `vh_數學B2_SubSection_2_2_3` | 直角三角形的測量 | **10** |
| `vh_數學B2_SubSection_2_2_4` | 非直角三角形測量 | **2** |
| `vh_數學B2_SubSection_2_2_5` | 簡單的立體測量 | **3** |

未導入：`2_2_1`／`2_2_2`（inactive、無 Runtime）→ 維持原狀／連對不適用。  
第3章起：未加入 allowlist → 仍連對。

測試：`scripts/test_b2_ch2_type_mastery_pilot.py` → **27/27 PASS**  
（舊連對不換算、同型一次、答錯保留、AI 阻擋、同章導航至餘弦定理）

---

## 5. 修改檔案

- `core/practice_type_mastery.py`（allowlist 擴第2章）
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §12.8
- `AGENTS.md`
- `scripts/test_b2_phase2_ch1_runtime_accept.py`
- `scripts/test_b2_ch2_type_mastery_pilot.py`
- `scripts/test_b2_ch1_type_mastery_pilot.py`（對齊新 allowlist）
- `scripts/_b2_deactivate_empty_1_4_shells.py`
- 報告／probe JSON（`b2_phase2_*`、`b2_ch2_*`、deactivate 證據）
- DB：僅 `skills_info.is_active` 兩列（有備份）

---

## 6. 回歸總表

| 測試 | 結果 |
|---|---|
| B2 ch1 runtime accept | **27/27 PASS** |
| B2 ch1 pilot script | **10/10 PASS** |
| B2 ch2 mastery pilot | **27/27 PASS** |
| B1 type mastery | **15/15 PASS** |
| B1 nav skip | **14/14 PASS** |
| ordered-named-values checker | **31 PASS** |
| 真人瀏覽器／iPad | **NOT_TESTED** |
| Multipart live submit（B2） | **NOT_TESTED** |

---

## 7. DB 備份與完整性

- 備份：`instance/backups/kumon_math_pre_b2_phase2_20261122_105325.db`
- 變更：兩空殼 → inactive；**未刪**作答／錯題／`student_problem_type_mastery`
- 停用後確認：`1_4_1`／`1_4_2` `active=False`；掌握列仍存在

---

## 8. 待人工驗收／治理

1. 真人瀏覽器驗證 B2 第1／2章 X/Y、MsgBox、導航。  
2. 第1章 A 類 SubSection 是否納入掌握制。  
3. `1_4_1`／`1_4_2` 是否未來要正式建 Generator（需 Source Evidence）。  
4. Stage 1 B2 教材 provenance／SHA-256。

## 9. 下一批建議

- 第3章向量：盤點 usable Y → 限定 allowlist。  
- 第1章 SubSection 掌握制決策後一次導入。  
- `1_4_1`／`1_4_2` 僅在有教材來源與 Domain 時開工。  
- **不自動進 B3／B4。**
