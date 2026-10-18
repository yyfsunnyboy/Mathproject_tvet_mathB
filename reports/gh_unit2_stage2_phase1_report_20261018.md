# 普高數學1 Unit 2 — Gencode V3 Stage 2 Phase 1 報告（2026-10-18）

範圍：Stage 1 封板後的 28 題（8/6/14）。未重新匯入、未改 skill mapping、未寫正式 DB tracker / published 元件、
未 promotion revision_0002、未 publish、未重啟 5000/5001、未 commit/push。所有持久化驗證只在 DB 複本與 sandbox 進行。

## 1. 28 題 V3 對應矩陣

狀態定義：REUSE＝舊 spec（variant 0＋sampler）仍符合新題；MODIFY＝同 operation 同結構、variant 0 改值；
REBUILD＝同 operation、結構改變需新 sampler；NEW＝無舊元件、既有 operation 可支援；
GROWTH＝需 Capability Growth；DEFERRED＝不可完整判分（數線作圖）。
「呈現差異」只記數學等價但寫法不同者（值與答案皆已核對）。

| id | 題目 | 新 skill | tracker skill（現況） | operation（problem_type） | family | 狀態 | 新 generator | 特殊作答 / 呈現差異 |
|---|---|---|---|---|---|---|---|---|
| 1027 | 例題1 | POINT | POINT | evaluate_number_line_division_points | number_line_division_points | MODIFY | 否（sampler 改內外同比） | 內分寫 AP:PB（課本 AP:BP） |
| 1028 | 隨堂練習1 | POINT | POINT | evaluate_number_line_division_points | number_line_division_points | MODIFY | 否 | 寫 AP=2PB（課本 AP=2BP） |
| 1029 | 例題2 | POINT | （無） | — | number_line_weighted_point_order | DEFERRED | — | (1) 數線作圖；(2) 三數排序 |
| 12323 | 隨堂練習2 | POINT | （無） | — | number_line_weighted_point_order | DEFERRED | — | 同例題2 |
| 1038 | 觀念澄清1 | POINT | **INEQ** | evaluate_absolute_value_statements | abs_concept_statement | GROWTH | 是 | 符號點 A(a) 距離 \|a+4\|；op 未綁 POINT |
| 1039 | 觀念澄清2 | POINT | **INEQ** | evaluate_absolute_value_statements | abs_concept_statement | MODIFY（綁定缺口） | 否 | ○/×；答案由 ○ 變 × |
| 1041 | 基礎題1 | POINT | **INEQ** | evaluate_number_line_division_points | number_line_division_points | MODIFY | 否 | 內分寫 AP:PB |
| 1042 | 基礎題2 | POINT | **INEQ** | select_extreme_weighted_point | weighted_point_comparison | MODIFY（綁定缺口） | 否（sampler 改同分母） | 選項標籤 A–D（課本 (1)–(4)，checker 兩者皆收） |
| 1030 | 例題3 | EQ | EQ | solve_absolute_value_equations | linear_abs_equation | REUSE | 否 | — |
| 1031 | 隨堂練習3 | EQ | EQ | solve_absolute_value_equations | linear_abs_equation | MODIFY | 否 | — |
| 1032 | 例題4 | EQ | EQ | solve_absolute_value_equations | piecewise_abs_equation | REUSE | 否 | — |
| 12327 | 隨堂練習4 | EQ | （無） | solve_absolute_value_equations | piecewise_abs_equation | GROWTH | 是 | 「=0」無法逐字呈現（見 §5） |
| 1043 | 基礎題3 | EQ | **INEQ** | solve_absolute_value_equations | linear_abs_equation | MODIFY | 否 | — |
| 1047 | 進階題7 | EQ | **INEQ** | solve_absolute_value_equations | piecewise_abs_equation | REUSE（需 rebind） | 否 | — |
| 1033 | 例題5 | INEQ | INEQ | solve_absolute_value_inequalities | linear_abs_inequality | REUSE | 否 | — |
| 1034 | 隨堂練習5 | INEQ | INEQ | solve_absolute_value_inequalities | linear_abs_inequality | MODIFY | 否（sampler 改 ≥） | — |
| 1035 | 例題6 | INEQ | INEQ | solve_absolute_value_inequalities | compound_abs_inequality | MODIFY | 否（sampler 改 ≤） | 聯立以「且」呈現（課本大括號） |
| 12331 | 隨堂練習6 | INEQ | （無） | solve_absolute_value_inequalities | compound_abs_inequality | NEW | 是（sampler） | 聯立以「且」呈現 |
| 1036 | 例題7 | INEQ | INEQ | solve_absolute_value_inequalities | piecewise_abs_inequality | REUSE | 否 | — |
| 12332 | 隨堂練習7 | INEQ | （無） | solve_absolute_value_inequalities | piecewise_abs_inequality | NEW | 是（sampler） | — |
| 1037 | 例題8 | INEQ | INEQ | recover_absolute_value_parameters | abs_parameter_recovery | REUSE | 否 | 需 revision_0002 adapter（inline math） |
| 12333 | 隨堂練習8 | INEQ | （無） | recover_absolute_value_parameters | abs_parameter_recovery | GROWTH | 是 | 算術小題＋新 prompt |
| 1040 | 觀念澄清3 | INEQ | INEQ | evaluate_absolute_value_statements | abs_concept_statement | MODIFY | 否 | ○/× |
| 1044 | 基礎題4 | INEQ | INEQ | solve_absolute_value_inequalities | linear_abs_inequality | MODIFY | 否（sampler 改 ≤） | — |
| 1045 | 基礎題5 | INEQ | INEQ | solve_absolute_value_inequalities | compound_abs_inequality | REBUILD | 是（sampler） | 聯立以「且」呈現 |
| 1046 | 基礎題6 | INEQ | INEQ | recover_absolute_value_parameters | abs_parameter_recovery | REUSE | 否 | — |
| 1048 | 進階題8 | INEQ | INEQ | recover_absolute_value_parameters | abs_parameter_recovery | MODIFY | 否 | — |
| 1049 | 進階題9 | INEQ | INEQ | recover_absolute_value_parameters | abs_parameter_recovery | REBUILD | 是（sampler） | 參數改為兩個上界 a、b |

