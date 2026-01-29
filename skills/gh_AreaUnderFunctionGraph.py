# ==============================================================================
# ID: gh_AreaUnderFunctionGraph
# Model: gemini-2.5-flash | Strategy: V9 Architect (cloud_pro)
# Duration: 70.71s | RAG: 3 examples
# Created At: 2026-01-29 12:38:21
# Fix Status: [Repaired]
# Fixes: Regex=1, Logic=0
#==============================================================================


# [V12.3 Elite Standard Math Tools]
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from functools import reduce
import ast
import base64
import io
import re

# [V11.6 Elite Font & Style] - Hardcoded
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False

def to_latex(num):
    if isinstance(num, int): return str(num)
    if isinstance(num, float): num = Fraction(str(num)).limit_denominator(100)
    if isinstance(num, Fraction):
        if num == 0: return "0"
        if num.denominator == 1: return str(num.numerator)
        sign = "-" if num < 0 else ""
        abs_num = abs(num)
        if abs_num.numerator > abs_num.denominator:
            whole = abs_num.numerator // abs_num.denominator
            rem_num = abs_num.numerator % abs_num.denominator
            if rem_num == 0: return r"{s}{w}".replace("{s}", sign).replace("{w}", str(whole))
            return r"{s}{w} \frac{{n}}{{d}}".replace("{s}", sign).replace("{w}", str(whole)).replace("{n}", str(rem_num)).replace("{d}", str(abs_num.denominator))
        return r"\frac{{n}}{{d}}".replace("{n}", str(num.numerator)).replace("{d}", str(num.denominator))
    return str(num)

def fmt_num(num, signed=False, op=False):
    latex_val = to_latex(num)
    if num == 0 and not signed and not op: return "0"
    is_neg = (num < 0)
    abs_str = to_latex(abs(num))
    if op:
        if is_neg: return r" - {v}".replace("{v}", abs_str)
        return r" + {v}".replace("{v}", abs_str)
    if signed:
        if is_neg: return r"-{v}".replace("{v}", abs_str)
        return r"+{v}".replace("{v}", abs_str)
    if is_neg: return r"({v})".replace("{v}", latex_val)
    return latex_val

# --- 2. Number Theory Helpers ---
def is_prime(n):
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

