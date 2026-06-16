# Gencode × AgentSkillV3 核心規範說明書

> **文件版本**：v1.4（Domain 層架構規劃增補 · 僅 SOP，待實作）  
> **適用範圍**：高職數學 B 版 Gencode Pipeline 全面升級至 V3「西堤套餐」微元件化架構  
> **上位法規**：[Gencode與AgentSkillV2整合總體設計_v0.3.md](../Gencode_AgentSkillV2整合/Gencode與AgentSkillV2整合總體設計_v0.3.md)（Layer 1–6 原則完整繼承，本文件僅增量定義 V3 微元件層）  
> **實體錨點目錄**：`docs/系統SOP/Gencode_AgentSkillV3整合/`  
> **實作狀態**：v1.4 新增之 `core/domain/`、`core/registry/taxonomy_registry.py` 條目為**架構規劃**；Codex 實作前以本 SOP 為準。

---

## 0. 文件目的

本文件是 **AgentSkillV3 微元件生成與發布** 的工程 SOP，面向 Codex / Gemini Flash 閉環管線與人工審核。  
所有敘述均對接倉庫內**已存在**的模組路徑；不存在之編譯器名稱標註為 V3 目標模組，並指明現行等價實作。

### 0.1 核心修訂原則

| 原則 | 剛性要求 |
|------|----------|
| **DB / 前台零侵入** | 嚴禁修改**學生學習數據表**與 `practice.py` 調度入口；教材例題權威庫之 Gencode 維運欄位增量見 §4.5（唯一允許之 DB 擴充範圍） |
| **同構題自動變異** | 核心定位是 **Isomorphic Question Generator**：概念不動、難度不動、變數個數與計算公式與原題完全相同，**僅更換數值**；反向求解或題型變更由教材後續獨立 Source 承載，不在此管線融合 |
| **一題一對一隔離** | 教材每一道例題 / 隨堂 / 自我評量 → 一個獨立 `components/{component_id}/` 資料夾 + 單一 `generate.py`；**嚴禁**多題合一、嚴禁 AI 自由發揮融合 |
| **天然順序繼承難度** | 依教材天生題號前綴（`ex_*` / `quiz_*` / `test_*`）注入 `ORDER_WEIGHT` 與 `DIFFICULTY_LEVEL`，免去複雜出題演算法 |
| **AI 角色定位** | Gemini Flash 僅扮演 **單題同構模板填空搬運工**；數學正確性由 Domain Function 算子盾牌 + Validator 接管 |

### 0.2 v1.4 Domain 層架構規劃摘要（待實作）

| # | 條款 | 對應章節 |
|---|------|----------|
| 1 | 數學核心按**數學本質**收斂至 `core/domain/`，不按學制拆分 | §2.5 |
| 2 | `generate.py` 全面減肥為搬運工；禁止 Sympy / distractors / visual_spec 計算 | §2.6 |
| 3 | `skill_id` 硬編碼僅允許停在 Registry 中繼層 | §2.7 |
| 4 | Full Matrix Dictionary 六大欄位由 Domain 一次算完 | §2.3.2、§2.5.4 |
| 5 | 首波實作檢查點：直線方程式 `build_line_equation_matrix` | §2.5.5 |
| 6 | 教材例題影子對接表 `gencode_component_tracker`（§4.5） | §4.5 |
| 7 | 後台定點熱拔插與零重啟動態加載 | §4.6 |

### 0.3 v1.3 務實落地摘要（保留）

| # | 條款 | 對應章節 |
|---|------|----------|
| 1 | 廢除概念聚類與課綱家族 hard-code 特例（原 §1.4.2 / §1.4.3） | — |
| 2 | 一題一 `generate.py` + 題號前綴天然難度 | §1.5 |
| 3 | 極端數學邊界統一由 Domain Function 算子盾牌控制 | §2.3 |
| 4 | 修補半徑縮至單題檔案；核心例題 verified 即可 Partial Publish | §4.3 |
| 5 | 保留 v1.2：AST 精準掃描、Full Matrix Dict、P0 Checker、Taxonomy MVP 六單元 | §2.3、§2.4、§1.4.1 |

| 概念 | 現行實作（已落地） | V3 目標模組 |
|------|-------------------|-------------|
| 外層薄入口 | `skills/{skill_id}.py` | 不變 |
| 執行期調度 | `core/gencode/runtime_skill_wrapper.py` | 不變 |
| 插槽算子庫 | `core/gencode/slot_generators.py` → `SLOT_REGISTRY` | 微元件內部可委派 |
| Phase 3 編譯 | `core/gencode/phase3_skill_codegen.py` → `build_phase3_skill_module_code()` | `core/gencode/skill_wrapper_compiler.py`（抽離封裝） |
| Checker 登錄 | `core/gencode/checker_registry.py` → `CHECKER_CAPABILITIES` | 不變 |
| B4 Payload 驗證 | `core/vocational_math_b4/domain/b4_validators.py` | 不變 |
| Phase 2 閉環修補 | `gencode_closed_loop/controller.py` | 擴展至 component 粒度 |
| K7–K12 題型白名單 | — | `configs/gencode_taxonomy/k12_component_taxonomy.yaml` |
| **共用 Domain 邏輯層** | 分散於 `core/*_domain_functions.py`、`core/vocational_math_b4/domain/` | **`core/domain/{領域}/{主題}_domain.py`**（v1.4 目標，見 §2.5） |
| **Domain 註冊中繼層** | — | **`core/registry/taxonomy_registry.py`**（v1.4 目標，見 §2.7） |
| **教材例題權威庫（維運）** | 既有 `TextbookExample` / Word 匯入 → `textbook_examples` | **`gencode_component_tracker` 影子表**（§4.5） |
| **熱拔插編譯重載** | — | 後台 `admin_trigger_rebuild` → `skill_wrapper_compiler`（§4.6） |
| 圖形語意驗證 | — | `core/gencode/visual_schema_validators.py`（V3 目標） |
| 語意等價批改 | `core/checkers/expression_equivalence_checker.py` 等 | `rational_or_decimal_checker`（V3 擴充） |

---

## 1. 核心設計理念

### 1.1 為何引入「西堤套餐」微元件資料夾結構

舊架構將整個 skill 的 `generate()` / `check()` / 多模板分支壓在**單一巨型** `skills/{skill_id}.py`（或同等體積的 agent skill 腳本）中，造成：

1. **Codegen 失敗半徑過大**：一個 problem type 語法錯誤，整檔 skill 無法 import，前台全面 500。
2. **修補閉環無法精準鎖定**：`gencode_closed_loop/controller.py` 只能依 `GENERATOR_REPAIR_CATALOG` 粗粒度覆寫，難以對應單一題型原子。
3. **插槽庫持續膨脹**：`slot_generators.SLOT_REGISTRY` 已承載 30+ slot；若繼續單檔堆疊，違反 V2 §1.5.6 Anti-Bloat 原則。
4. **並行開發衝突**：多人同時改同一 skill 檔，Git merge 成本高。

**西堤套餐**（Set Meal）比喻：一個 skill 是一套餐；**每一道教材原題**對應一道可獨立烹調、獨立上菜、獨立下架的菜色（`ex_3`、`quiz_5`、`test_2`…）。套餐對外仍叫同一個名字（`skill_id`），學生端與 DB Schema 無感。

**v1.3 定位一句話**：不做學院派概念聚類，只做**教材原題的同構數值變異生成器**。

### 1.2 標準目錄結構（V3 物理佈局）

本節為 **v1.4 實體檔案物理佈局與向後相容薄外殼** 的剛性防線。  
Codex / 管線產出之每一道教材原題 `py` 程式，**必須**依下列樹狀結構存放；違反即視為 Namespace 污染或向後相容破壞。

```text
skills/                               # 【老屋根目錄 — 行政入口層，路徑雷打不動】
  {skill_id}.py                         # 【自動生成 · 禁止手改】Thin Facade 薄外殼（見 §1.3）
  ...                                   # 其他既有 skill 薄外殼（vh_數學B1_*.py 等）同樣保留於此層

agent_skills_v3/                        # 【新屋軍火庫 — 微元件實體歸宿】
  {skill_id}/                           # 單一 skill 的物理邊界（一 skill 一子目錄）
    skill.json                          # 單元 meta + 動態發布門檻（見 §4.3）
    component_manifest.json             # Phase 3 自動生成：verified / failed 全記錄
    __init__.py                         # 【自動生成 · 禁止手改】新屋路由調度器（_COMPONENT_DISPATCH）
    components/                         # 微元件倉庫根；嚴禁在此層直接堆疊 .py
      src_{textbook_example_id}/        # 一題一資料夾；例：src_4545、src_4610（見 §1.2.2）
        metadata.py                     # 八維度 + ORDER_WEIGHT / DIFFICULTY_LEVEL（強制）
        generate.py                     # 單題同構生成器（Gemini Flash 產物 · 搬運工）
        get_hint.py                     # 三階段引導（強制）
        check.py                        # 薄委派或本地 check 包裝（可選）
        tests/                          # 專屬沙盒；與姊妹 component 物理隔離
          test_component_smoke.py       # 獨立 pytest，不 import 其他 component

configs/generated_registry/
  {scope}_verified_registry.v*.yaml   # Phase 3 尾端同步
```

#### 1.2.1 老屋保留，新屋新蓋（剛性三條）

| # | 層級 | 物理路徑 | 剛性要求 |
|---|------|----------|----------|
| 1 | **主技能薄外殼（老屋入口）** | `skills/{skill_id}.py` | **雷打不動**保留於 `skills/` **根目錄**下。它是行政入口、門面；前台消費者（如 `practice.py`）執行 `importlib.import_module("skills.{skill_id}")` 時**唯一認得**的向後相容防線。**嚴禁**移入 `agent_skills_v3/`、**嚴禁**更名、**嚴禁**移除或改寫 import 路徑。 |
| 2 | **微元件資料夾（新屋倉庫）** | `agent_skills_v3/{skill_id}/components/{component_id}/` | 每一道教材原題 Codegen 產出之 `py` 程式（`metadata.py`、`generate.py`、`get_hint.py` 及專屬測試），**必須嚴格**放在**同一** `skill_id` 子目錄下、**各自獨立**的 `{component_id}/` 資料夾內。 |
| 3 | **禁止大雜燴** | — | **嚴禁**將多道題的 `py` 程式大雜燴地擠在同一目錄（含 `components/` 根層、`agent_skills_v3/{skill_id}/` 根層、或跨 `skill_id` 共用目錄）。每個 `src_{textbook_example_id}/` 資料夾內部**必須**獨立包含 `metadata.py`、`generate.py`、`get_hint.py` 及專屬 `tests/`，以確保 Namespace 完全隔離；`failed` 題型與 `verified` 題型在物理上互不干涉，定點修補半徑不污染姊妹題。 |

#### 1.2.2 `component_id` 物理命名契約（第一階段 · 剛性）

為在第一階段**完全消除** AI 對題型前綴（`ex_*` / `quiz_*` / `test_*`）的分類與命名幻覺，物理微元件目錄命名**剛性規定如下**：