capability 一律為 `algebra.absolute_value_relations`（promoted-2e84b9cc07e4）。逐題 variant 0、變更說明、sampler：`tmp/gh_unit2/sources_v3.py`。

新題 variant 0 答案（人工推導，並經獨立 oracle 與 domain 交叉核對）：
- 例1 5、−25；隨1 0、−9；基1 7、8、−16；隨3 −4,−2 / −2,4 / −1,1/3；基3 −4,6 / −7/3,−1
- 隨5 (−∞,−3]∪[−1,∞) / [−2,6] / (−∞,−1)∪(1/3,∞)；例6 (1,2) / (−2,0]∪[1,3)；隨6 [−3,2) / (−1/2,1)∪(2,7/2)
- 隨7 (−∞,3]；基4 [2,8] / (−∞,−7)∪(3,∞) / [−1,6]；基5 (4,5) / (−1,0]∪[4/3,7/3)
- 進8 a=6、b=10；進9 a=2、b=7（暴力搜尋確認唯一）；觀2 ×；觀3 ○；基2 (4)
- 隨4 x=3；隨8 70、a=70、b=7（以上兩題為 GROWTH，僅作數學核對）

## 2–5. 數量統計

| 類別 | 題數 | 題目 |
|---|---|---|
| 舊元件可沿用（spec 不變） | **7** | 1030, 1032, 1033, 1036, 1037, 1046, 1047 |
| 舊元件需修改 | **14** | MODIFY 12：1027, 1028, 1031, 1034, 1035, 1039, 1040, 1041, 1042, 1043, 1044, 1048；REBUILD 2：1045, 1049 |
| 舊元件不可沿用 | 1 | 1038（GROWTH） |
| 新增元件 | **4** | 現可建 2：12331, 12332；需 GROWTH 2：12327, 12333 |
| DEFERRED | **2** | 1029, 12323 |

合計 7+14+1+4+2＝28；舊 22 題＝7+14+1。

「可沿用」只表示來源 spec 仍正確，不代表舊元件可直接上線，原因有三：
1. 舊 tracker 的 22 筆皆以舊內容 `verified`，見 §8。
2. 1037 等元件需搭配 revision_0002 adapter。
3. 1047 需改綁 EQ。

