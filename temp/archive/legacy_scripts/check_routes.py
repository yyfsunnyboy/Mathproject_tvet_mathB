#!/usr/bin/env python
"""
檢查 Flask 應用中已註冊的路由
"""

from app import create_app

app = create_app()

print("\n" + "="*80)
print("Flask 應用已註冊的路由")
print("="*80)

routes = []
for rule in app.url_map.iter_rules():
    routes.append({
        'endpoint': rule.endpoint,
        'methods': ','.join(rule.methods),
        'rule': rule.rule
    })

# 按路由排序
routes.sort(key=lambda x: x['rule'])

# 篩選出 adaptive-review 相關的路由
adaptive_routes = [r for r in routes if 'adaptive' in r['rule']]

print("\n📍 自適應複習相關路由:")
if adaptive_routes:
    for r in adaptive_routes:
        print(f"  {r['rule']:<50} [{r['methods']:<20}] {r['endpoint']}")
else:
    print("  ❌ 未找到任何自適應複習路由")

print("\n📍 所有 /api 路由:")
api_routes = [r for r in routes if '/api' in r['rule']]
for r in api_routes[:15]:  # 只顯示前 15 個
    print(f"  {r['rule']:<50} [{r['methods']:<20}] {r['endpoint']}")

if len(api_routes) > 15:
    print(f"  ... 還有 {len(api_routes) - 15} 個路由")

print("\n" + "="*80)
print(f"總共註冊了 {len(routes)} 個路由")
print("="*80 + "\n")
