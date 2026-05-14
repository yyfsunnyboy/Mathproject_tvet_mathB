# B1 第一章 1-1「數線與絕對值」DOCX 公式抽取清查報告

**生成日期：** 2026-05-14  
**分析者：** Cursor Agent（唯讀審計，不修改 production code）  
**基準代理檔案：** `uploads/1-2_-.docx`（同系列 Longteng 數學 B1 第 1-2 節，結構完全相同）  
**目標檔案：** `uploads/第一章 1-1 數線與絕對值-課本.docx`（尚未上傳，以 1-2 作為代理推斷）

---

## 一、DOCX 公式抽取流程摘要

### 1.1 整體管線（`extract_content_from_file`）

```
docx 檔案
  │
  ├─ pypandoc.convert_file(..., '--extract-media=...')
  │    → 將 word/media/ 裡的圖片解壓到 uploads/tmp_docx_media/{job_id}/media/
  │
  ├─ build_docx_media_relationship_map(docx, media_dir)
  │    → 讀 word/_rels/document.xml.rels，建立 rid → {path, content_type} 對照表
  │    → 只保留 type 含 "image" 的 rel（排除 oleObject, package...）
  │
  └─ 逐 block 走訪 doc.element.body.iterchildren()
       ├─ w:p → extract_docx_paragraph_with_equations(para)
       │        + extract_docx_image_rids_from_paragraph(para)
       └─ w:tbl → extract_docx_table_with_equations(table)
```

### 1.2 `extract_docx_paragraph_with_equations`（核心抽取）

```
for child in p_el 的直接子元素:
  cname = local(child.tag)

  if cname == "r":  (w:run)
    for rchild in run:
      if rname == "t":           → 純文字 ✓
      if rname in ("oMath","oMathPara"):   → OMML 解析 → LaTeX \(...\) ✓
      if rname in ("drawing","object","pict"):
          → _extract_docx_image_placeholder(child=w:r, state)
              ↳ 只找 {*}blip (DrawingML a:blip)
              ↳ 若無 blip → return ""    ← ★ 靜默丟棄

  elif cname in ("oMath","oMathPara"):  (段落級 OMML)
      → convert_omml_to_latex() → \(...\) ✓
```

### 1.3 `extract_docx_image_rids_from_paragraph`（媒體掛載）

```python
# 捕捉兩種嵌入圖片 RID：
for blip in p_el.findall(".//{*}blip"):       # DrawingML 圖片
    rids.append(blip.attrib["r:embed"])
for imagedata in p_el.findall(".//{*}imagedata"):  # VML 圖片（OLE 預覽）
    rids.append(imagedata.attrib["r:id"])
```

> 注意：這裡**有**捕捉 `v:imagedata`，但捕捉的是 WMF **預覽圖**，不是公式文字。
> 預覽圖會以 `type: "image"` block 出現在 `ordered_blocks`，
> 但已**與公式文字在段落中的位置脫節**。

---

## 二、各格式觀察結果（以 1-2 docx 代理資料）

| 公式格式 | XML 結構 | 數量（1-2） | 現有處理 | 結果 |
|---------|----------|------------|---------|------|
| **Word OMML** | `<m:oMath>` / `<m:oMathPara>` | **0** | `convert_omml_to_latex()` → `\(...\)` | — 本書無此格式 |
| **MathType OLE（Equation.DSMT4）** | `<w:object>` + `v:imagedata` + `.bin` | **270** | `_extract_docx_image_placeholder` → `""` | ★ **全數靜默丟棄** |
| **DrawingML 圖片** | `<w:drawing>` + `a:blip` | **~50** | `_extract_docx_image_placeholder` → `[FORMULA_IMAGE_N]` | 有 placeholder，但多為插圖非公式 |
| **WMF 預覽圖（OLE 附帶）** | `v:imagedata` RID → `.wmf` | **242 個唯一 RID** | `extract_docx_image_rids_from_paragraph` 捕捉 → image block | 位置與文字脫節，二進位格式 |
| **w:pict（獨立 VML 圖片）** | `<w:pict>` | 16 | `_extract_docx_image_placeholder` → 找不到 blip → `""` | 靜默丟棄 |
| **EMF 圖片** | `media/*.emf` | 5 | 同 WMF | 作為 image block |
| **OLE .bin（MathType 原始資料）** | `word/embeddings/oleObject*.bin` | **270** | **完全未讀取** | 無法還原公式文字 |
| **Word.Document.12 OLE** | `<w:object>` ProgID=`Word.Document.12` | 3 | 同上靜默丟棄 | 次要影響 |
| **table cell 內公式** | `w:tbl → w:td → w:p → w:object` | 有（數量未獨立統計）| `extract_docx_table_with_equations` → 遞迴呼叫段落抽取 | ★ **同樣靜默丟棄** |