**DEFERRED 原因：**
- 例題2（1029）與隨堂練習2（12323）的 (1) 都是「在右圖標出 P、Q、R」：數線作圖沒有任何已註冊的 checker 能判分。
- 兩題的 (2) 是三個加權點排序：現有 operation 只能選出單一極值，沒有排序作答型別。

Phase 1 rule pack 以 `requires_human_action / runtime_candidate=false` 將兩題標為 BLOCKED（intentional skip，不阻擋 READY）。若教師同意只出 (2)，需新增排序 operation（Growth），屬 Phase 2 決策。

## 6. Phase 1 分類器缺口與修復

**缺口（正式 DB、現行規則，唯讀 preflight）：**
- 例題與隨堂練習 14 題回報 `phase1_classifier_not_available`。原因是三個 gh skill 都沒有 rule pack 或 Python classifier。
- 習題 14 題被 `explicit_problem_type_metadata` 以 `basic_exercise / chapter_exercise / advanced_exercise` 判為「可解析」。這三個是**章節標籤而非數學題型，屬偽陽性**。
- 三個 skill 全為 NEEDS_CAPABILITY，但原因並不正確。

**修復（沿用既有註冊機制，未降低任何 gate）：**

1. 規則包草稿（官方 draft 目錄，經官方 `register_classifier_rulepack_from_draft` 流程）：
   - `reports/gencode_closed_loop/classifier_drafts/gh_PointDivisionFormulaOnNumberLine_classifier.yaml`
   - `reports/gencode_closed_loop/classifier_drafts/gh_LinearEquationsWithAbsoluteValue_classifier.yaml`
   - `reports/gencode_closed_loop/classifier_drafts/gh_LinearInequalitiesWithAbsoluteValue_classifier.yaml`

   每題都以 `source_examples` 明確對應到 domain operation：
   - DEFERRED 題標為 BLOCKED。
   - GROWTH 題標為 `needs_capability`。

   產生器為 `tmp/gh_unit2/build_rulepack_drafts.py`，資料來源是 Stage 1 skill map 與 `sources_v3`。**尚未寫入正式 `configs/gencode/classifiers/phase1_rule_packs.yaml`**，只註冊進 sandbox 複本 `tmp/gh_unit2/sandbox_phase1_rule_packs.yaml`。

2. `core/gencode/pipeline_orchestrator.py`（+38 行，只加嚴）：
   - rule pack 的 `source_examples[].needs_capability` 會回傳 `unresolved`。分類來源為 `phase1_rule_pack_needs_capability`，reason 為 `NEEDS_CAPABILITY:…`，disposition 是 needs_capability，**不是 skip**。
   - 新增 `_rulepack_operation_binding_gap`：若 rule pack 解析出的題型是該 skill 固定 domain 的 operation，但不在該 skill 的 `allowed_operations`，則判為 `NEEDS_CAPABILITY:domain_operation_not_bound_to_skill:<op>`。
     - 修補前，preflight 會顯示「可解析」，但建置時才被 `domain_operation_not_allowed` 擋下。
     - 對現有 47 個正式 rule pack 的 178 個題型逐一檢查，**0 個受影響**。

3. 測試：
   - 新增 `tests/gencode/test_phase1_rulepack_capability_gap.py`（6 項）。
   - `tests/gencode` 全套：修補前 90 failed / 2428 passed；修補後 86 failed / 2432 passed。新增失敗 0；差異只來自新測試。其餘 86 個失敗為既有問題，與本次無關。

## 7. NEEDS_CAPABILITY 是否已能經正式 preflight 解決

**分類器缺口已解決，但三個技能仍是 NEEDS_CAPABILITY，而且這次原因是真實的。** 下表為 DB 複本加 sandbox 規則包的官方 `evaluate_skill_v3_capability` 結果：

| skill | 修復前 | 修復後 | 可解析 | skip | 仍缺 capability |
|---|---|---|---|---|---|
| POINT | needs_capability（not_available ×4，偽陽性 ×4） | needs_capability | 3（1027, 1028, 1041） | 2（1029, 12323） | 1038 Growth；1039、1042 綁定缺口 |
| EQ | needs_capability（not_available ×4，偽陽性 ×2） | needs_capability | 5 | 0 | 12327 Growth |
| INEQ | needs_capability（not_available ×8，偽陽性 ×6） | needs_capability | 13 | 0 | 12333 Growth |

