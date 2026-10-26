# 數學2 Unit 1「數列與遞迴關係」GenCode V3 — 整單元審閱報告

- Bundle：`reports/domain_operation_workspaces/capability_sequence_progression_ba7ea8dc/revision_0001/promotion_bundle.json`（review.status = **ready_for_human_review**，approved_by 為空；尚未 Promotion、尚未 Publish）
- domain `sequence.progression`：7 個 operations，套件 5 個檔案（SHA-256 鎖定）；Bundle SHA-256 `3d1cb59939d97743…`
- 正式教材（唯讀核對）：39 題（Stage 1 READY）

## 三個 Skill 狀態

| Skill | 教材題數 | 可用 Component（PASS） | DEFERRED | 狀態 |
|---|---|---|---|---|
| `gh_Sequence` | 19 | 17 | 2 | Bundle 就緒、隔離發布演練通過 |
| `gh_RecursiveRelation` | 13 | 9 | 4 | Bundle 就緒、隔離發布演練通過 |
| `gh_MathematicalInduction` | 7 | 0 | 7 | 無可生成的 Component（全部 DEFERRED），不隨本單元發布 |

合計：39 題 = **26 PASS** + **13 DEFERRED**（覆蓋率 66.7%）。

## DEFERRED 與原因

- **12668**（例題2，gh_Sequence）：題幹依賴教材圖形（含圖形選項），目前沒有已驗證的圖形渲染與判圖契約，不可只靠文字出題：例題2 的數字螺旋路徑圖與 ①–④ 路徑選項圖
- **12673**（隨堂練習2，gh_Sequence）：題幹依賴教材圖形（含圖形選項），目前沒有已驗證的圖形渲染與判圖契約，不可只靠文字出題：隨堂練習2 的左手計數路徑圖（依圖歸納 a_n 與手指對應）
- **12686**（例題6，gh_RecursiveRelation）：圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律：例題6 的正六邊形地磚排列
- **12694**（1習題 基礎題5，gh_RecursiveRelation）：圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律：基礎題5 的正方形地磚排列
- **12696**（1習題 基礎題7，gh_RecursiveRelation）：第 (3) 小題要求使用數學歸納法驗證：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代
- **12698**（1習題 進階題9，gh_RecursiveRelation）：圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律：進階題9 的艾薛爾飛魚圖案
- **12700**（例題9，gh_MathematicalInduction）：第 (3) 小題要求使用數學歸納法驗證：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代
- **12701**（例題10，gh_MathematicalInduction）：整題是數學歸納法證明：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代
- **12702**（例題11，gh_MathematicalInduction）：圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律，並含圖形選項（單選）：例題11 的艾薛爾蜥蜴圖案
- **12703**（隨堂練習9，gh_MathematicalInduction）：第 (3) 小題要求使用數學歸納法驗證：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代
- **12704**（隨堂練習10，gh_MathematicalInduction）：整題是數學歸納法證明：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代
- **12705**（隨堂練習11，gh_MathematicalInduction）：圖形的規律只存在於教材圖形中（題幹文字沒有描述各圖的構造，只給前幾項），不能只靠文字出題，也不能由前幾項唯一確定一般規律：隨堂練習11 的艾薛爾蝴蝶圖案
- **12706**（1習題 進階題11，gh_MathematicalInduction）：整題是數學歸納法證明：含數學歸納法證明作答（寫出證明過程），目前沒有已授權的證明判分契約，不以自由文字或 AI 判斷替代

## 驗證摘要

| 項目 | 結果 |
|---|---|
| 沙盒測試 `tests/gencode/test_gh_math2_unit1_sequence_sandbox.py` | 73 項 PASS（逐 component 契約／20 seeds／獨立手算答案／錯解被拒／等價解被接受／驗證器拒絕被竄改答案／○× 平衡／格式提示不洩漏答案／顯示衛生） |
| 隔離 Phase 2 重建（暫存 store + DB 複本） | 26 / 26 component tracker = verified，failures = 0 |
| 沙盒 Phase 3 發布 `gh_RecursiveRelation`（暫存專案根目錄） | production_published，9 components，smoke / staging / production smoke = passed / passed / passed |
| 沙盒 Phase 3 發布 `gh_Sequence`（暫存專案根目錄） | production_published，17 components，smoke / staging / production smoke = passed / passed / passed |
| 學生端 facade `gh_RecursiveRelation`（正解／等價解／錯解逐一提交） | problems = 0，服務到 9 個 component |
| 學生端 facade `gh_Sequence`（正解／等價解／錯解逐一提交） | problems = 0，服務到 17 個 component |
| 正式路徑寫入掃描 | 無 |
| Promotion 預檢（唯讀） | blockers = ['human_review_not_approved', 'approved_revision_mismatch']（只剩人工核可） |
| 套件安全掃描 | 無禁用 import／I/O／隨機／eval／空函式；套件檔與核可雜湊逐位元相同；第三方只用 sympy |
| 與既有 `sequence.series` 交叉驗證 | 可比對的原語全部一致（80/80 項、20/20 等差、60/60 公比等） |
| 共用 variation audit `gh_Sequence` | unsafe_dynamic：dynamic 13 / 17；其餘為 ○× 二選一題（共用規則要求單選 4 選項，單元11 已發布 skill 同樣如此），逐項檢查其他判定全部通過 |
| 共用 variation audit `gh_RecursiveRelation` | unsafe_dynamic：dynamic 8 / 9；其餘為 ○× 二選一題（共用規則要求單選 4 選項，單元11 已發布 skill 同樣如此），逐項檢查其他判定全部通過 |

