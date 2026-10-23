# 普高數學1 Unit 5 Gencode V3 報告（停在 production promotion 前的人工審核）

狀態：**Stage 1 PASS、Stage 2 Sandbox／Gate PASS（44/46 READY、2 DEFERRED）；Promotion 等待專案負責人審核，尚未 promote、尚未 publish。**
Stage 1 證據見 `../gh_unit5_stage1/STAGE1_REPORT.md`。

## 1. Domain Operations：重用與新增

- **重用（未改動語意）**：共用 Checker `linear_equation_equivalent_checker`、`coordinate_pair_checker`、`rational_checker`、`expression_equivalence_checker`（radical_equivalence）、`solution_set_checker`（exact_rational）、`ordered_inequality_checker`、`choice_label_checker`、`multi_part_answer_checker`／`table_fill_checker`、`free_response_drawing_checker`；`visual_spec.js` 的 `coordinate_plane`／`cartesian_canvas` Renderer（含 `shade`）；`table_question_contract`；Unit 3 已升級的 multipart 選項物件渲染。
- **新增 Domain**：`analytic_geometry.line_equations`（20 個 operation，Fraction 精確運算；每個 operation 都有以 sympy 代入／定義性質重新檢驗的獨立 validator）：`compute_line_distances`, `evaluate_line_statement_truth`, `evaluate_slope_sign_statements`, `fill_line_property_table`, `graph_inequality_system`, `rank_line_slopes`, `read_region_signs_from_figure`, `select_points_same_side`, `slope_of_line_from_equation`, `solve_axis_triangle_area_line`, `solve_line_constructions`, `solve_line_equations`, `solve_line_parameters`, `solve_parallel_line_family`, `solve_rectangle_perpendicular_diagonals`, `solve_region_coefficients_from_figure`, `solve_translation_parameter`, `solve_triangle_region_system`, `solve_window_decorative_lines`, `translate_line_equation`。
  - 不沿用 vocational 靜態 domain（`coordinate_geometry.line_equation` 等）：它們以靜態 taxonomy 綁定 `vh_` Skill，promotion 機制不允許把 gh Skill 綁到既有靜態 domain；本 domain 以教材原題 givens 為 variant 0。
- **新增／擴充的共用能力（皆為純新增，未改既有行為）**
  1. `core/checkers/linear_relation_set_checker.py`：直線方程式／二元一次不等式的「無序集合」等價判分（`2x+y-6≤0` ＝ `-2x-y+6≥0`；等號與不等號不互通；不可解析回報 invalid input）。已接入 `checker_registry`、`multi_part_answer_checker`、`runtime_skill_wrapper.check_answer`。
  2. `multi_part_answer_checker` 新增 `coordinate_pair_checker` part 分派（原本多小題內的坐標答案會被判 unsupported）。
  3. 共用作圖批改新增 drawing type `linear_inequality_region`（`drawing_answer_analysis_service` ＋ `free_response_drawing_checker`）：原本 evaluator 只有 histogram／frequency_polygon／line_graph，二元一次不等式區域作圖會永遠回 system error。新 evaluator 由本地確定性比對邊界直線位置、實線／虛線與鋪色是否正確（探測點由 spec 決定；prompt 不洩漏答案），vision 只回報看到什麼。

## 2. 元件清單（44 個 READY）