| 項目 | 規範 |
|------|------|
| **禁止** | 管線或 AI **不得**猜測、推斷或自行發明 `ex_*` / `quiz_*` / `test_*` 作為硬碟目錄名 |
| **`component_id` 公式** | `src_{textbook_example_id}` — 直接取自 `textbook_examples.id` 主鍵 |
| **命名範例** | `textbook_examples.id = 4545` → `component_id = "src_4545"` |
| **硬碟實體路徑** | `agent_skills_v3/{skill_id}/components/src_{textbook_example_id}/` |
| **影子表對齊** | `gencode_component_tracker.component_id` **必須**與上述目錄名完全一致 |

> **備註**：`source_description`（例題 / 隨堂 / 自我評量）與 `ORDER_WEIGHT` / `DIFFICULTY_LEVEL` 仍由 §1.5 依教材語意注入 `metadata.py`；**僅**硬碟目錄名與 `component_id` 錨定主表主鍵，不經 AI 命名。

**老屋不動、新屋新蓋** 的行政契約（與上表互補）：

- **老屋（不變）**：`skills/` 根目錄薄外殼路徑、`SkillInfo` DB 表、`GENERATOR_SPECS` 白名單矩陣、`practice.py` 的 `importlib.import_module("skills.{skill_id}")` 調度入口——**全部不變**。
- **新屋（增量）**：數學邏輯與多模板分支**僅**遷入 `agent_skills_v3/{skill_id}/components/{component_id}/`；Phase 3 編譯器掃描 `verified` 子目錄後，自動寫入 `component_manifest.json`、`agent_skills_v3/{skill_id}/__init__.py`（新屋路由），並同步覆寫原位 `skills/{skill_id}.py`（老屋門面）。

### 1.3 自動生成 `__init__.py` 路由調度器

`core/gencode/skill_wrapper_compiler.py`（現行邏輯位於 `phase3_skill_codegen.build_phase3_skill_module_code`）在 Phase 3 執行：

1. 掃描 `agent_skills_v3/{skill_id}/components/` 下各 `{component_id}/` 子目錄，讀取 `component_manifest.json` 中 `status == "verified"` 的列。
2. 為每個 `component_id` 生成 import 與 dispatch 表項。
3. **寫入新屋路由**：更新 `agent_skills_v3/{skill_id}/__init__.py` 之 `_COMPONENT_DISPATCH`（禁止手改）。
4. **覆寫老屋門面**：同步自動覆寫原位 `skills/{skill_id}.py` Thin Facade（與 V2 形狀一致；**嚴禁**移出 `skills/` 根目錄，見 §1.2.1）。

**生成的 `__init__.py` 職責邊界**（與 V2 Thin Facade 同構）：

```python
# ── 自動生成，禁止手改 ──
from __future__ import annotations
from typing import Any
import random

from core.gencode.runtime_skill_wrapper import check_answer as _global_check
from core.gencode.runtime_skill_wrapper import generate_for_skill as _global_generate

SKILL_ID = "<skill_id>"
GENERATOR_SPECS = [...]  # 由 manifest 編譯
GENERATOR_KEYS = [...]

# component 級動態 import（僅 verified 組件）
_COMPONENT_DISPATCH: dict[str, Any] = {
    "<component_id>": {
        "generate": <callable from components.{component_id}.generate>,
        "get_hint": <callable from components.{component_id}.get_hint>,
    },
    ...
}

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict[str, Any]:
  # 1) 依 GENERATOR_SPECS 抽 problem_type / component_id
  # 2) 若 component 已 verified → 呼叫 _COMPONENT_DISPATCH[component_id]["generate"]
  # 3) 否則 fallback → _global_generate(SKILL_ID, GENERATOR_SPECS, ...)
  ...

def check(user_answer, correct_answer, question_payload=None):
  return _global_check(user_answer, correct_answer, payload=question_payload)

def get_hint(step: int, question_payload: dict | None = None) -> str:
  component_id = str((question_payload or {}).get("component_id") or "")
  fn = _COMPONENT_DISPATCH.get(component_id, {}).get("get_hint")
  if fn:
      return fn(step, question_payload)
  return ""
```

**向後相容保證**：

| 消費端 | 契約欄位 | V3 行為 |
|--------|----------|---------|
| `practice.py` | `generate(level, seed)` | 不變；仍 import `skills.{skill_id}` |
| DB `SkillInfo` | `skill_id` 字串 | 不變 |
| `GENERATOR_SPECS` | `problem_type_id`, `checker_key` | 由 manifest 編譯，欄位集合不擴張 |
| `runtime_skill_wrapper` | `answer_contract` 驅動批改 | `check()` 仍委派全域 checker 鏈 |
| RAG / Chroma | `skill_id:family_id` | 不變（AGENTS.md §9） |

### 1.4 Taxonomy Gate（輕量行政閘門）

**權威設定檔**：`configs/gencode_taxonomy/k12_component_taxonomy.yaml`

v1.3 **不再**以 Taxonomy 驅動概念聚類或題型拆分；Taxonomy 僅作**行政閘門**：確認 `skill_id` 落在 MVP 白名單內即可 `accepted` 進入 Phase 2。  
`component_id` 由教材實體題號決定（§1.5），**不由** Taxonomy 命名。

#### 1.4.1 首波 MVP 範疇鎖定（嚴禁全學制鋪開）

`configs/gencode_taxonomy/k12_component_taxonomy.yaml` 的**第一版實作嚴禁全學制鋪開**。  
垂直切片 MVP 測試期間，Taxonomy Gate **僅受理**下列 6 個核心單元；其餘 `skill_id` 一律標記 `human_approval_required` 且**不予收錄**。

| # | 單元範疇 | 代表 `skill_id`（首波鎖定） |
|---|----------|---------------------------|
| 1 | 高職 B1 直線方程式 | `vh_數學B1_PointSlopeForm`（及同族 `vh_數學B1_*Line*`） |
| 2 | 高職 B4 排列組合 | `vh_數學B4_*Permutation*` / `*Combination*` |
| 3 | 高職 B4 機率 | `vh_數學B4_*Probability*` |
| 4 | 高職 B4 統計 | `vh_數學B4_*Statistics*` / `*Mean*` / `*Std*` |
| 5 | 國中一次方程式 | `jh_數學*_*LinearEquation*` / `*OneVariable*` |
| 6 | 國中二次函數 | `jh_數學*_*QuadraticFunction*` / `*Quadratic*` |

**剛性規則**：

1. YAML 內以 `mvp_scope: v1` 區段包裹上述 6 類；Phase 1 **僅查詢**此區段。
2. `skill_id` 命中 MVP → 該 skill 下所有 `ex_*` / `quiz_*` / `test_*` 元件一律 `accepted` 進 Phase 2。
3. 不在 MVP 清單內的 `skill_id` → `human_approval_required`。

### 1.5 元件物理排序與天然難度契約

本節為 v1.3 **一題一 code** 與**天然順序排序**的剛性法規，取代舊版概念聚類與人工難度演算法。

#### 1.5.1 一題一對一物理隔離

`pipeline_orchestrator` 在 Phase 1 讀取案源時：

1. **不進行**任何概念聚類、題型融合或「大膽拆分」。
2. 每一筆 usable Source（例題、隨堂練習、自我評量）**強制**對應一個獨立 component 資料夾與**單一** `generate.py`。
3. `component_id` 直接取自教材實體題號或 `source_id`：

| 教材類型 | `component_id` 命名 | 範例 |
|----------|---------------------|------|
| 例題 | `ex_{題號}` | `ex_3` |
| 隨堂練習 | `quiz_{題號}` | `quiz_3` |
| 自我評量 / 課後習題 | `test_{題號}` | `test_7` |
| DB 有 `source_id` 時 | `{source_id}` 正規化 | `src_ex_3_001` |

**嚴禁**：多題共用一個 `generate.py`、AI 將兩道原題融合為一個 component、以 `target_task` 取代實體題號作為 `component_id`。

#### 1.5.2 天然難度權重注入

管線在生成 `metadata.py` 骨架時，依題號前綴**自動**注入（無需 AI 判定、無需複雜演算法）：

| 前綴系列 | `ORDER_WEIGHT` | `DIFFICULTY_LEVEL` | 語意 |
|----------|----------------|-------------------|------|
| `ex_*`（例題） | `10` | `"easy"` | 教材最前段、示範題 |
| `quiz_*`（隨堂練習） | `20` | `"easy"` | 課中練習；同級難度，排序靠後 |
| `test_*`（自我評量 / 課後） | `30` | `"hard"` | 單元後段評量題 |

```python
# metadata.py — 管線自動注入（禁止 AI 改寫）
ORDER_WEIGHT: Final[int] = 10          # ex_* → 10, quiz_* → 20, test_* → 30
DIFFICULTY_LEVEL: Final[str] = "easy"    # test_* → "hard"
SOURCE_REF: Final[str] = "ex_3"        # 回溯教材原題
```

**出題順序**：Phase 3 編譯 `GENERATOR_SPECS` 時依 `ORDER_WEIGHT` 升序排列；前台抽題可優先例題再隨堂再評量，**無需**額外難度推斷模組。

#### 1.5.3 同構變異契約（Isomorphic Contract）

每個 `generate.py` 僅服務**一道**原題，執行期行為：

- **固定**：題型結構、解題步驟數、變數個數、計算公式拓撲、`presentation_mode`、checker。
- **可變**：經 `seed` 驅動的數值參數（由 Domain Function `build_problem_matrix(seed=...)` 產生）。
- **禁止**：改變題型（如選擇題變填充題）、反向求解（除非該反向題在教材中有獨立 Source 與獨立 component）。

---

## 2. 八維度原子組件身分證合約

每個 `components/{component_id}/metadata.py` **必須**宣告下列八個維度。  
管線在 Phase 2 沙盒編譯前做靜態校驗；缺任一維度 → `component_contract_incomplete` blocker。

| 維度 | 欄位名 | 說明 |
|------|--------|------|
| D1 | `COMPONENT_ID` | 全域唯一；**必須**為教材實體題號（`ex_3` / `quiz_5` / `test_2`），見 §1.5 |
| D2 | `SKILL_ID` | 行政歸屬；唯讀，與 Word 匯入鎖定一致 |
| D3 | `TARGET_TASK` | 數學任務 token；對接 `template_slot_resolver.TASK_FAMILY_TO_SLOT` |
| D4 | `TEMPLATE_SLOT` | 執行期插槽名；必須存在於 `SLOT_REGISTRY` 或為 V3 新註冊 slot |
| D5 | `PRESENTATION_MODE` | 前台外觀 Key（見 §2.2） |
| D6 | `DOMAIN_LIBRARY` | 允許 import 的 Helper / Ops 白名單（見 §2.3） |
| D7 | `ANSWER_VERIFICATION_TYPE` | `checker_key` + `equivalence_type`；對接 `checker_registry` |
| D8 | `GENERATOR_READINESS` | `draft` / `runtime_ready` / `failed` / `verified` |

### 2.1 標準 Metadata 宣告範例

