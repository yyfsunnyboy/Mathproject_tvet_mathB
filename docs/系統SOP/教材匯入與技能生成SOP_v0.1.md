# 教材匯入與技能生成 SOP v0.1

> 適用專案：`Mathproject_tvet_mathB`  
> 適用範圍：高職數學 B 冊教材匯入、技能生成、題目檢查、自適應學習鏈接建立  
> 目前驗證版本：數學 B4  
> 建議狀態：B4 已完成第一版教材匯入，可進入 adaptive links 建置

---

## 0. 核心原則

本系統不是單純把課本轉成題庫，而是建立：

1. 課程章節結構
2. skill / concept 架構
3. 例題、隨堂練習、章節習題、自我評量、統測題的 source_type 分流
4. 題目與 skill 的映射
5. 公式、圖片、表格缺失的保護機制
6. 自適應學習可用題與不可用題標記
7. 主線、補救、回主線的 prerequisite 關係

工作原則：

```text
AI 負責初步抽取與結構化
程式規則負責防幻覺、格式正規化、source_type 與 skill 對齊
人工只處理少數 needs_review 題
```

---

## 1. 匯入前準備

### 1.1 確認專案與環境

進入專案目錄：

```powershell
cd E:\Python\Mathproject_tvet_mathB
.\venv\Scripts\activate
python app.py
```

匯入前確認頁面選項：

```text
curriculum：vocational / 高職
publisher：longteng / 龍騰
volume：數學B4
chapter：對應章節
section：對應小節
```

若 log 出現：

```text
curriculum='general'
已選擇「普高龍騰」專用分析模型
skill_id=gh_...
```

表示選錯或判斷錯誤，該次匯入資料不可保留。

正確 log 應為：

```text
curriculum='vocational'
已選擇 高職數學B4 專用分析模型
skill_id=vh_數學B4_...
```

---

## 2. 檔案匯入策略

### 2.1 建議匯入順序

不要一次匯完整冊。建議依小節匯入：

```text
1-1
1-2
1-3
1-4
1-5
第1章自我評量

2-1
2-2
2-3
第2章自我評量

3-1
3-2
3-3
第3章自我評量
```

每次只匯一個小節，確認題目與 skill 正常後再進下一節。

### 2.2 不建議一次匯入整章的情況

若章節包含大量：

```text
圖片
表格
公式物件
統測題
章末自我評量
```

應拆小節處理。

---

## 3. 匯入後第一層檢查：模型與 skill namespace

匯入完成後，第一優先檢查：

```text
curriculum 是否為 vocational
skill_id 是否全部為 vh_數學B4_
是否誤產生 gh_ 開頭 skill
是否誤產生奇怪混合 skill
```

### 3.1 不可接受狀況

```text
gh_FrequencyDistributionTableSteps
gh_HistogramsAndFrequencyPolygons
gh_CumulativeFrequencyDistributions
```

這代表使用到普高 skill 系統，必須刪掉該批匯入結果並重匯。

### 3.2 建議增加防呆

若：

```text
volume=數學B4
curriculum=vocational
```

但即將寫入：

```text
skill_id startswith gh_
```

應中止匯入並提示：

```text
Vocational MathB4 import cannot write gh_ skill_id
```

---

## 4. source_type 規則

匯入時必須正確分流：

| 題目來源 | source_type |
|---|---|
| 例題 | textbook_example |
| 隨堂練習 | in_class_practice |
| 基礎題 | basic_exercise |
| 進階題 | advanced_exercise |
| 自我評量 | self_assessment |
| 統測題 | exam_practice |
| 動動手 | textbook_practice |
| 想一想 | textbook_practice |

### 4.1 self_assessment 特別規則

自我評量題目本來就沒有 linked_example，因此：

```text
source_type=self_assessment
linked_example=None
```

是正常狀態。

不可因為 missing linked_example 就自動：

```text
needs_review=true
```

只有以下情況才 needs_review：

```text
formula_missing
needs_formula_review
needs_image_review
block_boundary_error
選項缺失
圖片缺失
題幹不可讀
```

---

## 5. 公式與符號正規化

### 5.1 填空符號

以下符號應正規化為 `[BLANK]` 或語意化為「空格」：

```text
□
□□
▢
◻
☐
（　）
(　)
＿＿
__
```