### 媒體檔案類型統計（1-2 docx）

```
word/media/ 共 292 檔：
  .wmf  ×239   ← 絕大多數是 MathType OLE 預覽圖
  .jpeg ×41    ← 課本插圖/照片
  .png  ×4     ← 插圖
  .emf  ×5     ← 向量圖（部分為 OLE 預覽）
  .jpg  ×3     ← 插圖

word/embeddings/ 共 273 檔：
  .bin  ×270   ← Equation.DSMT4 MathType 二進位資料
  其他   ×3    ← Word.Document.12 OLE
```

---

## 三、第 4、5、7 題公式遺失原因分析

> **注意：** 1-1 docx 尚未上傳，以下分析基於：  
> (a) 1-2 docx 代理結構（相同出版社/工具鏈）  
> (b) 1-1「數線與絕對值」章節的數學內容特性推斷

### 3.1 失敗類型判定

**主因：公式其實是 MathType OLE 物件（Equation.DSMT4）**，不是 OMML 也不是純圖片。

完整證據鏈：

```
1. document.xml 中 <m:oMath> 出現次數 = 0
   → 本書完全不使用 Word 原生 OMML 格式

2. <w:object ProgID="Equation.DSMT4"> 出現 270 次（1-2 節）
   → 所有數學式均由 MathType 4（DSMT 格式）插入

3. 每個 OLE 物件結構：
   <w:object>
     <v:shape>
       <v:imagedata r:id="rId##"/>   ← WMF 預覽圖（視覺呈現）
     </v:shape>
     <o:OLEObject ProgID="Equation.DSMT4" r:id="rId##"/>  ← .bin 原始資料
   </w:object>

4. _extract_docx_image_placeholder(run_el, ...) 只找 {*}blip
   → blips=0 → return ""
   → 277 個 OLE/VML 物件被靜默丟棄（經模擬驗證）
```

### 3.2 第 4、5、7 題具體推斷

1-1「數線與絕對值」典型題目包含：

| 題號 | 典型公式內容 | OLE 丟棄後變成 |
|------|-----------|--------------|
| 第 4 題 | `\|x\|`、`\|-3\|`、`\|a - b\|` 的計算 | 題幹：「試求下列各式之值：…」後公式消失，只剩文字框架 |
| 第 5 題 | 數線上距離 `d(A,B) = \|x₁ - x₂\|`，帶入具體座標 | 距離公式消失，但「km」「公里」等單位文字仍在 |
| 第 7 題 | 絕對值不等式 `\|x - a\| < r`，解出範圍 | 不等式消失，「解」「則 x =」等語句獨立存在 |

**共同失敗模式：**

```
原始段落（Word 視覺呈現）：
  "若 [OLE: |x-3|] = 5，求 x = ？"

extract_docx_paragraph_with_equations 輸出：
  "若  = 5，求 x = ？"    ← OLE 位置變成空字串
```

Gemini 接收到的是殘缺語句，無法正確推斷公式內容，因此：
- `problem_text` 缺失公式部分
- `solution` 的推導步驟中公式出現位置為空白
- AI 可能補填錯誤公式或輸出 `[FORMULA_MISSING]`

### 3.3 非主因確認