| id | Skill | Operation | 作答型態 | Checker | 圖形 | 不同題面(20 seeds) |
| --- | --- | --- | --- | --- | --- | --- |
| 12403 | LineSlope | rank_line_slopes | multi_part | ordered_inequality+rational | 有 | 20 |
| 12404 | LineSlope | evaluate_slope_sign_statements | solution_set | solution_set | 有 | 20 |
| 12436 | LineSlope | rank_line_slopes | short_answer | ordered_inequality | 有 | 20 |
| 12405 | EquationOfALine | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12406 | EquationOfALine | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12407 | EquationOfALine | slope_of_line_from_equation | rational | rational | — | 20 |
| 12408 | EquationOfALine | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12409 | EquationOfALine | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12410 | EquationOfALine | fill_line_property_table | table_fill | linear_equation_equivalent+rational | — | 20 |
| 12432 | EquationOfALine | evaluate_line_statement_truth | single_choice | choice_label | — | 20 |
| 12437 | EquationOfALine | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12445 | EquationOfALine | solve_axis_triangle_area_line | short_answer | linear_relation_set | — | 20 |
| 12411 | TranslationOfALine | translate_line_equation | equation | linear_equation_equivalent | — | 20 |
| 12412 | TranslationOfALine | translate_line_equation | equation | linear_equation_equivalent | — | 20 |
| 12438 | TranslationOfALine | solve_translation_parameter | rational | rational | — | 20 |
| 12413 | ParallelAndPerpendicularLines | solve_line_equations | multi_part | linear_equation_equivalent | — | 20 |
| 12414 | ParallelAndPerpendicularLines | solve_line_constructions | multi_part | coordinate_pair+linear_equation_equivalent | — | 20 |
| 12415 | ParallelAndPerpendicularLines | solve_line_constructions | coordinate_pair | coordinate_pair | — | 20 |
| 12416 | ParallelAndPerpendicularLines | solve_line_parameters | multi_part | rational | 有 | 20 |
| 12417 | ParallelAndPerpendicularLines | solve_line_constructions | multi_part | coordinate_pair+linear_equation_equivalent | 有 | 20 |
| 12418 | ParallelAndPerpendicularLines | solve_line_constructions | coordinate_pair | coordinate_pair | — | 20 |
| 12431 | ParallelAndPerpendicularLines | evaluate_line_statement_truth | single_choice | choice_label | — | 10 |
| 12433 | ParallelAndPerpendicularLines | evaluate_line_statement_truth | single_choice | choice_label | — | 20 |
| 12439 | ParallelAndPerpendicularLines | solve_line_parameters | rational | rational | — | 20 |
| 12440 | ParallelAndPerpendicularLines | solve_line_constructions | multi_part | coordinate_pair | — | 20 |
| 12444 | ParallelAndPerpendicularLines | solve_rectangle_perpendicular_diagonals | numeric_or_radical | expression_equivalence | 有 | 16 |
| 12446 | ParallelAndPerpendicularLines | solve_line_constructions | multi_part | coordinate_pair+expression_equivalence | 有 | 20 |
| 12419 | DistanceFromPointToLine | compute_line_distances | rational | rational | — | 20 |
| 12420 | DistanceFromPointToLine | compute_line_distances | rational | rational | — | 20 |
| 12421 | DistanceFromPointToLine | solve_window_decorative_lines | multi_part | linear_equation_equivalent | 有 | 20 |
| 12422 | DistanceFromPointToLine | solve_line_parameters | solution_set | solution_set | — | 20 |
| 12423 | DistanceFromPointToLine | compute_line_distances | numeric_or_radical | expression_equivalence | — | 20 |
| 12424 | DistanceFromPointToLine | solve_window_decorative_lines | multi_part | expression_equivalence+rational | 有 | 20 |
| 12434 | DistanceFromPointToLine | evaluate_line_statement_truth | single_choice | choice_label | — | 20 |
| 12448 | DistanceFromPointToLine | solve_parallel_line_family | multi_part | linear_equation_equivalent+rational | 有 | 20 |
| 12425 | LinearInequalityInTwoVariables | graph_inequality_system | drawing | free_response_drawing | 畫布(作圖) | 20 |
| 12426 | LinearInequalityInTwoVariables | graph_inequality_system | drawing | free_response_drawing | 畫布(作圖) | 20 |
| 12427 | LinearInequalityInTwoVariables | solve_triangle_region_system | multi_part | choice_label+linear_relation_set+rational | 有 | 20 |
| 12429 | LinearInequalityInTwoVariables | graph_inequality_system | drawing | free_response_drawing | 畫布(作圖) | 20 |
| 12430 | LinearInequalityInTwoVariables | read_region_signs_from_figure | solution_set | solution_set | 有 | 20 |
| 12435 | LinearInequalityInTwoVariables | evaluate_line_statement_truth | single_choice | choice_label | — | 20 |
| 12441 | LinearInequalityInTwoVariables | select_points_same_side | solution_set | solution_set | — | 20 |
| 12442 | LinearInequalityInTwoVariables | graph_inequality_system | drawing | free_response_drawing | 畫布(作圖) | 20 |
| 12443 | LinearInequalityInTwoVariables | solve_region_coefficients_from_figure | multi_part | rational | 有 | 20 |

