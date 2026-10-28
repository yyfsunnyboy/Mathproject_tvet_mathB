# 普高數學2 Unit 4 排列 — GenCode V3 審核報告（待人工發布授權）

- Bundle：`reports/domain_operation_workspaces/capability_discrete_permutations_5aaa48d3/revision_0001`（`ready_for_human_review`，尚未核准、未 Promotion、未 Publish）
- bundle 檔 SHA-256：`2cd7bbf9665a5c53bf415a5579696d296919de0dbcc0044479559b2b0bb4c4db`
- Domain：`discrete.permutations`（17 個 Operation，新套件 `permutations`，全為新增，無可重用的既有 Operation）
- 範圍：38 題 = 37 DYNAMIC + 1 FIXED_GRADED（12801）+ 0 FIXED_UNGRADED
  - `gh_LinearPermutation` 19 個 component（12774–12792）
  - `gh_PermutationWithIdenticalItems` 10 個動態 component（12793–12803 共 11 列，其中 12801 為固定題）
  - `gh_RepeatedPermutation` 8 個 component（12804–12811）

## 不適合動態化
- 12801：街道圖（缺邊）題，答案 62 須從印刷圖形讀取，圖形不可重畫或改變。以 PDF 向量圖與 PNG 像素圖兩路獨立還原街道圖，再以 DP 與列舉驗證 = 62；保留教材原題、自動判分（FIXED_GRADED），隨正式發布時合併進 `configs/fixed_textbook_practice.json`（`reports/gh_math2_unit4_fixed/build_fixed_config.py`，發布步驟 `fixed`）。

## 驗證結果（皆在隔離環境）
- `tests/gencode/test_gh_math2_unit4_permutations_sandbox.py`：119 passed（每 component 20 seeds、契約、獨立 oracle、題幹語意重算、教材原解對照、驗證器防竄改、退化輸入拒絕、圖形守門）
- `tests/test_gh_unit4_fixed_and_figures.py`：8 passed（12801 教材原題＋裁切圖＋共用 checker 判分、不洩漏答案、圖形題僅在圖形結構一致時附教材裁切圖）
- 隔離發布演練 `rehearse_unit4.py`：37/37 component tracker = verified（37 × 20 seeds，共 740 筆，0 失敗，最少 8 個相異題面）；三個 Skill 皆 `production_published`，smoke / staging / production smoke 皆 passed；學生端 facade problems = 0；正式路徑寫入掃描 = 空
- variation audit：`unsafe_dynamic`，原因與 Unit 1–3 先例相同（○× 二選一題不滿足審計的「四選項」規則），非阻擋項
- 圖形題 12794 / 12797（街道格）與 12803（氣球）：僅與教材圖形結構一致的變體附教材裁切圖並含「如圖／右圖」；其餘變體以文字敘述資料，不含圖形提示語

## 授權範圍（單次）
1. `deploy_unit4.py backup` → `record_approval.py` → `promote`（`--teacher-approved`）→ `fixed` → `quarantine` → `rebuild` → `publish` → `verify-live` → `accept`
2. 僅涉及：`core/domain/promoted/permutations`、`configs/gencode_promoted_capabilities.json`、`configs/fixed_textbook_practice.json`（新增 12801，保留既有 5 筆）、上述 3 個 Skill 的 `agent_skills_v3/`、`skills/`、`reports/gencode_v3_dryrun` 與 tracker
3. 不重啟 Flask 5000 / 5001、不動 Cloudflare、不影響 Unit 1–3 已發布 component