## 來源對應

| 教材 id | 題目 | 正式庫 Skill | operation | 子題型 |
|---|---|---|---|---|
| 12667 | 例題1 | gh_Sequence | `sequence_terms_from_formula` | formula_items |
| 12669 | 例題3 | gh_Sequence | `geometric_from_terms` | aperture |
| 12670 | 例題4 | gh_Sequence | `geometric_from_relations` | sum_pairs |
| 12671 | 例題5 | gh_Sequence | `progression_three_numbers` | geo_then_arith |
| 12672 | 隨堂練習1 | gh_Sequence | `sequence_terms_from_formula` | formula_items |
| 12674 | 隨堂練習3 | gh_Sequence | `geometric_from_terms` | list |
| 12675 | 隨堂練習4 | gh_Sequence | `geometric_from_relations` | product_positive |
| 12676 | 隨堂練習5 | gh_Sequence | `progression_three_numbers` | arith_positions |
| 12677 | 1習題 觀念澄清1 | gh_Sequence | `sequence_statements` | term_claim |
| 12678 | 1習題 觀念澄清2 | gh_Sequence | `sequence_statements` | progression_claim |
| 12679 | 1習題 觀念澄清3 | gh_Sequence | `sequence_statements` | both_claim |
| 12680 | 1習題 觀念澄清5 | gh_Sequence | `sequence_statements` | recurrence_claim |
| 12681 | 1習題 基礎題1 | gh_Sequence | `arithmetic_from_terms` | formula_items |
| 12682 | 1習題 基礎題2 | gh_Sequence | `geometric_from_relations` | two_terms |
| 12683 | 1習題 基礎題3 | gh_Sequence | `geometric_from_relations` | diff_sum |
| 12684 | 1習題 基礎題4 | gh_Sequence | `progression_three_numbers` | arith_geo_chain |
| 12685 | 1習題 進階題10 | gh_Sequence | `progression_three_numbers` | arith_geo_shift |
| 12687 | 例題7 | gh_RecursiveRelation | `recurrence_from_process` | subdivision |
| 12688 | 例題8 | gh_RecursiveRelation | `recurrence_from_process` | row_sums |
| 12689 | 隨堂練習6 | gh_RecursiveRelation | `recurrence_from_process` | tearing |
| 12690 | 隨堂練習7 | gh_RecursiveRelation | `recurrence_from_process` | subdivision |
| 12692 | 隨堂練習8 | gh_RecursiveRelation | `recurrence_from_process` | array_row_end |
| 12693 | 1習題 觀念澄清4 | gh_RecursiveRelation | `sequence_statements` | recurrence_term_claim |
| 12695 | 1習題 基礎題6 | gh_RecursiveRelation | `recurrence_from_process` | subdivision |
| 12697 | 1習題 基礎題8 | gh_RecursiveRelation | `progression_three_numbers` | geo_sum_relation |
| 12699 | 1習題 進階題12 | gh_RecursiveRelation | `recurrence_from_process` | nested_polygon |

operations = 7；子題型（operation × kind/style）= 23。

## 代表題（變體 0 = 教材題；變體 B = seed 7）

### 12667 · 例題1 · `sequence_terms_from_formula` / formula_items

教材原題：

> 寫出下列數列的前五項。
> (1)\(\left \langle { 2n-1 } \right \rangle\)。 (2)\(\left \langle { \frac { n } { 3n+1 } } \right \rangle\)。

**變體 0**（verify_payload = PASS）

```text
寫出下列數列的前五項。
(1)$\left\langle 2n-1\right\rangle$。
(2)$\left\langle \frac{n}{3n+1}\right\rangle$。
```
- 答案顯示：(1) 1, 3, 5, 7, 9；(2) 1/4, 2/7, 3/10, 4/13, 5/16
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 10 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
寫出下列數列的前五項。
(1)$\left\langle 3n-1\right\rangle$。
(2)$\left\langle \frac{3n+1}{2n+1}\right\rangle$。
```
- 答案顯示：(1) 2, 5, 8, 11, 14；(2) 4/3, 7/5, 10/7, 13/9, 16/11
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 10 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `3` → 拒絕；等價寫法 `2.0` → 接受

### 12669 · 例題3 · `geometric_from_terms` / aperture

教材原題：

> 已知相機光圈值
> \(2,\ 2\sqrt[] { 2 },\ 4,\ \ldots\)
> 構成一個等比數列 \(\left \langle { a_{ n } } \right \rangle\)。
> (1)求首項 \(a_{ 1 }\) 及公比r的值。
> (2)求第 \(6\) 項 \(a_{ 6 }\) 的值。
> (3)試問光圈值 \(32\) 出現在該數列的第幾項？

**變體 0**（verify_payload = PASS）

```text
已知相機光圈值
$2,\ 2 \sqrt{2},\ 4,\ \ldots$
構成一個等比數列 $\left\langle a_{n}\right\rangle$。
(1)求首項 $a_{1}$ 及公比 $r$ 的值。
(2)求第 $6$ 項 $a_{6}$ 的值。
(3)試問光圈值 $32$ 出現在該數列的第幾項？
```
- 答案顯示：(1) a₁=2, r=√2；(2) 8√2；(3) 第9項
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 4 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `3` → 拒絕；等價寫法 `2.0` → 接受

**變體 B**（verify_payload = PASS）

```text
已知相機光圈值
$5,\ 5 \sqrt{3},\ 15,\ \ldots$
構成一個等比數列 $\left\langle a_{n}\right\rangle$。
(1)求首項 $a_{1}$ 及公比 $r$ 的值。
(2)求第 $7$ 項 $a_{7}$ 的值。
(3)試問光圈值 $405 \sqrt{3}$ 出現在該數列的第幾項？
```
- 答案顯示：(1) a₁=5, r=√3；(2) 135；(3) 第10項
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 4 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `6` → 拒絕；等價寫法 `5.0` → 接受

### 12670 · 例題4 · `geometric_from_relations` / sum_pairs

教材原題：

> 已知等比數列 \(\left \langle { a_{ n } } \right \rangle\) 滿足 \(a_{ 1 } +a_{ 3 }=20\)、\(a_{ 2 } +a_{ 4 }=-10\)，求 \(a_{ 5 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{1}+a_{3}=20$、$a_{2}+a_{4}=-10$，求 $a_{5}$ 的值。
```
- 答案顯示：1
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{1}+a_{3}=40$、$a_{2}+a_{4}=80$，求 $a_{5}$ 的值。
```
- 答案顯示：128
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `129` → 拒絕；等價寫法 `128.0` → 接受

### 12671 · 例題5 · `progression_three_numbers` / geo_then_arith

教材原題：

> 已知a, 2, b三數成等比數列，且a, 2, \(b-1\) 三數成等差數列，求a的值。

**變體 0**（verify_payload = PASS）

```text
已知 $a,\ 2,\ b$ 三數成等比數列，且 $a,\ 2,\ b-1$ 三數成等差數列，求 $a$ 的值。
```
- 答案顯示：1、4
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['1', '4', '99']` → 拒絕；等價寫法 `['4', '1']` → 接受

