# Phase 5C-B0-Followup：B4 第 1 章課本代表題型 Must-Cover 驗證（唯讀）

**日期**：2026-05-06  
**範圍**：教師人工指出的 6 類代表題型 × 現行 `question_router`／generators／wrappers／`B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST`／章節單元練習可達性  
**限制**：未修改任何 production code、tests、generators、coverage matrix、adaptive routing；未新增 `problem_type_id`。

**參考文件**：`b4_phase5c_a_b4_ch1_unit_practice_generator_coverage_audit.md`、`b4_phase5c_b4_small_template_enrichment_summary.md`

---

## 1. Verification 目的

對照課本敘事與 **live deterministic 產題鏈**，判斷 6 類題型是否：

- 已有對應 **problem_type_id**／generator／router／wrapper；
- 技能是否在 **Chapter 1 單元練習 allowlist** 內而可實際抽到；
- 題幹語意是否與課本例 **足夠相似**（或僅數學結構相同）；
- 若缺，是否仍屬 **int-answer friendly** 而適合未來補 deterministic generator，或應歸 **AI-judged**。

---

## 2. 代表題型總表

| 編號 | 課本代表題型 | 建議 skill_id | 目前對應 skill_id | generator? | wrapper? | router? | allowlist? | 單元練習可達? | live sampling 相似題? | 判定 | 備註 |
|:----:|--------------|---------------|-------------------|------------|----------|---------|------------|---------------|----------------------|------|------|
| 1 | 乘法原理：兩類各選一人（例：內科 3、外科 4） | `vh_數學B4_MultiplicationPrinciple` | 同左 | 是 | 是 | 是（`mult_principle_independent_choices`） | 是 | 是 | **是**（結構同型；`seed=1` 預設為兩階段 **3×4**） | **supported_visible** | 題幹用「獨立階段」敘事，非「護理師」專屬用語，數學為兩步驟相乘。 |
| 2 | 質因數分解求正因數個數（例：\(600=2^3\cdot3\cdot5^2\)） | `vh_數學B4_MultiplicationPrinciple` | 同左 | 是 | 是 | 是（`divisor_count_prime_factorization`） | 是 | 是 | **是**（\(N=\prod p_i^{a_i}\) 問正因數個數） | **supported_visible** | 底數由抽樣決定，**不保證**出現「600」此一數值，但公式與課本例同型。 |
| 3 | 階乘方程求 \(n\)（例：\(7!\,n=10!\)、\(10!+8!=n\cdot8!\)） | `vh_數學B4_FactorialNotation` | 同左 | **部分** | 是 | 是（`factorial_equation_solve_n`） | 是 | 是 | **弱**（僅 \(\frac{n!}{(n-1)!}=k\) 型） | **partially_supported** | 現行 generator **僅**單一比值解 \(n=k\)；**未**涵蓋乘積移項、兩階乘和／積等課本變形。 |
| 4 | 相異物排列：角色分派（例：10 人選 3 人任班長、學藝、康樂） | `vh_數學B4_PermutationOfDistinctObjects` | 同左 | 是 | 是 | 是（`permutation_role_assignment`） | 是 | 是 | **是**（\(P(n,r)\)「不同職務」） | **supported_visible** | 題幹為泛化「不同職務」，**未**逐題列出職稱，數學一致。 |
| 5 | 相鄰／**不相鄰**（例：3 男 2 女，兩女必鄰／兩女不鄰） | `vh_數學B4_PermutationOfDistinctObjects` | 同左 | **部分** | 是 | 是（`permutation_adjacent_block` 等） | 是 | 是 | **相鄰：是**；**不相鄰：否** | **partially_supported** | `permutation_adjacent_block` 為 **必鄰**（捆綁法）；程式庫中 **未**檢出「不得相鄰／插空」專用 generator。 |
| 6 | 棋盤格最短路徑（任意走、經乙、不經乙） | （課本多歸排列組合／乘法原理延伸） | **無單一對應** | **否** | — | **否** | — | — | **否** | **missing_generator** | `question_router`／`generators` 內 **無** lattice path／\(\binom{m+n}{m}\) 類 **problem_type**；與 `mult_principle_independent_choices` 語意也不同。 |

**說明**

- **單元練習可達**：上述 skill 皆在 `b4_chapter1_deterministic_allowlist.py` 之 `B4_CHAPTER_1_ADAPTIVE_SKILL_ALLOWLIST` 內（除第 6 類無 skill）。
- **live sampling**：第 1 類以唯讀執行 `mult_principle_independent_choices(..., seed=1)`／router 指定 `problem_type_id` 可得到 **counts [3,4]** 之兩階段相乘，與護理師例同構。

---

## 3. 逐題判定

### 3.1 乘法原理：兩類各選一人

- **歸類**：`vh_數學B4_MultiplicationPrinciple`。
- **現有**：`mult_principle_independent_choices`（`counting.py`）；題型為多階段獨立選法相乘。
- **單元練習**：在 allowlist；與其他 2 個題型（因數個數、數字不重複）**共用 router 三筆**，抽中機率非 100%，屬正常 **exposure** 議題。
- **課本語感**：可用 **3×4** 等參數對齊護理師例；若教師堅持「科別＋人名」敘事，屬 **template／曝光** 層，非缺 generator。

### 3.2 質因數分解求正因數個數

- **歸類**：`vh_數學B4_MultiplicationPrinciple`。
- **現有**：`divisor_count_prime_factorization`；題幹為 \(N=\prod p_i^{a_i}\)，求正因數個數 \(\prod(a_i+1)\)。
- **單元練習**：同上，三題型抽樣。
- **與 600 例**：數學完全同型；**不保證**出現 \(2^3\cdot3^1\cdot5^2\) 此一組合。