例：

```text
試填入下列各式□之值
```

應改為：

```text
試填入下列各式空格之值
```

### 5.2 排列組合 P/C

所有排列組合記號統一為：

```latex
P^{n}_{r}
C^{n}_{r}
```

支援轉換：

```text
⁵P₃ → P^{5}_{3}
P₃⁵ → P^{5}_{3}
P^5_3 → P^{5}_{3}
P_{3}^{5} → P^{5}_{3}
{}^{5}P_{3} → P^{5}_{3}

⁸C₂ → C^{8}_{2}
C₂⁸ → C^{8}_{2}
C^8_2 → C^{8}_{2}
{}^{8}C_{2} → C^{8}_{2}
```

安全限制：

```text
不可從 [FORMULA_MISSING] 猜公式
不可從 [FORMULA_IMAGE_*] 猜公式
不可把 P(A) 當排列 P
不可把機率 P(A∩B) 改成排列
```

### 5.3 機率事件符號

機率章中，以下應包成 LaTeX inline math：

```text
P(A) → \(P(A)\)
P(B) → \(P(B)\)
P(A \cap B) → \(P(A \cap B)\)
P(A \cup B) → \(P(A \cup B)\)
P(A') → \(P(A')\)
P(B') → \(P(B')\)
P(A-B) → \(P(A-B)\)
P(B-A) → \(P(B-A)\)
```

不可改成排列組合。

### 5.4 集合符號

集合題應包成 inline math：

```text
A \subset B → \(A \subset B\)
A \cap B → \(A \cap B\)
A \cup B → \(A \cup B\)
A={1,2,3} → \(A=\{1,2,3\}\)
```

---

## 6. 圖片與表格題處理

### 6.1 圖片題目前策略

目前圖片題先不作為學生自動抽題來源。

若題目依賴圖片但未掛上 image_assets，標記：

```json
{
  "has_image": true,
  "needs_image_review": true,
  "missing_docx_image_asset": true,
  "adaptive_usable": false
}
```

並在題目文字中可加：

```text
（圖片待補）
```

### 6.2 圖片題可接受狀態

圖片缺失不代表整章失敗，只要：

```text
題目有建立
skill 正確
source_type 正確
needs_image_review=true
沒有讓 AI 猜圖片內容
```

即可先給過。

### 6.3 不可接受狀態

```text
圖片題沒有圖
也沒有 needs_image_review
答案是 AI 根據不存在圖片猜出來
```

這種題必須手修或停用。

### 6.4 未來處理方向

圖片題後續分三類：

```text
統計圖表題：優先用 chart_data 自動生成
幾何 / 路線 / 棋盤圖：保留原圖或人工補少數重要題
低價值圖片題：停用或刪除
```

現階段不建議為圖片問題重構匯入器。

---

## 7. 章節專用規則摘要

### 7.1 第 1 章：排列組合

建議 skill 主線：

```text
AdditionPrinciple
MultiplicationPrinciple
PermutationOfDistinctObjects
PermutationOfNonDistinctObjects
CombinationDefinition
CombinationProperties
BinomialTheorem
BinomialCoefficientIdentities
PascalTriangle
```

重點檢查：

```text
P/C 格式是否正確
填空符號是否正確
低價值 [FORMULA_MISSING] 純計算題可略過
自我評量依 1-1 / 1-2 / ... 小節歸類
```

### 7.2 第 2 章：機率

建議 skill 主線：

```text
BasicConceptsOfSets
SampleSpaceAndEvents
ProbabilityDefinition
ProbabilityProperties
ConditionalProbability
IndependentEvents
MathematicalExpectation
ApplicationsOfExpectation
```

重點檢查：

```text
P(A) 不可被改成排列
P(A \cup B)、P(A \cap B) 要包成 inline math
集合符號要包成 inline math
自我評量不要全部 needs_review
```

### 7.3 第 3 章：統計

建議 skill 主線：

```text
MeaningOfStatistics
SamplingSurvey
SamplingMethods
DataOrganizationAndCharts
FrequencyDistributionTableConstruction
HistogramsAndFrequencyPolygons
CumulativeFrequencyTablesAndGraphs
CentralTendencyMeasures
WeightedMean
DispersionMeasures
VarianceAndStandardDeviation
LinearTransformationOfData
NormalDistributionAndEmpiricalRule
OpinionPollInterpretation
```