def get_positive_factors(n):
    factors = set()
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            factors.add(i)
            factors.add(n // i)
    return sorted(list(factors))

def get_prime_factorization(n):
    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1
    return factors

def gcd(a, b): return math.gcd(int(a), int(b))
def lcm(a, b): return abs(int(a) * int(b)) // math.gcd(int(a), int(b))

# --- 3. Fraction Generator & Helpers ---
def simplify_fraction(n, d):
    common = math.gcd(n, d)
    return n // common, d // common

def _calculate_distance_1d(a, b):
    return abs(a - b)

def get_random_fraction(min_val=-10, max_val=10, denominator_limit=10, simple=True):
    for _ in range(100):
        den = random.randint(2, denominator_limit)
        num = random.randint(min_val * den, max_val * den)
        if den == 0: continue
        val = Fraction(num, den)
        if simple and val.denominator == 1: continue 
        if val == 0: continue
        return val
    return Fraction(1, 2)

# --- 7 下 強化組件 A: 數線區間渲染器 (針對不等式) ---
def draw_number_line(points_map, x_min=None, x_max=None, intervals=None, **kwargs):
    """
    intervals: list of dict, e.g., [{'start': 3, 'direction': 'right', 'include': False}]
    """
    values = [float(v) for v in points_map.values()] if points_map else [0]
    if intervals:
        for inter in intervals: values.append(float(inter['start']))
    
    if x_min is None: x_min = math.floor(min(values)) - 2
    if x_max is None: x_max = math.ceil(max(values)) + 2
    
    fig = Figure(figsize=(8, 2))
    ax = fig.add_subplot(111)
    ax.plot([x_min, x_max], [0, 0], 'k-', linewidth=1.5)
    ax.plot(x_max, 0, 'k>', markersize=8, clip_on=False)
    ax.plot(x_min, 0, 'k<', markersize=8, clip_on=False)
    
    # 數線刻度規範
    ax.set_xticks([0])
    ax.set_xticklabels(['0'], fontsize=18, fontweight='bold')
    
    # 繪製不等式區間 (7 下 關鍵)
    if intervals:
        for inter in intervals:
            s = float(inter['start'])
            direct = inter.get('direction', 'right')
            inc = inter.get('include', False)
            color = 'red'
            # 畫圓點 (空心/實心)
            ax.plot(s, 0.2, marker='o', mfc='white' if not inc else color, mec=color, ms=10, zorder=5)
            # 畫折線射線
            target_x = x_max if direct == 'right' else x_min
            ax.plot([s, s, target_x], [0.2, 0.5, 0.5], color=color, lw=2)

    for label, val in points_map.items():
        v = float(val)
        ax.plot(v, 0, 'ro', ms=7)
        ax.text(v, 0.08, label, ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')

    ax.set_yticks([]); ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 7 下 強化組件 B: 直角坐標系渲染器 (針對方程式圖形) ---
def draw_coordinate_system(lines=None, points=None, x_range=(-5, 5), y_range=(-5, 5)):
    """
    繪製標準坐標軸與直線方程式
    """
    fig = Figure(figsize=(5, 5))
    ax = fig.add_subplot(111)
    ax.set_aspect('equal') # 鎖死比例
    
    # 繪製網格與軸線
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axhline(0, color='black', lw=1.5)
    ax.axvline(0, color='black', lw=1.5)
    
    # 繪製直線 (y = mx + k)
    if lines:
        import numpy as np
        for line in lines:
            m, k = line.get('m', 0), line.get('k', 0)
            x = np.linspace(x_range[0], x_range[1], 100)
            y = m * x + k
            ax.plot(x, y, lw=2, label=line.get('label', ''))

    # 繪製點 (x, y)
    if points:
        for p in points:
            ax.plot(p[0], p[1], 'ro')
            ax.text(p[0]+0.2, p[1]+0.2, p.get('label', ''), fontsize=14, fontweight='bold')

    ax.set_xlim(x_range); ax.set_ylim(y_range)
    # 隱藏刻度，僅保留 0
    ax.set_xticks([0]); ax.set_yticks([0])
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def draw_geometry_composite(polygons, labels, x_limit=(0,10), y_limit=(0,10)):
    """[V11.6 Ultra Visual] 物理級幾何渲染器 (Physical Geometry Renderer)"""
    fig = Figure(figsize=(5, 4))
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.set_aspect('equal', adjustable='datalim')
    all_x, all_y = [], []
    for poly_pts in polygons:
        polygon = patches.Polygon(poly_pts, closed=True, fill=False, edgecolor='black', linewidth=2)
        ax.add_patch(polygon)
        for p in poly_pts:
            all_x.append(p[0])
            all_y.append(p[1])
    for text, pos in labels.items():
        all_x.append(pos[0])
        all_y.append(pos[1])
        ax.text(pos[0], pos[1], text, fontsize=20, fontweight='bold', ha='center', va='center',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=1))
    if all_x and all_y:
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        rx = (max_x - min_x) * 0.3 if (max_x - min_x) > 0 else 1.0
        ry = (max_y - min_y) * 0.3 if (max_y - min_y) > 0 else 1.0
        ax.set_xlim(min_x - rx, max_x + rx)
        ax.set_ylim(min_y - ry, max_y + ry)
    else:
        ax.set_xlim(x_limit)
        ax.set_ylim(y_limit)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=300)
    del fig
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 4. Answer Checker (V11.6 Smart Formatting Standard) ---
def check(user_answer, correct_answer):
    if user_answer is None: return {"correct": False, "result": "未提供答案。"}
    
    # 將字典或複雜格式轉為乾淨字串
    def _format_ans(a):
        if isinstance(a, dict):
            if "quotient" in a: 
                return r"{q}, {r}".replace("{q}", str(a.get("quotient",""))).replace("{r}", str(a.get("remainder","")))
            return ", ".join([r"{k}={v}".replace("{k}", str(k)).replace("{v}", str(v)) for k, v in a.items()])
        return str(a)

    def _clean(s):
        # 雙向清理：剝除 LaTeX 符號與空格
        return str(s).strip().replace(" ", "").replace("，", ",").replace("$", "").replace("\\", "").lower()
    
    u = _clean(user_answer)
    c_raw = _format_ans(correct_answer)
    c = _clean(c_raw)
    
    if u == c: return {"correct": True, "result": "正確！"}
    
    try:
        import math
        if math.isclose(float(u), float(c), abs_tol=1e-6): return {"correct": True, "result": "正確！"}
    except: pass
    
    return {"correct": False, "result": r"答案錯誤。正確答案為：{ans}".replace("{ans}", c_raw)}



