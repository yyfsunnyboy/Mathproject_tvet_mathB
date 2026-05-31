# MathType DOCX 批次轉 LaTeX 流程 v0.1（Windows 專用）

## 目的
將原始 `.docx`（含 MathType/方程物件）透過桌面版 Microsoft Word + MathType 轉為 LaTeX 文字版 DOCX，輸出為 `*_Latex.docx`，供 `converted_docx_latex` 匯入模式使用。

## 範圍限制
- 不修改 DB schema。
- 不修改教材匯入主流程。
- 不變更 OCR / pix2tex / PDF 管線。
- 不覆蓋原始檔。

## 前置條件
1. Windows 環境。
2. 已安裝桌面版 Microsoft Word。
3. 已安裝 MathType（且 Word 內可用）。
4. Python 環境可執行：
   - `python-docx`
   - `pywin32`（僅實際轉換時需要）
   - 若缺少 `pywin32`，工具會回報 `failed_pywin32_missing`，並提示：
     - `python -m pip install pywin32`
     - `python -m pywin32_postinstall -install`

## 指令模式（主線）

### 0) Discovery（先跑）
先探索 Word 內可用 MathType/Equation 命令候選，再進行 auto。

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --discover-mathtype ^
  --report "reports\import_debug\mathtype_discovery_report.md"
```

### 1) interactive + auto（正式主線）
只指定資料夾，程式列出候選 DOCX，輸入編號後轉單檔。

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --input-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)" ^
  --output-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊_latex" ^
  --interactive ^
  --auto ^
  --overwrite ^
  --report "reports\import_debug\mathtype_convert_auto_report.md"
```

若 A/B 找不到可執行命令，可啟用 UI fallback：

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --input-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)" ^
  --output-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊_latex" ^
  --interactive ^
  --auto ^
  --allow-ui-automation ^
  --overwrite ^
  --report "reports\import_debug\mathtype_convert_auto_ui_report.md"
```

### 2) batch + auto
批次轉候選檔，可用 `--limit` 控制筆數。

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --input-folder "K:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)" ^
  --output-folder "K:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊_latex" ^
  --batch ^
  --auto ^
  --report "reports\import_debug\mathtype_convert_batch_report.md"
```

### 3) semi-auto（fallback）
當 auto 找不到可執行命令時，才使用 `--semi-auto`：
- Python 會開啟 Word 與目標 DOCX。
- 使用者在 Word 手動執行 MathType → Convert Equations（轉 LaTeX 文字）。
- 回到終端按 Enter，程式才會另存 `*_Latex.docx` 並進行 LaTeX 訊號驗證。
- `--batch --semi-auto` 會逐檔停下等待 Enter。
- `--semi-auto` 會繞過 macro 偵測，不以 macro 存在與否作為成敗條件。

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --input-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)" ^
  --output-folder "H:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊_latex" ^
  --interactive ^
  --semi-auto ^
  --report "reports\import_debug\mathtype_convert_interactive_semi_auto_report.md"
```

### 4) dry-run
只列候選與跳過原因，不啟動 Word。

```bash
python scripts\batch_mathtype_convert_docx.py ^
  --input-folder "K:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊(分章節)" ^
  --output-folder "K:\我的雲端硬碟\Python\books\技高\龍騰數B 第一冊_latex" ^
  --dry-run ^
  --report "reports\import_debug\mathtype_batch_convert_dry_run.md"
```

## 檔案篩選規則
只處理原始 `.docx`，排除：
- `.pdf`
- `.doc`
- `.tmp`
- `~$` 開頭
- 檔名含 `Latex/latex`（包含 `_Latex` / `_latex`）

若輸出資料夾已有：
- `原檔名_Latex.docx` 或
- `原檔名_latex.docx`

預設跳過（除非加 `--overwrite`）。

## 轉換行為與診斷
- 工具透過 `win32com` 啟動 `Word.Application`。
- 不使用 SendKeys。
- auto 模式會優先嘗試：`--macro-name`、`--command-onaction`、`--command-caption`、再走 discovery 高信心候選。
- 自動策略順序：A `Application.Run` macro -> B `CommandBar control.Execute()` -> C `--allow-ui-automation`（非預設）。
- 若找不到可執行命令，該檔標記 `failed_no_auto_command`。
- report 會附上 diagnostics（從 Word 可觀察到的候選名稱），包含：
  - `com_addins`
  - `macro_candidates`
  - `commandbar_candidates`

## 轉換後驗證
輸出後以 `python-docx` 統計 LaTeX 訊號：
- `$`, `\(`, `\)`, `\[`, `\]`, `\frac`, `\sqrt`, `\le`, `\ge`, `\left`, `\right`, `\overline`, `\triangle`

判定：
- `latex_signal_count == 0` -> `suspicious_no_latex_signal`
- `latex_signal_count > 0` -> `converted`

## 報表內容
Markdown report 包含：
- Summary（input/output/mode/counts）
- Per file table：`index`, `filename`, `status`, `reason`, `output_path`, `latex_signal_count`
- Diagnostics 區塊（macro/command/addins）

## 驗證
```bash
python -m py_compile scripts\batch_mathtype_convert_docx.py
python -m pytest tests\test_batch_mathtype_convert_docx_filter.py -q
```