要轉為 READY，需要經人工核准的 revision_0003，見 §9。依指示，未把任何狀態直接改成 PASS。

**順序限制（重要）：**
- 5000/5001 以 `--no-reload` 執行，所以 orchestrator 修補要重啟後才生效；本輪未重啟。
- 若在舊程式執行中就把規則包註冊進正式 YAML（YAML 依 mtime 即時生效），舊程式會忽略 `needs_capability` 標記，造成 1038、12327、12333 偽 READY。
- 因此正式註冊必須排在重啟之後。

## 8. tracker 錯綁影響分析

**現況：**
- 22 筆 tracker 皆為 `verified`，內容是舊題。
- 其中 6 筆 skill 與新 row 不符：1038、1039、1041、1042 應改綁 POINT；1043、1047 應改綁 EQ。
- 三個 skill 都**沒有 production package**（`agent_skills_v3/gh_*` 不存在），所以沒有已 publish 的元件會受影響。

| 改綁 | operation | 目標 skill 是否允許 | 結論 |
|---|---|---|---|
| 1041 → POINT | division | 允許 | 可改綁，但需以新值重建 |
| 1043、1047 → EQ | equations | 允許 | 可改綁；1043 需以新值重建 |
| 1039 → POINT | statements | **不允許**（POINT 只允許 division） | 需 revision_0003 擴充 POINT 的 `skill_bindings` |
| 1042 → POINT | extreme | **不允許** | 同上 |
| 1038 → POINT | statements（新 kind） | **不允許** | Growth 加綁定 |

`skill_bindings` 位於 human-approved promotion store（`configs/gencode_promoted_capabilities.json`）。build 時由 `skill_fixed_domain_authority` 強制檢查，不能用改 tracker 的方式繞過。

INEQ 目前仍允許全部 6 個 operation，但新 row 已不再需要 division、equations、extreme。建議在 revision_0003 一併收窄，避免跨 skill 的錯誤綁定。

**已確認的建置風險：**
- `admin_gencode_action_service.run_admin_v3_dryrun_for_skill` 在 auto 模式下，只要 `tracker_status == "verified"` 就跳過重建（約第 429–431 行）。它不比對 source_hash，也不比對 tracker 的 skill。
- 若以 auto 模式跑官方建置，會沿用舊題舊值的元件，例如 1034、1035、1040、1044、1045、1048、1049、1041、1043。
- 舊 tracker 的 `induced_spec` 因 source_hash 改變而不可重用，所以官方路徑目前也無法帶入課本衍生的 variants。若不處理，元件會改用 domain 的 seeded 預設值，失去 variant 0 對課本的忠實度。

**建議：**
- 改綁一律透過「以新 skill 重新產生」完成；不用 SQL UPDATE，也不刪除舊列。
- 先在 DB 複本執行，以 regenerate/force 模式重建。
- 正式 DB 的 tracker 調整另行授權。

## 驗證結果（每個可支援題型）

`tmp/gh_unit2/test_unit2_v3_phase1.py`：以 revision_0002 進行隔離的 temp-store promotion，正式 store 與 package root 經檢查未變。
- Python 3.11.15：**99 passed**
- Python 3.14.6：**99 passed**

| 驗證項 | 內容 |
|---|---|
| 1. generator sampling | 21 題可建項目各取樣到 100 個以內的 variant（1037、1046 情境受限各 9 個；12332 為 72 個），全數經 domain validator 驗證，且具決定性 |
| 2. 獨立數學 oracle | 自寫有理數分段求根與區間成員檢查，不呼叫 domain solver；所有 variant 0 與全部取樣 variant 皆一致；進9、進8、例8、基6 另以暴力搜尋確認參數唯一 |
| 3. 正確答案接受 | 19 組等價寫法，例如 `x\le 3`、`-2<x\le 0 或 1\le x<3`、`-\frac{7}{3}, -1`、`36.5`、`D`／`4` |
| 4. 錯誤答案拒絕 | 22 組，含漏解、多解、正負號錯、參數對調、○× 相反、錯選項 |
| 5. 邊界 | 端點開閉對調皆被拒絕：例6 0 與 1 為閉、隨6 −3 閉而 2 開、隨7 3 閉、隨5、基4、基5 |
| 6. LaTeX | 所有 question_text 的 `$` 成對、`\left`/`\right` 與大括號平衡，數學外沒有裸 LaTeX，也沒有 `\(` |
| 7. Python 3.11 | 通過，3.14 也通過 |
| 8. 學生 runtime 契約 | `validate_answer_contract_capability == ok`、`validate_answer_contract_consistency == []`、`check_answer(self)` 為真 |