import matplotlib.pyplot as plt
import io
import base64
import re
from datetime import datetime
from fractions import Fraction
import numpy as np

# --- Helper Functions ---
def _generate_coordinate_value(min_val, max_val, allow_fraction=False):
    """
    功能: 生成一個浮點數座標值，並提供其分解結構 (整數部、分子、分母、正負號)，符合 V10.2 A 規範。
    V13.1 禁絕假分數: 若生成分數，必須確保 `num < den` 且 `den > 1`。
    V13.5 整數優先: 若 `float_val` 為整數，則 `float_val` 將被轉換為 `int` 類型，並確保 `num=0, den=0`。
    """
    float_val = 0.0
    int_part = 0
    num = 0
    den = 0
    is_neg = False

    if allow_fraction and random.random() < 0.5: # 50% chance for fraction if allowed
        # Generate a float that can be represented as a simple fraction (e.g., x.5 or x.25)
        # We ensure the denominator is small (e.g., 2 or 4)
        denominator = random.choice([2, 4])
        # Generate numerator such that the float_val is within min_val and max_val
        # and has a non-zero fractional part if it's a proper fraction.
        
        # Try to generate a number within the range [min_val, max_val]
        # and then convert it to a fraction.
        raw_val = random.uniform(min_val, max_val)
        
        # Convert to fraction, then check for proper fraction and simplify
        frac_candidate = Fraction(raw_val).limit_denominator(denominator)
        
        if frac_candidate.denominator == 1: # It's an integer, try again or just treat as int
            float_val = int(frac_candidate)
        else:
            float_val = float(frac_candidate)
            is_neg = float_val < 0
            abs_frac = abs(frac_candidate)
            int_part = math.floor(abs_frac)
            num = abs_frac.numerator - int_part * abs_frac.denominator
            den = abs_frac.denominator
            
            # Ensure num < den (proper fraction part) and den > 1
            if num == 0: # If it's effectively an integer (e.g. 2/2 -> 1)
                float_val = int(float_val)
                int_part = abs(int(float_val))
                den = 0
            elif den == 0: # Should not happen with Fraction, but for robustness
                float_val = int(float_val)
                int_part = abs(int(float_val))

    if den == 0: # It's an integer or simplified to an integer
        float_val = random.randint(min_val, max_val)
        int_part = abs(int(float_val))
        num = 0
        den = 0
        is_neg = float_val < 0
        
    return (float_val, (int_part, num, den, is_neg))

def _format_coordinate(data):
    """
    功能: 將 `_generate_coordinate_value` 產生的數據結構格式化為 LaTeX 字串。
    V10.2 C. LaTeX 模板規範: 嚴格使用 `.replace("{n}", str(num))` 進行代換。
    V13.0 格式精確要求: 處理整數時，確保輸出為 `str(int(val))` 而非 `str(float(val))`。
    """
    float_val, (int_part, num, den, is_neg) = data
    
    sign = "-" if is_neg else ""
    
    if num == 0 and den == 0: # Integer
        return f"{int(float_val)}"
    elif int_part == 0: # Pure fraction
        return r"{sign}\frac{{{num}}}{{{den}}}".replace("{sign}", sign).replace("{num}", str(num)).replace("{den}", str(den))
    else: # Mixed fraction
        return r"{sign}{int_part}\frac{{{num}}}{{{den}}}".replace("{sign}", sign).replace("{int_part}", str(int_part)).replace("{num}", str(num)).replace("{den}", str(den))