| 假設 | 排除理由 |
|------|--------|
| OMML 解析不足 | document.xml 中 `<m:oMath>` = 0，無 OMML |
| table cell extraction 漏掉 | `extract_docx_table_with_equations` 正確遞迴呼叫段落抽取，但核心 OLE 丟棄問題仍在 |
| EMF/WMF 圖片格式問題 | WMF 確實存在且被媒體管線捕捉，但問題是位置脫節與無文字內容，非格式讀取失敗 |

---

## 四、建議套件或工具鏈

### 方案 A：OLE .bin 直接解析（最高品質，最複雜）

| 工具 | 說明 | 限制 |
|------|------|------|
| `mathtype-sdk`（商業） | Design Science 官方 Python SDK，可解析 DSMT4 → MathML/LaTeX | 商業授權，需購買 |
| `mtef_to_latex`（社群，非官方） | 手工解析 DSMT MTEF 二進位格式 | 維護少，不完整 |
| LibreOffice CLI | `soffice --headless --convert-to fodt` 轉 ODF，ODF 中公式為 MathML | 需安裝 LibreOffice，速度慢 |

### 方案 B：WMF 預覽圖 → Vision AI OCR（中等品質，較易實作）

```
v:imagedata → WMF 檔 → Inkscape/LibreOffice 轉 PNG → Gemini Vision / GPT-4o 識別公式
```

| 工具 | 說明 |
|------|------|
| `Inkscape --export-png` | 將 WMF 轉換為 PNG（批量可行） |
| `cairosvg` + `wand` (ImageMagick) | Python 內直接轉 WMF → PNG |
| Gemini Vision `generate_content([prompt, img])` | 已在 `_vision_ocr_page_text` 有相同模式 |

> 此方案的架構已有先例：`_vision_ocr_page_text` 已做頁面圖片 → Gemini OCR。
> 只需擴展為「OLE WMF 預覽圖 → Vision OCR → 插回段落對應位置」。

### 方案 C：最小修正（推薦，低風險）

僅修正 `_extract_docx_image_placeholder` 的 `v:imagedata` 盲點：

```python
# 現有（有缺陷）
def _extract_docx_image_placeholder(run_el, paragraph_state):
    image_blips = run_el.findall(".//{*}blip")
    if not image_blips:
        return ""   # ← OLE VML 全部丟棄

# 修正目標
def _extract_docx_image_placeholder(run_el, paragraph_state):
    image_blips = run_el.findall(".//{*}blip")
    vml_imagedata = run_el.findall(".//{*}imagedata")  # 新增 VML 支援

    if not image_blips and not vml_imagedata:
        return ""
    
    count = len(image_blips) + len(vml_imagedata)
    for _ in range(count):
        paragraph_state["formula_image_count"] += 1
        ...
    return "".join(placeholders)
```

效果：
- OLE 公式位置不再靜默丟棄，改為產出 `[FORMULA_IMAGE_N]` placeholder
- Gemini 收到完整語義框架（「若 [FORMULA_IMAGE_1] = 5，求 x = ?」）
- AI 可結合 WMF 圖像推斷公式內容

---

## 五、最小修正方案（詳細）

### 5.1 `_extract_docx_image_placeholder`

**檔案：** `core/textbook_processor.py`，約第 323 行  
**改動量：** +3 行

```python
def _extract_docx_image_placeholder(run_el, paragraph_state):
    image_blips = run_el.findall(".//{*}blip")
    vml_imagedata = run_el.findall(".//{*}imagedata")   # ← 新增
    if not image_blips and not vml_imagedata:            # ← 修改判斷
        return ""
    placeholders = []
    for _ in image_blips:
        paragraph_state["formula_image_count"] += 1
        placeholders.append(f"[FORMULA_IMAGE_{paragraph_state['formula_image_count']}]")
        paragraph_state["needs_formula_review"] = True
    for _ in vml_imagedata:                              # ← 新增迴圈
        paragraph_state["formula_image_count"] += 1
        placeholders.append(f"[FORMULA_IMAGE_{paragraph_state['formula_image_count']}]")
        paragraph_state["needs_formula_review"] = True
    return "".join(placeholders)
```

### 5.2 WMF 媒體路徑傳遞（選配）

