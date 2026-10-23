# 普高數學1 Unit 8「多項式的除法原理」Gencode V3 部署紀錄（2026-10-23）

## 結果

| Skill | 教材題數 | Sandbox PASS | Published | Failed |
|---|---:|---:|---:|---:|
| gh_BasicConceptsOfPolynomials | 1 | 1 | 1 | 0 |
| gh_ArithmeticOperationsOfPolynomials | 18 | 18 | 18 | 0 |
| gh_RemainderTheorem | 13 | 13 | 13 | 0 |
| gh_FactorTheorem | 11 | 11 | 11 | 0 |
| Total | 43 | 43 | 43 | 0 |

## Domain

- 新增 `algebra.polynomial_division`（revision_0001，13 個 operation），package `core/domain/promoted/algebra_polynomial_division`；精確 Fraction 運算，validator 以 sympy 獨立重算。
- 既有 promoted Domain 無多項式除法能力（技高 B1 `polynomial_domain.py` 為來源導向，未重用）；只使用既有共用 Checker，未改任何 Checker／Runtime／前端／Unit 1–7。
- Bundle sha256：審查版 `dafdb73cbb5e34f07e7c9b327b67280cd191eb7ce1ba207e1573b46893e47cfa`（owner 於 2026-10-23 核准，approved_by yeh.ivan@hlbh.hlc.edu.tw）。

## Gate 與驗收

- `tests/domain/test_algebra_polynomial_division_domain.py` 17 PASS；`tests/gencode/test_gh_unit8_polynomial_division_sandbox.py` 88 PASS。
- 隔離演練 `rehearse_unit8.py`：43/43 verified、四 Skill production_published、正式路徑寫入 0。
- 正式：backup（integrity ok）→ promote → quarantine（無既有產物）→ rebuild 43/43 verified → publish（smoke／staging／production 皆 passed）→ verify-live（manifest 1/18/13/11 與 specs 一致、tracker 43 列全 verified）→ accept（新程序＋DB 複本：四 Skill 練習頁 200、43 題皆出題，正確／錯誤／等價判分全對，無 `DOMAIN_CAPABILITY_UNRESOLVED`／`domain_binding_mismatch`；多小題 31 次）。
- Factor／Remainder 的 `variation_status=unsafe_dynamic` 來自 4 選項選擇題啟發式（○× 與多選題），與 Unit 6／7 相同，非 publish Gate。

## 圖形處理

12552（黑板）、12555（綜合除法遮蓋表）以 LaTeX 在題幹動態重現，無固定圖片（Renderer 無文字／表格圖元）。
12555 原題條件（f(−2)=8，首項被遮）推得答案 3/256，其他變體為整數。

## 正式 DB 變更範圍

`gencode_component_tracker` 新增 43 列（12517–12559，全部 verified；841 → 884）。備份：`backups/unit8_polynomial_division/20261023_172907/`。

## Runtime 注意

Skill 綁定在程序 import registry 時讀取一次；執行中的 Flask 需重啟後才有 Unit 8 綁定（重啟前 Unit 8 題目以 `domain_binding_mismatch` 拒絕出題，不錯判、不寫 tracker）。網站實機驗收待重啟後進行。