```python
# agent_skills_v3/vh_數學B1_LinearFunction/components/ex_3/metadata.py
from __future__ import annotations
from typing import Final

# ── D1–D2：身份 ──────────────────────────────────────────
COMPONENT_ID: Final[str] = "ex_3"
SKILL_ID: Final[str] = "vh_數學B1_LinearFunction"
SOURCE_REF: Final[str] = "ex_3"              # 回溯教材原題（管線注入）

# ── 天然難度（管線依前綴自動注入，禁止 AI 改寫）────────────
ORDER_WEIGHT: Final[int] = 10                 # ex_*=10, quiz_*=20, test_*=30
DIFFICULTY_LEVEL: Final[str] = "easy"         # test_* → "hard"

# ── D3–D4：數學任務與插槽 ────────────────────────────────
TARGET_TASK: Final[str] = "determine_linear_function_from_two_points"
TEMPLATE_SLOT: Final[str] = "linear_function_two_point_choice"

# ── D5：外觀 Key（穩定集合，禁止自創）────────────────────
PRESENTATION_MODE: Final[str] = "single_choice"
# 合法值全集：
#   integer | choice | single_choice | rational | interval_set
#   | equation | text_short | handwriting

# ── D6：Domain 白名單（僅允許 import 下列模組）────────────
DOMAIN_LIBRARY: Final[tuple[str, ...]] = (
    "core.domain.coordinate_geometry.line_equation_domain.build_line_equation_matrix",
    # 經 taxonomy_registry 解析；禁止在 generate.py 硬編碼 skill_id
)

# ── D7：批改合約（精確對接 checker_registry）──────────────
ANSWER_VERIFICATION_TYPE: Final[dict[str, str]] = {
    "checker_key": "choice_label_checker",       # → core.checkers.choice_label_checker
    "equivalence_type": "choice_label",          # CHECKER_CAPABILITIES 內合法等價類型
    "answer_type": "single_choice",              # payload answer_type
    "module": "core.checkers.choice_label_checker",
}

# ── D8：就緒狀態 ─────────────────────────────────────────
GENERATOR_READINESS: Final[str] = "draft"  # 沙盒通過後由管線改為 verified

# ── 語意附帶（非八維度，但 Phase 1 必填）──────────────────
SEMANTIC_REQUIRED_CONCEPTS: Final[tuple[str, ...]] = (
    "斜率",
    "兩點決定直線",
)
MATH_OBJECTS: Final[tuple[str, ...]] = (
    "coordinate_point",
    "linear_function",
    "horizontal_line",   # 水平線 — Phase 1 拆分依據
    "vertical_line",     # 鉛直線
)
TAXONOMY_PATH: Final[str] = "coordinate_geometry:line_equation"
```

### 2.2 PRESENTATION_MODE 穩定 Key 對照表

以下為前台 Web 與 `answer_contract.presentation_mode` **已穩定支援**的外觀 Key。  
AI Codegen **不得**自創新 Key；若需擴充，須先修改 `core/gencode/answer_format_hint.py` 與前台 renderer。

| Key | 典型 `answer_type` | 前台輸入元件 | 對接 Checker |
|-----|-------------------|--------------|--------------|
| `integer` | `integer` / `numeric` | 數字輸入框 | `integer_checker` / `numeric_checker` |
| `choice` | `choice` / `multi_choice` | 選項群組（泛用） | `choice_label_checker` |
| `single_choice` | `single_choice` | A/B/C/D 單選 | `choice_label_checker` |
| `rational` | `rational` / `fraction` | 分數輸入 | `rational_checker` / `fraction_checker` |
| `interval_set` | `interval` / `interval_set` | 區間輸入 | `interval_checker` |
| `equation` | `equation` / `expression` | 方程式輸入 | `equation_checker` / `linear_equation_equivalent_checker` |
| `text_short` | `text_short` / `short_answer` | 短文字 | `text_short_checker` |
| `handwriting` | `handwriting` / `manual_review` | 手寫板 + 相機上傳（文字框 disabled） | `ai_judged_checker` / `manual_review_checker` |

> **備註**：歷史資料中 `presentation_mode: "short_answer"` 與 `text_short` 外觀等價；V3 新組件統一使用上表 Key，`skill_wrapper_compiler` 負責向後映射。

#### 2.2.1 手寫題前端硬體連動（`handwriting` 專用）

當 `PRESENTATION_MODE == "handwriting"` 時，`runtime_skill_wrapper` 在 `finalize_generator_payload()` 階段**必須**注入下列前台控制宣告（沿用既有 payload 欄位，**不修改** `practice.py` 路由邏輯）：

```python
payload.update({
    "answer_type": "handwriting",
    "answer_input_type": "handwriting",
    "requires_handwriting": True,
    "input_mode": "handwriting",
    "text_input_disabled": True,          # 前台據此將文字輸入框設為 disabled
    "allow_camera_upload": True,
    "allow_canvas_drawing": True,
    "runtime_mode": "visual_or_handwriting_ai_checked",
    "check_mode": "handwriting_ai_checked",
    "grading_mode": "ai_judged_free_response",
})
```

**剛性防線**：

- 前台渲染系統讀取 `text_input_disabled: True` 後，**禁止**學生以鍵盤輸入文字答案；僅允許相機圖片上傳或畫布手寫。
- 批改由具備 Vision 能力的後台 LLM 執行語意判定；component 內**不得**自寫 `check()` 邏輯覆寫此路徑。
- 樹狀圖 / 列表題仍走 B4 `visual_or_handwriting_ai_checked` 契約；component 只輸出結構化數據，不觸碰前台元件選擇邏輯。

### 2.3 DOMAIN_LIBRARY 精確對接表

`DOMAIN_LIBRARY` 宣告的是 **Python import 路徑字串**，不是自由描述。  
Codegen 產生的 `generate.py` 只能 `from ... import ...` 此清單內的符號。

> **算子盾牌原則（v1.3）**：所有極端特例（如鉛直線分母為零崩潰、水平線退化、分母為零等）與數學變異，**統一**由工程師預先寫好的共用 Domain Function 算子盾牌進行 **deterministic** 控制。  
> Gemini Flash **僅允許**扮演搬運工：將算子回傳的 **Full Matrix Dictionary** 填入該單一題目的 f-string 模板，**禁止**自行解算或依題型在規格書內開專章 hard-code。  
> 規格書不再為每一種數學邊界撰寫獨立條文；邊界行為以算子庫實作與沙盒驗證為準。

| 領域 token | Helper 類別（首選） | Ops 類別（細算子） | 模組路徑 |
|------------|----------------------|-------------------|----------|
| `coordinate_geometry` | `build_line_equation_matrix` | — | **`core/domain/coordinate_geometry/line_equation_domain.py`**（v1.4 目標） |
| `algebra` | `build_linear_equation_matrix` | — | **`core/domain/algebra/linear_equation_domain.py`**（v1.4 目標） |
| `counting` | `build_permutation_combination_matrix` | — | **`core/domain/counting/permutation_combination_domain.py`**（v1.4 目標） |
| `statistics` | `build_descriptive_statistics_matrix` | — | **`core/domain/statistics/descriptive_statistics_domain.py`**（v1.4 目標） |
| `integer` | `IntegerFunctionHelper` | `IntegerOps` | `core/integer_domain_functions.py` / `core/prompts/domain_function_library.py`（現行） |
| `fraction` / `rational` | `FractionFunctionHelper` | `FractionOps` | `core/fraction_domain_functions.py`（現行） |
| `polynomial` | `PolynomialFunctionHelper` | `PolynomialOps` | `core/polynomial_domain_functions.py`（現行） |
| `radical` | `DomainFunctionHelper` | `RadicalOps` | `core/domain_functions.py` / `core/scaffold/domain_libs.py`（現行） |
| `calculus` | — | `CalculusOps` | `core/prompts/domain_function_library.py`（現行） |
| `geometry_slot` | — | `SLOT_REGISTRY[slot]` | `core/gencode/slot_generators.py`（現行） |
| `b4_payload` | `validate_*` / `check_*` | — | `core/vocational_math_b4/domain/b4_validators.py`（現行） |

> **遷移原則**：v1.4 目標模組上線後，`DOMAIN_LIBRARY` 白名單以 `core/domain/` 為 canonical；現行 `core/*_domain_functions.py` 僅作過渡 re-export，新題型**不得**再擴充舊路徑。

#### 2.3.1 Codegen 剛性防線：Domain Function 驅動（禁止 AI 自算）

**鐵律**（寫入 Gemini Flash Codegen 系統提示詞，違反即沙盒 AST / 語意掃描 blocker）：

> `generate.py` 內**禁止**出現 AI 自行撰寫的數學四則運算、手動組裝干擾項、或以 `random` 直接捏造「看起來合理」的錯誤答案。  
> 所有**正確答案**與**干擾項（distractors）**必須透過呼叫 `DOMAIN_LIBRARY` 白名單內的 Domain Function / Helper 計算並回傳。  
> AI 僅負責題幹字串的包裝、`SCENARIO_POOL` 填空（見 §3.4）、以及將 Domain Function 回傳值嵌入 payload。

**合法 / 非法對照**：

```python
# ❌ 非法：AI 自算答案與干擾項
correct = a * b + c
wrong = [correct + 1, correct - 2, correct * 2]

# ✅ 合法：委派 Domain Function，解開 Full Matrix Dict（見 §2.3.2、§2.5）
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix
matrix = build_line_equation_matrix(
    seed=seed,
    line_type="two_points",
    curriculum_profile="vocational_high_b",
    difficulty_profile="easy",
)
correct = matrix["answer"]["canonical_form"]
distractors = matrix["distractors"]
```

**沙盒 AST 掃描規則**（Phase 2.5；v1.2 精準化，避免誤殺控制流）：

##### 敏感區白名單（不得誤殺）

下列運算屬**控制流 / 基礎資料結構**，AST 掃描器**一律放行**，不觸發 `ai_math_operation_forbidden`：

| 敏感情境 | 合法範例 |
|----------|----------|
| 難度 / 層級遞增 | `level + 1`、`difficulty + 1` |
| 種子衍生 | `seed + 17`、`random.Random(seed + attempt)` |
| 迴圈邊界 | `range(n + 1)`、`for i in range(level + 2)` |
| 幾何顯示範圍 | `x_range = [-8, 8]`、`y_range = (-10, 10)` |
| 數值夾限 / 微調 | `min(1.0, base + 0.1)`、`max(-9, x - 1)` |
| 陣列索引 | `choices[i + 1]`、`SCENARIO_POOL[seed % len(SCENARIO_POOL)]` |
| 字串模板拼接 | `f"點 A({x}, {y})"`（非數學語意運算） |

##### 剛性阻擋條件（精準左值比對）

僅當**同時滿足**下列三條，才判定 `ai_math_operation_forbidden`：

1. **運算算子**：存在 `+`、`-`、`*`、`/`、`//`、`%`、`**` 之一的二元運算。
2. **賦值左值（Lvalue）敏感**：該運算結果直接或間接賦值至下列名稱之一，或其子欄位：
   - `answer`、`correct_answer`、`choices`、`distractors`、`options`
   - `visual_spec` 內的幾何數學坐標（如 `points[].x`、`points[].y`、`lines[].y`、`lines[].x`）
