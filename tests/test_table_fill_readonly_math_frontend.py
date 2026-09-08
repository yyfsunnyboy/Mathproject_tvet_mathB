# -*- coding: utf-8 -*-
"""Frontend contract: table_fill readonly cells go through MathJax wrapping."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

TEMPLATE = Path("templates/index.html")


def _function_body(source: str, name: str) -> str:
    marker = f"function {name}"
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for idx in range(brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace : idx + 1]
    raise AssertionError(f"function body not found: {name}")


def test_table_fill_readonly_cells_use_shared_math_wrapper():
    source = TEMPLATE.read_text(encoding="utf-8")
    render_body = _function_body(source, "renderTableQuestion")
    blank_body = _function_body(source, "renderBlankCellInput")

    assert "setReadonlyTableCellContent(th, header)" in render_body
    assert "setReadonlyTableCellContent(tdCell, cell)" in render_body
    assert "typesetTableFillMath(container)" in render_body
    assert "11616" not in render_body
    assert "example_id" not in render_body

    assert "wrapTableCellForMath" not in blank_body
    assert "setReadonlyTableCellContent" not in blank_body
    assert "renderMathContent" not in blank_body
    assert "className = 'table-fill-input'" in blank_body


def test_wrap_table_cell_for_math_covers_degree_and_pi_without_plain_text(tmp_path: Path):
    node = shutil.which("node")
    source = TEMPLATE.read_text(encoding="utf-8")
    look = "function looksLikeTexMath" + _function_body(source, "looksLikeTexMath")
    wrap = "function wrapTableCellForMath" + _function_body(source, "wrapTableCellForMath")
    if not node:
        assert r"\\[a-zA-Z]+" in look
        assert "${trimmed}" in wrap
        return

    js_path = tmp_path / "wrap_table_cell.js"
    js_path.write_text(
        look
        + "\n"
        + wrap
        + """
const samples = {
  deg0: wrapTableCellForMath('0^\\\\circ'),
  deg30: wrapTableCellForMath('30^\\\\circ'),
  pi6: wrapTableCellForMath('\\\\dfrac{\\\\pi}{6}'),
  pi: wrapTableCellForMath('\\\\pi'),
  pi32: wrapTableCellForMath('\\\\dfrac{3\\\\pi}{2}'),
  already: wrapTableCellForMath('$\\\\pi$'),
  plain: wrapTableCellForMath('度'),
  number: wrapTableCellForMath('12'),
  empty: wrapTableCellForMath('')
};
console.log(JSON.stringify(samples));
""",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [node, str(js_path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    samples = json.loads(proc.stdout.strip().splitlines()[-1])
    assert samples["deg0"] == r"$0^\circ$"
    assert samples["deg30"] == r"$30^\circ$"
    assert samples["pi6"] == r"$\dfrac{\pi}{6}$"
    assert samples["pi"] == r"$\pi$"
    assert samples["pi32"] == r"$\dfrac{3\pi}{2}$"
    assert samples["already"] == r"$\pi$"
    assert samples["plain"] == "度"
    assert samples["number"] == "12"
    assert samples["empty"] == ""