當前 `extract_docx_image_rids_from_paragraph` 已捕捉 WMF RID，但 `rel_map` 建立時
`extracted_path` 是 pypandoc 解壓後的路徑。需確認 pypandoc 是否會解壓 OLE 附帶的 WMF：

```bash
# 驗證指令（在專案根目錄執行）：
python -c "
import pypandoc, os
pypandoc.convert_file('uploads/1-2_-.docx', 'markdown',
    extra_args=['--wrap=none', '--extract-media=reports/b1_import_debug/test_media'])
import os
for f in os.listdir('reports/b1_import_debug/test_media/media'):
    print(f)
"
```

若 WMF 被正確解壓，則 `rel_map[rid]["extracted_path"]` 已指向正確路徑，
後續 Vision OCR 管線可直接使用。

### 5.3 潛在 Vision OCR 擴充（中期）

```python
# 在 _build_page_analysis_payload 或 extract_content_from_file 的 docx 分支中：
# 對每個 [FORMULA_IMAGE_N] placeholder，嘗試 WMF → PNG → Gemini Vision
def _ocr_vml_formula_image(wmf_path: str) -> str | None:
    """Convert WMF to PNG and run Gemini Vision OCR for formula text."""
    try:
        from wand.image import Image as WandImage
        with WandImage(filename=wmf_path) as img:
            img.format = "png"
            png_path = wmf_path + ".png"
            img.save(filename=png_path)
        # 呼叫現有的 _vision_ocr_page_text 或直接呼叫 Gemini
        ...
    except Exception:
        return None
```

---

## 六、是否建議重匯 B1 1-1

### 建議流程

```
步驟 1  上傳「第一章 1-1 數線與絕對值-課本.docx」
步驟 2  套用最小修正（修改 _extract_docx_image_placeholder，+3 行）
步驟 3  重新執行匯入
步驟 4  確認 problem_text 中出現 [FORMULA_IMAGE_N] 而非空白
步驟 5  （選配）啟用 Vision OCR fallback，讓 AI 辨識 WMF 圖中的絕對值公式
步驟 6  手動審核第 4、5、7 題，確認公式位置正確
```

### 結論

| 項目 | 答案 |
|------|------|
| 公式遺失主因 | MathType OLE（Equation.DSMT4），`_extract_docx_image_placeholder` 只偵測 `a:blip`，`v:imagedata` 全被靜默丟棄 |
| 是否 OMML 解析不足 | **否**，本書完全不使用 OMML |
| 是否圖片/EMF/WMF 問題 | **部分**，WMF 被媒體管線捕捉但位置與文字脫節；根本問題是 placeholder 未產生 |
| 是否 OLE/MathType object | **是，這是根本原因** |
| 是否 table cell 漏掉 | **否**，table extraction 正確遞迴，但受到同一 OLE 問題影響 |
| 建議重匯 B1 1-1 | **是，但必須先套用最小修正，否則重匯結果相同** |
| 預計修正範圍 | 1 個函數，+3 行，不動架構 |

---

## 附錄：關鍵程式碼位置速查

| 函數 | 檔案位置 | 說明 |
|------|---------|------|
| `extract_docx_paragraph_with_equations` | `core/textbook_processor.py:335` | 段落公式抽取主函數 |
| `_extract_docx_image_placeholder` | `core/textbook_processor.py:323` | ★ **有缺陷的 blip-only 偵測** |
| `extract_docx_image_rids_from_paragraph` | `core/textbook_processor.py:438` | 媒體 RID 捕捉（已有 v:imagedata） |
| `build_docx_media_relationship_map` | `core/textbook_processor.py:400` | RID → 路徑對照表 |
| `_omml_node_to_latex` | `core/textbook_processor.py:274` | OMML → LaTeX（本書未使用到） |
| `extract_docx_table_with_equations` | `core/textbook_processor.py:385` | table cell 遞迴抽取 |
| `extract_content_from_file` (docx 分支) | `core/textbook_processor.py:1152` | 整體 docx 管線入口 |

---

*本報告純為靜態程式碼審計與 docx 結構分析，不含任何 production code 修改。*