3. **無 Domain 算子特徵**：該 Code Block（同一 `def` 或同一 `while` 迴圈體）內，**完全沒有**對 `DOMAIN_LIBRARY` 白名單 Helper / Ops 的呼叫特徵（如 `_helper.`、`build_problem_matrix`、`CountingFunctionHelper` 等）。

> **設計意圖**：阻擋 AI 在答案路徑上「手算數學」；不阻擋 `level + 1` 這類與數學語意無關的控制流。

**其他沙盒規則**：

1. 選擇題：干擾項必須來自 Domain Function 回傳的 `distractors` 欄位，或 Helper 的 `build_*_distractors()`；禁止硬編碼四個字串選項。
2. 若 `visual_spec` 坐標由 Domain Function 的 `visual_spec` 鍵提供，component 內禁止對坐標重新四則運算。

#### 2.3.2 Domain Function 回傳契約：Full Matrix Dictionary

全面廢除單一 `compute_answer()` 回傳純量或單一字串的設計。  
`core/domain/` 下所有算子庫（v1.4 目標）及過渡期 `core/*_domain_functions.py`，**必須**回傳下列標準完整字典（Full Matrix Dictionary）：

```python
# Full Matrix Dictionary — 六大矩陣欄位（Domain 端一次算完，generate.py 禁止加工）
ProblemMatrix = {
    "givens": {                    # 已知條件（點、斜率、係數等原始數值）
        "point_a": (1, 3),
        "point_b": (3, 7),
        "slope": 2,
    },
    "answer": {                    # SymPy 算出的精確答案（結構化；非字串手拼）
        "canonical_form": "y=2x+1",
        "general_form": "2x-y+1=0",
        "line_type": "oblique_line",
    },
    "distractors": [               # 單選題誘答選項（已由算子生成，禁止 generate.py 改寫）
        "y=x+1",
        "y=2x-1",
        "y=-2x+1",
    ],
    "explanation_steps": [         # 步驟化解析提示（供 get_hint / 教師端）
        "代入點斜式",
        "化簡得斜截式",
    ],
    "validation_facts": {          # 驗證事實（供 Validator / Checker 交叉驗證）
        "slope": 2,
        "is_integer_slope": True,
        "line_passes_through": [(1, 3), (3, 7)],
    },
    "visual_spec": {               # 繪圖規格與坐標（僅數據，不在此時渲染）
        "kind": "coordinate_plane_spec",
        "points": [{"x": 1, "y": 3, "label": "A"}, {"x": 3, "y": 7, "label": "B"}],
        "lines": [{"type": "slope_intercept", "m": 2, "b": 1}],
        "x_range": [-8, 8],
        "y_range": [-8, 8],
    },
}
```

> **payload 封裝**：`generate.py` 可將 `matrix["answer"]["canonical_form"]` 填入 `payload["correct_answer"]` 等前台欄位，但**不得**對答案、誘答項或坐標做任何數學運算或重新推導。

**AI（Gemini Flash）搬運工角色**：

| 允許 | 禁止 |
|------|------|
| 呼叫 `build_problem_matrix()` 解開 Dict | 對 `givens` 內數值自行四則運算推導答案 |
| 將 `answer` / `distractors` 填入 payload 與 choices | 手動組裝或改寫 `distractors` 陣列 |
| 用 `givens` + `SCENARIO_POOL` 模板包裝 `question_text` | 對 `validation_facts` / `visual_spec` 坐標二次運算 |
| 將 `explanation_steps` 轉寫入 `metadata.derivation` | 覆寫 `answer` 字串內容 |

**沙盒斷言**（Phase 2.5）：`generate()` 內必須存在對 `core/domain/` 入口函式的呼叫（如 `matrix = build_line_equation_matrix(...)`），且 `payload["correct_answer"]` 可追溯至 `matrix["answer"]`（如 `matrix["answer"]["canonical_form"]`），**未經**手算改寫。

**幾何坐標算子**（水平線 / 鉛直線 / 兩點距離 / 分點 / 中點等）不在 component 內重寫 matplotlib；  
component 輸出結構化 `visual_spec`（見 §3.2），由底層 `slot_generators` 或 B4 visual runtime 統一渲染。

### 2.4 ANSWER_VERIFICATION_TYPE 與 checker_registry 對接

`core/gencode/checker_registry.py` 中 `runtime_available == True` 的 Key 為 V3 合法批改器：

| checker_key | module 路徑 | 典型 equivalence_type |
|-------------|-------------|----------------------|
| `choice_label_checker` | `core.checkers.choice_label_checker` | `choice_label`, `choice_label_exact` |
| `integer_checker` | pipeline（`runtime_skill_wrapper` 內建） | `numeric_exact`, `numeric_equivalence` |
| `numeric_checker` | pipeline | `numeric_exact`, `numeric_tolerance` |
| `rational_checker` | pipeline | `rational_equivalent`, `fraction_equal` |
| `fraction_checker` | pipeline | `fraction_equal` |
| `decimal_tolerance_checker` | pipeline | `decimal_tolerance` |
| `percentage_checker` | pipeline | `percentage_equivalent` |
| `expression_equivalence_checker` | `core.checkers.expression_equivalence_checker` | `algebraic_equivalent`, `expression_equivalence` |
| `expression_checker` | pipeline | 同上 |
| `equation_checker` | pipeline / `core.checkers`（語意擴充版） | `equation_equivalent`, `linear_equation_equivalent` |
| `linear_equation_equivalent_checker` | `core.checkers.linear_equation_equivalent_checker` | `linear_equation_equivalent` |
| `rational_or_decimal_checker` | `core.checkers.rational_or_decimal_checker`（V3 語意擴充） | `rational_decimal_equivalent` |
| `solution_set_checker` | `core.checkers.solution_set_checker` | `unordered_solution_set`, `set_equal` |
| `set_checker` | `core.checkers.solution_set_checker` | 同上 |
| `interval_checker` | `core.checkers.interval_checker` | `interval_equivalence`, `interval_set` |
| `quadrant_checker` | `core.checkers.quadrant_checker` | `normalized_label` |
| `coordinate_pair_checker` | `core.checkers.coordinate_pair_checker` | `coordinate_pair_equivalence`, `ordered_pair` |
| `tuple_checker` | `core.checkers.coordinate_pair_checker` | 同上 |
| `text_checker` | pipeline | `exact_text`, `normalized_text_equivalence` |
| `text_short_checker` | pipeline | `exact_string`, `case_insensitive_string` |
| `matrix_checker` | pipeline | `matrix_exact` |
| `manual_review_checker` | pipeline | `manual_review_or_ai_judged` |
| `ai_judged_checker` | pipeline | `manual_review_or_ai_judged` |

#### 2.4.1 高階語意等價檢查器（Semantic Checker）

以下兩項為 V3 **數學語意閉環**核心；component 的 `check.py` **不得**自行比對字串，必須在 `metadata.py` 宣告對應 `checker_key` 並委派 `runtime_skill_wrapper.check_answer()`。

##### 垂直切片優先級（v1.2 MVP 基礎設施）

首波垂直切片以 `vh_數學B1_PointSlopeForm`（直線方程式）為上線標竿。下列兩個 Checker 為**最優先穩定**的底層基礎設施，須在 Phase 2 沙盒與 Phase 3 smoke 全數通過後，方可標記 component `verified`：

| 優先級 | checker_key | 首波適用單元 | 穩定性要求 |
|--------|-------------|-------------|-----------|
| **P0** | `linear_equation_equivalent_checker` | B1 直線方程式、`vh_數學B1_PointSlopeForm` | 斜截式與一般式等價判定 100% 通過回歸測試 |
| **P0** | `rational_or_decimal_checker` | B1/B4 含分數或小數答案之題型 | `1/2` ≡ `0.5` 等價判定 100% 通過回歸測試 |

**代數比對剛性要求**（不允許因前台輸入格式多變而誤判）：

1. **直線方程式**：底層透過 SymPy 移項化簡與係數比例判定法，確保下列寫法語意等價、皆判正確：
   - 斜截式 `y = 2x + 1`
   - 一般式 `2x - y + 1 = 0` 或 `x - y + 1 = 0`（同一直線之等價變形）
   - 頂點式 / 點斜式經化簡後與上列同族者
2. **分數小數**：底層透過 SymPy 有理數化簡，確保 `1/2`、`0.5`、`0.50` 在題目語意允許小數時皆判正確；**禁止**僅做字串相等比對。

**1. `rational_or_decimal_checker`（P0）**

| 項目 | 說明 |
|------|------|
| 用途 | 分數 / 小數 / 整數混合答案的語意等價判定 |
| 底層機制 | 自動調用 SymPy 代數化簡，將學生輸入與標準答案歸一化至同一有理數語意 |
| 等價範例 | `1/2` ≡ `0.5` ≡ `0.50`（在題目允許小數語意時）→ 皆判正確 |
| `equivalence_type` | `rational_decimal_equivalent` |
| module | `core.checkers.rational_or_decimal_checker`（V3 目標；現行可過渡至 `expression_equivalence_checker` + SymPy） |

**2. `linear_equation_equivalent_checker`（P0 — 直線方程式首波主 Checker）**

| 項目 | 說明 |
|------|------|
| 用途 | 直線方程式專用語意等價；`vh_數學B1_PointSlopeForm` 等 B1 直線族**預設**使用此 Checker |
| 底層機制 | SymPy 移項化簡 + 係數比例判定；將斜截式、一般式、點斜式歸一化至同一直線語意 |
| 等價範例 | `y = 2x + 1` ≡ `2x - y + 1 = 0` ≡ `y - 2x = 1` → 皆判正確 |
| `equivalence_type` | `linear_equation_equivalent` |
| module | `core.checkers.linear_equation_equivalent_checker` |

**3. `equation_checker`（泛用方程式 — 非首波 P0，多項式擴充用）**

| 項目 | 說明 |
|------|------|
| 用途 | 方程式型答案的語意等價；專用於直線方程式、多項式恒等式 |
| 底層機制 | 移項化簡 + 係數比例判定法；將不同表示法歸一化至同一幾何物件 |
| 等價範例 | 斜截式 `y = x + 1` ≡ 一般式 `x - y + 1 = 0` ≡ `y - x = 1` → 皆判為同一條直線，算答對 |
| `equivalence_type` | `equation_equivalent` 或 `linear_equation_equivalent` |
| module | 優先 `core.checkers.linear_equation_equivalent_checker`；多項式恒等式擴充走 `equation_checker` |

> **首波切片選用規則**：直線方程式類 component（`TARGET_TASK` 含 `line_equation` / 兩點式 / 點斜式）**必須**綁定 `linear_equation_equivalent_checker`，不得降級為純字串比對。  
> **與 `equation_checker` 的分工**：`equation_checker` 為泛用入口；直線子類以 `linear_equation_equivalent_checker` 為 P0 快速路徑。

靜態校驗規則（Phase 2.5）：

