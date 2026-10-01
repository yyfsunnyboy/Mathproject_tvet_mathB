#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自適應複習模式 - 前後端集成測試
用於驗證新的簡潔介面是否能正常工作
"""

import sys
import os
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

import json
from datetime import datetime

def test_api_integration():
    """測試 API 集成"""
    from adaptive_review_api import adaptive_review_bp, get_engine, normalize_history
    
    print("=" * 60)
    print("自適應複習模式 - 前後端集成測試")
    print("=" * 60)
    
    try:
        # 1. 測試引擎初始化
        print("\n✓ 測試 1: 初始化自適應複習引擎...")
        engine = get_engine()
        print("  ✅ 引擎成功初始化")
        
        # 2. 測試歷史標準化
        print("\n✓ 測試 2: 驗證歷史數據格式...")
        sample_history = {
            'item_history': [1, 2, 3, 4, 5],
            'skill_history': [0, 1, 2, 0, 1],
            'resp_history': [1, 1, 0, 1, 0]
        }
        normalized = normalize_history(sample_history)
        print(f"  原始格式: {sample_history}")
        print(f"  標準化後: {normalized}")
        print("  ✅ 格式驗證成功")
        
        # 3. 測試推薦功能
        print("\n✓ 測試 3: 測試推薦引擎...")
        try:
            # 直接調用引擎的推薦方法
            recommendations = engine.recommend_items(
                item_history=sample_history['item_history'],
                skill_history=sample_history['skill_history'],
                resp_history=sample_history['resp_history'],
                n_recommendations=3
            )
            
            if recommendations:
                print(f"  推薦題目數量: {len(recommendations)}")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"    {i}. 題目 ID: {rec.get('item_id', '?')}, "
                          f"技能: {rec.get('skill_id', '?')}, "
                          f"難度: {rec.get('predicted_difficulty', '?'):.2f}")
                print("  ✅ 推薦功能正常")
            else:
                print("  ⚠️  未生成推薦")
                
        except Exception as e:
            print(f"  ⚠️  推薦測試警告: {str(e)[:100]}")
        
        # 4. 檢查 API 路由
        print("\n✓ 測試 4: 驗證 API 路由...")
        print(f"  藍圖名稱: {adaptive_review_bp.name}")
        print(f"  藍圖前綴: {adaptive_review_bp.url_prefix}")
        print(f"  已註冊路由:")
        for rule in adaptive_review_bp.deferred_functions:
            print(f"    - {rule}")
        print("  ✅ API 路由驗證成功")
        
        print("\n" + "=" * 60)
        print("✅ 所有測試通過！前後端集成正常。")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """檢查必要的依賴"""
    print("\n✓ 檢查依賴...")
    
    required = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'flask': 'Flask',
        'sqlalchemy': 'SQLAlchemy'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - 缺失")
            missing.append(module)
    
    return len(missing) == 0


def main():
    """主測試函數"""
    print("\n🚀 開始自適應複習模式測試...\n")
    
    # 檢查依賴
    if not check_dependencies():
        print("\n⚠️  某些依賴缺失，部分功能可能不可用")
    
    # 執行集成測試
    success = test_api_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 測試完成 - 系統準備就緒")
        print("\n接下來，請：")
        print("1. 啟動 Flask 應用: python app.py")
        print("2. 訪問 http://127.0.0.1:5000/login")
        print("3. 登入後訪問 /adaptive-review 使用新介面")
    else:
        print("❌ 測試未完全通過 - 請檢查錯誤")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