def _format_fraction_for_latex(value, signed=False):
    """
    功能: 將浮點數值格式化為 LaTeX 格式的分數或整數，用於函數方程式的係數。
    V5. 排版與 LaTeX 安全: 嚴禁使用 f-string 或 % 格式化，必須使用 `.replace()`。
    """
    if value == 0:
        return "0"
        
    sign_str = ""
    if signed and value > 0:
        sign_str = "+"
    elif value < 0:
        sign_str = "-"
    
    abs_value = abs(value)
    
    if abs_value.is_integer():
        return sign_str + str(int(abs_value))
    
    frac = Fraction(abs_value).limit_denominator(10)
    int_part = int(frac) # Integer part
    num = frac.numerator - int_part * frac.denominator # Numerator of the fractional part
    den = frac.denominator

    if den == 1: # Should be integer already, but if Fraction simplified to int
        return sign_str + str(int(abs_value))
    elif int_part == 0: # Pure fraction
        return sign_str + r"\frac{{{num}}}{{{den}}}".replace("{num}", str(num)).replace("{den}", str(den))
    else: # Mixed fraction
        return sign_str + r"{int_part}\frac{{{num}}}{{{den}}}".replace("{int_part}", str(int_part)).replace("{num}", str(num)).replace("{den}", str(den))

def _draw_coordinate_plane(line_eq=None, region_x_bounds=None, x_intercept=None, y_intercept=None):
    """
    功能: 繪製座標平面、函數圖形及指定區域邊界。
    V17.1 圖表必須可解: ax.set_xticks(range(-plot_limit, plot_limit + 1)) 和 ax.set_yticks(range(-plot_limit, plot_limit + 1)) 必須確保 X 軸與 Y 軸的主要整數刻度可見。
    V13.0 格線對齊: 座標軸範圍必須是對稱整數，且 xticks 間隔必須固定為 1。
    V13.5 座標範圍: 座標範圍必須對稱且寬裕 (例如至少 -8 到 8)。
    V10.2 D. 視覺一致性: ax.set_aspect('equal') 確保網格為正方形。原點 0 標註為 18 號加粗字體。
    V13.6 Arrow Ban: 嚴禁使用 arrowprops。必須使用 ax.plot(limit, 0, ">k", clip_on=False) 繪製箭頭。
    V13.5 標籤隔離: ax.text 僅能標註點的名稱 (Label)，嚴禁包含座標值。
    防洩漏原則: 繪圖函式僅接收「題目已知數據」。嚴禁將「答案數據」傳入繪圖函式。
    ULTRA VISUAL STANDARDS (V11.6): dpi=300, ax.set_aspect('equal'), white halos for ABCD text.
    Mandatory Axis Ticks (CRITICAL CODING STANDARDS): Explicit set_xticks, set_yticks.
    Axis Visibility: spines at zero.
    Grid Lines: ax.grid(True, linestyle=':', alpha=0.6).
    """
    a, b = line_eq

    # Determine plot limits dynamically but ensure a minimum range
    min_x_val, max_x_val = -8, 8
    min_y_val, max_y_val = -8, 8

    if x_intercept is not None:
        min_x_val = min(min_x_val, math.floor(x_intercept - 2))
        max_x_val = max(max_x_val, math.ceil(x_intercept + 2))
    if y_intercept is not None:
        min_y_val = min(min_y_val, math.floor(y_intercept - 2))
        max_y_val = max(max_y_val, math.ceil(y_intercept + 2))
    if region_x_bounds:
        c1, c2 = region_x_bounds
        min_x_val = min(min_x_val, math.floor(c1 - 2))
        max_x_val = max(max_x_val, math.ceil(c2 + 2))
        y_at_c1 = a * c1 + b
        y_at_c2 = a * c2 + b
        min_y_val = min(min_y_val, math.floor(min(0, y_at_c1, y_at_c2) - 2)) # Include 0 for x-axis
        max_y_val = max(max_y_val, math.ceil(max(0, y_at_c1, y_at_c2) + 2)) # Include 0 for x-axis
        
    # Ensure symmetry and minimum range
    plot_limit_x = int(max(abs(min_x_val), abs(max_x_val), 8)) + 1
    plot_limit_y = int(max(abs(min_y_val), abs(max_y_val), 8)) + 1
    
    # Take the larger of the two limits to ensure square plot_limit
    plot_limit = max(plot_limit_x, plot_limit_y)
    
    # Adjust plot_limit to be at least 8 in both directions
    plot_limit = max(plot_limit, 8)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=300) # ULTRA VISUAL STANDARDS: dpi=300

    # Set up the axes
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Draw arrows for axes (V13.6 Arrow Ban)
    ax.plot(plot_limit, 0, ">k", clip_on=False, transform=ax.get_yaxis_transform()) # X-axis arrow
    ax.plot(0, plot_limit, "^k", clip_on=False, transform=ax.get_xaxis_transform()) # Y-axis arrow

    # Set axis limits
    ax.set_xlim(-plot_limit, plot_limit)
    ax.set_ylim(-plot_limit, plot_limit)

    # Mandatory Axis Ticks (CRITICAL CODING STANDARDS)
    ax.set_xticks(range(-plot_limit, plot_limit + 1))
    ax.set_yticks(range(-plot_limit, plot_limit + 1))
    ax.tick_params(axis='both', which='major', labelsize=10) # Adjust font size for ticks

    # Grid Lines (CRITICAL CODING STANDARDS)
    ax.grid(True, linestyle=':', alpha=0.6)

    # V10.2 D. 視覺一致性: ax.set_aspect('equal')
    ax.set_aspect('equal')

    # Plot the function line f(x) = ax + b
    x_vals_line = np.linspace(-plot_limit, plot_limit, 400) # Use linspace for smooth line
    y_vals_line = a * x_vals_line + b
    ax.plot(x_vals_line, y_vals_line, color='blue', linewidth=2) # No label, per V13.5

    # Shade the region based on type
    if region_x_bounds: # Type 2: x=c1, x=c2, x-axis
        c1, c2 = region_x_bounds
        
        # Create a finer x range for accurate filling within [c1, c2]
        x_fill = np.linspace(c1, c2, 100)
        y_fill = a * x_fill + b
        
        # Fill the region between the function and the x-axis
        ax.fill_between(x_fill, y_fill, 0, color='lightgray', alpha=0.5, hatch='///', edgecolor='black')

        # Draw vertical lines at c1 and c2
        ax.plot([c1, c1], [0, a * c1 + b], color='purple', linestyle='--', linewidth=1)
        ax.plot([c2, c2], [0, a * c2 + b], color='purple', linestyle='--', linewidth=1)
        
    elif x_intercept is not None and y_intercept is not None: # Type 1: x-axis, y-axis
        # This region is a triangle formed by (0,0), (x_intercept, 0), (0, y_intercept)
        
        # Vertices of the triangle
        triangle_x = [0, x_intercept, 0]
        triangle_y = [0, 0, y_intercept]
        
        # Fill the triangle region
        ax.fill(triangle_x, triangle_y, color='lightgray', alpha=0.5, hatch='///', edgecolor='black')
        
        # Draw outlines for the x-axis and y-axis segments of the triangle
        ax.plot([0, x_intercept], [0, 0], color='purple', linestyle='--', linewidth=1) # x-axis segment
        ax.plot([0, 0], [0, y_intercept], color='purple', linestyle='--', linewidth=1) # y-axis segment

    # Label the origin '0' (V10.2 D. 視覺一致性)
    ax.text(0.1, -0.8, '0', fontsize=18, fontweight='bold', ha='left', va='top')

    # Save plot to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    image_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)

    return image_base64