重點檢查：

```text
3-1 基礎題 1～8、進階題 9～10 是否完整
3-2 基礎題 1～8、進階題 9～10 是否完整
3-3 例題與常態分配題是否完整
圖片題是否標 needs_image_review
公式缺失題是否標 needs_formula_review
```

---

## 8. 匯入完成判斷標準

### 8.1 可以給過

若符合：

```text
curriculum=vocational
skill_id=vh_數學B4_...
題目大多完整
source_type 正確
圖片題已標記 needs_image_review
公式缺失題已標記 needs_formula_review
沒有 AI 補猜公式
沒有 gh_ skill 污染
```

即可給過。

### 8.2 不給過，需重匯

若出現：

```text
curriculum=general
skill_id=gh_...
大量漏題
例題 / 隨堂練習沒有匯入
習題明確題號大量消失
公式缺失但 AI 自行補公式
圖片題沒有圖也沒有 needs_image_review
```

需刪掉該批資料，修規則後重匯。

### 8.3 可手修，不必重匯

若只是：

```text
少數 1～2 題漏掉
少數 LaTeX 沒包好
少數 skill 分錯
圖片題待補
單題詳解錯誤
metadata 殘留
```

直接手修，不要重匯整節。

---

## 9. B4 完成後下一步：adaptive links

完成 B4 題庫後，不建議立刻匯 B1～B3。  
建議先建立 B4 自適應學習鏈接：

```text
skill_curriculum
skill_prerequisites
skill_family_bridge
adaptive_usable 題目標記
```

### 9.1 建議新增腳本

```text
scripts/build_mathb4_adaptive_links.py
```

功能：

```text
1. 檢查 B4 skill 是否存在
2. 建立主線順序
3. 建立 prerequisite 關係
4. 建立 skill_family_bridge
5. 將 needs_review / 圖片待補 / formula_missing 題標 adaptive_usable=false
6. 輸出 reports/mathb4_adaptive_links.md
```

執行方式：

```powershell
python scripts/build_mathb4_adaptive_links.py --dry-run
python scripts/build_mathb4_adaptive_links.py --apply
```

---

## 10. B4 匯入完成備份

完成一冊後，必須先備份資料庫核心表。

建議匯出：

```text
skills_info
skill_curriculum
textbook_examples
skill_family_bridge
skill_prerequisites
```

若使用後台 DB maintenance，確認 log 類似：

```text
exporting core table skills_info
exporting core table skill_curriculum
exporting core table textbook_examples
exporting core table skill_family_bridge
exporting core table skill_prerequisites
```

備份後再繼續進行 adaptive links 或下一冊匯入。

---

## 11. 操作總結

本 SOP 建議的工作流：

```text
1. 小節匯入
2. 檢查 curriculum / skill namespace
3. 檢查 source_type
4. 檢查題目完整性
5. 檢查符號與公式
6. 圖片題標記待補
7. 少數錯題手修
8. 一章完成後檢查自我評量
9. 一冊完成後備份
10. 建立 adaptive links
11. 再考慮匯入下一冊
```

目前 B4 狀態可定義為：

```text
數學B4 教材匯入初版完成
圖片題暫不啟用
少數 needs_review 題保留人工複核
下一步：建立 B4 自適應學習鏈接
```

---

## Chapter Runtime 建置流程（Phase 4E 經驗版）

### 一、適用範圍

本流程適用於高職數學 B 冊章節 runtime 建置、deterministic int-answer 一般練習頁，以及 generator、question_router、skill wrapper、web smoke test、freeze report 的標準建置流程。後續 B4 Chapter 2 / Chapter 3，以及 B1～B3 題型建置，應以本節作為 runtime 建置基準。

本流程不包含 adaptive route、future_ai_judged / handwriting checked runtime、free-response 題型、證明 / 推導 / 圖形 / 完整列舉題型。

### 二、核心原則

