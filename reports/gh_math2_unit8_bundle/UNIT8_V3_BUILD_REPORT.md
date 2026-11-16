# 普高數學2 單元08 一維數據分析 — GenCode V3 建置報告

- 範圍：curriculum `general`、volume `數學2`、Skills `gh_Mean` / `gh_MedianAndPercentiles` / `gh_VarianceAndStandardDeviation` / `gh_DataScalingAndShifting`、textbook_examples **12912–12946**（35 題）。
- 狀態：**PACKAGE_READY**（Bundle `ready_for_human_review`）。**未** Promotion、**未** Publish、**未**寫入正式 tracker／promoted store。

## 產物

| 項目 | 位置 |
|---|---|
| 候選 Domain 套件 | `agent_domains_candidate/univariate_statistics/` |
| Sandbox Gate 測試 | `tests/gencode/test_gh_math2_unit8_univariate_statistics_sandbox.py` |
| Review Bundle | `reports/domain_operation_workspaces/capability_statistics_univariate_descriptive_3b91cfbb/revision_0001/` |
| 本報告 | `reports/gh_math2_unit8_bundle/UNIT8_V3_BUILD_REPORT.md` |

Domain `statistics.univariate_descriptive`：21 個 operation。總體使用母體公式（σ² = Σ(x−μ)²/n，對應 Excel `STDEV.P`）；答案以雙路徑（直接公式／展開數列）交叉驗證，不一致即拒絕出題。

## 四 Skill 狀態

| Skill | 題數 | Components | Sandbox | Tracker（正式） |
|---|---:|---:|---|---|
| gh_Mean | 9 | 9 | PASS | 0（未寫入） |
| gh_MedianAndPercentiles | 9 | 9 | PASS | 0 |
| gh_VarianceAndStandardDeviation | 10 | 10 | PASS | 0 |
| gh_DataScalingAndShifting | 7 | 7 | PASS | 0 |

## Family／Operation 覆蓋（35/35，無 BLOCKED）

| family | operation | 題目 |
|---|---|---|
| arithmetic_mean | arithmetic_mean | 12912 例1、12915 隨堂1 |
| weighted_mean_table | weighted_mean | 12913 例2 |
| weighted_mean_insurance | weighted_mean | 12916 隨堂2 |
| weighted_mean_unknown | weighted_mean_unknown | 12936 基礎2 |
| geometric_growth | geometric_growth_mean | 12914 例3、12937 基礎3 |
| geometric_growth_unknown | geometric_growth_unknown | 12917 隨堂3 |
| mean_claim | true_false_stat | 12931 觀念澄清1 |
| median_lists | median_lists | 12918 例4 |
| median_consecutive | median_consecutive | 12921 隨堂4 |
| percentile_frequency | percentile_frequency | 12919 例5、12922 隨堂5 |
| quartile_frequency | quartile_frequency | 12920 例6 |
| list_summary | list_summary_stats | 12935 基礎1 |
| quartile_inference | statement_selection | 12923 隨堂6 |
| median_claim | true_false_stat | 12934 觀念澄清4 |
| percentile_claims | statement_selection | 12946 進階6 |
| mean_var_sd | mean_variance_sd | 12924 例7、12927 隨堂7 |
| standard_deviation | standard_deviation | 12925 例8、12929 隨堂9、12938 基礎4 |
| compare_sd | compare_standard_deviation | 12928 隨堂8 |
| unknown_given_sd | unknown_given_sd | 12940 進階7 |
| sd_claim | true_false_stat | 12932 觀念澄清2 |
| grade_distribution | grade_distribution_read | 12926 例9 |
| grade_distribution_followup | grade_distribution_read | 12930 隨堂10 |
| linear_transform | linear_mean_sd | 12942 例10、12945 隨堂11 |
| linear_find_scale | linear_find_scale_sd | 12939 基礎5 |
| standardize | standardize_scores | 12943 例11 |
| monthly_mean_sd | monthly_mean_sd | 12944 例12 |
| scaling_claim | true_false_stat | 12933 觀念澄清3 |
| scaling_multi_select | statement_selection | 12941 進階8 |

新建 Generator：35（`src_12912`–`src_12946`）。沿用正式 promoted Domain：0（無既有統計 Domain）。Legacy `skills/backup_GenByGemini/gh_*.py` 未使用。

## Gate 結果

| Gate | 結果 |
|---|---|
| Sandbox pytest（`.venv`） | **40/40 PASS** |
| Seed0 教材錨點（例1/2/7/8、基礎2、進階7、例10/12、基礎5、隨堂7） | PASS |
| 表格題 stem 含 LaTeX `array` | PASS（含例2/5/6/11/12、隨堂2/5、基礎2、例9 資料表） |
| 例題9 多選 ①②④ + 頂標數學較高 | PASS（以 109 學測百分比向量作資料表，非重裁 PDF） |
| 正式教材 35 題 | 唯讀確認；未修改 |
| Promotion／Publish／正式 tracker | **未執行** |

### 變體數說明（非 FAIL）

下列 family 因題型本質（○×、多選敘述、學測圖表資料、唯一整數解結構）表面變體較少，測試允許 ≥1，不視為 Gate FAIL：

`12923, 12926, 12928, 12930–12934, 12940, 12941, 12946`

其餘 component 要求 ≥15 個 distinct surfaces（實際建置多為 20）。

## 表格／圖形

- **8 題統計表**：由 Domain／adapter 動態重建 LaTeX `array`（通過 sandbox）。
- **例題9／隨堂10**：生成側以國文／數學 0–15 級分百分比**資料表**承載題意；正式教材 PDF crop（Stage 1 資產）仍保留於教材例題，**未**改裁切、**未**重新匯入。生成題不依賴 Flask 顯示該 PNG。

## 隨堂練習10 `needs_review=true`

僅出現在 `source_description` 顯示字串；`notes.needs_review` 為空。V3 以 `textbook_example_id=12930` 輸入，**未**阻擋。

## 尚待人工決定

1. 是否核准 revision_0001 進行 Promotion／Publish（需另備部署腳本：backup → promote → rebuild → publish → verify-live → accept）。
2. 例題9／隨堂10 是否接受「資料表生成」替代「固定 PDF 圖」；若要求生成端也輸出長條圖，需另開 visual renderer 工作（本輪未做）。
3. 正式 Flask 載入 promoted 套件後可能需要重啟 5001（本輪未重啟）。

## 安全邊界（本輪遵守）

- 未修改／刪除正式 35 題教材列。
- 未重新匯入 DOCX／PDF。
- 未 Promotion／Publish／寫入正式 `gencode_component_tracker`。
- 未 commit／push；未重啟 Flask 5000／5001／Cloudflare。