# --- Main generate function ---
def generate(level=1):
    """
    V3. 頂層函式: 必須直接定義於模組最外層。
    V4. 題型鏡射: 內部使用 random.choice([1, 2]) 選擇題型。
    """
    problem_type = random.choice([1, 2])

    a_options_type1 = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]
    a_options_type2 = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
    b_options = [float(i) for i in range(-8, 9) if i != 0] # Exclude 0 for b initially

    a_float = 0.0
    b_float = 0.0
    x_intercept_float = None
    y_intercept_float = None
    c1_float = None
    c2_float = None
    correct_area = 0.0

    question_text = ""
    image_base64 = ""
    
    if problem_type == 1:
        # Type 1 (Maps to Example 1: Linear Function & Axes)
        # Description: 計算一次函數 y = ax + b 的圖形與 x 軸、 y 軸所圍成的區域面積。
        while True:
            a_float = random.choice(a_options_type1)
            b_float = random.choice(b_options) # b is never 0 here
            
            y_intercept_float = b_float
            x_intercept_float = -b_float / a_float # a_float is never 0 here

            # Ensure intercepts are within reasonable bounds for plotting
            if abs(x_intercept_float) <= 10 and abs(y_intercept_float) <= 10:
                break
        
        # Area calculation for a triangle
        correct_area = 0.5 * abs(x_intercept_float) * abs(y_intercept_float)

        # Format coefficients for LaTeX
        a_latex = _format_fraction_for_latex(a_float)
        b_latex = _format_fraction_for_latex(b_float, signed=True)
        
        # Build function string safely (Equation Robustness)
        func_parts = []
        if a_float == 1.0:
            func_parts.append("x")
        elif a_float == -1.0:
            func_parts.append("-x")
        elif a_float != 0:
            func_parts.append(a_latex + "x")
        
        if b_float != 0:
            func_parts.append(b_latex)
        
        func_str = "y = " + "".join(func_parts)
        if func_str == "y = ": # Should not happen with current logic, but safety
            func_str = "y = 0"

        question_text = r"設函數 ${func_str}$ 的圖形與$x$軸、$y$軸所圍成的區域為$R$。求$R$的面積。".replace("{func_str}", func_str)
        
        image_base64 = _draw_coordinate_plane(line_eq=(a_float, b_float), x_intercept=x_intercept_float, y_intercept=y_intercept_float)

    else: # problem_type == 2
        # Type 2 (Maps to Example 2: Linear Function & Vertical Lines)
        # Description: 計算一次函數 y = ax + b 的圖形與 x 軸、直線 x=c1 和 x=c2 所圍成的區域面積。
        while True:
            a_float = random.choice(a_options_type2)
            b_float = random.choice(b_options) # b is never 0 here
            
            if a_float == 0 and b_float == 0: # Avoid y=0 case, though b_options already prevents b=0
                b_float = random.choice([float(i) for i in range(-8, 9) if i != 0])
                
            c1_float = float(random.randint(-5, 0))
            c2_float = float(random.randint(int(c1_float) + 2, int(c1_float) + 7))
            
            # Calculate y values at c1 and c2
            y1_at_c1 = a_float * c1_float + b_float
            y2_at_c2 = a_float * c2_float + b_float

            # Ensure y-values are not extremely large for plotting
            if abs(y1_at_c1) <= 10 and abs(y2_at_c2) <= 10:
                break
        
        # Area calculation (considering potential x-intercept within [c1, c2])
        x_intercept_val = -b_float / a_float if a_float != 0 else None
        
        if x_intercept_val is not None and c1_float < x_intercept_val < c2_float:
            # Function crosses x-axis within the interval, split into two triangles/trapezoids
            # Area is the sum of absolute areas
            area1 = 0.5 * abs(y1_at_c1) * abs(x_intercept_val - c1_float)
            area2 = 0.5 * abs(y2_at_c2) * abs(c2_float - x_intercept_val)
            correct_area = area1 + area2
        elif a_float == 0: # Horizontal line y = b_float (rectangle)
            correct_area = abs(b_float) * (c2_float - c1_float)
        else: # No x-intercept in [c1, c2], or x-intercept is outside; it's a single trapezoid/rectangle/triangle
            correct_area = 0.5 * (abs(y1_at_c1) + abs(y2_at_c2)) * (c2_float - c1_float)
        
        # Format coefficients for LaTeX
        a_latex = _format_fraction_for_latex(a_float)
        b_latex = _format_fraction_for_latex(b_float, signed=True)
        
        # Build function string safely (Equation Robustness)
        func_parts = []
        if a_float == 1.0:
            func_parts.append("x")
        elif a_float == -1.0:
            func_parts.append("-x")
        elif a_float != 0:
            func_parts.append(a_latex + "x")
        
        if b_float != 0:
            func_parts.append(b_latex)
        
        func_str = "y = " + "".join(func_parts)
        if func_str == "y = ": # If a_float and b_float are both zero, should be y=0
            func_str = "y = 0"

        c1_str = _format_fraction_for_latex(c1_float)
        c2_str = _format_fraction_for_latex(c2_float)

        question_text = r"設函數 ${func_str}$ 的圖形與$x$軸、直線 $x={c1_str}$ 和 $x={c2_str}$ 所圍成的區域為$R$。求$R$的面積。".replace("{func_str}", func_str).replace("{c1_str}", c1_str).replace("{c2_str}", c2_str)
        
        image_base64 = _draw_coordinate_plane(line_eq=(a_float, b_float), region_x_bounds=(c1_float, c2_float))

    # V7. 數據與欄位
    correct_answer_str = str(round(correct_area, 5)) # Round to a few decimal places for comparison
    
    return {
        "question_text": question_text,
        "correct_answer": correct_answer_str,
        "answer": correct_answer_str,
        "image_base64": image_base64,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }

# --- Check function (CRITICAL CODING STANDARDS: Verification & Stability) ---

    """
    V3. 頂層函式: 必須直接定義於模組最外層。
    V3. 自動重載: 確保不依賴全域狀態。
    V1.2 強韌閱卷邏輯 (Robust Check Logic):
    V13.5 禁絕複雜比對: 嚴禁在 check() 內寫 if/else 字串拆解。
    V12.6 結構鎖死: 必須實作「數值序列比對」。
    等價性支援: 支援浮點數比較，允許微小誤差 (abs(user_num - correct_num) < 1e-6)。
    CRITICAL CODING STANDARDS: Universal Check Template.
    Function Definition Integrity: Explicit 
    """
    import re, math
    # 1. 清洗雙方輸入 (移除 LaTeX, 變數名, 空格)
    def clean(s):
        s = str(s).strip().replace(" ", "").lower()
        s = re.sub(r'^[a-z]+=', '', s) # 移除 k=, x=, y=
        s = s.replace("$", "").replace("\\", "")
        return s
    
    u = clean(user_answer)
    c = clean(correct_answer)
    
    # 2. 嘗試數值比對 (支援分數與小數)
    try:
        def parse_val(val_str):
            if "/" in val_str:
                n, d = map(float, val_str.split("/"))
                return n/d
            return float(val_str)
        
        if math.isclose(parse_val(u), parse_val(c), rel_tol=1e-5):
            return {"correct": True, "result": "正確！"}
    except:
        pass
        
    # 3. 降級為字串比對
    if u == c: return {"correct": True, "result": "正確！"}
    return {"correct": False, "result": f"答案錯誤。"}

