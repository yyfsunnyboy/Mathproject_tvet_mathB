# B1 PointSlopeForm 垂直平分線題型調查與修復

**日期**：2026-11-22  
**Skill**：`vh_數學B1_PointSlopeForm`  
**狀態**：FIXED_AND_VERIFIED（Runtime）；等待人工驗收  
**證據**：`reports/gencode_closed_loop/pointslope_bisector_fix_latest.json`

---

## 七問答覆

### 1. B1 原始教材是否有垂直平分線例題？Source ID？

**有。** 正式 DB `textbook_examples`：

| Source ID | 題幹摘要 | 章節 |
|---|---|---|
| **4542** | 設 \(A(-1,1)\)、\(B(3,-1)\)，求 \(\overline{AB}\) 之垂直平分線方程式 | 2-2 直線方程式 |
| **4557** | 試求之垂直平分線方程式（隨堂；同結構） | 2-2 |
| **4550** | 兩鄉鎮等距之直線道路（垂直平分線應用敘事） | 2-2 |

教材 canonical（4542）：中點 \((1,0)\) → **`2x - y - 2 = 0`**

### 2. 正確歸屬哪個 Skill？

**`vh_數學B1_PointSlopeForm`**（DB `skill_id` 已正確；未改綁、未跨 Skill 強制合併）。

### 3. 原本是否有 Generator？

**有 component 檔案**（`src_4542`／`src_4557`／`src_4550` 皆在 package），但 **數學題型被錯標成基本點斜式**：

- `problem_type_id = write_line_equation_from_point_slope`
- `line_type = point_slope`
- `generate()` 呼叫 `build_line_equation_matrix(..., line_type="point_slope")`

因此實際產出的是「過點＋斜率」題，**不是**垂直平分線。

### 4. 為什麼學生端沒有出現？

屬於 **A＋B 混合，核心是題型錯標（非單純缺輪替）**：

1. **結構錯**：component 存在卻生成基本點斜式（假裝覆蓋）。  
2. **輪替塌縮**：`practice_type_rotation` 以 `problem_type_id` 分組；修復前 14 個 component **全部同一 type_key** → 學生端只看到一種「基本點斜式」題型池。

判定：**不是 C（從零缺 Generator）**；是既有 component **錯接題型**。

### 5. 修復了哪些檔案？

| 檔案 | 變更 |
|---|---|
| `components/src_4542|4557|4550/generate.py` | 改走 `write_perpendicular_bisector_from_two_points` slot |
| `components/src_4542|4557|4550/metadata.py` | 正確 PROBLEM_TYPE／TARGET_TASK／checker |
| `skills/vh_數學B1_PointSlopeForm.py` | SPECS `problem_type_id`／`line_type` 更正 |
| `agent_skills_v3/.../__init__.py`、`component_manifest.json` | 同上 |
| `core/gencode/slot_generators.py` | 垂直／水平特例修正；支援 presentation_variant；特例抽樣 |
| `core/domain/.../line_equation_domain.py` | `perpendicular_bisector_application` 支援水平／垂直線段 |

Flask 5001 已受控重啟以載入新碼（未動 5000／Cloudflare）。

### 6. 修復前後可用題型數？

| | 可用 `problem_type_id`（輪替 type_key） |
|---|---|
| **修復前** | **1**：`write_line_equation_from_point_slope` |
| **修復後** | **2**：基本點斜式 + **`write_perpendicular_bisector_from_two_points`** |

（同 Skill 仍有兩點式／截距／中線等教材例題被錯標為點斜式，本輪僅修垂直平分線相關；其餘列為後續 P2。）

### 7. 是否已在正式 Runtime 驗證能出垂直平分線題？

**是（隔離 DB 學生端 Route＋離線）**：

- 強制 `src_4542`／`src_4550`：題幹含「垂直平分／距離相等」；正解 PASS、錯答 FAIL  
- 基本 `src_4540` 仍 PASS  
- 題型輪替 12 抽內同時出現兩種 `problem_type_id`  
- 等價：取負號形式可接受（`linear_equation_equivalent_checker`）  
- 水平／垂直線段特例：中垂線分別為 \(x=\text{const}\)／\(y=\text{const}\)

---

## Promotion／Evidence

本輪為 **題型保真／Registry SPECS 修復**，Runtime 已驗。  
**未自行 Promotion／Publish**；Domain Evidence 正式包仍依既有 Gate 待人工核准。

---

## 完成後停止

等待人工在 `/practice/vh_數學B1_PointSlopeForm` 確認可輪到垂直平分線題。  
**不自動進入其他 Skill／B2。**
