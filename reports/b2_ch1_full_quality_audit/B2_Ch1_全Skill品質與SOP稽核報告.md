# B2 第 1 章「三角函數」全 Skill 品質與 SOP 稽核報告

**日期**：2026-11-22（UTC stamp `20261122_160007`）  
**範圍**：僅 B2 第 1 章；不進第 2～4 章／B1／B3／B4  
**證據目錄**：`reports/b2_ch1_full_quality_audit/`  
**自動化**：`scripts/_b2_ch1_full_quality_audit.py`（隔離 DB：`VACUUM INTO`，含 WAL）  
**停止**：本報告交付後停止，等待教師驗收。

---

## 1. 第 1 章完整 Skill 清單（DB／Curriculum／Inventory）

共 **19** 筆（含 inactive 治理項）。

| Skill | 名稱 | active | TE | Y | 掌握制 | status |
|---|---|---:|---:|---:|---|---|
| `vh_數學B2_DirectedAngle` | 有向角 | N | 0 | 0 | 舊連對 | INACTIVE_OK |
| `vh_數學B2_RatioAndRatioValue` | 比與比值 | Y | 2 | 1 | X/Y | PASS |
| `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` | 銳角三角函數 | Y | 11 | 4 | X/Y | PASS（含 P2 變化） |
| `vh_數學B2_AngleMeasurementAndConversion` | 角的度量與換算 | Y | 5 | 1 | X/Y | PASS |
| `vh_數學B2_TrigonometricValuesOfSpecialAngles` | 特別角 | Y | 5 | 2 | X/Y | PASS |
| `vh_數學B2_ArcLengthAndAreaOfSector` | 扇形弧長與面積 | Y | 8 | 2 | X/Y | PASS（含 P2） |
| `vh_數學B2_CalculatingFunctionValuesUsingCalculator` | 計算機 | Y | 2 | 1 | X/Y | PASS |
| `vh_數學B2_FundamentalTrigonometricIdentities` | 基本關係式 | Y | 10 | 3 | X/Y | PASS |
| `vh_數學B2_CoterminalAngles` | 同界角 | Y | 8 | 1 | X/Y | PASS |
| `vh_數學B2_SubSection_1_3_1` | 標準位置角 | Y | 3 | 1 | 舊連對 | NEEDS_DECISION |
| `vh_數學B2_SubSection_1_3_2` | 任意角三角函數 | Y | 3 | 1 | 舊連對 | FIXED（標籤）+ NEEDS_DECISION |
| `vh_數學B2_SubSection_1_3_4` | 象限正負 | Y | 7 | 2 | 舊連對 | NEEDS_DECISION（P2 變化） |
| `vh_數學B2_SubSection_1_3_5` | 象限角求值 | Y | 3 | 1 | 舊連對 | NEEDS_DECISION |
| `vh_數學B2_SubSection_1_3_6` | 任意角求值 | Y | 6 | 2 | 舊連對 | NEEDS_DECISION（P2） |
| `vh_數學B2_SubSection_1_3_7` | 銳角轉換 | Y | 7 | 4 | 舊連對 | NEEDS_DECISION（P2） |
| `vh_數學B2_SubSection_1_4_1` | 正弦圖形（空殼） | N | 0 | 0 | — | INACTIVE_OK |
| `vh_數學B2_SubSection_1_4_2` | 餘弦圖形（空殼） | N | 0 | 0 | — | INACTIVE_OK |
| `vh_數學B2_SubSection_1_4_3` | 正切圖形 | Y | 8 | 3 | 舊連對 | NEEDS_DECISION |
| `vh_數學B2_SubSection_1_4_4` | 圖形變化與週期 | Y | 13 | 9 | 舊連對 | NEEDS_DECISION（多題型低變化） |

具名掌握制試點：**8**；A 類可練習 SubSection：**8**；空殼 inactive：**2**（另加 DirectedAngle）。

詳細 JSON：`AUDIT_REPORT.json`／`AUDIT_REPORT.md`。

---

## 2. Source／Skill／圖形保真

| 檢查 | 結果 |
|---|---|
| TE 11583 → 扇形 `ArcLengthAndAreaOfSector` | **PASS**（live DB） |
| TE 11584 → 銳角 `TrigonometricFunctionsOfAcuteAngles` | **PASS**（live DB） |
| 11584 纜車圖頂點 B／Canvas SOP（前輪） | **PASS**（圖在繪圖區、題幹無大圖） |
| 稽核副本注意 | 不可只用 `shutil.copy2` 主檔；必須 `VACUUM INTO` 納入 WAL，否則會誤判舊 skill_id／active |

---

## 3. Generator 參數變化（每題型 seed 抽樣 30）

- 全部 active 且 Y>0 的 Runtime `problem_type`：**出題成功 30/30**（無 GENERATOR_SAMPLE_FAIL）。
- **高變化**：角度量換算、扇形 `sector_arc_and_area`、同界角等。
- **LIMITED／LOW_VARIATION_SUSPECT（P2，未本輪強改）**：
  - 銳角：`simplify_fundamental_trig_expression`、`solve_right_triangle_projection`（多為單 component 原題參數族）
  - 扇形：`compute_chord_and_arc_length`（鞦韆類）
  - `SubSection_1_4_4` 多個題型僅 1 組唯一 stem（教材保真優先，不虛構參數）