**變體 B**（verify_payload = PASS）

```text
已知 $a,\ 4,\ b$ 三數成等比數列，且 $a,\ 4,\ b-2$ 三數成等差數列，求 $a$ 的值。
```
- 答案顯示：2、8
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `-1, 4`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['2', '8', '99']` → 拒絕；等價寫法 `['8', '2']` → 接受

### 12672 · 隨堂練習1 · `sequence_terms_from_formula` / formula_items

教材原題：

> 寫出下列數列的前五項。
> (1)\(\left \langle { 1-n ^ { 2 } } \right \rangle\)。 (2)\(\left \langle { \frac { \left ( { -1 } \right ) ^ { n } } { 2n } } \right \rangle\)。

**變體 0**（verify_payload = PASS）

```text
寫出下列數列的前五項。
(1)$\left\langle 1-n^{2}\right\rangle$。
(2)$\left\langle \frac{(-1)^{n}}{2n}\right\rangle$。
```
- 答案顯示：(1) 0, -3, -8, -15, -24；(2) -1/2, 1/4, -1/6, 1/8, -1/10
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 10 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `1` → 拒絕；等價寫法 `0.0` → 接受

**變體 B**（verify_payload = PASS）

```text
寫出下列數列的前五項。
(1)$\left\langle 2+n+n^{2}\right\rangle$。
(2)$\left\langle \frac{3(-1)^{n}}{2n}\right\rangle$。
```
- 答案顯示：(1) 4, 8, 14, 22, 32；(2) -3/2, 3/4, -1/2, 3/8, -3/10
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 10 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `5` → 拒絕；等價寫法 `4.0` → 接受

### 12674 · 隨堂練習3 · `geometric_from_terms` / list

教材原題：

> 已知3, −6, 12,…, −384構成一個等比數列 \(\left \langle { a_{ n } } \right \rangle\)。
> (1)求首項 \(a_{ 1 }\) 及公比r的值。　(2)求第 \(5\) 項 \(a_{ 5 }\) 的值。　(3)試問 −384是第幾項？

**變體 0**（verify_payload = PASS）

```text
已知$3,\ -6,\ 12,\ldots,\ -384$構成一個等比數列 $\left\langle a_{n}\right\rangle$。
(1)求首項 $a_{1}$ 及公比 $r$ 的值。
(2)求第 $5$ 項 $a_{5}$ 的值。
(3)試問 $-384$ 是第幾項？
```
- 答案顯示：(1) a₁=3, r=-2；(2) 48；(3) 第8項
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 4 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `4` → 拒絕；等價寫法 `3.0` → 接受

**變體 B**（verify_payload = PASS）

```text
已知$2,\ -4,\ 8,\ldots,\ 32$構成一個等比數列 $\left\langle a_{n}\right\rangle$。
(1)求首項 $a_{1}$ 及公比 $r$ 的值。
(2)求第 $4$ 項 $a_{4}$ 的值。
(3)試問 $32$ 是第幾項？
```
- 答案顯示：(1) a₁=2, r=-2；(2) -16；(3) 第5項
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 4 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `3` → 拒絕；等價寫法 `2.0` → 接受

### 12675 · 隨堂練習4 · `geometric_from_relations` / product_positive

教材原題：

> 已知等比數列 \(\left \langle { a_{ n } } \right \rangle\) 的每項均為正數，且滿足 \(a_{ 1 } a_{ 3 }=1\)、\(a_{ 4 }=4\)，求 \(a_{ 1 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 的每項均為正數，且滿足 $a_{1}a_{3}=1$、$a_{4}=4$，求 $a_{1}$ 的值。
```
- 答案顯示：1/2
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `3/2` → 拒絕；等價寫法 `0.5` → 接受

