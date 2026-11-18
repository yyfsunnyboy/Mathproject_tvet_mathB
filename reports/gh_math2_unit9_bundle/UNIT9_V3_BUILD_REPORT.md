# 普高數學2 Unit 9 二維數據分析 — GenCode V3 候選建置報告

**狀態**：Candidate Domain + Sandbox + Bundle `ready_for_human_review`（未核准、未 Promotion、未 Publish）  
**Domain**：`statistics.bivariate_descriptive`  
**Bundle**：`reports/domain_operation_workspaces/capability_statistics_bivariate_descriptive_affe15e1/revision_0001`  
**Dry-run**：`tmp/gh_math2_unit9_sandbox_dryrun`（21 Publish 候選）  
**混合出題**：5 題 DEFERRED 已登錄 `configs/fixed_textbook_practice.json`（`mode=ungraded`）

---

## 1. 範圍與原則

- 教材 Stage 1 既有封板列（ids 12947–12972）唯讀引用；**未**重匯入、**未**改正式 DB、**未**重啟 Flask。
- **Partial Publish**：能通過正式 Gate 的題目走 GenCode V3；不能合理動態生成或拓撲不完整者保留完整原題。
- GenCode 是變化性手段，不是保留教材的先決條件。
- Exact `Fraction`；雙路徑交叉；不一致即拒絕樣本。

### 教科書公式（實作）

- \(S_{xx}=\sum(x-\mu_x)^2\)，\(S_{yy}=\sum(y-\mu_y)^2\)，\(S_{xy}=\sum(x-\mu_x)(y-\mu_y)\)
- \(r=S_{xy}/(\sqrt{S_{xx}}\sqrt{S_{yy}})\)
- y 對 x 迴歸：\(m=S_{xy}/S_{xx}=r\cdot\sigma_y/\sigma_x\)，\(b=\mu_y-m\mu_x\)

---

## 2. 發布清單（21 V3 + 5 原題）

### GenCode V3 候選（21；Publish 清單）

| Skill | IDs |
| --- | --- |
| gh_CorrelationCoefficient | 12949–12953, 12957–12959, 12967–12968, 12972（11） |
| gh_LeastSquaresMethodAndRegressionLine | 12955–12956, 12961–12962, 12964–12966, 12969–12971（10） |
| gh_ScatterPlot | （無 V3 元件） |

Sandbox：`tests/gencode/test_gh_math2_unit9_bivariate_statistics_sandbox.py`（含 retained 12963 預測運算證據）。

### DEFERRED / 原題保留（5；fixed ungraded）

| ID | 原因 | Fallback |
| --- | --- | --- |
| 12947 | 僅繪散布圖 | 原題 + handwriting 畫布；未評分 |
| 12948 | 讀既有散布圖判相關方向 | 原題 + 圖；未評分 |
| 12954 | 四張散布圖 r 排序 | 原題 + 圖；未評分 |
| 12960 | 依圖選可能的 r | 原題 + 圖／選項；未評分 |
| 12963 | 例題6 拓撲＝選散布圖 + 迴歸估計；V3 僅覆蓋估計 | 完整原題 + 圖；未評分。預測半段 domain op 保留為 RETAINED 證據，**不**進 Publish |

---

## 3. 混合出題 Runtime（隔離驗收）

機制（既有，未另建系統）：

1. Publish 後：`textbook_order_practice` 依 Stage 1 `source_order` 混合 `src_<id>` 與 `fixed_textbook_practice` 登錄列。
2. 未登錄列不出題；故五題 DEFERRED 必須登錄（已完成）。
3. 三 Skill 已在 `UNGRADED_NO_VERIFIED_ANSWER_SKILLS`；fixed `ungraded` 亦不寫成績／掌握度。
4. 跨題依賴（12967）仍帶入例題6 資料且未評分。

測試：`tests/test_gh_math2_unit9_mixed_fallback_practice.py` + 既有 source-dependency 測試 → **PASS**。

---

## 4. 26 題學生練習去向

| 去向 | 數量 | IDs |
| --- | ---: | --- |
| V3 動態生成（核准 Publish 後） | 21 | 見上表 |
| 原題未評分練習（mixed / Fallback） | 5 | 12947, 12948, 12954, 12960, 12963 |
| 暫時不可安全出題 | 0 | — |

Publish 前（尚無 facade）：三 Skill 皆走原題 Fallback；五題因 fixed 登錄帶 scaffold／handwriting；其餘亦因 Skill 列入未評分清單而不自動判分。

---

## 5. 驗證

```text
pytest tests/gencode/test_gh_math2_unit9_bivariate_statistics_sandbox.py \
       tests/test_gh_math2_unit9_mixed_fallback_practice.py \
       tests/test_gh_math2_unit9_source_dependency_practice.py -q
→ 40 passed
```

未跑全域 pytest。正式 DB 唯讀。未執行正式瀏覽器／`verify-live`／`accept`。

---

## 6. 教師一次確認事項

1. 是否核准 revision_0001 對 **21** 題 Promotion／Publish。  
2. 五題 DEFERRED 維持原題未評分是否可接受（含 12963 完整原題而非半套 Generator）。  
3. `pending_final_acceptance` 是否改為指定教師身分。  
4. Publish 後是否重啟 Flask 5001。

---

## 7. 安全邊界（本輪遵守）

- 未修改正式 26 題教材列；未重新匯入。  
- 未 Promotion／Publish／寫入正式 tracker。  
- 未 commit／push；未重啟 Flask 5000／5001／Cloudflare。  
- 未將 `pending_final_acceptance` 改為已核可。