- 判定原則：合法變化少者如實標示；**不為湊數量出不合理題**。

---

## 4. 數學正確性與 Checker

| 項目 | 結果 |
|---|---|
| `SubSection_1_3_2` 答案 `3/5,-4/5,-3/4` | **PASS**（checker True） |
| `FundamentalTrigonometricIdentities` 差角多值（如 `{-1/2,1/2}`） | **PASS**（正負分支可接受；flip_check True） |
| B2 §1-3 phase3／components 測試 | **105 passed** |
| AI Tutor／OCR 全章 live | **NOT_TESTED**（本輪僅契約抽樣；不宣稱整章 Tutor PASS） |
| 響應式 390／1180 全 Skill 巡檢 | **NOT_TESTED**（僅延續 11584 SOP 證據；不全章 UI 巡檢） |

---

## 5. 題目可讀性與答案欄位（FIXED）

### Root Cause（`SubSection_1_3_2` 顯示 sin／cos／tan）

`b2_13_component_payload._selected_parts` 在組裝 multipart 時，用內部 key 覆寫已 humanize 的 `label`，留下 `display_label=$\sin\theta$` 與 `label=sin` 不一致；舊前端路徑若未優先 `display_label` 就會漏出內部 key。

### 修復

- `core/gencode/b2_13_component_payload.py`：保留 Domain 標籤／`_student_facing_part_label`；multipart 末段再 humanize
- `core/gencode/b2_12_component_payload.py`：同樣避免 key 覆寫
- `static/js/multipart_field_renderer.js`、`templates/index.html`：標籤解析優先 `display_label → math_label → label`
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §9：補強內部 key 不得當學生標示
- Flask 5001：清理多個殘留 listener 後受控單實例重啟

### 瀏覽器證據

- 重啟後 `.multi-part-row label` → `sinθ`／`cosθ`／`tanθ`（MathJax）
- 截圖：`evidence/subsection_1_3_2_labels_desktop.png`
- keys 仍為 `sin/cos/tan`（Checker／順序不變）

---

## 6. Canvas／圖片 SOP

- 正式規範維持：題幹精簡、題圖只在手寫區、不重複圖。
- TE 11584 前輪 SOP 版面修復保留；本輪未再把大圖移入題幹。
- 手機／iPad 全章：**NOT_TESTED**（不擴大巡檢）。

---

## 7. X/Y 與 SubSection 治理建議（需人工決策）

目前畫面：具名 Skill 顯示「已掌握題型 X/Y」；A 類 SubSection 顯示「連續答對：暫無門檻」（契約允許，未批次切掌握制）。

| Skill | 建議 | 理由 |
|---|---|---|
| `1_3_1`～`1_3_2`、`1_3_4`～`1_3_7` | **建議納入掌握制**（待核准） | 有 TE＋facade＋Y≥1，屬真實練習節點 |
| `1_4_3`、`1_4_4` | **建議納入掌握制**，但先處理低變化／Y 過大可讀性 | `1_4_4` Y=9 且多題型低變化，納入前需教師確認 Y 是否過關合理 |
| `1_4_1`、`1_4_2` | **維持 inactive 組織／未完成節點** | TE=0／Y=0；不得當過關目標 |
| 全部 A 類 | **禁止**把舊連對直接換算 MASTERED | §12.4／§12.8 |

---

## 8. SOP 缺漏與實際修改

| 項目 | 動作 |
|---|---|
| Multipart display label 不得被 component 組裝覆寫為內部 key | **已補** VOCATIONAL §9 |
| Skill Classification／Generator 變化／圖片 Canvas | 既有契約已涵蓋；本輪不重複長文 |
| Runtime PASS ≠ Promotion PASS | 維持既有分層；本輪未 Promotion |

---

## 9. 已修復 Bug

1. **FIXED**：`SubSection_1_3_2`（及共用 b2_12／b2_13 組裝）學生欄位顯示內部 `sin/cos/tan`
2. **先前已修復、本輪回歸 PASS**：11583／11584 Skill 歸屬；11584 Canvas SOP；空殼 1_4_1／1_4_2 inactive

## 10. 尚待人工決策／驗收

1. 8 個 A 類 SubSection 是否加入 `B2_TYPE_MASTERY_PILOT_SKILL_IDS`
2. P2 低變化題型：維持教材保真單 component，或授權擴參數族
3. 教師瀏覽器驗收：`1_3_2` 標籤、`1_4_4` 練習體感、11584 圖位
4. AI Tutor／OCR／390／iPad 全章：**NOT_TESTED**

## 11. 未做（遵守限制）

- 未改正式 DB 教材／學生掌握  
- 未重建整冊 Generator／未重匯入教材  
- 未 commit／push；未動 Flask 5000／Cloudflare  

**Flask 5001**：已清理多實例後單進程重啟（載入標籤修復）。

---

## 結案

第 1 章全 Skill 靜態＋契約抽樣完成；P0／P1 有證據項（欄位標示）已限定修復。  
**停止，等待教師驗收。不自動進入其他章節。**