```python
from core.gencode.checker_registry import validate_answer_contract_capability

result = validate_answer_contract_capability({
    "checker_key": metadata.ANSWER_VERIFICATION_TYPE["checker_key"],
    "answer_type": metadata.ANSWER_VERIFICATION_TYPE["answer_type"],
    "equivalence_type": metadata.ANSWER_VERIFICATION_TYPE["equivalence_type"],
})
assert result["checker_capability_status"] != "blocked"
```

B4 機率統計題額外通過 `b4_validators.validate_problem_payload_contract()` 與 `validate_answer_in_choices()` 等生成期守衛。

### 2.5 共用 Domain 邏輯層架構（v1.4 規劃 · 待實作）

本節定義 **數學核心邏輯的唯一歸宿**。不再依學制（國中 / 普高 / 技高）分開撰寫邏輯；所有 SymPy 計算、誘答選項（distractors）生成、`visual_spec` 坐標推導，**一律**收斂於 `core/domain/`。

#### 2.5.1 設計原則

| 原則 | 剛性要求 |
|------|----------|
| **按數學本質分層** | 目錄以數學領域組織（`coordinate_geometry`、`algebra`、`counting`、`statistics`），不以 `vh_` / `jh_` 學制前綴組織 |
| **嚴禁 skill_id 滲透** | `core/domain/` 內**不得**出現任何行政 `skill_id`；課綱差異以 `curriculum_profile` 參數控制 |
| **一次算完** | 單一入口函式回傳完整 **Full Matrix Dictionary**（§2.3.2 六大欄位） |
| **generate.py 零數學** | component 層禁止 SymPy、禁止手寫 distractors、禁止重算 visual 坐標 |

#### 2.5.2 目標模組清單（第一階段）

| 模組路徑 | 入口函式 | 涵蓋數學本質 | MVP 優先 |
|----------|----------|-------------|----------|
| `core/domain/coordinate_geometry/line_equation_domain.py` | `build_line_equation_matrix(...)` | 兩點式、點斜式、水平線、鉛直線、斜直線 | **P0** |
| `core/domain/counting/permutation_combination_domain.py` | `build_permutation_combination_matrix(...)` | 排列、組合、計數原理 | P1 |
| `core/domain/algebra/linear_equation_domain.py` | `build_linear_equation_matrix(...)` | 一元一次、聯立方程 | P1 |
| `core/domain/statistics/descriptive_statistics_domain.py` | `build_descriptive_statistics_matrix(...)` | 平均、加權、標準差、全距 | P1 |

#### 2.5.3 控制參數契約（課綱差異的唯一入口）

Domain 函式**統一**接受下列參數；課綱 / 難度差異由內部解讀，**不得**在 component 內 if-else `skill_id`：

```python
def build_line_equation_matrix(
    *,
    seed: int | None,
    line_type: str,                    # two_points | point_slope | horizontal_line | vertical_line | oblique_line
    curriculum_profile: str,           # 例：vocational_high_b | junior_high | general_high
    difficulty_profile: str,           # 例：easy | medium | hard（可與 metadata DIFFICULTY_LEVEL 對接）
    constraints: dict[str, object] | None = None,  # 例：禁止複雜斜率證明、整數係數限定
) -> dict[str, object]:
    ...
```

**`curriculum_profile` 範例語意**（以技高數 B 直線方程式為例）：

- 允許：基礎斜率、點斜式、兩點式、水平 / 鉛直退化
- 禁止：過於複雜的斜率幾何證明、非課綱範圍之解析幾何推論
- 數值範圍、係數型態（整數 / 有理數）由 `constraints` 與 `difficulty_profile` 聯合決定

#### 2.5.4 `line_equation_domain` 內部職責（P0 標竿）

`build_line_equation_matrix` 須在**單一函式族**內處理：

| `line_type` | 內部行為 |
|-------------|----------|
| `two_points` | 兩點求直線；自動偵測退化為水平 / 鉛直 |
| `point_slope` | 已知一點與斜率 |
| `horizontal_line` | $y = k$；分母為零等邊界在此處理 |
| `vertical_line` | $x = k$；禁止誤用一般斜率公式 |
| `oblique_line` | 一般斜直線；SymPy 化簡斜截式 / 一般式 |

回傳之 `answer` 為**結構化 dict**（含 `canonical_form`、`general_form`、`line_type`）；`distractors` 與 `visual_spec` 必須與 `validation_facts` 數學一致。

#### 2.5.5 第一階段實作檢查點（直線方程式）

調整 `components/{component_id}/generate.py` 與 `line_equation_domain.py` 時，驗收**必須**確認：

- [ ] Domain 回傳六大欄位齊全：`givens`、`answer`、`distractors`、`explanation_steps`、`validation_facts`、`visual_spec`
- [ ] `generate.py` 內**無** `import sympy`、**無** distractors 組裝演算法、**無** visual 坐標四則運算
- [ ] `payload["correct_answer"]` 可追溯至 `matrix["answer"]`（未經手算改寫）
- [ ] 鉛直線 / 水平線退化案例由 Domain 內部 deterministic 處理（不在 SOP 開專章 hard-code）
- [ ] `curriculum_profile="vocational_high_b"` 時數值範圍符合技高 B 課綱

### 2.6 `generate.py` 搬運工契約（生成調度層）

`components/{component_id}/generate.py` 在 v1.4 架構下**全面減肥**，職責僅剩：

1. 從 `metadata.py` 讀取 `DOMAIN_LIBRARY` 與 profile 參數（`curriculum_profile`、`difficulty_profile`）。
2. 呼叫對應 Domain 入口函式（經 Registry 解析，見 §2.7）。
3. 將 Full Matrix Dictionary **原樣搬運**至 payload（允許 f-string 題幹模板填空，禁止數學加工）。

```python
# ✅ v1.4 合法 generate.py 骨架（搬運工）
from core.domain.coordinate_geometry.line_equation_domain import build_line_equation_matrix

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict:
    matrix = build_line_equation_matrix(
        seed=seed,
        line_type="two_points",
        curriculum_profile="vocational_high_b",
        difficulty_profile="easy",
        constraints={"integer_coefficients": True},
    )
    givens = matrix["givens"]
    answer = matrix["answer"]["canonical_form"]
    choices = [answer] + list(matrix["distractors"])
    # ... 僅模板填空與 payload 封裝，無 SymPy、無坐標重算
    return {
        "question_text": f"過點 A{givens['point_a']} 與 B{givens['point_b']} 的直線方程式為何？",
        "correct_answer": answer,
        "choices": choices,
        "visual_spec": matrix["visual_spec"],
        "math_core": {"givens": givens, "derivation": matrix["explanation_steps"]},
    }
```

```python
# ❌ v1.4 禁止：generate.py 內自行計算
import sympy as sp
slope = (y2 - y1) / (x2 - x1)          # ai_math_operation_forbidden
distractors = [f"y={slope}x+{b+1}", ...]  # 禁止
visual_spec["points"][0]["x"] = x1 + 1    # 禁止
```

### 2.7 Domain 註冊與對應層（Registry 中繼）

**目標模組**：`core/registry/taxonomy_registry.py`（或倉庫內等價 registry 檔；實作前以本 SOP 路徑為準）

本層為 **skill_id → Domain Function** 的唯一硬編碼中繼站：

| 職責 | 說明 |
|------|------|
| 綁定行政 skill | 將 `vh_數學B1_PointSlopeForm` 等外層 `skill_id` 映射至 `line_equation_domain.build_line_equation_matrix` |
| 注入 profile 預設 | 為技高 B 單元預置 `curriculum_profile="vocational_high_b"` |
| 解析 component 參數 | 依 `metadata.TARGET_TASK` / `line_type` 傳入 Domain 函式 |

```python
# taxonomy_registry.py — skill_id 僅允許出現在此層
SKILL_TO_DOMAIN: dict[str, dict] = {
    "vh_數學B1_PointSlopeForm": {
        "domain_module": "core.domain.coordinate_geometry.line_equation_domain",
        "entrypoint": "build_line_equation_matrix",
        "default_curriculum_profile": "vocational_high_b",
    },
    "vh_數學B4_SimplePermutation": {
        "domain_module": "core.domain.counting.permutation_combination_domain",
        "entrypoint": "build_permutation_combination_matrix",
        "default_curriculum_profile": "vocational_high_b",
    },
}
```

**剛性原則**：

1. `skill_id` 硬編碼**只能**停留在 Registry / Taxonomy 設定層；**絕對禁止**傳入 `core/domain/` 內部。
2. 新增國中 / 普高題型時，僅調整 `metadata` 的 `curriculum_profile` 與 Registry 預設，**不修改**底層數學代碼。
3. Phase 1 / Phase 2 管線透過 Registry 解析 Domain 入口；`generate.py` **不得**硬編碼 `skill_id` 分支。

---

## 3. 應用問題與圖片題特殊處理防線

### 3.1 Phase 1：單題故事層與數學核心層解構（同構用）

**目標**：為**每一道**教材原題建立同構變異模板；數學核心由 Domain Function 算子盾牌產生，AI 僅負責題幹填空。

**強制三步解構**（每題獨立，在 `problem_type_induction` / Phase 1 merge 階段執行）：

```
┌─────────────────────────────────────────────────────────────┐
│ 原始 Source Example（課本文本 + 圖 + 答案）                    │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer A：Story Layer         │
              │ - 人名、單位、情境動詞          │
              │ - 非數學修飾語                │
              │ → scenario_pool / literacy_stem │
              └─────────────┬───────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer B：Math Core Layer     │
              │ - target_task                │
              │ - givens / unknowns / constraints│
              │ → Domain Function 算子盾牌     │
              └─────────────┬───────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Layer C：Presentation Layer  │
              │ - presentation_mode Key      │
              │ - answer_contract            │
              │ → ex_* / quiz_* / test_*     │
              └─────────────────────────────┘
```

**操作規則**（v1.3 同構優先）：

1. **一題一 component**：每道教材原題對應獨立 `component_id`（§1.5）；Story / Math Core / Presentation 三層僅用於**單題**模板填空，不驅動跨題聚類。
2. **Story 不得綁定 Checker**：`answer_contract` 只能來自 Math Core + Presentation；應用題故事層固定於該題 `SCENARIO_POOL`（§3.4）。
3. **禁止跨題拆分或合併**：同一課本題號即一個 component；若教材將「求斜率」與「寫方程式」列為兩道獨立題，則為兩個 `ex_*` / `quiz_*`，**不得** AI 融合或拆分。
4. **去糖衣驗證**：Math Core 必須能在純數學模式下由 Domain Function 產生合法 payload；數值與答案僅來自算子盾牌。

### 3.2 圖片掛載機制：禁止 AI 手寫繪圖

| 角色 | 允許 | 禁止 |
|------|------|------|
| Gemini Flash（component `generate.py`） | 輸出 `visual_spec` JSON（坐標、線段、標籤、統計表） | `import matplotlib`、`plt.`、`PIL.`、任何 `image_base64 =` 賦值 |
| 底層管線 | 將 `visual_spec` 轉為 `image_base64`，附掛至 payload | — |
| Visual Validator | 對 `visual_spec` 執行幾何重算與範圍檢查（見 §3.2.2） | — |
| 前台 | 讀取 `image_base64` 或 `visual_asset_type` 渲染 | 執行 component 內嵌繪圖代碼 |

