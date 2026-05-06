# Phase 5C-B0.1：B4 第 1 章二項式／組合恒等式 Must-Cover 驗證（唯讀）

**日期**：2026-05-06  
**範圍**：教師補充之統測常見 **6 類**二項式／組合恒等式代表題 × 現行 `question_router`、`generators/binomial.py`、`generators/combination.py`、wrappers、Chapter 1 deterministic allowlist  
**限制**：未修改任何程式、測試、generator、coverage matrix、routing；未新增 `problem_type_id`。

---

## 1. Verification 目的

確認統測常見的 **組合數和式／二項係數和／奇偶項和／展開與指定項／二變數與 Laurent 型** 等敘述，在 **live deterministic 單元練習鏈** 中是否已有對應 **problem_type**、是否 **allowlist 可出**、題幹是否與課本 **同構或僅部分同構**；並標註 **binomial_expansion_basic** 等政策排除項。

---

## 2. 代表題型總表

| 編號 | 課本／統測代表題型 | 建議 skill_id | 目前對應 skill_id | generator? | wrapper? | router? | allowlist? | 單元練習可達? | live 相似題? | 判定 | 備註 |
|:----:|-------------------|---------------|-------------------|------------|----------|---------|------------|---------------|--------------|------|------|
| 1 | 組合數 **錯列／遞移和**（例 \(C^3_0+C^3_1+C^4_2+\cdots\)） | `vh_數學B4_BinomialCoefficientIdentities` 或 `CombinationProperties` | **無專屬對應** | **否**（無專用題型） | — | **否** | 技能在 allowlist 但 **無此題** | 否 | **否** | **missing_generator** | `combination.py` 無 hockey-stick／對角和；`binomial.py` 亦無。 |
| 2 | **二項式係數總和** \(C^{n}_0+\cdots+C^{n}_n\)（例 \(n=12\)） | `vh_數學B4_BinomialCoefficientIdentities` | 同左 | **是** | 是 | 是（`binomial_coefficient_sum`） | 是 | 是 | **部分**（數學同 \((a+b)^n\) 令 \(x=1\)） | **partially_supported**／**supported_low_exposure** | 題幹為「\((ax+b)^n\) **所有係數和**」，非逐項寫 \(\sum C(n,k)\)；\(a=b=1\) 時答案為 \(2^n\)。 |
| 3 | **偶數項／奇數項係數和** | `vh_數學B4_BinomialCoefficientIdentities` | 同左 | **是** | 是 | 是（`binomial_odd_even_coefficient_sum`） | 是 | 是 | **部分** | **partially_supported** | 題幹為「**奇數／偶數次項**係數和」對 \((ax+b)^n\) 展開；與純 \(\sum_{k\text{偶}} C(n,k)\) 在 \((1+x)^n\) 語境下同構，**用語與抽樣**未必常出現 \((1+1)^n\)。 |
| 4 | **完整二項式展開**（例 \((3x+2)^4\)） | `vh_數學B4_BinomialTheorem` | 同左 | **是**（`binomial_expansion_basic`） | 是（wrapper 存在） | **否**（未掛入 `_REGISTRY`） | 是（skill） | 否（此題型） | **否**（runtime） | **excluded_or_future_ai_judged** | 答案為 **係數 list**／`supports_multiple_choice: False`；屬 Phase 4E **excluded**，**不得**硬接 int-only adaptive。 |
| 5 | **二變數齊次** \((2x-3y)^4\) 求 \(x^2y^2\) 係數 | `vh_數學B4_BinomialTheorem` | 同左 | **否**（無獨立題型） | 是 | **否** | 是 | — | **否** | **missing_generator** | 現有 `binomial_specific_term_coefficient` 為 **單變數** \((ax+b)^n\) 之 \(x^k\) 係數，**非** \((ax+by)^n\) 多項指數配對。 |
| 6 | **Laurent 型** \(\left(x-\frac{3}{x}\right)^6\) 求 \(x^4\) 係數 | `vh_數學B4_BinomialTheorem` | 同左 | **否** | 是 | **否** | 是 | — | **否** | **missing_generator** | `binomial_specific_*` 為整數次 \((ax+b)^n\)；**無** \(\frac{1}{x}\) 底。`binomial_specific_coefficient_with_negative_term` 僅 **負常數** \(b\)，非負次方。 |

---

## 3. 逐題判定

### 3.1 組合數錯列／遞移和（Hockey-stick 類）

- **歸類**：課本多在「組合恒等式／巴斯卡」脈絡；系統 **無**對應 `problem_type_id`。
- **現況**：`combination_properties_simplification` 有對稱、兩項和等；**無** \(\sum_j C(j,k)\) 或錯列下標之 **封閉題**。
- **單元練習**：`BinomialCoefficientIdentities`／`CombinationProperties` 雖在 allowlist，**無法**產出此形。
- **deterministic int**：和／差化簡後多為 **單一 int**，**適合**未來新 generator（本報告不實作）。

### 3.2 二項式係數總和 \( \sum_k C(n,k)=2^n \)

