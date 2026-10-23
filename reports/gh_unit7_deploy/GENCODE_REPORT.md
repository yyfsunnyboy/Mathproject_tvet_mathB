# 普高數學1 Unit 7「圓與直線的關係」Gencode V3 部署紀錄（2026-10-23）

## 結果

| Skill | 教材題數 | Sandbox PASS | Published | Failed |
|---|---:|---:|---:|---:|
| gh_JudgingTheRelationshipOfCircleAndLine | 21 | 21 | 21 | 0 |
| gh_TangentLinesOfACircle | 15 | 15 | 15 | 0 |
| Total | 36 | 36 | 36 | 0 |

12482 發布後品質發現已定向修復並重新發布（見下）。

## Domain

- 新增 `analytic_geometry.circle_line_relations`（revision_0001，7 個 operation），package `core/domain/promoted/analytic_geometry_circle_lines`。
- 重用 `analytic_geometry.circle_equations` 的 exact `circle_geometry`、`analytic_geometry.line_equations` 的 `line_geometry`／`figures`，以及既有共用 Checker；未修改任何 Checker、Unit 1–6 Domain 或 runtime。
- Bundle 審查版 sha256 `72cb405d646c6ad27d13df5f400bcceb7ab09ea0a800e64d06083fbaf0dc0c2a`；寫入核准紀錄後 `1572b8146aef78f0f08f9ce6fc9913c15d134edcf79071efbbb5ecbf74326663`（僅 review 區塊不同，package 檔案 hash 不變）。
- 前端：`static/js/visual_spec.js` 新增 opt-in `show_grid: false`（量測型圖不畫單位格，預設行為不變）。

## Gate 與驗收

- `tests/domain/test_analytic_geometry_circle_lines_domain.py` 31 PASS；`tests/gencode/test_gh_unit7_circle_lines_sandbox.py` 42 PASS（12482 修復後新增 1 項，受影響子集 5 PASS）。
- 隔離演練（`rehearse_unit7.py`）：Phase 2 36/36 verified、Phase 3 兩 Skill production_published、正式路徑寫入 0。
- 正式：backup（integrity ok）→ promote → quarantine（無既有產物）→ rebuild 36/36 verified → publish（smoke/staging/production 皆 passed）→ verify-live（manifest 21/15 verified 與 specs 一致、tracker 36/36 verified）→ accept（新程序 + DB 複本：兩 Skill 練習頁 200、36 題皆經 `/get_next_question` 出題、圖形題回傳 `visual_spec`、正確／等價／錯誤判分全對、無 `DOMAIN_CAPABILITY_UNRESOLVED`／`domain_binding_mismatch`）。
- 發布服務的 `variation_status=unsafe_dynamic` 來自 4 選項選擇題啟發式：○× 題（12491–12494、12508）只有 2 個選項、單線關係題（12488、12497）只有 3 個選項，與教材一致；Unit 6 的 ○× 題相同。非 publish Gate。

## 正式 DB 變更範圍

`gencode_component_tracker` 新增 36 列（12481–12516，全部 verified；805 → 841），連帶 `sqlite_sequence`。其他表無變更；12481–12516 以外的 tracker 列無變更。備份：`backups/unit7_circle_line_relations/20261023_160156/`。

## Runtime 注意

Skill 綁定在程序 import registry 時讀取一次。執行中的 Flask 5001（15:15 啟動）重啟前無 Unit 7 綁定，Unit 7 題目會以 `domain_binding_mismatch` 拒絕出題（不錯判、不寫 tracker）；網站實機驗收待重啟後進行。Unit 6 先前的 `DOMAIN_CAPABILITY_UNRESOLVED: no_required_capabilities` 為同一機制（Promotion 前啟動的程序）。

## 12482 品質發現與定向修復（已完成）

發現：20 個變體中 5 個在相切條件的兩根裡有一根使圓退化（r²=0，圓心落在直線上）而被捨去，答案只剩一個值；詳解未說明捨去理由，與教材（兩個有效根）不一致。數學答案正確、Gate 未攔下。

修復（owner 核准方案 A，16:29）：只改 `unit7_specs.s12482` 的變體取樣，要求 (ak−bd)²=4f(a²+b²) 的兩根都使 ad+bk≠0；Domain package 未變（與 promoted 版本 byte 相同），無需重新 Promotion。新增 sandbox 斷言「12482 每個變體都有兩個解」。
流程：backup `20261023_163030`（integrity ok）→ quarantine 只移 `src_12482` → rebuild 12482 verified（20 變體）→ 重新發布 Judging（smoke/staging/production passed）→ verify-live 與 accept 皆 PASS；12482 已發布 20 變體全為兩解。
範圍：已發布檔案只有 `src_12482/generate.py` 變更（Tangent 0 變更）；DB 只有 Judging 21 列 tracker 的 `updated_at`（重新發布）與 12482 的 `induced_spec_payload`，狀態與 ID 皆不變。第一輪各步驟紀錄保存在 `round1_full_deploy/`。

## 風險註記

`configs/general_high_source_skill_map.json` 尚未持久化 12513、12515 改綁 Judging 的人工修正；未來重新匯入 Unit 7 可能退回 Tangent。本輪依正式 DB 21/15 綁定建置與驗證。
