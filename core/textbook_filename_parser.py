import os
import re

def parse_textbook_filename_metadata(filename: str) -> dict:
    """
    解析教材檔名中的元數據 (Chapter, Section, Title)。
    支援格式：
    1. 一般小節：「第一章 1-2 平面坐標系與線型函數-課本.docx」
    2. 自我評量：「第一章 自我評量-課本.docx」
    """
    if not filename:
        return {}
        
    base_name = os.path.basename(filename)
    # 移除副檔名與後綴
    clean_name = re.sub(r'(-課本)?\.(docx|doc|pdf)$', '', base_name, flags=re.IGNORECASE).strip()
    
    metadata = {
        'chapter_label': None,
        'chapter_index': None,
        'section_code': None,
        'section_index': None,
        'section_title': clean_name,
        'source_scope': 'section_textbook'
    }
    
    # 中文數字轉阿拉伯數字映射 (簡單支援前十章)
    cn_num_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10
    }
    
    # 1. 解析章節標籤 (例如：第一章)
    chap_match = re.search(r'第([一二三四五六七八九十\d]+)章', clean_name)
    if chap_match:
        metadata['chapter_label'] = chap_match.group(0)
        chap_val = chap_match.group(1)
        metadata['chapter_index'] = cn_num_map.get(chap_val)
            
    # 2. 解析自我評量 (優先判斷)
    if '自我評量' in clean_name:
        metadata['section_code'] = f"{metadata['chapter_index']}-review" if metadata['chapter_index'] else "review"
        metadata['section_index'] = 99
        metadata['section_title'] = '自我評量'
        metadata['source_scope'] = 'chapter_review'
        return metadata

    # 3. 解析小節編號與標題 (例如：1-2 平面坐標系與線型函數 或 1-1_-)
    # 支援更寬鬆的格式，包含底線或連字號
    sec_match = re.search(r'(\d+)-(\d+)[\s_-]*(.*)', clean_name)
    if sec_match:
        metadata['section_code'] = f"{sec_match.group(1)}-{sec_match.group(2)}"
        metadata['section_index'] = int(sec_match.group(2))
        
        # 清理標題，移除開頭的底線或連字號
        raw_title = sec_match.group(3).strip()
        metadata['section_title'] = re.sub(r'^[_-]+', '', raw_title).strip() or clean_name
        
        # 如果 chapter_index 尚未解析出，則從 section_code 第一段推導
        if not metadata['chapter_index']:
            metadata['chapter_index'] = int(sec_match.group(1))
            metadata['chapter_label'] = f"第{metadata['chapter_index']}章"
            metadata['chapter_title'] = metadata['chapter_label']

    return metadata
