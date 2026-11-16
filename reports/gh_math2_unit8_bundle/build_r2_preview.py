"""MathJax preview of revision_0002 stems (sandbox components only; nothing is published).

Writes ``reports/gh_math2_unit8_bundle/revision_0002_preview.html``.
"""

from __future__ import annotations

import html
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from agent_domains_candidate.univariate_statistics.build_sandbox import DRYRUN  # noqa: E402
from agent_domains_candidate.univariate_statistics.sandbox_harness import register_candidate_in_memory  # noqa: E402
from agent_domains_candidate.univariate_statistics.univariate_statistics_specs import COMPONENTS, SKILLS  # noqa: E402

SHOW = [12913, 12936, 12916, 12919, 12922, 12920, 12943, 12944, 12926, 12930,
        12923, 12941, 12946, 12931, 12932, 12933, 12934, 12928, 12940, 12914, 12937, 12917, 12939, 12942, 12945]
OUT = ROOT / "reports" / "gh_math2_unit8_bundle" / "revision_0002_preview.html"


def main() -> None:
    register_candidate_in_memory()
    blocks = []
    for cid in SHOW:
        path = DRYRUN / SKILLS[COMPONENTS[cid][0]] / "components" / f"src_{cid}" / "generate.py"
        spec = importlib.util.spec_from_file_location(f"pv{cid}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for seed in (0, 3):
            payload = module.generate(seed=seed)
            stem = html.escape(payload["question_text"]).replace("\n", "<br>")
            answer = html.escape(str(payload["display_answer"]))
            blocks.append(f'<section data-cid="{cid}" data-seed="{seed}"><h3>src_{cid} seed {seed}</h3>'
                          f'<div class="stem">{stem}</div><p class="ans">答案：{answer}</p></section>')
    OUT.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Unit 8 revision_0002 preview</title>"
        "<script>window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']]}};</script>"
        "<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'></script>"
        "<style>body{font-family:sans-serif;max-width:1100px;margin:auto}section{border-bottom:1px solid #ccc;padding:6px}"
        ".ans{color:#555}</style></head><body>" + "".join(blocks) + "</body></html>",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