**已知 checker 格式限制**（已記錄為測試，未修改共用 checker）：
- `rational_checker` 不接受帶變數前綴的數值答案，例如 `x=5`、`y=-25`、`\overline{AB}=7`，只接受裸數值或分數／小數。
- 解集合與不等式 checker 能接受 `x=… 或 x=…`、區間與不等式兩種寫法。

## 9. Phase 2–4 最低工作清單

**Phase 2：能力與設定（需人工核准）**
1. 教師審閱三份規則包草稿與 §1 矩陣。
2. 先重啟（另行授權）讓 orchestrator 修補生效，**之後**才以 `register_classifier_rulepack_from_draft(skill, confirm=True)` 正式註冊。
3. 建立 revision_0003，以 revision_0002 為基礎，包含：
   - `skill_bindings`：POINT 增加 `evaluate_absolute_value_statements`、`select_extreme_weighted_point`；建議收窄 INEQ。
   - statements 新 kind：符號點距離（1038）。
   - equations：允許零常數側（12327 的「=0」）；或由教師同意改用等價式 |x+3|=2x 呈現。
   - recovery：新 prompt `standard_weight`，加上算術小題的複合 payload（12333）；或拆成兩個元件，由教師決定。
   - adapter 呈現：內分比可寫成 AP:BP／AP=2BP；以「且」連接的聯立不等式改用大括號（cases）呈現。
4. 決定 DEFERRED 兩題是否只出 (2)；若要出，需新增排序 operation。

**Phase 3：建置（DB 複本加 staging）**

5. 以 regenerate/force 模式建置，不使用 auto 模式（避免沿用舊 verified 元件）。用正式路徑把 `sources_v3` 的 variants 帶入 `generation_constraints`：沿用 formal_regen 的 `v3_induced_spec` 方式，或補一個官方的 carrier。
6. 以新 skill 重新產生 1038、1039、1041、1042（POINT）與 1043、1047（EQ）；新增 12327、12331、12332、12333 的 tracker；1029、12323 記為 intentional skip。

**Phase 4：驗證與發布閘門**

7. 對產出元件重跑 `test_unit2_v3_phase1` 的同等檢查（元件層 smoke，py3.11/3.14），並在 staging 以瀏覽器目視檢查 MathJax 與選項按鈕。
8. 正式 tracker 調整、promotion revision_0002/0003、publish 皆需另行明確授權。

## 本輪異動檔案

- 修改：`core/gencode/pipeline_orchestrator.py`（Phase 1 rule pack 的 needs_capability 標記與 operation 綁定檢查）。
- 新增：
  - `tests/gencode/test_phase1_rulepack_capability_gap.py`
  - 本報告
  - 三份 classifier 草稿（`reports/gencode_closed_loop/classifier_drafts/`）
- 暫存（gitignored，`tmp/gh_unit2/`）：
  - `sources_v3.py`、`test_unit2_v3_phase1.py`、`build_rulepack_drafts.py`
  - `preflight_unit2.py`、`rulepack_regression.py`、`dump_variant0.py`、`variant0_payloads.json`
  - `sandbox_phase1_rule_packs.yaml`、`stage2_copy.db`（DB 複本）
  - `preflight_current.json`、`preflight_sandbox.json`、`gencode_before.txt`、`gencode_after.txt`
- 未變更：
  - 正式 DB
  - 正式 rule pack YAML
  - `configs/gencode_promoted_capabilities.json`
  - Stage 1 封板資料
  - revision_0002 工作區

**Runtime 影響：** 目前沒有。orchestrator 修補需重啟才會生效；規則包也尚未正式註冊。
