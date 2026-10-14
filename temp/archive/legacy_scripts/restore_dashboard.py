import codecs
import re

with codecs.open('templates/dashboard.html', 'r', 'utf-8') as f:
    content = f.read()

regex = r"(<small>.*?\{\{\s*skill\.questions_solved\s*\}\}.*?</small>\s*</div>\s*)<a href=\"\{\{\s*url_for\('practice\.practice',\s*skill_id=skill\.skill_id\)\s*\}\}\"[^>]*>\s*開始練習\s*</a>"

replacement = r"""\1{% set is_b4_ch1_tree_diagram = (
                        curriculum == 'vocational'
                        and volume == '數學B4'
                        and (chapter_display|string).startswith('1')
                        and (
                            skill.skill_id == 'vh_數學B4_TreeDiagramCounting'
                            or skill.skill_ch_name == '樹狀圖'
                            or 'TreeDiagramCounting' in (skill.skill_id|string)
                        )
                    ) %}
                    <a href="{{ url_for('practice.free_response_practice_page', curriculum=curriculum, volume=volume, chapter_id='1', problem_type='tree_diagram_listing', variant='early_stopping_game') if is_b4_ch1_tree_diagram else url_for('practice.practice', skill_id=skill.skill_id) }}" class="btn-practice">
                        開始練習
                    </a>"""

if re.search(regex, content, re.DOTALL):
    content = re.sub(regex, replacement, content, count=1, flags=re.DOTALL)
    with codecs.open('templates/dashboard.html', 'w', 'utf-8') as f:
        f.write(content)
    print("Successfully restored dashboard.html")
else:
    print("Target not found in dashboard.html via regex")