#### 3.2.1 `visual_spec.kind` 全中學數學範疇

V3 將 `kind` 擴展為下列 **canonical spec 類型**（`visual_spec.kind` 欄位值）：

| kind | 語意 | 典型數學場景 |
|------|------|-------------|
| `coordinate_plane_spec` | 坐標平面上的點、線、函數圖形 | 直線方程式、兩點距離、象限 |
| `geometry_diagram_spec` | 純幾何構圖（不一定有坐標軸） | 三角形、中線、角平分線 |
| `statistics_chart_spec` | 統計圖表 | 長條圖、折線圖、累積頻率 |
| `tree_diagram_spec` | 樹狀圖 / 列表樹 | 排列組合、機率樣本空間 |
| `table_spec` | 數據表格 | 分組頻率、二維列聯表 |
| `number_line_spec` | 數線 | 不等式解區間、絕對值 |

**`coordinate_plane_spec` 標準形狀**（component 輸出，管線消費）：

```python
visual_spec = {
    "kind": "coordinate_plane_spec",
    "points": [{"x": 1, "y": 2, "label": "A"}],
    "lines": [
        {"type": "horizontal", "y": 3, "label": "L1"},
        {"type": "vertical", "x": -2, "label": "L2"},
        {"through_points": ["A", "B"], "label": "L3"},  # 過兩點的直線
    ],
    "x_range": [-8, 8],
    "y_range": [-8, 8],
}
# generate() 回傳前禁止自行渲染；由 slot_generators 或 visual runtime 統一轉換：
# payload["image_base64"] = render_visual_spec(visual_spec)
# payload["visual_asset_type"] = "coordinate_plane_spec"
```

#### 3.2.2 圖形語意驗證器（Visual Validator）

**模組**：`core/gencode/visual_schema_validators.py`（V3 目標）

##### 三層權責剛性劃分（產生 / 搬運 / 審核）

| 層級 | 職責 | 剛性邊界 |
|------|------|----------|
| **Domain 邏輯層**（`core/domain/`） | **產生** | 利用 SymPy 等算子** deterministic** 產出答案、干擾項與 `visual_spec` 繪圖數據；寫入 Full Matrix Dictionary |
| **Component 層**（`generate.py`） | **搬運** | 僅將 Domain 回傳的 `visual_spec` 填入 payload，並以 f-string 包裝題幹；**嚴禁** SymPy、數學四則運算、坐標重算 |
| **Validator 層**（`visual_schema_validators`） | **審核** | **完整保留**代數幾何重算與斷言權力；沙盒驗證鏈中須放行 Validator 重新計算直線方程式、點線關係等，對搬運結果做剛性交叉驗證 |

> **與 §2.3.1 AST 掃描的關係**：`ai_math_operation_forbidden` **僅約束** `generate.py`（Component 層）不得在答案路徑手算數學；Validator 層的幾何重算屬**審核權**，不列入 AI 自算限制，亦不得被 AST 規則誤殺。

當 component payload 含 `visual_spec` 時，Phase 2.5 沙盒 **Fail-Fast** 驗證鏈必須調用此模組，進行**數學幾何剛性重算**，確保圖文 100% 一致：

| 驗證函式 | 觸發條件 | 檢查內容 |
|----------|----------|----------|
| `validate_coordinate_points_in_range` | `kind` 含 `coordinate` / `geometry` | 所有點 `(x,y)` 落在 `x_range` × `y_range` 內 |
| `validate_line_passes_through_points` | `lines[].through_points` 存在 | 重算直線方程，驗證必過宣告的兩點 |
| `validate_horizontal_line_y` | `lines[].type == "horizontal"` | 水平線 `y` 值與題幹 givens 一致 |
| `validate_vertical_line_x` | `lines[].type == "vertical"` | 鉛直線 `x` 值與題幹 givens 一致 |
| `validate_tree_diagram_branch_counts` | `kind == "tree_diagram_spec"` | 樹分支數與 `expected_paths` / `expected_count` 一致 |
| `validate_statistics_chart_data` | `kind == "statistics_chart_spec"` | 圖表數據列與 `math_core.givens` 數值一致 |

驗證失敗 → `visual_semantic_mismatch` blocker；觸發 component 級修補閉環（優先檢查 Domain 產出與 `generate.py` 搬運是否一致，**不**改繪圖引擎；Validator 重算邏輯本身不得削弱）。

**附掛規則**：

- `presentation_mode` 為 `single_choice` / `choice` / `integer` 時，均可帶 `image_base64`；圖為題幹附件，不改變 `checker_key`。
- `handwriting` + 樹狀圖/列表題：走 B4 `visual_or_handwriting_ai_checked` 契約（`core/routes/practice.py` 既有路徑），component 只輸出 `expected_paths` / `tree_depth` 等數據。

### 3.3 `get_hint(step)` 三階段引導式提示（強制 Skeleton）

每個 component **必須**實作 `get_hint.py`，且通過沙盒測試 `step in {1,2,3}` 均回傳非空字串。

```python
# agent_skills_v3/{skill_id}/components/{component_id}/get_hint.py
from __future__ import annotations
from typing import Any

def get_hint(step: int, question_payload: dict[str, Any] | None = None) -> str:
    """
    三階段引導式提示 — 強制語意骨架。
    step=1 閱讀轉譯 | step=2 數學建模 | step=3 算式推導
    """
    payload = question_payload or {}
    story_ctx = str(payload.get("story_context") or "")
    math_core = payload.get("math_core") or {}
    givens = math_core.get("givens") or payload.get("metadata", {}).get("givens") or []

    if step == 1:
        # ── 閱讀轉譯：從故事層提取已知與所求，不給公式 ──
        given_text = "、".join(str(g) for g in givens) if givens else "題目給定的條件"
        return (
            f"請先閱讀題目，找出已知條件與要求的量。"
            f"{'情境：' + story_ctx if story_ctx else ''}"
            f"目前已知：{given_text}。請用一句話說明「要求什麼」。"
        )

    if step == 2:
        # ── 數學建模：建立變數、選擇數學物件，不展開完整計算 ──
        target = str(math_core.get("target") or payload.get("metadata", {}).get("target") or "未知量")
        objects = math_core.get("math_objects") or []
        obj_text = "、".join(objects) if objects else "適當的數學關係"
        return (
            f"將文字條件轉成數學語言：設定變數，並指出此題屬於「{obj_text}」類型。"
            f"目標是求：{target}。"
        )

    if step == 3:
        # ── 算式推導：給出關鍵一式或下一步，不直接給最終答案 ──
        derivation = math_core.get("derivation") or payload.get("metadata", {}).get("derivation") or []
        if derivation:
            return f"依序思考：{' → '.join(str(d) for d in derivation)}。寫出關鍵算式後再化簡。"
        return "寫出本題適用的核心公式，代入已知數值，逐步化簡得到答案。"

    return ""  # step 非法時回空；沙盒測試僅驗證 1–3
```

**強制要求**：

- `generate()` 回傳的 payload **應**包含 `math_core` 子物件（含 `givens`, `target`, `math_objects`, `derivation`），供 `get_hint` 數據驅動。
- 禁止在 hint 中輸出與 `correct_answer` 等價的最終數值（防洩答）。
- RAG 三層檢索（圖譜 / 課本 / SKILL.md）仍為 Review 模式補充；`get_hint` 為確定性鷹架，不依賴 LLM 即時生成。

### 3.4 應用問題「挖洞模板化」：`SCENARIO_POOL` 規範

應用題 / 情境字題的 Story Layer **禁止**在學生練習時由 LLM 即時自由發揮。Codegen 提示範本**強制**要求 AI 將應用題編寫為預定義字典陣列：

```python
# generate.py — 應用題強制結構（AI 模板工程師產出）
SCENARIO_POOL = [
    {
        "id": "prize_draw",
        "subject": "小朋友",       # 故事主體 A
        "object": "獎品",          # 故事客體 B
        "verb": "抽取",
        "template": "{subject}從箱中{verb}{object}，已知...求...",
    },
    {
        "id": "ice_cream_shop",
        "subject": "學生",
        "object": "冰淇淋",
        "verb": "購買",
        "template": "某{object}店，{subject}{verb}後...求...",
    },
    # ... 至少 3 筆，由 Phase 1 scenario_pool 驅動
]

def _pick_scenario(seed: int | None) -> dict:
    rng = random.Random(seed)
    return rng.choice(SCENARIO_POOL)

def generate(level: int = 1, seed: int | None = None, **kwargs) -> dict:
    scenario = _pick_scenario(seed)
    # Math Core 由 Domain Function 計算（見 §2.3.1）
    math_result = _DOMAIN_HELPER.compute(...)  # 正確答案來自算子，非 AI
    question_text = scenario["template"].format(
        subject=scenario["subject"],
        object=scenario["object"],
        verb=scenario["verb"],
        # ... 僅允許 f-string / format 剛性填空
    )
    ...
```

**剛性規則**：

1. Runtime 出題時**僅**透過 `seed` 從 `SCENARIO_POOL` 抽選故事層；禁止呼叫 LLM 改寫題幹。
2. 允許變異的僅為 `SCENARIO_POOL` 內預審詞彙；數值、答案、圖形坐標仍由 Domain Function 決定。
3. `question_text` 內的數學條件必須與 `math_core` 一致；沙盒以 `visual_schema_validators` 與 payload validator 交叉驗證。
4. 違反（執行期呼叫 `call_ai_*` 生成題幹）→ `runtime_llm_story_forbidden` blocker。

---

## 4. 優雅降級與放手哲學

### 4.1 子組件沙盒隔離測試

每個 `component_id` 在併入 manifest 前，**獨立**執行沙盒測試（不 import 姊妹 component）：

```bash
python -m pytest agent_skills_v3/{skill_id}/components/{component_id}/tests/ -q
```

**最低通過清單**：

1. `metadata.py` 八維度靜態校驗通過。
2. `generate(level=1, seed=0)` 連續 5 次無例外；payload 通過 `validate_generator_payload()` + `validate_generated_question_format()`。
3. `check(correct, correct)` 為 True；`check(wrong, correct)` 為 False。
4. B4 題型額外通過 `b4_validators.validate_problem_payload_contract()`。
5. `get_hint(1..3)` 皆非空。
6. 若含 `visual_spec`：斷言 component 內**無** `matplotlib` / `PIL` import；且通過 `visual_schema_validators` 全項檢查。
7. 斷言 `generate.py` 無違反 §2.3.1 的 AI 自算數學運算。
8. 應用題斷言存在 `SCENARIO_POOL` 且執行期不呼叫 LLM 改寫題幹。

沙盒失敗**只標記該 component**，不影響其他 component 的測試進程。

### 4.2 單一組件修補閉環（v1.3：修補半徑 = 單一題目檔案）

因採行「一題一 `generate.py`」架構，`gencode_closed_loop/controller.py` 的修補半徑**縮小至單一題目檔案**：

