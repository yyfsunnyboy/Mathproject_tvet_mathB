# -*- coding: utf-8 -*-
"""B1 completion MsgBox navigation: same-chapter first, then next chapter."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MATHPROJECT_DATABASE_URI",
    f"sqlite:///{(ROOT / 'instance' / 'kumon_math.db').as_posix()}",
)

import config as app_config

app_config.Config.SQLALCHEMY_DATABASE_URI = os.environ["MATHPROJECT_DATABASE_URI"]

from app import app as flask_app
from core.practice_type_mastery import resolve_next_b1_practice_skill


STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _ok(label: str, cond: bool, detail: str = "") -> dict:
    print(("PASS" if cond else "FAIL"), label, detail)
    return {"label": label, "pass": bool(cond), "detail": detail}


def main() -> int:
    results = []
    with flask_app.app_context():
        # 1) Mid-chapter → same chapter next skill (not cross-section by display_order alone)
        mid = resolve_next_b1_practice_skill("vh_數學B1_AbsoluteValueInequality")
        results.append(
            _ok(
                "same_chapter_mid",
                mid.get("nav_kind") == "same_chapter"
                and mid.get("skill_id")
                == "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
                and mid.get("chapter") == "1 坐標系與函數圖形"
                and str(mid.get("button_label") or "").startswith("繼續挑戰："),
                str(mid),
            )
        )

        # 2) Near end of section still same chapter (Expansion → next practiceable in ch1)
        near = resolve_next_b1_practice_skill(
            "vh_數學B1_AbsoluteValueInequalityExpansionAndGeometricMeaning"
        )
        results.append(
            _ok(
                "same_chapter_after_skip_inactive",
                near.get("nav_kind") == "same_chapter"
                and near.get("chapter") == "1 坐標系與函數圖形"
                and near.get("skill_id")
                not in {
                    "vh_數學B1_NumberLine",
                    "outline_vocational_數學B1_11",
                    "vh_數學B1_FunctionConcept",
                },
                str(near),
            )
        )
        results.append(
            _ok(
                "skips_numberline_inactive",
                near.get("skill_id") != "vh_數學B1_NumberLine",
                near.get("skill_id"),
            )
        )

        # 3) Last practiceable of chapter 1 → first of chapter 2
        cross = resolve_next_b1_practice_skill("vh_數學B1_QuadraticInequalitySolution")
        results.append(
            _ok(
                "cross_chapter_to_ch2_first",
                cross.get("nav_kind") == "chapter_complete"
                and cross.get("skill_id") == "vh_數學B1_SlopeOfALine"
                and cross.get("chapter") == "2 直線方程式"
                and cross.get("button_label") == "前往下一章",
                str(cross),
            )
        )

        # 4) Last practiceable of volume (ch3) → dashboard
        last = resolve_next_b1_practice_skill("vh_數學B1_RationalEquation")
        results.append(
            _ok(
                "volume_last_to_dashboard",
                last.get("nav_kind") == "volume_complete"
                and last.get("target") == "dashboard"
                and last.get("skill_id") is None
                and last.get("button_label") == "返回學習儀表板",
                str(last),
            )
        )

        # 5) Empty shell / subsection never selected as next from Factoring path
        # PolynomialFactoring next should not be SubSection332
        fac = resolve_next_b1_practice_skill("vh_數學B1_PolynomialFactoring")
        results.append(
            _ok(
                "skip_subsection_shell",
                fac.get("skill_id") != "vh_數學B1_SubSection332",
                str(fac),
            )
        )

        # 6) Chapter-2 mid skill stays in chapter 2
        ps = resolve_next_b1_practice_skill("vh_數學B1_PointSlopeForm")
        results.append(
            _ok(
                "chapter2_same_chapter",
                ps.get("nav_kind") == "same_chapter"
                and ps.get("chapter") == "2 直線方程式"
                and str(ps.get("skill_id") or "").startswith("vh_數學B1_")
                and str(ps.get("button_label") or "").startswith("繼續挑戰："),
                str(ps),
            )
        )

        # 7) B2 untouched helper gate
        b2 = resolve_next_b1_practice_skill("vh_數學B2_Foo")
        results.append(
            _ok(
                "b2_fallback",
                b2.get("nav_kind") == "fallback_dashboard" and b2.get("skill_id") is None,
                str(b2),
            )
        )

        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        results.append(_ok("ui_same_skill_label", "繼續挑戰：" in html or "繼續挑戰下一個技能" in html))
        results.append(_ok("ui_next_chapter_label", "前往下一章" in html or "next_button_label" in html))
        results.append(_ok("ui_stay_skill", "留在目前技能" in html))
        results.append(_ok("ui_uses_nav_kind", "next_nav_kind" in html))
        results.append(_ok("ui_chapter_complete_copy", "太棒了！你完成這一章了！" in html))

    failed = [r for r in results if not r["pass"]]
    out = {
        "passed": len(results) - len(failed),
        "total": len(results),
        "failed": failed,
        "results": results,
    }
    path = ROOT / "reports/gencode_closed_loop" / f"b1_completion_navigation_{STAMP}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "reports/gencode_closed_loop/b1_completion_navigation_latest.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("SUMMARY", out["passed"], "/", out["total"], "wrote", path)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
