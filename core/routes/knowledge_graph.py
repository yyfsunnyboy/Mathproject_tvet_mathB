# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/routes/knowledge_graph.py
功能說明 (Description): 知識圖譜視覺化路由，提供知識點前置關係的樹狀圖展示
執行語法 (Usage): 由系統調用
版本資訊 (Version): V1.0
更新日期 (Date): 2026-01-31
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""

from flask import request, jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy import and_

from . import core_bp
from models import db, SkillInfo, SkillPrerequisites, SkillCurriculum, StudentAbility
from core.adaptive_config import ABILITY_DEFAULT, CONCEPT_DEFAULT, CALCULATION_DEFAULT

# ==========================================
# 知識圖譜頁面
# ==========================================

@core_bp.route('/knowledge-graph')
@login_required
def knowledge_graph():
    """
    顯示知識圖譜視覺化頁面
    """
    return render_template('knowledge_graph.html', username=current_user.username)


# ==========================================
# 知識圖譜資料 API
# ==========================================

@core_bp.route('/api/knowledge-graph/data')
@login_required
def get_knowledge_graph_data():
    """
    獲取知識圖譜的節點和連接資料
    
    查詢參數:
        curriculum: 課程類型 (junior_high, general, vocational)
        grade: 年級 (7, 8, 9, 10, 11, 12)
        volume: 冊別 (如 "數學1上")
        chapter: 章節 (如 "第一章")
    
    返回:
        JSON 格式的圖譜資料，包含 nodes 和 links
    """
    try:
        # 獲取篩選參數
        curriculum = request.args.get('curriculum')
        grade = request.args.get('grade', type=int)
        volume = request.args.get('volume')
        chapter = request.args.get('chapter')
        
        # 建立查詢條件
        query = db.session.query(SkillCurriculum).join(
            SkillInfo, SkillCurriculum.skill_id == SkillInfo.skill_id
        ).filter(SkillInfo.is_active == True)
        
        # 應用篩選條件
        if curriculum:
            query = query.filter(SkillCurriculum.curriculum == curriculum)
        if grade:
            query = query.filter(SkillCurriculum.grade == grade)
        if volume:
            query = query.filter(SkillCurriculum.volume == volume)
        if chapter:
            query = query.filter(SkillCurriculum.chapter == chapter)
        
        # 獲取符合條件的技能
        curriculum_entries = query.all()
        skill_ids = [entry.skill_id for entry in curriculum_entries]
        
        if not skill_ids:
            return jsonify({'nodes': [], 'links': []})
        
        # 獲取這些技能的詳細資訊
        skills = db.session.query(SkillInfo).filter(
            SkillInfo.skill_id.in_(skill_ids)
        ).all()
        
        # 獲取學生的能力值
        abilities = db.session.query(StudentAbility).filter(
            StudentAbility.user_id == current_user.id,
            StudentAbility.skill_id.in_(skill_ids)
        ).all()
        ability_dict = {a.skill_id: a for a in abilities}
        
        # 獲取前置關係
        prerequisites = db.session.query(SkillPrerequisites).filter(
            SkillPrerequisites.skill_id.in_(skill_ids)
        ).all()
        
        # 建立課程資訊字典
        curriculum_dict = {entry.skill_id: entry for entry in curriculum_entries}
        
        # 構建節點資料
        nodes = []
        for skill in skills:
            ability = ability_dict.get(skill.skill_id)
            curriculum_info = curriculum_dict.get(skill.skill_id)
            
            # 計算掌握狀態
            if ability:
                ability_a = ability.ability_a
                concept_u = ability.concept_u
                calculation_c = ability.calculation_c
                
                if ability_a >= 100:
                    mastery_status = 'mastered'
                elif ability_a >= 50:
                    mastery_status = 'learning'
                else:
                    mastery_status = 'not_started'
            else:
                ability_a = ABILITY_DEFAULT
                concept_u = CONCEPT_DEFAULT
                calculation_c = CALCULATION_DEFAULT
                mastery_status = 'not_started'
            
            node = {
                'id': skill.skill_id,
                'name': skill.skill_ch_name,
                'description': skill.description,
                'category': skill.category,
                'ability_a': round(ability_a, 1),
                'concept_u': round(concept_u, 1),
                'calculation_c': round(calculation_c, 1),
                'mastery_status': mastery_status
            }
            
            # 添加課程資訊（如果有）
            if curriculum_info:
                node.update({
                    'curriculum': curriculum_info.curriculum,
                    'grade': curriculum_info.grade,
                    'volume': curriculum_info.volume,
                    'chapter': curriculum_info.chapter,
                    'section': curriculum_info.section
                })
            
            nodes.append(node)
        
        # 構建連接資料
        links = []
        for prereq in prerequisites:
            links.append({
                'source': prereq.prerequisite_id,
                'target': prereq.skill_id
            })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==========================================
# 獲取篩選選項 API
# ==========================================

@core_bp.route('/api/knowledge-graph/filters')
@login_required
def get_knowledge_graph_filters():
    """
    獲取可用的篩選選項（課程、年級、冊別、章節）
    """
    try:
        curriculum = request.args.get('curriculum')
        grade = request.args.get('grade', type=int)
        volume = request.args.get('volume')
        
        result = {}
        
        # 獲取所有課程類型
        if not curriculum:
            curriculums = db.session.query(SkillCurriculum.curriculum).distinct().all()
            result['curriculums'] = [c[0] for c in curriculums]
            return jsonify(result)
        
        # 獲取該課程的所有年級
        if curriculum and not grade:
            grades = db.session.query(SkillCurriculum.grade).filter(
                SkillCurriculum.curriculum == curriculum
            ).distinct().order_by(SkillCurriculum.grade).all()
            result['grades'] = [g[0] for g in grades]
            return jsonify(result)
        
        # 獲取該年級的所有冊別
        if curriculum and grade and not volume:
            volumes = db.session.query(SkillCurriculum.volume).filter(
                SkillCurriculum.curriculum == curriculum,
                SkillCurriculum.grade == grade
            ).distinct().all()
            result['volumes'] = [v[0] for v in volumes]
            return jsonify(result)
        
        # 獲取該冊別的所有章節
        if curriculum and grade and volume:
            chapters = db.session.query(SkillCurriculum.chapter).filter(
                SkillCurriculum.curriculum == curriculum,
                SkillCurriculum.grade == grade,
                SkillCurriculum.volume == volume
            ).distinct().all()
            result['chapters'] = [c[0] for c in chapters]
            return jsonify(result)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