1. 讀取 `GENERATOR_REPAIR_CATALOG` 或 component 路徑映射，**僅**鎖定 `components/{component_id}/generate.py`（該 `component_id` 對應一道原題，如 `quiz_5`）。
2. 將 `blockers` + `generation_errors` 作為 Negative Feedback 餵給 Gemini Flash。
3. 覆寫**該單檔**後重跑沙盒；**不得**連帶修改姊妹題 `ex_*` / `quiz_*` / `test_*` 檔案。

```text
MAX_RETRY_PER_COMPONENT = 3   # 每道原題獨立計次
```

### 4.3 放手降級與動態發布門檻（v1.3 Partial Publish）

> **v1.3 修訂**：核心例題（`required_core_components`，通常為 `ex_*` 系列）`verified` 即可 **Partial Publish**；單一隨堂或自我評量失敗不阻斷發布、不觸發 skill 級 `SYSTEM_INTERRUPT`。

#### 4.3.1 `skill.json` 發布門檻宣告

```json
{
  "skill_id": "vh_數學B4_SimplePermutation",
  "display_name": "簡單排列",
  "expected_component_count": 5,
  "required_core_components": [
    "ex_1",
    "ex_2"
  ]
}
```

| 欄位 | 說明 |
|------|------|
| `expected_component_count` | 此 skill 預期應有的 component 總數（例題 + 隨堂 + 自我評量）；用於覆蓋率審計 |
| `required_core_components` | **必須 verified 才能發布**的核心例題 `component_id` 清單（建議以 `ex_*` 為主） |

##### 4.3.1.1 `required_core_components` 權限剛性鎖定（禁止 AI 自動判定）

`agent_skills_v3/{skill_id}/skill.json` 中的 `required_core_components` 為**發布門檻憲法級欄位**，寫入權限嚴格限定：

| 合法寫入來源 | 說明 |
|-------------|------|
| `k12_component_taxonomy.yaml` 內該 `skill_id` 的靜態 `required_core_components` 條目 | **首選唯一自動來源** |
| 架構師人工預置 / PR 審核合併 | 僅限擴充 MVP 範疇時 |

**嚴禁行為**（Phase 1 案源誘導、Phase 2 Codegen、修補閉環、AI 提示詞）：

1. 管線程式**不得**依誘導結果動態新增、刪除或改寫 `required_core_components`。
2. Gemini Flash **不得**在 `generate.py` / `metadata.py` 或任何產物中輸出「建議 core 清單」並由腳本寫回 `skill.json`。
3. 禁止 AI 投機性地將高難度核心題型從 `required_core_components` 移除，以規避發布門檻。

**防禦意圖**：確保發布門檻反映課綱真實核心，而非 AI 討好式降標。

> `expected_component_count` 亦僅能由 Taxonomy 靜態條目或架構師預置；AI 與 Phase 1/2 管線同樣**不得**自動修改。

#### 4.3.2 動態發布判定邏輯

| 條件 | 管線行為 |
|------|----------|
| 單一 `quiz_*` / `test_*` component 重試 3 次仍失敗 | 標記 `GENERATOR_READINESS = "failed"`；寫入 manifest `status: failed`；**停止該題修補**；從發布清單剔除 |
| `required_core_components`（核心例題，通常 `ex_*`）**全部** `verified` | **Partial Publish**：將其餘 `verified` 題目編譯發布；`failed` 的隨堂 / 自我評量**直接剔除**，前台僅載入通過題目 |
| `required_core_components` 僅 1 個且該項 `verified` | **允許 Partial Publish**（小技能豁免） |
| 任一 `required_core_components` 未達 `verified` | `publish_status: blocked`；**仍不觸發** `SYSTEM_INTERRUPT` |
| 無 `required_core_components` 宣告時（舊 skill 過渡） | fallback：`verified_count >= max(2, ceil(expected_component_count * 0.5))` |
| controller 無法定位任何可修補檔案，或 skill 級基礎設施損壞 | **唯一**觸發 `SYSTEM_INTERRUPT` 的情境 |

**關鍵原則（v1.3）**：

- `SYSTEM_INTERRUPT` **禁止**因單一 `quiz_*` / `test_*` 失敗而觸發；確保前台學生練習**絕對順暢、不崩潰**。
- 只要 `skill.json` 預置的核心例題組件處於 `verified`，系統便將通過題目編譯發布（Partial Publish），失敗題目靜默剔除。
- `publish_status` 可為 `partial_published`（含剔除的 failed 題）或 `full_published`（全部 verified）。

```python
# 動態發布決策虛擬碼（skill_wrapper_compiler 內）
skill_meta = load_skill_json(skill_id)
required = skill_meta.get("required_core_components") or []
verified_ids = {c["component_id"] for c in manifest["components"] if c["status"] == "verified"}

if required:
    core_ok = all(cid in verified_ids for cid in required)
    if core_ok:
        compile_partial_router(skill_id, [c for c in manifest["components"] if c["status"] == "verified"])
        sync_verified_registry(skill_id, verified_ids)
        publish_status = "partial_published" if any_failed else "full_published"
    else:
        publish_status = "blocked_core_components_missing"
else:
    # 舊 skill 過渡 fallback
    verified = [c for c in manifest["components"] if c["status"] == "verified"]
    threshold = max(2, math.ceil(skill_meta.get("expected_component_count", 2) * 0.5))
    publish_status = "partial_published" if len(verified) >= threshold else "blocked_insufficient_components"
```

### 4.4 manifest 記錄格式

`component_id` **必須**為教材實體題號（§1.5），不得使用 `target_task` 或任務聚類命名。

```json
{
  "skill_id": "vh_數學B1_LinearFunction",
  "compiled_at": "2026-06-15T14:30:00+08:00",
  "publish_status": "partial_published",
  "components": [
    {
      "component_id": "ex_1",
      "status": "verified",
      "presentation_mode": "single_choice",
      "checker_key": "choice_label_checker",
      "retry_count": 1
    },
    {
      "component_id": "quiz_5",
      "status": "failed",
      "last_error": "generator_semantically_unsafe: choices mismatch",
      "retry_count": 3
    }
  ]
}
```

---

### 4.5 教材例題權威庫資料庫（DB Schema）增量設計

本節為 v1.4 **線上滾動式維運**所需之**唯一允許** DB 增量設計。  
**不修改** `textbook_examples` 既有欄位結構；Gencode 管線狀態、Low-Code 誘導規格與沙盒錯誤日誌**全部**收斂至獨立影子對接表 `gencode_component_tracker`。  
**嚴禁**修改學生練習紀錄、答題軌跡、成績彙總等學習數據表。

#### 4.5.1 Canonical DDL（SQLite 3 · Production 對齊）

```sql
-- =============================================================================
-- Gencode × AgentSkillV3 獨立維運影子對接表
-- 方言：SQLite 3
-- 核心作用：建立 textbook_examples(id) 與硬碟微元件物理路徑的剛性對接橋樑
-- =============================================================================
CREATE TABLE IF NOT EXISTS gencode_component_tracker (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    textbook_example_id     INTEGER NOT NULL,   -- 主錨點：1 對 1 關聯 textbook_examples.id
    skill_id                TEXT    NOT NULL,   -- 行政錨點：利於依單元批次 Partial Publish 查詢
    component_id            TEXT    NOT NULL,   -- 物理錨點：src_{textbook_example_id}，如 'src_4545'
    gencode_status          TEXT    NOT NULL DEFAULT 'pending', -- 狀態機核心
    induced_spec_payload    TEXT,               -- Low-Code 維運核心：去糖衣後的 JSON 字串
    gencode_error_log       TEXT,               -- Sandbox / Validator 幾何代數崩潰日誌
    created_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at              TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    CONSTRAINT fk_gencode_component_tracker_example
        FOREIGN KEY (textbook_example_id) REFERENCES textbook_examples (id) ON DELETE CASCADE,
    CONSTRAINT fk_gencode_component_tracker_skill
        FOREIGN KEY (skill_id) REFERENCES skills_info (skill_id) ON DELETE CASCADE,
    CONSTRAINT uq_gencode_tracker_example_id
        UNIQUE (textbook_example_id),
    CONSTRAINT uq_gencode_tracker_namespace_pool
        UNIQUE (skill_id, component_id),
    CONSTRAINT ck_gencode_status_values
        CHECK (gencode_status IN (
            'pending', 'usable', 'generating', 'verified', 'failed',
            'enrichment', 'needs_human_review', 'needs_regeneration'
        ))
);

CREATE INDEX IF NOT EXISTS idx_gencode_tracker_query_gate
    ON gencode_component_tracker (skill_id, gencode_status);

CREATE INDEX IF NOT EXISTS idx_gencode_tracker_reverse_lookup
    ON gencode_component_tracker (textbook_example_id);
```

**雙重 UNIQUE 防線語意**：

| 約束名 | 欄位 | 防線目的 |
|--------|------|----------|
| `uq_gencode_tracker_example_id` | `textbook_example_id` | 一筆教材原題**最多**對應一列 tracker；禁止同一 `textbook_examples.id` 被重複掛載 |
| `uq_gencode_tracker_namespace_pool` | `(skill_id, component_id)` | 同一 skill 命名空間內 `component_id` 不可重複；對齊 `agent_skills_v3/{skill_id}/components/{component_id}/` 物理隔離 |

#### 4.5.2 `gencode_status` 狀態機（CHECK 約束合法值）

| 值 | 語意 | 典型觸發 |
|----|------|----------|
| `pending` | 尚未進入 Phase 2 或等待管理員觸發重構 | Phase 1 完成、尚未 Codegen |
| `usable` | 誘導規格已就緒，可進入 Codegen 佇列 | Phase 1 induced spec 寫入 tracker |
| `generating` | Phase 2 Codegen / 修補閉環進行中 | Gemini Flash 產出或 controller 重試 |
| `verified` | 單題沙盒通過，可進入 manifest 白名單 | Phase 2.5 全項通過 |
| `failed` | 單題驗證失敗（含 3 次修補後放手） | AST / Validator / smoke 失敗 |
| `enrichment` | 補充題 / 非核心例題；可不阻斷 Partial Publish | 人工標記或 Phase 1 分類 |
| `needs_human_review` | 需人工審核後方可繼續 | Taxonomy Gate / 語意對齊阻擋 |
| `needs_regeneration` | 誘導規格或 Domain 參數已變更，待重跑 Codegen | 後台修正 `induced_spec_payload` 後 |

#### 4.5.3 影子表 Service 層契約（行政歸屬斷言）

後端 Service 層在**新增或更新** `gencode_component_tracker` 紀錄前，**必須**強制檢查並斷言：

```text
gencode_component_tracker.skill_id == textbook_examples.skill_id
```

（其中 `textbook_examples` 為 `textbook_example_id` 所指向之列。）