- **現有**：`binomial_coefficient_sum`（`binomial.py`）；數學上 \(\sum\) 係數 \(=\sum_k C(n,k)a^{n-k}b^k\big|_{x=1}=(a+b)^n\)。
- **Router**：掛在 `vh_數學B4_BinomialCoefficientIdentities`，與 `binomial_equation_solve_n`、`binomial_odd_even_coefficient_sum` **三選一**，曝光受 seed 影響。
- **與課本差異**：題面通常 **不**逐項列出 \(C^{12}_0+\cdots+C^{12}_{12}\)，而寫「\((ax+b)^n\) 所有係數和」。
- **判定**：**partially_supported**；若要「統測卷面」一致，屬 **template／敘述 enrichment**，非新數學。

### 3.3 偶數／奇數項係數和

- **現有**：`binomial_odd_even_coefficient_sum`；對 \((ax+b)^n\) 係數序列，依 **\(x\) 次方奇偶**（即索引 \(k\) 奇偶）加總。
- **與課本**：\((1+x)^n\) 下即 \(C(n,0)+C(n,2)+\cdots\) 等；抽樣常為一般 \(a,b\)，**敘述**未必像純組合數和。
- **單元練習**：同上，**三題型輪抽**，屬 **supported_low_exposure** 成分。

### 3.4 完整展開 \((3x+2)^4\)

- **現有程式**：`binomial_expansion_basic`（`binomial.generate`／`binomial_expansion_basic`），答案為 **係數序列**（`list`），`supports_multiple_choice: False`。
- **Router**：**未**列入 `vh_數學B4_BinomialTheorem` 的 `_REGISTRY`；`BinomialTheorem` 僅 `binomial_specific_term_coefficient`、`binomial_middle_term_coefficient`、`binomial_specific_coefficient_with_negative_term`。
- **Allowlist gate**：`b4_chapter1_deterministic_allowlist` 將 **`binomial_expansion_basic`** 列為 **excluded** deterministic adaptive。
- **結論**：**excluded_or_future_ai_judged**；**不建議**為了統測卷而硬改 int-only runtime（與 Phase 4E-16A/B 決策一致）。

### 3.5 二變數 \((2x-3y)^4\)，\(x^2y^2\) 係數

- **現有**：僅 **單變數** \((ax+b)^n\) 之指定 \(x^k\)（`binomial_specific_term_coefficient`）。
- **缺口**：需 **多項式／multinomial** 或固定 \(r,s\) 使 \(n=r+s\) 之 **二項**在 \(x,y\) 上分配；**目前無**。
- **deterministic int**：係數為 **int**，**適合**未來新 `problem_type`（不在本階段）。

### 3.6 \(\left(x-\frac{3}{x}\right)^6\)，\(x^4\) 係數

- **現有**：無 \((x + c/x)^n\) 之一般項；負常數版僅 **\((ax+b)^n\)** 且 \(b<0\)。
- **數學**：一般項涉及 **分式與指數聯立**，與現有 domain 不同。
- **deterministic int**：答案常為 int，**可**設計專題 generator；**目前 missing**。

---

## 4. 高優先真缺口

| 項目 | 狀態 |
|------|------|
| **組合遞移／錯列和** | **完全缺** generator／router |
| **二變數指定項係數** | **完全缺**（非單變數 \((ax+b)^n\) 可表） |
| **Laurent／含 \(\frac{1}{x}\) 底** | **完全缺** |
| **完整展開** | **有 generator、不接 router、adaptive 排除** → 應維持 **AI-judged／structured answer**，**不**硬接 int runtime |

---

## 5. 下一步建議（僅建議）

| 狀況 | 建議 |
|------|------|
| `binomial_coefficient_sum`／`binomial_odd_even` 已支援但卷面不像「\(\sum C(n,k)\)」 | **exposure calibration** + **small template enrichment**（加「令 \(x=1\)」或顯式 Sigma 敘述 **若產品允許**） |
| Hockey-stick／遞移和 | **new deterministic generator**（Phase 5C-B3），或教師材料 RAG，**非**僅改模板 |
| \((ax+by)^n\) 指定 \(x^py^q\) | **new deterministic generator**（multinomial 特例） |
| \((x+c/x)^n\) 指定次方 | **new deterministic generator**（參數化 \(n,c\)，指數方程求 \(r\)） |
| 完整展開 | **future AI-judged**／係數列正規化／手寫批改 backlog |

---

## 6. 建議優先順序（P1／P2／P3）

| 優先 | 題型／工作 | 理由 |
|------|------------|------|
| **P1** | **二變數指定項係數** \((ax+by)^n\) | 統測極常見、答案 **int**、與現有單變數 generator **明確分離**、補齊後覆蓋感最大。 |
| **P1** | **Laurent 型** \(\left(x+c/x\right)^n\) 指定次方 | 同為高頻、**int**、目前 **零支援**。 |
| **P2** | **組合遞移／錯列和** | 重要恒等式；需 **新題型** 或教材引導，工程量大於純模板。 |
| **P2** | **係數總和／奇偶項和** 之 **卷面對齊** | 數學已在 `binomial_coefficient_sum`／`binomial_odd_even_coefficient_sum`；**曝光 + 敘述**即可改善「看不出有考」。 |
| **P3** | **完整展開** | 維持 **excluded**；走 **AI-judged**，不與 int-only 混流。 |

---

**一句話結論**：統測卷上「**純組合數 Sigma**」「**雙變數／Laurent 指定項**」在現行 B4 **多為真缺口**；「**係數總和／奇偶和**」多半已由 **二項式代入法**覆蓋但 **題面不像課本**；「**完整展開**」**刻意不進** deterministic runtime。
