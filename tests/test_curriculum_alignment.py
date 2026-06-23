import pytest
from app import create_app
from core.utils import (
    normalize_curriculum,
    get_curriculum_label,
    get_curriculum_options,
    get_curriculum_aliases,
    CURRICULUM_DEFINITIONS
)

@pytest.fixture
def app_ctx():
    app = create_app()
    with app.app_context():
        yield

def test_curriculum_definitions_order():
    options = get_curriculum_options()
    assert len(options) == 3
    assert options[0]['key'] == 'junior_high'
    assert options[0]['label'] == '國中'
    assert options[1]['key'] == 'general'
    assert options[1]['label'] == '普高'
    assert options[2]['key'] == 'vocational'
    assert options[2]['label'] == '技高'

def test_normalize_curriculum():
    # Canonical keys remain unchanged
    assert normalize_curriculum('junior_high') == 'junior_high'
    assert normalize_curriculum('general') == 'general'
    assert normalize_curriculum('vocational') == 'vocational'
    
    # Aliases normalized correctly
    assert normalize_curriculum('junior') == 'junior_high'
    assert normalize_curriculum('國中') == 'junior_high'
    
    assert normalize_curriculum('general_high') == 'general'
    assert normalize_curriculum('senior_high') == 'general'
    assert normalize_curriculum('普高') == 'general'
    assert normalize_curriculum('senior') == 'general'
    
    assert normalize_curriculum('vocational_high') == 'vocational'
    assert normalize_curriculum('technical') == 'vocational'
    assert normalize_curriculum('技高') == 'vocational'
    
    # Special and missing values
    assert normalize_curriculum(None) is None
    assert normalize_curriculum('all') == 'all'
    assert normalize_curriculum('unknown_val') == 'unknown_val'

def test_get_curriculum_label():
    assert get_curriculum_label('junior_high') == '國中'
    assert get_curriculum_label('國中') == '國中'
    assert get_curriculum_label('general') == '普高'
    assert get_curriculum_label('senior_high') == '普高'
    assert get_curriculum_label('vocational') == '技高'
    assert get_curriculum_label('技高') == '技高'
    assert get_curriculum_label('unknown') == 'unknown'

def test_get_curriculum_aliases():
    aliases_jh = get_curriculum_aliases('junior_high')
    assert 'junior_high' in aliases_jh
    assert '國中' in aliases_jh
    assert 'junior' in aliases_jh
    
    aliases_general = get_curriculum_aliases('general')
    assert 'general' in aliases_general
    assert 'general_high' in aliases_general
    assert 'senior_high' in aliases_general
    assert '普高' in aliases_general
    
    aliases_voc = get_curriculum_aliases('vocational')
    assert 'vocational' in aliases_voc
    assert 'technical' in aliases_voc
    assert '技高' in aliases_voc