# [Auto-Injected Patch v11.0] Universal Return, Linebreak & Handwriting Fixer
def _patch_all_returns(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        # 1. 針對 check 函式的布林值回傳進行容錯封裝
        if func.__name__ == 'check' and isinstance(res, bool):
            return {'correct': res, 'result': '正確！' if res else '答案錯誤'}
        
        if isinstance(res, dict):
            # [V11.3 Standard Patch] - 解決換行與編碼問題
            if 'question_text' in res and isinstance(res['question_text'], str):
                # 僅針對「文字反斜線+n」進行物理換行替換，不進行全局編碼轉換
                import re
                # 解決 r-string 導致的 \n 問題
                res['question_text'] = re.sub(r'\n', '\n', res['question_text'])
            
            # --- [V11.0] 智能手寫模式偵測 (Auto Handwriting Mode) ---
            # 判定規則：若答案包含複雜運算符號，強制提示手寫作答
            # 包含: ^ / _ , | ( [ { 以及任何 LaTeX 反斜線
            c_ans = str(res.get('correct_answer', ''))
            # [V13.1 修復] 移除 '(' 與 ','，允許座標與數列使用純文字輸入
            triggers = ['^', '/', '|', '[', '{', '\\']
            
            # [V11.1 Refined] 僅在題目尚未包含提示時注入，避免重複堆疊
            has_prompt = "手寫" in res.get('question_text', '')
            should_inject = (res.get('input_mode') == 'handwriting') or any(t in c_ans for t in triggers)
            
            if should_inject and not has_prompt:
                res['input_mode'] = 'handwriting'
                # [V11.3] 確保手寫提示語在最後一行
                res['question_text'] = res['question_text'].rstrip() + "\n(請在手寫區作答!)"

            # 3. 確保反饋訊息中文
            if func.__name__ == 'check' and 'result' in res:
                if res['result'].lower() in ['correct!', 'correct', 'right']:
                    res['result'] = '正確！'
                elif res['result'].lower() in ['incorrect', 'wrong', 'error']:
                    res['result'] = '答案錯誤'
            
            # 4. 確保欄位完整性
            if 'answer' not in res and 'correct_answer' in res:
                res['answer'] = res['correct_answer']
            if 'answer' in res:
                res['answer'] = str(res['answer'])
            if 'image_base64' not in res:
                res['image_base64'] = ""
        return res
    return wrapper

import sys
for _name, _func in list(globals().items()):
    if callable(_func) and (_name.startswith('generate') or _name == 'check'):
        globals()[_name] = _patch_all_returns(_func)