1. coverage matrix 是進度唯一來源之一。
2. 不以「感覺已完成」作為完成依據。
3. 每批最多處理 2～3 個 generator。
4. generator 先完成 pytest，再做 sample QA。
5. sample QA 通過後，才接 question_router / wrapper。
6. router / wrapper 測試通過後，才做 web smoke test。
7. web smoke test 通過後，才更新 coverage matrix 與 freeze summary。
8. 不適合 deterministic int-answer runtime 的題型，不硬接。
9. `list[int]`、`list[str]`、圖形、完整展開、完整列舉、證明、推導、手寫過程題，應標記 manual_review / future_ai_judged。
10. Chapter closure report 是進入 adaptive route 前的凍結基線。

### 三、標準流程

#### Step 0：建立 coverage matrix

1. 盤點 problem_type。
2. 標記 priority。
3. 標記 runtime_ready / planned_only / excluded / manual_review-like。
4. 明確區分 generator_ready、router_ready、wrapper_ready、web_smoke_tested。
5. coverage matrix 必須反映實際 runtime 狀態，不得只記錄理論規劃。

#### Step 1：選定一小批 generator

1. 每批最多 2～3 個。
2. 優先選 int-answer、選擇題、短答案。
3. 避免先碰 list / free-response / 視覺題。

#### Step 2：實作 deterministic generator

1. 使用 seed。
2. 支援 `seen_parameter_tuples`。
3. answer 由 domain function 計算。
4. output contract 完整。
5. choices 合法。
6. LaTeX 合規。
7. 不讀 DB / session / route / frontend。
8. 不呼叫 AI / LLM。

#### Step 3：generator pytest

1. 驗 answer 正確。
2. 驗 choices。
3. 驗 metadata。
4. 驗 LaTeX。
5. 驗 placeholder 不存在。
6. 驗 seed deterministic。
7. 驗 seed 1～5 `parameter_tuple` 不重複。
8. 驗 `seen_parameter_tuples`。
9. 驗 50 次重抽失敗 raise `ValueError`。

#### Step 4：sample QA report

1. 每個 generator 產生 seed 1～5 共 5 題。
2. 人工檢查題幹是否像課本。
3. 檢查 explanation 是否清楚。
4. 檢查 LaTeX。
5. 檢查 choices / answer / metadata。
6. 若 QA 發現問題，先做 QA-Fix，不接 router。

#### Step 5：接入 question_router / wrapper

1. 只在 QA 通過後接入。
2. 優先使用既有 wrapper。
3. wrapper 不直接 import generator。
4. wrapper 不寫題型邏輯。
5. wrapper check 只做 int / string 比對。
6. 新 skill 才新增 wrapper。
7. 不接入 `list[int]` / `list[str]` 題型。

#### Step 6：router / wrapper pytest

1. `generate_for_skill` 指定 `problem_type_id` 可產題。
2. 不指定 `problem_type_id` 時只會產出該 skill 支援清單。
3. `correct_answer == answer`。
4. choices 合法。
5. router_trace 完整。
6. canonical `skill_id` 正確。
7. 不得重新引入亂碼 alias，例如 `vh_?詨飛B4_*`。

#### Step 7：web smoke test

1. 開 practice page。
2. 可正常產題。
3. 可判斷答對 / 答錯。
4. LaTeX 顯示正常。
5. terminal 無 500 error。
6. 多按幾次下一題，確認不同 problem_type 有機會出現。

#### Step 8：freeze

1. 更新 coverage matrix。
2. 更新 coverage summary。
3. 輸出 phase freeze summary。
4. 記錄 pytest passed 數量。
5. 記錄 web smoke test 頁面。
6. 記錄未修改哪些檔案。
7. 若只做 depth expansion，不要亂改原始 coverage 分母。

#### Step 9：closure report

1. planned_only 歸零或全部有明確 future path 後產出。
2. 說明 runtime_ready 數量。
3. 說明 manual_review / excluded-like 題型。
4. 說明不代表全教學型態完成。
5. 作為 adaptive route 前置基線。

### 四、Output Contract 標準

generator payload 必須包含：

1. `question_text`
2. `choices`
3. `answer`
4. `explanation`
5. `skill_id`
6. `subskill_id`
7. `problem_type_id`
8. `generator_key`
9. `difficulty`
10. `diagnosis_tags`
11. `remediation_candidates`
12. `source_style_refs`
13. `parameters`

補充規範：

