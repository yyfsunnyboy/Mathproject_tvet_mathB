# 普高數學1 Unit 6 Gencode V3 報告（停在 production promotion 前的人工審核）

狀態：**Stage 1 PASS、Stage 2 Sandbox／Gate PASS（32/32 READY、0 DEFERRED）；Promotion 等待專案負責人審核，尚未 promote、尚未 publish。**
Stage 1 證據見 `../gh_unit6_stage1/STAGE1_REPORT.md`。

## 1. Domain Operations：重用與新增

- **重用（未改動）**：
  - 共用 Checker：`equation_checker`（`equation_equivalent`，sympy 比較 lhs−rhs 的常數倍，圓方程式標準式／一般式互通）、`inequality_solution_checker`、`coordinate_pair_checker`、`rational_checker`、`expression_equivalence_checker`（根式、π 形式）、`solution_set_checker`、`linear_equation_equivalent_checker`（中垂線）、`choice_label_checker`、`multi_part_answer_checker`。**沒有新增或修改任何共用 Checker、Runtime、前端或 DB。**
  - Unit 5 已發布 domain `analytic_geometry.line_equations` 的精確幾何／圖形原語（`line_geometry`：中點、中垂線、外心、Radical；`figures`：`coordinate_plane`）以 import 重用；`visual_spec.js` 既有的 `circles` primitive 作圖。
  - 不沿用 `circle.plane`（vocational 靜態 domain）：它以靜態 taxonomy 綁定 `vh_` Skill，promotion 機制不允許把 gh Skill 綁到既有靜態 domain（`skill_binding_conflict_static`）；教材原題 givens 作為 variant 0。
- **新增 Domain**：`analytic_geometry.circle_equations`（10 個 operation，Fraction 精確運算；每個 operation 都有以 sympy 多項式恆等式／代入／定義性質重新檢驗的獨立 validator，不呼叫同一建構程式碼）：
  `write_circle_equations`（圓心半徑／圓心＋過點／直徑／同心過點／圓心在軸上／外接圓／中垂線／x²+y²=k／直徑參數）、`analyze_general_circle`（一般式→圓心半徑／標準式與圖形判斷／參數範圍／由半徑求參數／兩解參數＋圓心／由圓心求係數）、`solve_distance_ratio_locus`（阿波羅尼斯圓，含反比應用與半圓）、`classify_points_against_circle`、`solve_circle_point_distances`、`solve_point_position_parameter_range`、`evaluate_circle_statement_truth`、`solve_mohr_circles`、`solve_storm_entry_time`、`solve_circular_arch_height`。
- 一題一 Generator；Domain 負責數學、Generator 只抽樣與組題、Checker 依 Answer Contract 判分；沒有單題硬編判題規則。

## 2. 元件清單（32 個 READY，3 個 Skill）

| Skill | 元件（textbook example id） | Operation |
| --- | --- | --- |
| gh_StandardFormOfACircle（9） | 12449 12450 12451 12452 12476 12479 | write_circle_equations |
| | 12470 12474 | evaluate_circle_statement_truth |
| | 12480 | solve_circular_arch_height |
| gh_GeneralFormOfACircle（14） | 12453 12454 12455 12458 12459 12460 12462 12463 12475 | analyze_general_circle |
| | 12456 12457 12461 | solve_distance_ratio_locus |
| | 12471 12472 | evaluate_circle_statement_truth |
| gh_PointAndCircleRelationship（9） | 12464 | classify_points_against_circle |
| | 12465 12468 12477 | solve_circle_point_distances |
| | 12466 | solve_mohr_circles |
| | 12467 | solve_point_position_parameter_range |
| | 12469 | write_circle_equations |
| | 12473 | evaluate_circle_statement_truth |
| | 12478 | solve_storm_entry_time |

作答型態：`multi_part`（各 part 自己的 checker：`equation_checker`／`coordinate_pair_checker`／`rational_checker`／`expression_equivalence_checker`／`solution_set_checker`／`choice_label_checker`）、單一 `equation`（12450、12456、12461）、單一 `inequality`（12455、12463、12467）、`single_choice`（12470–12474 ○×、12478）、單一 `rational`（12458、12480）。沒有任何題需要超出 Spec §5 的作答拓撲，故 **無 DEFERRED**。