- 每元件 20 個 deterministic seeds：生成確定、canonical 答案被接受、每個小題的錯誤值被拒絕、等價寫法被接受、Answer Contract／integrity validator 通過；題面（題幹＋圖＋表＋答案）不同數 ≥ 18（12431 自然輸入域僅 10 種、12444 僅 16 種）。
- 12410 為 `table_fill`（7 個 inline 儲存格、不顯示 field_key）；12425／12426／12429／12442 為 `drawing`（`canvas`、禁用文字輸入與一般 submit、`ai_check_required`、`success_dialog_required`），畫布為 `cartesian_canvas`，不會產生一般文字框。

## 3. DEFERRED（2 題，不拖累其他題；非 production tracker enum，僅排除記錄）

| id | 責任層 | 原因 | 後續條件 |
| --- | --- | --- | --- |
| 12428 | Answer Contract（Spec §5.5） | 一題要求三個獨立圖示；drawing 契約只定義單一 canvas、單一圖 | 先由規範定義多圖作答拓撲 |
| 12447 | Answer Contract（Spec §4.4／§5.5） | 同題要求作圖＋格子點個數；multi_part 內無 drawing part 契約，drawing 又不得降級為 short_answer | 先由規範定義「drawing＋數值」複合拓撲 |

## 4. 驗證（Impact-Based，僅相關範圍）

| 範圍 | 結果 |
| --- | --- |
| `tests/domain/test_analytic_geometry_lines_domain.py`（教材詳解／手算為 oracle） | 74 PASS |
| `tests/gencode/test_gh_unit5_line_equations_sandbox.py`（44 元件契約、oracle、判分、圖形、table、drawing） | 56 PASS |
| `tests/gencode/test_linear_relation_set_checker.py`（共用 Checker 等價／錯答／parse） | 26 PASS |
| `tests/test_inequality_region_drawing_evaluator.py`（作圖 evaluator，含 mock vision 端到端） | 16 PASS |
| 受共用修改影響的既有測試：drawing／line_graph／ordered_inequality（46）、multi_part／簡分數／等價／循環小數等（305） | 全 PASS |
| Unit 3 既有 `test_gh_unit3_exponents_sandbox.py`（Unit 3/4 能力不受影響） | 64 PASS |
| 預演 `rehearse_unit5.py`：**隔離 promotion**（temp store／temp package root，核可標記 `isolated_test_only`，只證明正式 promotion 的 preflight＋post-verification 會過）→ 正式 Phase 2（`run_gencode_phase2_raw`）44/44 tracker＝verified → 正式 Phase 3（`publish_single_v3_skill_to_production`，sandbox root）6 Skill 皆發布（5 個 `production_published`、`gh_LinearInequalityInTwoVariables` 因 DEFERRED 為 `partial_published`）→ 學生端 facade 每 Skill 80 seeds 無問題 | PASS；寫入掃描：production DB／configs／core/domain/promoted／skills／agent_skills_v3／dryrun／staging **0 變更** |
| 圖形實測（現行服務提供的 `visual_spec.js` 真實 Renderer）：12403／12404／12416／12417／12421／12427／12430／12436／12443／12444／12446／12448 | 皆可渲染且與教材圖一致；shade 區域（12427／12443）改用 a/b/c 邊界線後正確塗色 |
| 多小題作答區（`MultipartFieldRenderer`）：12427（2 輸入＋1 下拉）、12414、12403 | 控制項數量與題型契約一致 |