### 3.3 階乘方程求 \(n\)（乘積／和式）

- **歸類**：`vh_數學B4_FactorialNotation`。
- **現有**：`factorial_equation_solve_n` **僅**產生 \(\frac{n!}{(n-1)!}=k\)（即 \(n=k\)）之敘述（見 `counting.py` 內文）。
- **缺口**：\(7!\cdot n=10!\)（兩階乘商為整數）、\(10!+8!=n\cdot8!\) 等需 **約化／移項** 的變形 **未**覆蓋。
- **判定**：**partially_supported**；若要對齊課本，需 **新變體或新題型**（本報告不新增 `problem_type_id`，僅記錄缺口）。

### 3.4 角色分派（\(P(n,r)\)）

- **歸類**：`vh_數學B4_PermutationOfDistinctObjects`。
- **現有**：`permutation_role_assignment`（`permutation.py` 之 `generate`）；\(P(n,r)\) 與「不同職務」一致。
- **單元練習**：在五筆 router entry 中抽樣；**曝光**低於單 entry 技能，但題型 **已支援**。
- **課本**：班長／學藝／康樂可視為 **\(r=3\) 三職**；現為泛化職務敘述。

### 3.5 相鄰／不相鄰

- **相鄰**：`permutation_adjacent_block`；捆綁後 \((n-b+1)!\times b!\)，可對應「兩女必鄰」（\(n=5,b=2\)）等。
- **不相鄰**：全文檢索 `permutation.py`／`counting.py`／`combination.py` **無**「不相鄰」「插空」等 **獨立** problem type；**判定為真缺口**（數學上多為 int-answer，適合未來 deterministic）。
- **單元練習**：`PermutationOfDistinctObjects` 在 allowlist；相鄰題 **可出現**；不相鄰 **目前無法**由現 generator 產出。

### 3.6 棋盤格最短路徑（含過境／禁過境）

- **預期數學**：格線僅能向上／向右時，總步數為 \(\binom{m+n}{m}\)；經過特定點可拆段相乘；不經過某點可用總數減去經過該點（或排容）。
- **現況**：B4 `question_router` **無**對應 entry；generators **無**棋盤／捷運方格敘事之專用題型（僅 `mult_principle_independent_choices` 有「搭公車、轉捷運」等 **文字**，非格點路徑計數）。
- **判定**：**missing_generator**；若僅考單純 \(\binom{m+n}{m}\)，屬 **int-answer friendly**，適合列 **Phase 5C-B3** 候選（實作不在本 follow-up）。

---

## 4. 高優先真缺口（驗證後）

| 缺口 | 說明 |
|------|------|
| **棋盤／格線最短路徑** | Router／generator **皆無**；課本代表性高，且典型子題為 **整數組合數**。 |
| **排列「不相鄰／插空」** | **必鄰**已有 `permutation_adjacent_block`；**不鄰**無對應 deterministic 題型。 |
| **階乘方程變形** | 有 `factorial_equation_solve_n` 但 **題幹形狀過窄**；課本乘除、加乘混合例 **未覆蓋**。 |

**已支援但可能「感覺少」**（非真缺 generator）：乘法原理（護理師敘事）、因數個數（特定 600）、角色分派（具名職稱）— 多為 **template／曝光** 問題。

---

## 5. 下一步建議（僅建議，不改程式）

| 狀況 | 建議標籤 |
|------|-----------|
| 已有 generator 與 allowlist，但與課本敘事或抽中率不符 | **Phase 5C-B1 exposure calibration**（router 抽樣／教學路徑加權／模板用語；**不**在本階段動程式） |
| 同一 `problem_type` 可擴句、不新增題型 | **Phase 5C-B4.1 small template enrichment**（與 5C-B4 同哲學；**本 follow-up 不修改 generator**） |
| 完全無 generator、且 int-answer 合理 | **Phase 5C-B3 new deterministic generator**（例：格線最短路徑、不相鄰排列） |
| 證明、多段文字、圖示、或答案非單一 int | **future AI-judged backlog**（本 6 類中多數仍偏 int，僅若未來加入「畫路徑說明」等再評估） |

---

## 6. 建議優先順序（P1／P2／P3）

| 優先 | 題型／議題 | 理由 |
|------|------------|------|
| **P1** | **棋盤格最短路徑**（含經過／不經過定點） | **完全缺**；課本與統測常見；核心答案多為 **組合數或乘積**，適合 deterministic。 |
| **P2** | **不相鄰排列** | **必鄰已有**；**不鄰**為對偶重要題型，int-answer 明確，補齊後課本覆蓋感提升大。 |
| **P2** | **階乘方程變形** | 已有入口 skill／router slot，但 **題幹形狀不足**；擴充變體比從零建 skill 便宜。 |
| **P3** | 乘法原理「兩科各選一人」**專屬語境**、因數題 **固定數值 600**、角色分派 **具名職務** | 屬 **template／曝光**，數學已支援；可排在真缺口之後。 |

---

**結論（一句話）**：6 類中 **4 類**在現行鏈上為 **supported**（其中階乘方程僅 **部分**題幹形狀、相鄰僅 **半套**）；**棋盤最短路徑為完整 missing**；**女生不相鄰為明確 missing**。後兩者最適合列為下一輪 **B3 能力建置**優先，階乘變形與曝光列 **B1／B4.1**。