**變體 B**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 的每項均為正數，且滿足 $a_{1}a_{3}=25$、$a_{4}=125$，求 $a_{1}$ 的值。
```
- 答案顯示：1
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

### 12676 · 隨堂練習5 · `progression_three_numbers` / arith_positions

教材原題：

> 已知成等比的1, r, \(r ^ { 2 }\) 三數恰為另一等差數列之第1, 2, 5項，求r的值。（有兩解）

**變體 0**（verify_payload = PASS）

```text
已知成等比的 $1,\ r,\ r^{2}$ 三數恰為另一等差數列之第 $1,\ 2,\ 5$ 項，求 $r$ 的值。（有兩解）
```
- 答案顯示：1、3
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['1', '3', '99']` → 拒絕；等價寫法 `['3', '1']` → 接受

**變體 B**（verify_payload = PASS）

```text
已知成等比的 $-2,\ -2r,\ -2r^{2}$ 三數恰為另一等差數列之第 $1,\ 4,\ 8$ 項，求 $r$ 的值。（有兩解）
```
- 答案顯示：1、4/3
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['1', '4/3', '99']` → 拒絕；等價寫法 `['4/3', '1']` → 接受

### 12677 · 1習題 觀念澄清1 · `sequence_statements` / term_claim

教材原題：

> 下列敘述對的打「○」，錯的打「×」。
> 數列 \(\left \langle { \frac { n ^ { 2 } +2 } { 2n-1 } } \right \rangle\) 的第 \(5\) 項為3。

**變體 0**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $\left\langle \frac{n^{2}+2}{2n-1}\right\rangle$ 的第 $5$ 項為 $3$。
```
- 答案顯示：○
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `B` → 拒絕

**變體 B**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $\left\langle \frac{2n^{2}-3}{n+2}\right\rangle$ 的第 $2$ 項為 $\frac{1}{4}$。
```
- 答案顯示：×
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `A` → 拒絕

○× 分佈（20 seeds）：A(○)=10、B(×)=10

### 12678 · 1習題 觀念澄清2 · `sequence_statements` / progression_claim

教材原題：

> 下列敘述對的打「○」，錯的打「×」。
> 數列4, 6, 9是等比數列。

**變體 0**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $4,\ 6,\ 9$ 是等比數列。
```
- 答案顯示：○
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `B` → 拒絕

**變體 B**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $5,\ 10,\ 20$ 是等差數列。
```
- 答案顯示：×
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `A` → 拒絕

○× 分佈（20 seeds）：A(○)=8、B(×)=12

### 12679 · 1習題 觀念澄清3 · `sequence_statements` / both_claim

教材原題：

> 下列敘述對的打「○」，錯的打「×」。
> 數列5, 5, 5既是等差數列也是等比數列。

**變體 0**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $5,\ 5,\ 5$ 既是等差數列也是等比數列。
```
- 答案顯示：○
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `B` → 拒絕

**變體 B**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
數列 $5,\ 5,\ 5,\ 4$ 既是等差數列也是等比數列。
```
- 答案顯示：×
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `A` → 拒絕

○× 分佈（20 seeds）：A(○)=7、B(×)=13

### 12680 · 1習題 觀念澄清5 · `sequence_statements` / recurrence_claim

教材原題：

> 下列敘述對的打「○」，錯的打「×」。
> 若等差數列 \(\left \langle { a_{ n } } \right \rangle\) 的首項為5，公差為 \(-3\)，則 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式為
> \(\left \{ \begin{array}{l} a_{ 1 } =5 \\ a_{ n } =a_{ n-1 } -3\quad （n\ge 2） \end{array} \right.\)。

**變體 0**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
若等差數列 $\left\langle a_{n}\right\rangle$ 的首項為 $5$，公差為 $-3$，則 $\left\langle a_{n}\right\rangle$ 的遞迴關係式為 $\left\{\begin{array}{l} a_{1}=5 \\ a_{n}=a_{n-1}-3\quad (n\ge 2) \end{array}\right.$。
```
- 答案顯示：○
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `B` → 拒絕