已知、不阻擋的 Phase 3 variation audit 警示（審計器不認得這些題型）：○× 單選為 2 選項（審計器要求 4 選項）、drawing 無法以文字自我批改、圖形／表格題的題幹文字不變。Unit 3 的同類題型亦同。

## 5. 人工審核（Spec／PipelineFlow §4.6：只保留在 production promotion 前）

- 審核包：`reports/domain_operation_workspaces/capability_analytic_geometry_lines_8a2f6d15/revision_0001/`（`promotion_bundle.json` ＋ `production_package/` 5 檔，與 `agent_domains_candidate/analytic_geometry_lines/` 同名檔位元組相同）。
- bundle sha256：`302f665f647d68ce8a3e2641475c923dbd459f8ac99f0abd4a852156639e2b48`
- preflight：僅剩 `human_review_not_approved`、`approved_revision_mismatch` 兩項（審核欄位尚未填寫）；套件雜湊、import、Checker 註冊、skill binding、無靜態衝突皆通過。
- 本報告與腳本**不寫入**核可。核可由負責人在對話中明確表示後，才把 `review` 改為 `status=human_approved`、`approved_by`、`approved_revision=1`。

## 6. 核可後的執行步驟（`reports/gh_unit5_deploy/deploy_unit5.py`，逐步、各步產出 json）

1. `backup --confirm`（DB 備份＋tracker／store／既有 wrapper）
2. `promote --confirm --teacher-approved`（須 bundle 已核可；原子 promotion，失敗自動回滾）
3. `quarantine --confirm`（移走 sandbox 試建的 dryrun 元件，由正式 Phase 2 重建）
4. `rebuild --confirm`（正式 Phase 2：44 個 tracker＝verified，並再驗 20 seeds；任何失敗即停止、不發布）
5. `publish --confirm`（正式 Phase 3：staging smoke → production；僅 `verified` 元件進 wrapper）
6. `verify-live`（facade 學生端 smoke）；回滾：`rollback-publish --confirm`
7. Flask 5000 是否重啟由負責人決定（本流程不重啟、不停止任何服務）

---

## 附錄：revision 2 — 補完 12428、12447（46/46）

- 新增 operation（revision 2，既有 20 個不變）：`graph_inequality_series`（12428：三個獨立作圖）、`graph_inequality_with_lattice_count`（12447：作圖＋格子點數，以掃描與 Pick 定理雙重驗證）。審核包 `revision_0002/`，bundle sha256 `06ccd656d366f333c8c3382ef307cf732563736b0f9071136629ba40f9a22a5e`，preflight 僅剩兩個審核欄位。
- 共用契約擴充：`multi_part` 的 part 可為 drawing（`input_type: canvas`，每個 part 獨立 canvas、獨立 expected_drawing_spec、獨立判分，整題 all-parts-correct）。`multi_part_answer_checker` 逐 part 呼叫既有 `free_response_drawing_checker`；未作答 → missing_part，grader 失敗／低信心 → 例外（系統狀況，不當作答錯）。前端 `multipart_field_renderer.js` 新增 canvas part（值為 `{composite, strokes}` JSON，存在隱藏 `.multi-part-input`，收集邏輯不變）。
- 驗證：domain 77、sandbox 元件 46、相關既有回歸共 486 PASS；以 mock vision 驗證各 canvas 獨立判分、缺圖、系統錯誤；瀏覽器實測三個獨立 canvas 只畫其中一個，其餘值為空。隔離預演（revision 2 升級既有 revision 1）46/46 tracker verified，6 個 Skill 皆 `production_published`，production 路徑 0 寫入。
- 核可後僅需：`backup`、`promote`、`quarantine`、`rebuild`（只建 12428、12447）、`publish`（只發布 gh_LinearInequalityInTwoVariables）、`verify-live`；原 44 題不重建。
