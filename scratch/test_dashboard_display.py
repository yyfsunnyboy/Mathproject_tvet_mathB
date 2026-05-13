import re
from app import app
from models import SkillCurriculum
from core.utils import get_chapters_by_curriculum_volume

def _clean_chapter_display(chapter_display):
    chapter_display = str(chapter_display or "")
    chapter_display = re.sub(r'^\?+', '', chapter_display).strip()
    return chapter_display

def test_dashboard_logic(curriculum, volume):
    with app.app_context():
        chapters_raw = get_chapters_by_curriculum_volume(curriculum, volume)
        is_mathb = (curriculum == 'vocational' and 'B' in str(volume))
        
        chapter_cards = []
        if is_mathb:
            chapter_info = []
            for ch in chapters_raw:
                rep = SkillCurriculum.query.filter_by(
                    curriculum=curriculum, volume=volume, chapter=ch
                ).order_by(SkillCurriculum.display_order).first()
                chapter_info.append({
                    'raw': ch,
                    'section': rep.section if rep else "",
                    'display_order': rep.display_order if rep else 999
                })
            
            def section_sort_key(item):
                sec = str(item['section'] or "")
                match = re.search(r'(\d+)-(\d+)', sec)
                if match:
                    return (int(match.group(1)), int(match.group(2)))
                return (999, 999)
            
            chapter_info.sort(key=section_sort_key)
            
            for idx, info in enumerate(chapter_info, start=1):
                ch_raw = info['raw']
                display_name = _clean_chapter_display(ch_raw)
                clean_title = re.sub(r'^\d+\s*', '', display_name).strip()
                new_display = f"{idx} {clean_title}"
                chapter_cards.append({
                    'raw': ch_raw,
                    'display': new_display
                })
        else:
            chapter_cards = [
                {'raw': ch, 'display': _clean_chapter_display(ch)}
                for ch in chapters_raw
            ]
            
        print(f"Results for {curriculum} {volume}:")
        for card in chapter_cards:
            print(f"  [{card['display']}] (raw: {card['raw']})")

if __name__ == "__main__":
    print("--- Testing B1 ---")
    test_dashboard_logic('vocational', '數學B1')
    print("\n--- Testing B4 ---")
    test_dashboard_logic('vocational', '數學B4')
