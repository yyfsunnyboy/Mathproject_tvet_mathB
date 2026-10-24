# 普高數學1 Unit 9「一次與二次函數」Gencode V3 部署紀錄（2026-10-23）

## 結果（部分發布 38/43）

| Skill | 教材題數 | Sandbox PASS | Published | Failed |
|---|---:|---:|---:|---:|
| gh_LinearFunctions | 8 | 8 | 8 | 0 |
| gh_QuadraticFunctions | 35 | 30 | 30 | 0（5 題 DEFERRED） |
| Total | 43 | 38 | 38 | 0 |

## DEFERRED（5 題）

12567、12568、12570、12576、12587：拋物線描繪題。既有 drawing 契約（`drawing_answer_analysis_service`）沒有拋物線／function_graph grader，無法正式批改，不進 wrapper／tracker。補齊需新增共用 grader（超出本輪範圍）。

## Domain

- 新增 `function.linear_quadratic`（revision_0001，8 個 operation），package `core/domain/promoted/function_linear_quadratic`；答案以 Fraction／sympy 計算，validator 以 sympy／mpmath 另法重算。
- 重用 `algebra.polynomial_division.polynomial_core` 的文字輔助與 `analytic_geometry.line_equations` 的圖形輔助及既有共用 Checker（含 `free_response_drawing_checker` line_graph）；未改 Checker／Runtime／前端／其他單元。
- Bundle 審查版 sha256 `719e435c82a6acdeb401936f5e9b1ac2036e8e5560589fe93643123c47d9311e`（owner 核准，approved_by yeh.ivan@hlbh.hlc.edu.tw）。

## Gate 與驗收

- `tests/domain/test_function_linear_quadratic_domain.py` 17 PASS；`tests/gencode/test_gh_unit9_functions_sandbox.py` 126 PASS。
- 隔離演練 `rehearse_unit9.py`：38/38 verified、兩 Skill production_published、正式路徑寫入 0。
- 正式：backup（integrity ok）→ promote → quarantine（無既有產物）→ rebuild 38/38 verified → publish（smoke／staging／production passed）→ verify-live（manifest 8/30 與 specs 一致、tracker 38/38 verified）→ accept（新程序＋DB 複本：兩 Skill 練習頁 200、38 題皆出題，判分全對；12560 含 AI 判圖畫布，僅驗證出題與契約）。
- `variation_status=unsafe_dynamic` 來自選擇題啟發式（○×、多選、概念題固定選項），非 publish Gate。

## 正式 DB 變更範圍

`gencode_component_tracker` 新增 38 列（884 → 922，皆 verified）。備份：`backups/unit9_function_models/20261023_220434/`。

## Runtime 注意

Skill 綁定在程序 import registry 時讀取一次；Flask 需重啟後才有 Unit 9 綁定。