**變體 B**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
若等比數列 $\left\langle a_{n}\right\rangle$ 的首項為 $5$，公比為 $-2$，則 $\left\langle a_{n}\right\rangle$ 的遞迴關係式為 $\left\{\begin{array}{l} a_{1}=6 \\ a_{n}=-2a_{n-1}\quad (n\ge 2) \end{array}\right.$。
```
- 答案顯示：×
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `A` → 拒絕

○× 分佈（20 seeds）：A(○)=9、B(×)=11

### 12681 · 1習題 基礎題1 · `arithmetic_from_terms` / formula_items

教材原題：

> 設等差數列 \(\left \langle { a_{ n } } \right \rangle\) 滿足 \(a_{ 10 }=20\)、\(a_{ 20 }=10\)。
> (1)	求首項 \(a_{ 1 }\) 及公差d的值。
> (2)	此數列從第幾項開始出現負數？

**變體 0**（verify_payload = PASS）

```text
設等差數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{10}=20$、$a_{20}=10$。
(1)求首項 $a_{1}$ 及公差 $d$ 的值。
(2)此數列從第幾項開始出現負數？
```
- 答案顯示：a₁=29, d=-1；第31項
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `30` → 拒絕；等價寫法 `29.0` → 接受

**變體 B**（verify_payload = PASS）

```text
設等差數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{8}=\frac{25}{2}$、$a_{12}=\frac{13}{2}$。
(1)求首項 $a_{1}$ 及公差 $d$ 的值。
(2)此數列從第幾項開始出現負數？
```
- 答案顯示：a₁=23, d=-3/2；第17項
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `24` → 拒絕；等價寫法 `23.0` → 接受

### 12682 · 1習題 基礎題2 · `geometric_from_relations` / two_terms

教材原題：

> 已知等比數列 \(\left \langle { a_{ n } } \right \rangle\) 滿足 \(a_{ 3 }=-3\)、\(a_{ 6 } =9\sqrt[] { 3 }\)，求首項 \(a_{ 1 }\) 及公比r的值。

**變體 0**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{3}=-3$、$a_{6}=9 \sqrt{3}$，求首項 $a_{1}$ 及公比 $r$ 的值。
```
- 答案顯示：a₁=-1, r=-√3
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `0` → 拒絕；等價寫法 `-1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{1}=4$、$a_{2}=4 \sqrt{2}$，求首項 $a_{1}$ 及公比 $r$ 的值。
```
- 答案顯示：a₁=4, r=√2
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `5` → 拒絕；等價寫法 `4.0` → 接受

### 12683 · 1習題 基礎題3 · `geometric_from_relations` / diff_sum

教材原題：

> 已知等比數列 \(\left \langle { a_{ n } } \right \rangle\) 滿足 \(a_{ 2 } -a_{ 1 }=2\)、\(a_{ 1 } +a_{ 3 }=10\)，求 \(a_{ 4 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{2}-a_{1}=2$、$a_{1}+a_{3}=10$，求 $a_{4}$ 的值。
```
- 答案顯示：16、27
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['16', '27', '99']` → 拒絕；等價寫法 `['27', '16']` → 接受

**變體 B**（verify_payload = PASS）

```text
已知等比數列 $\left\langle a_{n}\right\rangle$ 滿足 $a_{2}-a_{1}=3$、$a_{1}+a_{3}=25$，求 $a_{5}$ 的值。
```
- 答案顯示：256/9、2401/2
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['256/9', '2401/2', '99']` → 拒絕；等價寫法 `['2401/2', '256/9']` → 接受

### 12684 · 1習題 基礎題4 · `progression_three_numbers` / arith_geo_chain

教材原題：

> 已知一數列 \(-2\), a, b, 18滿足前三項成等差數列，且後三項成等比數列，求a的值。

**變體 0**（verify_payload = PASS）

```text
已知一數列 $-2,\ a,\ b,\ 18$ 滿足前三項成等差數列，且後三項成等比數列，求 $a$ 的值。
```
- 答案顯示：1/2、2
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `3, 8`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['1/2', '2', '99']` → 拒絕；等價寫法 `['2', '1/2']` → 接受

**變體 B**（verify_payload = PASS）

```text
已知一數列 $-6,\ a,\ b,\ -1$ 滿足前三項成等差數列，且後三項成等比數列，求 $a$ 的值。
```
- 答案顯示：-4、-9/4
- 契約：solution_set / short_answer / checkers = ['solution_set_checker']；輸入欄位 1 個；格式提示 `2, 5`（與答案無關）
- 判分抽查（第一欄）：正解 → 接受；錯解 `['-4', '-9/4', '99']` → 拒絕；等價寫法 `['-9/4', '-4']` → 接受

### 12685 · 1習題 進階題10 · `progression_three_numbers` / arith_geo_shift

教材原題：

> 設三正數成等差數列且其總和為30。已知此三數依序分別加上1, 6, 47後會成為等比數列，求此三數中最小的數。

**變體 0**（verify_payload = PASS）

```text
設三正數成等差數列且其總和為$30$。已知此三數依序分別加上$1, 6, 47$後會成為等比數列，求此三數中最小的數。
```
- 答案顯示：3
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `4` → 拒絕；等價寫法 `3.0` → 接受

**變體 B**（verify_payload = PASS）

```text
設三正數成等差數列且其總和為$33$。已知此三數依序分別加上$12, 53, 238$後會成為等比數列，求此三數中最小的數。
```
- 答案顯示：4
- 契約：rational / short_answer / checkers = ['rational_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `5` → 拒絕；等價寫法 `4.0` → 接受

### 12687 · 例題7 · `recurrence_from_process` / subdivision

教材原題：

> 取一個白色正三角形，將其等分成 \(4\) 個相同的小正三角形，然後將中間的三角形塗成黑色；接著再將剩下的 \(3\) 個白色小正三角形，分別等分成 \(4\) 個相同的更小正三角形，並將中間更小的正三角形塗成黑色。重複這樣的步驟，如下圖所示。
> 依此規律可畫第 \(5\) 圖、第 \(6\) 圖、……，並設 \(a_{ n }\) 為第n圖中白色三角形的總數。
> (1)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (2)求 \(a_{ 6 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
取一個白色正三角形，將其等分成 $4$ 個相同的小正三角形，然後將中間的小正三角形塗成黑色；接著再將剩下的 $3$ 個白色小正三角形，分別等分成 $4$ 個相同的更小的正三角形，並將中間的小正三角形塗成黑色。重複這樣的步驟。
第 $1$ 圖是最初的白色正三角形，第 $2$ 圖是第一次塗成黑色後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中白色三角形的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)求 $a_{6}$ 的值。
```
- 答案顯示：(1) a₁=1，倍數 3；(2) 243
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
取一個白色正三角形，將其等分成 $9$ 個相同的小正三角形，然後將其中 $3$ 個小正三角形塗成黑色；接著再將剩下的 $6$ 個白色小正三角形，分別等分成 $9$ 個相同的更小的正三角形，並將其中 $3$ 個小正三角形塗成黑色。重複這樣的步驟。
第 $1$ 圖是最初的白色正三角形，第 $2$ 圖是第一次塗成黑色後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中白色三角形的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)求 $a_{7}$ 的值。
```
- 答案顯示：(1) a₁=1，倍數 6；(2) 46656
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

### 12688 · 例題8 · `recurrence_from_process` / row_sums

教材原題：

> 古代陣法中，「魚鱗陣」的將領位於陣形的正後方，士兵依右圖排列：第 \(1\) 列有 \(1\) 人、第 \(2\) 列有 \(3\) 人、第 \(3\) 列有 \(5\) 人、……，以此類推。設 \(a_{ n }\) 是前n列士兵的總人數。
> (1)求 \(a_{ 1 }\)、\(a_{ 2 }\)、\(a_{ 3 }\)、\(a_{ 4 }\) 的值。
> (2)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (3)求 \(a_{ 6 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
古代陣法中，「魚鱗陣」的將領位於陣形的正後方，士兵依序排列：第 $1$ 列有 $1$ 人、第 $2$ 列有 $3$ 人、第 $3$ 列有 $5$ 人、……，以此類推。設 $a_{n}$ 是前 $n$ 列士兵的總人數。
(1)求 $a_{1}$、$a_{2}$、$a_{3}$、$a_{4}$ 的值。
(2)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 2)$，框內是 $n$ 的式子，請填入。
(3)求 $a_{6}$ 的值。
```
- 答案顯示：(1) 1, 4, 9, 16；(2) 2*n-1；(3) 36
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 6 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
古代陣法中，「魚鱗陣」的將領位於陣形的正後方，士兵依序排列：第 $1$ 列有 $1$ 人、第 $2$ 列有 $4$ 人、第 $3$ 列有 $7$ 人、……，以此類推。設 $a_{n}$ 是前 $n$ 列士兵的總人數。
(1)求 $a_{1}$、$a_{2}$、$a_{3}$、$a_{4}$ 的值。
(2)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 2)$，框內是 $n$ 的式子，請填入。
(3)求 $a_{7}$ 的值。
```
- 答案顯示：(1) 1, 5, 12, 22；(2) 3*n-2；(3) 70
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 6 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

### 12689 · 隨堂練習6 · `recurrence_from_process` / tearing

教材原題：

> 桌上有 \(2\) 張紙，每一次操作都把其中一張紙撕成 \(4\) 張。設 \(a_{ n }\) 代表經過n次操作後，桌面上大小不同紙張的總數。
> (1)求 \(a_{ 2 }\) 的值。
> (2)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (3)經幾次操作後，桌面上剛好有 \(101\) 張紙？

**變體 0**（verify_payload = PASS）

```text
桌上有 $2$ 張紙，每一次操作都把其中一張紙撕成 $4$ 張。設 $a_{n}$ 代表經過 $n$ 次操作後，桌面上大小不同紙張的總數（$a_{0}=2$）。
(1)求 $a_{2}$ 的值。
(2)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 1)$，請填入框內的值。
(3)經幾次操作後，桌面上剛好有 $101$ 張紙？
```
- 答案顯示：(1) 8；(2) 3；(3) 33 次
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `9` → 拒絕；等價寫法 `8.0` → 接受

**變體 B**（verify_payload = PASS）

```text
桌上有 $1$ 張紙，每一次操作都把其中一張紙撕成 $3$ 張。設 $a_{n}$ 代表經過 $n$ 次操作後，桌面上大小不同紙張的總數（$a_{0}=1$）。
(1)求 $a_{3}$ 的值。
(2)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 1)$，請填入框內的值。
(3)經幾次操作後，桌面上剛好有 $109$ 張紙？
```
- 答案顯示：(1) 7；(2) 2；(3) 54 次
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `8` → 拒絕；等價寫法 `7.0` → 接受

### 12690 · 隨堂練習7 · `recurrence_from_process` / subdivision

教材原題：

> 取一個線段，將其等分成 \(3\) 個線段，然後將中間那一段刪除；接著再將剩下的 \(2\) 個線段，分別等分成 \(3\) 個線段，並將中間的那一段刪除。重複這樣的步驟，如下圖所示。
> 依此規律可畫第 \(5\) 圖、第 \(6\) 圖、……，並設 \(a_{ n }\) 為第n圖中的線段個數（\(a_{ 1 }=1\)、\(a_{ 2 }=2\)）。
> (1)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (2)求 \(a_{ 9 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
取一個線段，將其等分成 $3$ 個相同的線段，然後將中間那一段刪除；接著再將剩下的 $2$ 個線段，分別等分成 $3$ 個相同的更小的線段，並將中間那一段刪除。重複這樣的步驟。
第 $1$ 圖是最初的線段，第 $2$ 圖是第一次刪除後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中線段的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)求 $a_{9}$ 的值。
```
- 答案顯示：(1) a₁=1，倍數 2；(2) 256
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
取一個線段，將其等分成 $3$ 個相同的線段，然後將中間那一段刪除；接著再將剩下的 $2$ 個線段，分別等分成 $3$ 個相同的更小的線段，並將中間那一段刪除。重複這樣的步驟。
第 $1$ 圖是最初的線段，第 $2$ 圖是第一次刪除後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中線段的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)求 $a_{8}$ 的值。
```
- 答案顯示：(1) a₁=1，倍數 2；(2) 128
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

### 12692 · 隨堂練習8 · `recurrence_from_process` / array_row_end

教材原題：

> 將所有的正整數依序排列如右圖所示：第一列有 \(1\) 個數字，第二列有 \(2\) 個數字，第三列有 \(3\) 個數字，……；下一列都比上一列增加 \(1\) 個數字，以此類推。設 \(a_{ n }\) 代表第n列最右邊的數字（\(a_{ 1 }=1\)、\(a_{ 2 }=3\)、\(a_{ 3 }=6\),…）。
> (1)寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (2)求 \(a_{ 6 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
將所有的正整數依序排列如下：第一列有 $1$ 個數字，第二列有 $2$ 個數字，第三列有 $3$ 個數字，……；下一列都比上一列增加 $1$ 個數字，以此類推。設 $a_{n}$ 代表第 $n$ 列最右邊的數字（$a_{1}=1$、$a_{2}=3$、$a_{3}=6$,…）。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 2)$，框內是 $n$ 的式子，請填入。
(2)求 $a_{6}$ 的值。
```
- 答案顯示：(1) n；(2) 21
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(n)+1` → 拒絕

**變體 B**（verify_payload = PASS）

```text
將從 $5$ 開始的所有正整數依序排列如下：第一列有 $2$ 個數字，第二列有 $3$ 個數字，第三列有 $4$ 個數字，……；下一列都比上一列增加 $1$ 個數字，以此類推。設 $a_{n}$ 代表第 $n$ 列最右邊的數字（$a_{1}=6$、$a_{2}=9$、$a_{3}=13$,…）。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=a_{n-1}+\boxed{\ }\ (n\ge 2)$，框內是 $n$ 的式子，請填入。
(2)求 $a_{9}$ 的值。
```
- 答案顯示：(1) n+1；(2) 58
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(n+1)+1` → 拒絕；等價寫法 `1 + n` → 接受

### 12693 · 1習題 觀念澄清4 · `sequence_statements` / recurrence_term_claim

教材原題：

> 下列敘述對的打「○」，錯的打「×」。
> 若數列 \(\left \langle { a_{ n } } \right \rangle\) 遞迴關係式為 \(\left \{ \begin{array}{l} a_{ 1 } =2 \\ a_{ n } =2a_{ n-1 } \quad （n\ge 2） \end{array} \right.\)，則 \(a_{ 4 }=8\)。

**變體 0**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
若數列 $\left\langle a_{n}\right\rangle$ 遞迴關係式為 $\left\{\begin{array}{l} a_{1}=2 \\ a_{n}=2a_{n-1}\quad (n\ge 2) \end{array}\right.$，則 $a_{4}=8$。
```
- 答案顯示：×
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `A` → 拒絕

**變體 B**（verify_payload = PASS）

```text
下列敘述對的打「○」，錯的打「×」。
若數列 $\left\langle a_{n}\right\rangle$ 遞迴關係式為 $\left\{\begin{array}{l} a_{1}=4 \\ a_{n}=2a_{n-1}\quad (n\ge 2) \end{array}\right.$，則 $a_{4}=32$。
```
- 答案顯示：○
- 契約：single_choice / single_choice / checkers = ['choice_label_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `B` → 拒絕

○× 分佈（20 seeds）：A(○)=10、B(×)=10

### 12695 · 1習題 基礎題6 · `recurrence_from_process` / subdivision

教材原題：

> 取一個白色正方形，將其等分成 \(9\) 個相同的小正方形，然後將左上角的正方形塗成藍色；接著再將剩下的 \(8\) 個白色小正方形，分別等分成 \(9\) 個相同的更小正方形，並將左上角更小的正方形塗成藍色，如下圖所示。
> 依此規律可畫第 \(4\) 圖、第 \(5\) 圖、……，並設 \(a_{ n }\) 為第n圖中白色正方形的總數。
> (1)	寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (2)	從第幾個圖開始，白色正方形的總數會超過 \(1000\) 個？

**變體 0**（verify_payload = PASS）

```text
取一個白色正方形，將其等分成 $9$ 個相同的小正方形，然後將左上角的小正方形塗成藍色；接著再將剩下的 $8$ 個白色小正方形，分別等分成 $9$ 個相同的更小的正方形，並將左上角的小正方形塗成藍色。重複這樣的步驟。
第 $1$ 圖是最初的白色正方形，第 $2$ 圖是第一次塗成藍色後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中白色正方形的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)從第幾個圖開始，白色正方形的總數會超過 $1000$ 個？
```
- 答案顯示：(1) a₁=1，倍數 8；(2) 第5個圖
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

**變體 B**（verify_payload = PASS）

```text
取一個白色正方形，將其等分成 $9$ 個相同的小正方形，然後將其中 $2$ 個小正方形塗成藍色；接著再將剩下的 $7$ 個白色小正方形，分別等分成 $9$ 個相同的更小的正方形，並將其中 $2$ 個小正方形塗成藍色。重複這樣的步驟。
第 $1$ 圖是最初的白色正方形，第 $2$ 圖是第一次塗成藍色後的圖形，依此規律可畫第 $3$ 圖、第 $4$ 圖、……，並設 $a_{n}$ 為第 $n$ 圖中白色正方形的總數。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{1}=\boxed{\ },\ a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請分別填入兩個框內的值。
(2)從第幾個圖開始，白色正方形的總數會超過 $5000$ 個？
```
- 答案顯示：(1) a₁=1，倍數 7；(2) 第6個圖
- 契約：multi_part / multiple_inputs / checkers = ['rational_checker']；輸入欄位 3 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `2` → 拒絕；等價寫法 `1.0` → 接受

### 12697 · 1習題 基礎題8 · `progression_three_numbers` / geo_sum_relation

教材原題：

> 人類的大拇指自指尖到腕骨是由三塊骨頭所組成的，令自指尖到腕骨的這三塊骨頭的長度分別為 \(a_{ 1 }\)、\(a_{ 2 }\)、\(a_{ 3 }\)。據統計，當 \(a_{ 1 }\)、\(a_{ 2 }\)、\(a_{ 3 }\) 成等比數列且滿足 \(a_{ 3 }=a_{ 2 } +a_{ 1 }\) 時，大拇指的型態被認為是最完美的。試求完美大拇指三塊骨頭長度的公比。

**變體 0**（verify_payload = PASS）

```text
人類的大拇指自指尖到腕骨是由三塊骨頭所組成的，令自指尖到腕骨的這三塊骨頭的長度分別為 $a_{1}$、$a_{2}$、$a_{3}$。據統計，當 $a_{1}$、$a_{2}$、$a_{3}$ 成等比數列且滿足 $a_{3}=a_{2}+a_{1}$ 時，大拇指的型態被認為是最完美的。試求完美大拇指三塊骨頭長度的公比。
```
- 答案顯示：1/2+√5/2
- 契約：numeric_or_radical / short_answer / checkers = ['expression_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(1/2+sqrt(5)/2)+1` → 拒絕；等價寫法 `sqrt(5)/2 + 1/2` → 接受

**變體 B**（verify_payload = PASS）

```text
已知三個正數 $a_{1}$、$a_{2}$、$a_{3}$ 成等比數列且滿足 $a_{3}=a_{2}+4a_{1}$，求公比。
```
- 答案顯示：1/2+√17/2
- 契約：numeric_or_radical / short_answer / checkers = ['expression_checker']；輸入欄位 1 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(1/2+sqrt(17)/2)+1` → 拒絕；等價寫法 `sqrt(17)/2 + 1/2` → 接受

### 12699 · 1習題 進階題12 · `recurrence_from_process` / nested_polygon

教材原題：

> 如右圖，以正方形 \(T_{ 1 }\) 各邊中點為頂點連成四邊形 \(T_{ 2 }\)，再以 \(T_{ 2 }\) 各邊中點為頂點連成四邊形 \(T_{ 3 }\)，如此繼續下去，可得到一系列的正方形 \(T_{ 1 }\)、\(T_{ 2 }\)、\(T_{ 3 }\),…。設 \(T_{ 1 }\) 的周長為16，並令 \(a_{ n }\) 表正方形 \(T_{ n }\) 的周長。
> (1)	寫出數列 \(\left \langle { a_{ n } } \right \rangle\) 的遞迴關係式。
> (2)	求 \(a_{ 10 }\) 的值。

**變體 0**（verify_payload = PASS）

```text
以正方形 $T_{1}$ 各邊中點為頂點連成四邊形 $T_{2}$，再以 $T_{2}$ 各邊中點為頂點連成四邊形 $T_{3}$，如此繼續下去，可得到一系列的正方形 $T_{1}$、$T_{2}$、$T_{3}$,…。設 $T_{1}$ 的周長為 $16$，並令 $a_{n}$ 表正方形 $T_{n}$ 的周長。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請填入框內的值。
(2)求 $a_{10}$ 的值。
```
- 答案顯示：(1) √2/2；(2) √2/2
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(sqrt(2)/2)+1` → 拒絕

**變體 B**（verify_payload = PASS）

```text
以正方形 $T_{1}$ 各邊中點為頂點連成四邊形 $T_{2}$，再以 $T_{2}$ 各邊中點為頂點連成四邊形 $T_{3}$，如此繼續下去，可得到一系列的正方形 $T_{1}$、$T_{2}$、$T_{3}$,…。設 $T_{1}$ 的周長為 $24$，並令 $a_{n}$ 表正方形 $T_{n}$ 的周長。
(1)寫出數列 $\left\langle a_{n}\right\rangle$ 的遞迴關係式 $a_{n}=\boxed{\ }\times a_{n-1}\ (n\ge 2)$，請填入框內的值。
(2)求 $a_{5}$ 的值。
```
- 答案顯示：(1) √2/2；(2) 6
- 契約：multi_part / multiple_inputs / checkers = ['expression_checker', 'rational_checker']；輸入欄位 2 個
- 判分抽查（第一欄）：正解 → 接受；錯解 `(sqrt(2)/2)+1` → 拒絕

## 一次性授權前仍需注意

1. 共用 variation audit 對 5 個 ○× 二選一題標示 unsafe_dynamic（共用規則），依單元11 先例視為非阻斷；若要改共用規則另案處理。
2. gh_MathematicalInduction 全部 7 題 DEFERRED（證明題無判分契約、圖形規律題），該 Skill 本單元沒有可發布 Component；如需覆蓋，需要先有『數學歸納法證明』的判分契約。
3. gh_RecursiveRelation 的遞迴關係式以『填入範本空格』作答（首項、公比／增量／n 的式子），因為沒有共用 checker 能可靠判定自由格式的遞迴方程式（equation_checker 會誤判 `a_n=a_{n-1}+5` 等錯誤式為正確，已實測）。
4. 6 題圖形規律題 DEFERRED（12668、12673、12686、12694、12698，另 12702、12705）。
5. 匯入器共通修復與 Stage 2 程式碼尚未 commit。
