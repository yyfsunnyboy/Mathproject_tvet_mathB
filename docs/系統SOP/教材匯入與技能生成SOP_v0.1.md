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