- 每元件 20 個 deterministic seeds：生成確定、canonical 答案被接受、每個 part 的錯誤值被拒絕、等價寫法被接受、Answer Contract／integrity validator 通過；題面（題幹＋圖＋答案）不同數 ≥ 18（實測全為 20）。
- 圖形：12457（A、B 與線段）、12466（A、B 與線段 AB，不畫答案圓以免洩題）、12480（拱門圓＋Q A P B R＋門柱）；以 Chrome headless 實跑 `visual_spec.js` 驗證可渲染。12478 的新聞框文字直接放入題幹，不需圖。
- 與 Stage 1 修正的對應：12474 的 `2\pi`（匯入器丟失的 π）、12478 的新聞數據、12466 詳解皆已納入並有測試（`test_stems_carry_the_source_numbers_at_variant_zero`、`test_source_oracles_from_the_textbook_solutions`）。

## 3. 驗證（Impact-Based，僅相關範圍）

| 範圍 | 結果 |
| --- | --- |
| `tests/domain/test_analytic_geometry_circles_domain.py`（教材詳解手算為 oracle；32 個元件的 validator 竄改答案必拒；退化輸入必拒） | 53 PASS |
| `tests/gencode/test_gh_unit6_circle_equations_sandbox.py`（32 元件契約、oracle、判分、圖形、20 seeds；π／根式／等價方程式／不等式等價與錯答） | 38 PASS |
| 預演 `rehearse_unit6.py`：**隔離 promotion**（temp store／temp package root，核可標記 `isolated_test_only`，只證明正式 promotion 的 preflight＋post-verification 會過）→ 正式 Phase 2（`run_gencode_phase2_raw`）32/32 tracker＝verified、每元件 20 seeds 重驗 → 正式 Phase 3（`publish_single_v3_skill_to_production`，sandbox root）3 Skill 皆 `production_published` → 學生端 facade 每 Skill 80 seeds：無 canonical 被拒、無錯答被接受 | PASS；寫入掃描：production DB／configs／core/domain/promoted／skills／agent_skills_v3／dryrun／staging **0 變更** |

未重跑：Unit 3–5 既有測試（本次沒有修改任何共用 Checker／Runtime／前端／既有 domain 檔案）。

## 4. 人工審核（Spec／PipelineFlow §4.6：只保留在 production promotion 前）

- 審核包：`reports/domain_operation_workspaces/capability_analytic_geometry_circles_5c7b9e24/revision_0001/`（`promotion_bundle.json` ＋ `production_package/` 4 檔，與 `agent_domains_candidate/analytic_geometry_circles/` 同名檔位元組相同）。
- bundle sha256：`c9ed3154c16920b41d775e6c0144cdb646b6aa73cbb383a8639b9426811675f6`
- production_package 檔案 sha256：
  - `circle_equations_adapter.py` `dd681d1d24e692e89d96140980726898f4940cdc2e80003d24d79a03512e94a1`
  - `circle_equations_domain.py` `54228ea7e06f256d2076f5e61dedf9fab53e4668598adebb1e9d61d1d926da57`
  - `circle_geometry.py` `b848685f38731085f4ac0445d67e0a2d6fd108e0d3a149048bccc878e88dee6a`
- preflight：僅剩 `human_review_not_approved`、`approved_revision_mismatch` 兩項（審核欄位尚未填寫）；套件雜湊、import、Checker 註冊、skill binding、無靜態衝突皆通過。
- 審核重點：(1) 套件 import 依賴已 promote 的 `core.domain.promoted.analytic_geometry_lines.{line_geometry,figures}`；(2) 3 個 Skill 綁定；(3) 習題 Skill 重新歸屬（Stage 1）。
- 本報告與腳本**不寫入**核可。核可由負責人在對話中明確表示後，才把 `review` 改為 `status=human_approved`、`approved_by`、`approved_revision=1`。

## 5. 核可後的執行步驟（`reports/gh_unit6_deploy/deploy_unit6.py`，逐步、各步產出 json）

1. `backup --confirm`（DB 備份＋tracker／store／既有 wrapper）
2. `promote --confirm --teacher-approved`（須 bundle 已核可；原子 promotion，失敗自動回滾）
3. `quarantine --confirm`（移走 dryrun 元件，由正式 Phase 2 重建）
4. `rebuild --confirm`（正式 Phase 2：32 個 tracker＝verified，並再驗 20 seeds；任何失敗即停止、不發布）
5. `publish --confirm`（正式 Phase 3：staging smoke → production；僅 `verified` 元件進 wrapper）
6. `verify-live`（facade 學生端 smoke）；回滾：`rollback-publish --confirm`
7. Flask 5000 是否重啟由負責人決定（本流程不重啟、不停止任何服務）