| 項目 | 剛性要求 |
|------|----------|
| 寫入前校驗 | `INSERT` / `UPSERT` / `UPDATE` tracker 前，以 `textbook_example_id` 讀取 `textbook_examples.skill_id`，與待寫入之 `skill_id` 比對 |
| 不一致處置 | 斷言失敗 → 拒絕寫入，回傳 `skill_id_mismatch`（或等價 blocker）；**禁止**靜默覆寫或跨 skill 掛載 |
| `component_id` 連帶 | 寫入時 `component_id` **必須**為 `src_{textbook_example_id}`（見 §1.2.2），與硬碟目錄名一致 |

**防線意圖**：影子表為 `textbook_examples` 與微元件物理路徑的橋樑；跨表 `skill_id` 不一致將導致 Partial Publish、編譯器白名單與 `practice.py` 路由全面錯位。

#### 4.5.4 `induced_spec_payload` 內容契約

存放 Phase 1 **剛性去糖衣**後、由 AI 提取之純數學結構，**不含**自由發揮之故事層噪點。SQLite 3 以 `TEXT` 儲存 JSON 字串。建議 JSON 骨架：

```json
{
  "component_id": "src_4545",
  "skill_id": "vh_數學B1_PointSlopeForm",
  "target_task": "determine_linear_function_from_two_points",
  "presentation_mode": "single_choice",
  "math_core": {
    "givens": {},
    "constraints": {}
  },
  "story_template": "過點 {point_a} 與 {point_b} 的直線方程式為何？",
  "domain_params": {
    "line_type": "two_points",
    "curriculum_profile": "vocational_high_b",
    "difficulty_profile": "easy"
  }
}
```

管理員於後台修正文本噪點或 `domain_params` 後，透過 §4.6 觸發定點重構；**不得**在此欄位寫入可執行 Python 或 SymPy 程式碼。

#### 4.5.5 `gencode_error_log` 寫入規則

- 僅在狀態轉為 `failed`（或 `needs_regeneration` 保留前次摘要）時追加或覆寫（保留最近一次失敗摘要即可）。
- 範例：`Missing validation_facts matrix`、`ai_math_operation_forbidden: distractors assigned without Domain call`、`visual_semantic_mismatch: line does not pass through point B`。
- `verified` 時應清空或標記為 `NULL`，避免管理後台誤判。

---

### 4.6 後台「⚡重構出題程式」按鈕與動態熱拔插（Hot Swap）機制

本節將批次管線 CLI 行為，標準化為後台 **Low-Code 維運**操作，支援**單題定點**修復與**零重啟**上線。

#### 4.6.1 觸發源（管理後台）

| 項目 | 規範 |
|------|------|
| 按鈕文案 | **⚡產生/重構出題程式**（或等價 i18n key：`admin.gencode.rebuild_component`） |
| 作用範圍 | 單一 `component_id`（如 `src_4545`、`src_4610`）；**不得**一次觸發整 skill 全量重跑 |
| 前置條件 | 管理員已修正 `gencode_component_tracker.induced_spec_payload`（題幹模板、Domain 參數等） |
| 執行方式 | 非同步背景工作（Celery / RQ / 內建 job queue）；HTTP 立即回傳 `job_id`，避免阻塞後台 UI |

#### 4.6.2 定點 Codegen 與驗證（Phase 2 子集）

管線被喚醒後，**僅鎖定**該題：

1. 讀取 `gencode_component_tracker.induced_spec_payload` → 生成或覆寫 `agent_skills_v3/{skill_id}/components/{component_id}/generate.py`（及必要之 `metadata.py` / `get_hint.py`）。
2. 對該 `component_id` **獨立**執行 Phase 2.5 沙盒（AST、Full Matrix Dict、Validator、P0 Checker）；修補半徑仍為單檔，最多 3 次（§4.2）。
3. 通過 → `gencode_component_tracker.gencode_status = 'verified'`，清空 `gencode_error_log`，並由 Python 主動更新 `updated_at = datetime('now', 'localtime')`。
4. 失敗 → `gencode_status = 'failed'`，寫入 `gencode_error_log`，同步更新 `updated_at`；**不**觸發 skill 級 `SYSTEM_INTERRUPT`（§4.3）。

#### 4.6.3 編譯器一鍵重載（Reload Compiler）

單題 `verified` 後，自動調用 `skill_wrapper_compiler.py`（現行等價：`phase3_skill_codegen`）：

1. 重新掃描該 `skill_id` 下**所有** `gencode_component_tracker.gencode_status = 'verified'` 的列（見 Pipeline §3.4 Step 4 場景 2 SQL；**必須** `ORDER BY textbook_example_id ASC, component_id ASC`）。
2. 重寫 `component_manifest.json` 與 `agent_skills_v3/{skill_id}/__init__.py` 的 `_COMPONENT_DISPATCH` 路由器。
3. 重新生成 `skills/{skill_id}.py` Thin Facade 之 `GENERATOR_SPECS` / `GENERATOR_KEYS`。
4. 執行 Phase 3 smoke（可僅抽樣新修復之 `component_id` + 核心 `ex_*` 回歸）。

#### 4.6.4 零重啟動態加載契約

| 層級 | 剛性要求 |
|------|----------|
| `__init__.py` 路由器 | 抽題命中 `component_id` 時，須透過 `importlib.import_module` 載入 `components.{component_id}.generate`；若模組已載入，須對該模組執行 `importlib.reload` 以取得最新 `generate.py` |
| `runtime_skill_wrapper` | 在 `generate_for_skill()` 路徑中，優先走 component dispatch；動態載入失敗時 fallback 既有 slot 路徑，**不得**使學生請求 500 |
| `practice.py` | **不修改**對外 API；仍 `importlib.import_module("skills.{skill_id}")` 後呼叫 `generate()` |
| 運維禁令 | Manifest 白名單更新後，**不允許**重啟整個 Web 伺服器作為發布手段；熱拔插必須在進行中請求下安全生效 |

```python
# __init__.py 動態載入契約（概念虛擬碼）
import importlib

def _load_component_generate(component_id: str):
    module_path = f"agent_skills_v3.{SKILL_ID}.components.{component_id}.generate"
    mod = importlib.import_module(module_path)
    return importlib.reload(mod) if module_path in sys.modules else mod
```

**熱拔插閉環**：後台按鈕 → 單題 Codegen + 驗證 → `gencode_component_tracker` 標記 `verified` → Reload Compiler → `importlib.reload` → 下一筆學生 `practice` 請求即命中新程式。

#### 4.6.5 影子表維運契約（剛性）

**時間戳更新契約（`updated_at`）**：

- 本表時間戳更新採用**做法 A**：由 Python 程式在執行 `UPDATE` SQL 時**主動填入** `datetime('now', 'localtime')`。
- **明確不啟用**資料庫隱式 Trigger 自動維護 `updated_at`，以保持管線維護與除錯的完全透明度。

**物理路徑推導契約**：

- 本表**不存儲** `component_path` 字串欄位。
- 執行期微元件路徑統一由 `skill_id` 與 `component_id` 依規則公式**動態拼接**：

```text
agent_skills_v3/{skill_id}/components/{component_id}/
```

- 避免硬碟目錄搬移或路徑重構時，DB 內過期絕對路徑造成數據漂移。

---

## 5. 與 V2 法規的銜接

| V2 條款 | V3 延伸 |
|---------|---------|
| 薄入口外殼原則（§13） | `skills/{skill_id}.py` 仍為唯一前台 import 路徑 |
| 插槽去耦合（§14） | component 委派 `SLOT_REGISTRY`，禁止複製 slot 邏輯 |
| Phase 錯誤對照地圖（§16） | V3 新增本目錄為 AgentSkillV3 專屬權威；Phase 1–2 仍對照 V2 總體設計 |
| `skill_id:family_id` RAG 身份 | component 內 `diagnosis_tags` 不改變 family 鍵 |

---

## 6. Codex 任務執行檢查清單

- [ ] **物理佈局防線（§1.2）**：`skills/{skill_id}.py` 保留於 `skills/` 根目錄；每題 `py` 獨立於 `agent_skills_v3/{skill_id}/components/{component_id}/`；無大雜燴目錄
- [ ] **雙重寫入（§1.3、Pipeline §3.4 Step 4）**：Phase 3 已同步更新 `__init__.py` 之 `_COMPONENT_DISPATCH` 與原位 `skills/{skill_id}.py` Thin Facade
- [ ] 新數學邏輯寫入 **`core/domain/`**；`generate.py` 僅搬運；**不修改** `practice.py` 與學生學習數據表
- [ ] `gencode_component_tracker` 已依 §4.5 Canonical DDL 建立；雙重 UNIQUE + CHECK 約束生效；Service 層 `skill_id` 斷言（§4.5.3）已實作
- [ ] 第一階段 `component_id` 為 `src_{textbook_example_id}`；硬碟路徑 `agent_skills_v3/{skill_id}/components/src_{id}/`（§1.2.2）
- [ ] 後台「⚡重構出題程式」僅觸發單題 Codegen；通過後 Reload Compiler + `importlib.reload`（§4.6）
- [ ] **一題一 `generate.py`**：`component_id` 為 `ex_*` / `quiz_*` / `test_*` 實體題號（§1.5）；無多題合一、無 AI 融合
- [ ] `ORDER_WEIGHT` / `DIFFICULTY_LEVEL` 依前綴由管線注入；`skill_id` 在 Taxonomy MVP 六單元內（§1.4.1）
- [ ] `skill_id` 硬編碼僅出現在 `taxonomy_registry`；`core/domain/` 內無 skill_id（§2.7）
- [ ] `generate.py` 為搬運工：無 SymPy、無 distractors 演算法、無 visual 坐標重算（§2.6）
- [ ] Full Matrix Dictionary 六大欄位由 Domain 一次算完（§2.3.2、§2.5.4）
- [ ] 直線方程式 P0：`build_line_equation_matrix` 檢查點通過（§2.5.5）
- [ ] `PRESENTATION_MODE` 使用穩定 Key；`handwriting` 已注入 `text_input_disabled` 等 payload 宣告
- [ ] `generate.py` 通過 AST 精準掃描（§2.3.1）；敏感區白名單運算未被誤殺
- [ ] 應用題已實作該題專屬 `SCENARIO_POOL`；執行期無 LLM 即時改寫題幹
- [ ] 直線 / 分數題已綁定 P0 Checker：`linear_equation_equivalent_checker` / `rational_or_decimal_checker`（§2.4.1）
- [ ] 無 matplotlib / PIL；`visual_spec` 由 Domain **產生**、`generate.py` **搬運**、Validator **審核**（§3.2.2 三層權責）；Validator 幾何重算不受 AST 自算限制
- [ ] `get_hint.py` 三階段 skeleton 已實作
- [ ] 沙盒測試獨立通過後才寫入 `component_manifest.json`
- [ ] `required_core_components` **僅**來自 Taxonomy / 架構師預置，未被 AI 或管線改寫（§4.3.1.1）
- [ ] 核心例題 `verified` 即可 Partial Publish；`quiz_*` / `test_*` 失敗剔除、不觸發 `SYSTEM_INTERRUPT`（§4.3）

---

*本文件為 AgentSkillV3 架構大會審查規格書 v1.4（Domain 層架構規劃增補 · 待實作）。修訂須同步更新 `SOP_Gencode_AgentSkillV3_PipelineFlow.md`。*
