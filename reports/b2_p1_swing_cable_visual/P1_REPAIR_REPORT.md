# P1：B2 鞦韆／纜車 Skill 歸屬與圖文配對修復報告

日期：2026-11-22  
範圍：B2 第1章相關 Skill 最小修復；不重匯教材；不 commit／push；Flask 5001 已受控重啟。

## 1. Source ID

| 題 | TE ID | 教材位置 | 原始題型標籤 |
|---|---|---|---|
| 鞦韆（弦 AB＋弧 AB） | **11583** | 數學B2／第1章／1-2 銳角三角函數／1-2習題 進階題 9 | `advanced_exercise` |
| 纜車（45°／900公尺） | **11584** | 同節／1-2習題 進階題 10 | `advanced_exercise` |

PDF 權威：`textbook_import/source/vocational/math_B2/第一章 1-2 銳角三角函數-課本.pdf` page 20（page_index=19）。

## 2. 正式教材章節與 Skill 歸屬

| 題 | 教材小節（來源位置） | 數學概念（教師／Domain） | 修復後 Skill ID |
|---|---|---|---|
| 11583 | 1-2 習題（進階題9） | 扇形弦長＋弧長 | `vh_數學B2_ArcLengthAndAreaOfSector` |
| 11584 | 1-2 習題（進階題10） | 銳角直角三角投影 | `vh_數學B2_TrigonometricFunctionsOfAcuteAngles` |

說明：兩題物理上落在 1-2 習題頁，但 11583 的 Domain 操作是 `compute_chord_and_arc_length`（弧長委派 `sector_arc_and_area`），依教師指定與數學概念歸扇形 Skill；11584 為 `solve_right_triangle_projection`（45°、900m），歸銳角三角函數 Skill。

## 3. 修復前／後映射

### 修復前

| TE | Skill | problem_type_id | component | visual |
|---|---|---|---|---|
| 11583 | `TrigonometricFunctionsOfAcuteAngles` | `compute_chord_and_arc_length` | `src_11583` | 進階題9 PNG（內容實際是纜車） |
| 11584 | `TrigonometricValuesOfSpecialAngles` | `solve_right_triangle_projection` | `src_11584` | 進階題10 PNG（纜車＋熟習度自評表污染） |

### 修復後

| TE | Skill | problem_type_id | component | visual |
|---|---|---|---|---|
| 11583 | `ArcLengthAndAreaOfSector` | `compute_chord_and_arc_length` | `src_11583` | page-20 重裁鞦韆圖（bbox `[410,255,555,400]`） |
| 11584 | `TrigonometricFunctionsOfAcuteAngles` | `solve_right_triangle_projection` | `src_11584` | page-20 重裁纜車圖（bbox `[400,412,560,598]`，不含自評表） |

Checker／answer：

- 11583：`chord_length=2`，`arc_length=2*pi/3`（PASS／錯答 FAIL 已驗）
- 11584：`elevation=500+450*sqrt(2)`，`horizontal_projection=450*sqrt(2)`（PASS）

## 4. 圖文不符真正原因（多因分開）

1. **題型 Registry 錯誤（主因之一）**  
   鞦韆題被掛在 AcuteAngles；學生在 `/practice/vh_數學B2_TrigonometricFunctionsOfAcuteAngles` 會抽到扇形弦弧題。

2. **教材圖形配對錯誤（主因之二）**  
   自動 PDF crop 讓 11583／11584 使用**同一起點 bbox**（`429.91,418.70,...`），進階題9 檔案內容其實是纜車圖；進階題10 又吃進「熟習度自評表」。  
   → 即使只修 Skill，若不重裁，鞦韆題仍會配錯圖。

3. **前端 Canvas 殘留**  
   非本例主因（單題首載即錯圖）。但仍存在切題非同步載入競態風險。

4. **非同步載入競態（次要防護）**  
   `applyQuestionScratchpadBackground` 已加 `question_uid` guard，避免舊圖覆蓋新題。

## 5. 修改檔案與 DB 影響

### 程式／資產

- `core/gencode/b2_12_component_specs.py`（skill_id remap）
- `agent_skills_v3/vh_數學B2_*`：搬移 `src_11583`／`src_11584`；更新 `__init__.py`、`component_manifest.json`
- `skills/vh_數學B2_TrigonometricFunctionsOfAcuteAngles.py` 等三個 facade
- `static/question_assets/.../進階題9|10_vocation_fig1.png`（重裁；舊檔 `.bak_*`）
- `templates/adaptive_practice_v2.html`（切題圖片 uid 防護）
- `docs/VOCATIONAL_PRACTICE_RUNTIME_CONTRACT.md` §11 第6點
- `docs/系統SOP/Gencode_AgentSkillV3整合/KnownIssues_TechnicalDebt.md`（個案紀錄）
- `scripts/repair_b2_p1_swing_cable_mapping.py`、`scripts/test_b2_p1_swing_cable_repair.py`

### DB

- 備份：`instance/backups/kumon_math_pre_b2_p1_swing_cable_20261122_110812.db`
- `textbook_examples.id IN (11583,11584)`：更新 `skill_id` + `notes.image_assets`
- **未刪除／未搬移** `student_problem_type_mastery`（目前 Acute 無 `compute_chord_and_arc_length` 孤兒列）

## 6. 題型分母／Mastery／導航

| Skill | 修復後 Y（usable types） |
|---|---|
| AcuteAngles | **4**：right / constraints / simplify / projection |
| SpecialAngles | **2**：exact special / projection（仍保留 11560／11570） |
| ArcLength | **2**：sector_arc_and_area + compute_chord_and_arc_length |

回歸：

- `scripts/test_b2_p1_swing_cable_repair.py` → **ALL_PASS**
- `scripts/test_b2_ch1_type_mastery_pilot.py` → **10/10 PASS**（Acute 顯示 0/4）
- `scripts/test_b2_ch2_type_mastery_pilot.py` → **27/27 PASS**（前次已跑）

相容性：不遷移 mastery；若未來出現 Acute 對 `compute_chord_and_arc_length` 的舊 MASTERED，只會成為非 usable 孤兒列，不計入 X，也不刪除。

## 7. Runtime 實際驗證

- 直接呼叫 component generate／facade sampling：Acute 40 seeds **無鞦韆**；可見纜車；Sector 出鞦韆且 visual 指向進階題9。
- Checker True／錯答 False。
- Flask **5001** 已受控重啟載入新程式；HTTP `/get_next_question` 需登入（401），未做瀏覽器登入巡檢。
- 未動 Flask 5000／Cloudflare。

## 8. 是否需補充 SOP

- **不新建平行 SOP。**
- 已在既有 `VOCATIONAL` §11 補第6點：Skill 歸屬與圖文配對必須分開判定。
- 已在 `KnownIssues_TechnicalDebt.md` 登錄本個案；通用 auto-gate 仍未覆蓋全冊（IMPLEMENTATION_GAP 維持）。

## 停止條件

本輪僅處理發現的 B2 鞦韆／纜車相關 Skill 與必要共用元件；不自動進入 B2 第3章或 B3／B4。
