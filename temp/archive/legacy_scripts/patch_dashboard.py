import re
import codecs

with codecs.open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Using a simpler regex that just matches the {% set is_b4_ch1_tree_diagram ... %} block
# and the <a> tag right after it.
regex = r"\{% set is_b4_ch1_tree_diagram =.*?\s*<a href=\"[^\"]+\"\s+class=\"btn-practice\">\s*[^<]+\s*</a>"

replacement = """<a href="{{ url_for('practice.practice', skill_id=skill.skill_id) }}" class="btn-practice">
                        開始練習
                    </a>"""

if re.search(regex, content, re.DOTALL):
    content = re.sub(regex, replacement, content, count=1, flags=re.DOTALL)
    print("Replaced dashboard logic successfully")
else:
    print("Dashboard regex not found")

with codecs.open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
