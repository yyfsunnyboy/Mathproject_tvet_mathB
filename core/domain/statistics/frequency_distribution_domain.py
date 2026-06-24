"""Statistics domain functions for frequency-distribution-table construction."""

from __future__ import annotations

import random
from typing import Any


def build_frequency_distribution_table_matrix(
    *,
    seed: int | None = None,
    domain_operation: str = "frequency_table_construction_review",
    curriculum_profile: str = "vocational_high_b",
    difficulty_profile: str = "easy",
    constraints: dict[str, Any] | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build a reusable Full Matrix Dictionary for frequency table construction."""
    rng = random.Random(seed)
    constraints = dict(constraints or {})
    categories = list(constraints.get("categories") or ["A組", "B組", "C組", "D組"])
    if len(categories) < 3:
        raise ValueError("categories_must_have_at_least_three_items")
    frequencies = constraints.get("frequencies")
    if frequencies is None:
        frequencies = [rng.randint(3, 9) for _ in categories]
    frequencies = [int(x) for x in frequencies]
    if len(frequencies) != len(categories):
        raise ValueError("frequencies_length_mismatch")
    if any(x < 0 for x in frequencies):
        raise ValueError("frequency_must_be_non_negative")

    frequency_map = dict(zip(categories, frequencies, strict=True))
    target_label = str(constraints.get("target_label") or rng.choice(categories))
    if target_label not in frequency_map:
        target_label = categories[0]
    answer_value = frequency_map[target_label]
    total = sum(frequencies)

    # Build matplotlib table + grids or histograms depending on operation
    import io
    import base64
    import matplotlib.pyplot as plt

    # Set up matplotlib image generation for visual_aids/image_base64
    image_b64 = ""
    visual_aids = []
    distractor_values: list[int] = []

    # Map operation custom specifications
    if domain_operation == "frequency_distribution_chart_construction":
        # Draw the table and coordinates/grid for student to draw graph
        fig, (ax_tbl, ax_grid) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=120)
        try:
            # 1. Left side: Table
            ax_tbl.axis("off")
            tbl_title = str(constraints.get("title") or "次數分配表")
            ax_tbl.set_title(tbl_title, fontsize=12, fontweight="bold", pad=10)
            headers = ["組別", "次數"]
            rows_data = [[label, f"{frequency_map[label]} 人"] for label in categories]
            tbl = ax_tbl.table(cellText=rows_data, colLabels=headers, loc="center", cellLoc="center")
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            tbl.scale(1.0, 1.6)

            # 2. Right side: Empty Grid coordinates for drawing
            ax_grid.set_title("請在此繪製直方圖與折線圖", fontsize=11, fontweight="bold", pad=10)
            # Determine suitable limits
            y_max = max(frequencies) + 2
            ax_grid.set_xlim(-0.5, len(categories) - 0.5)
            ax_grid.set_ylim(0, y_max)
            ax_grid.set_xticks(range(len(categories)))
            ax_grid.set_xticklabels(categories, fontsize=9)
            ax_grid.set_ylabel("次數 (人)", fontsize=10)
            ax_grid.set_xlabel("組別", fontsize=10)
            ax_grid.grid(True, which="both", linestyle="--", alpha=0.5)
            ax_grid.set_axisbelow(True)

            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        finally:
            plt.close(fig)

        # Correct answer format for sketch-drawing question type is descriptive or empty (graded by teacher review/manual or coordinate equivalence, here we match textbook answer representation)
        ans_text = "直方圖與折線圖已繪製於畫布。"
        ans_val = ans_text
        explanation_steps = [
            "1. 依據次數分配表，橫軸標示各組組界，縱軸標示次數，繪製相連的長方形直方圖。",
            "2. 取各長方形頂部中點，並在左右兩端次數為 0 處各取一點（通常為相鄰組中點），用線段依序連接，即為次數分配折線圖。"
        ]
    elif domain_operation == "histogram_distribution_update":
        # 3829: Given initial histogram, show changes, student answers the new group frequencies
        # Initial table data (heights distribution of kids)
        # 100~105: 2, 105~110: 5, 110~115: 8, 115~120: 7, 120~125: 3
        # If seed changes, we randomize slightly but keep 25 total.
        init_freqs = list(frequencies)
        if len(init_freqs) < 5:
            init_freqs = [rng.randint(2, 6) for _ in range(5)]
        
        # Ensure 115~120 (index 3) has at least 2 so that decrement by 1 results in at least 1
        if init_freqs[3] < 2:
            init_freqs[3] = 2

        # Adjust frequencies to look like heights of 25 kids
        while sum(init_freqs) != 25:
            idx = rng.choice([0, 1, 2, 4]) # Do not change index 3 so it stays stable >= 2
            if sum(init_freqs) < 25:
                init_freqs[idx] += 1
            elif init_freqs[idx] > 1:
                init_freqs[idx] -= 1

        height_bins = ["100~105", "105~110", "110~115", "115~120", "120~125"]
        init_map = dict(zip(height_bins, init_freqs, strict=True))

        # We transfer out one kid of 117 cm (belongs to 115~120) -> freq decreases by 1
        # We transfer in one kid of 112 cm (belongs to 110~115) -> freq increases by 1
        trans_out_val = constraints.get("trans_out_val", 117)
        trans_in_val = constraints.get("trans_in_val", 112)

        out_bin = "115~120"
        in_bin = "110~115"

        final_freqs = list(init_freqs)
        final_freqs[3] -= 1 # 115~120 index is 3
        final_freqs[2] += 1 # 110~115 index is 2
        final_map = dict(zip(height_bins, final_freqs, strict=True))

        # Draw the initial histogram
        fig, ax = plt.subplots(figsize=(6, 3.8), dpi=120)
        try:
            ax.bar(height_bins, init_freqs, width=0.9, color="skyblue", edgecolor="black", alpha=0.8)
            ax.set_title("小朋友身高分佈直方圖", fontsize=11, fontweight="bold")
            ax.set_xlabel("身高 (cm)", fontsize=9)
            ax.set_ylabel("人數 (人)", fontsize=9)
            y_max = max(init_freqs) + 2
            ax.set_ylim(0, y_max)
            ax.grid(axis="y", linestyle="--", alpha=0.5)
            ax.set_axisbelow(True)
            for spine in ("top", "right"):
                ax.spines[spine].set_visible(False)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            image_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        finally:
            plt.close(fig)

        ans_text = f"{out_bin}組次數減1，{in_bin}組次數加1"
        ans_val = ans_text
        explanation_steps = [
            f"1. 轉出一位身高 {trans_out_val} 公分的小朋友，屬於 {out_bin} 組，因此該組人數減少 1 人（{init_map[out_bin]} -> {final_map[out_bin]} 人）。",
            f"2. 轉入一位身高 {trans_in_val} 公分的小朋友，屬於 {in_bin} 組，因此該組人數增加 1 人（{init_map[in_bin]} -> {final_map[in_bin]} 人）。",
            f"3. 其餘各組人數不變。"
        ]
        # Override table rows for 3829 visual spec
        categories = height_bins
        frequency_map = init_map
        frequencies = init_freqs
    else:
        ans_val = answer_value
        explanation_steps = [
            "依資料分類整理各組出現次數。",
            f"查看 {target_label} 的次數。",
            f"{target_label} 的次數為 {answer_value}。",
        ]

    if image_b64:
        visual_aids = [{"type": "image/png", "value": image_b64}]

    return {
        "givens": {
            "categories": categories,
            "frequencies": frequencies,
            "frequency_map": frequency_map,
            "target_label": target_label,
            "total_frequency": total,
            "curriculum_profile": curriculum_profile,
            "difficulty_profile": difficulty_profile,
        },
        "answer": {
            "canonical_form": str(ans_val),
            "general_form": str(ans_val),
            "coefficients": {"frequency": ans_val} if isinstance(ans_val, int) else {},
            "value": ans_val,
            "unit": "次" if isinstance(ans_val, int) else "",
        },
        "distractors": [str(x) for x in distractor_values[:3]],
        "explanation_steps": explanation_steps,
        "validation_facts": {
            "domain_operation": domain_operation,
            "task_type": domain_operation,
            "frequency_map": frequency_map,
            "target_label": target_label,
            "answer_value": ans_val,
            "total_frequency": total,
        },
        "visual_spec": {
            "type": "table",
            "title": "次數分配表" if domain_operation != "histogram_distribution_update" else "身高分佈直方圖",
            "headers": ["組別", "次數"],
            "rows": [[label, frequency_map[label]] for label in categories],
        },
        "visual_aids": visual_aids,
        "image_base64": image_b64,
    }