1. router / wrapper 層可補 `correct_answer`。
2. `parameters` 必須包含 `parameter_tuple`。
3. answer 型態原則上為 `int`。
4. `multiple_choice=True` 時，choices 需 4 個唯一且含 answer。
5. `multiple_choice=False` 時，`choices == []`。
6. LaTeX 必須包在 `$...$`。
7. 不可輸出裸 `2^2`、`C(n,r)`、`P(n,r)`。

### 五、LaTeX 規範

1. 數學式用 `$...$`。
2. 指數用 `^{...}`。
3. 乘號用 `\times`。
4. 組合用 `$C^{n}_{r}$` 或 `$\binom{n}{r}$`。
5. 排列用 `$P^{n}_{r}$`。
6. 階乘用 `$n!$`。
7. 二項式用 `$(ax+b)^{n}$`。
8. 不允許裸文字 `2^2`。
9. 不允許裸文字 `C(n,r)`。
10. 不允許裸文字 `P(n,r)`。
11. 不允許 explanation 中出現 `5!*2!` 或全形 `×` 未包 LaTeX。

### 六、manual_review / future_ai_judged 判定規則

下列題型不應硬接 deterministic runtime，應改列：

```text
manual_review / future_ai_judged / future_free_response / normalization_required
```

適用類型：

1. answer 為 `list[int]` 的完整係數列表題，例如 `binomial_expansion_basic`。
2. answer 為 `list[str]` 的完整列舉題，例如 `tree_diagram_listing` 若要求列出所有結果。
3. 視覺化題，例如樹狀圖、圖形作答。
4. 證明 / 推導題，例如 `pascal_triangle_derivation`。
5. 手寫過程題，需 AI / OCR / teacher review。

這些題型不是放棄，而是走另一條 runtime：

1. textbox disabled / readonly。
2. 學生用手寫區或上傳圖片作答。
3. OCR / vision model 解析學生作答。
4. AI 助教依 rubric 判斷：
   - `correct`
   - `incorrect`
   - `partially_correct`
   - `needs_review`

### 七、B4 Chapter 1 實例摘要

| 類別 | 數量 |
|---|---:|
| problem_type 總數 | 28 |
| runtime_ready | 25 |
| planned_only | 0 |
| manual_review / excluded-like | 3 |

runtime_ready 包含 Counting / Addition / Multiplication Principle、Permutation、Combination、Factorial、Binomial int-answer。

manual_review / excluded-like：

1. `binomial_expansion_basic`
2. `tree_diagram_listing`
3. `pascal_triangle_derivation`

說明：

1. 這代表 deterministic int-answer runtime 實質收尾。
2. 不代表 Chapter 1 所有教學型態完成。
3. adaptive route 尚未接入。
4. future_ai_judged runtime 尚未接入。

### 八、常見錯誤與禁止事項

1. 不要還沒 QA 就接 router。
2. 不要 web smoke 未測就 freeze。
3. 不要為了提高 coverage 硬接 `list[int]` / `list[str]`。
4. 不要把樹狀圖改成假計數題後宣稱完成樹狀圖能力。
5. 不要把完整展開題硬塞進 int-answer wrapper。
6. 不要在 wrapper 寫 generator 邏輯。
7. 不要修改 route / frontend 解決單一題型問題。
8. 不要重新引入亂碼 `skill_id` alias。
9. 不要讓 coverage matrix 與實際 router 狀態脫節。
10. 不要一次大量接入未經 QA 的題型。

### 九、進入 adaptive route 前的條件

進入 Phase 4F adaptive route 前，至少需具備：

1. Chapter deterministic runtime closure report。
2. coverage matrix planned_only 已歸零，或所有 planned_only 都有明確 future path。
3. 主要 skill practice page 已 web smoke 通過。
4. question_router canonical `skill_id` 已清理。
5. manual_review 題型不混入 deterministic runtime。
6. 已選定 3～5 個穩定 skill 作為 adaptive 試接候選。
7. 另建 adaptive coverage matrix，不與 deterministic coverage 混淆。

## 本次更新紀錄

更新日期：2026-05-05。

1. 新增 Chapter Runtime 建置流程。
2. 納入 B4 Chapter 1 deterministic runtime closure 經驗。
3. 明確加入 manual_review / future_ai_judged 判定規則。
4. 明確記錄不適合硬接 int-answer runtime 的題型。
5. 本次參考文件均已讀取；未缺少指定 reports。
