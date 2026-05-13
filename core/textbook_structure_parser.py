import os
import yaml
import logging

logger = logging.getLogger(__name__)

class TextbookStructureMap:
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path
        self.data = self._load_yaml()
        self.section_lookup = self._build_lookup()

    def _load_yaml(self):
        if not os.path.exists(self.yaml_path):
            logger.warning(f"Structure YAML not found: {self.yaml_path}")
            return {}
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading structure YAML: {e}")
            return {}

    def _build_lookup(self):
        lookup = {}
        chapters = self.data.get('chapters', [])
        for chap in chapters:
            chap_idx = chap.get('index')
            chap_title = chap.get('title')
            sections = chap.get('sections', [])
            for sec in sections:
                code = sec.get('code')
                lookup[code] = {
                    'chapter_index': chap_idx,
                    'chapter_title': f"{chap_idx} {chap_title}",
                    'section_code': code,
                    'section_title': f"{code} {sec.get('title')}",
                    'display_order_base': sec.get('order', chap_idx * 10000),
                    'type': sec.get('type', 'section_textbook')
                }
        return lookup

    def get_metadata(self, section_code):
        return self.section_lookup.get(section_code)

def get_structure_map(curriculum, volume, publisher='longteng'):
    """
    獲取指定課綱、冊別、出版商的結構地圖。
    """
    # 預設路徑：configs/textbook_structure/{publisher}_{volume}_structure.v0.1.yaml
    filename = f"{publisher}_{volume}_structure.v0.1.yaml"
    path = os.path.join('configs', 'textbook_structure', filename)
    
    if os.path.exists(path):
        return TextbookStructureMap(path)
    return None
