#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
범례에 면적 정보 추가
각 카테고리 규칙의 라벨을 "카테고리 (필지수, 면적㎡, 면적평)" 형식으로 업데이트
"""

from qgis.core import QgsProject

# 레이어 가져오기
layers = QgsProject.instance().mapLayersByName('jubulli_categorized')
if not layers:
    print("❌ 레이어를 찾을 수 없습니다: jubulli_categorized")
    exit(1)

layer = layers[0]

# 카테고리별 통계 계산
category_stats = {
    'GREEN': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0},
    'BLUE': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0},
    'RED': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0}
}

for feature in layer.getFeatures():
    category = feature['CATEGORY']
    if category in category_stats:
        category_stats[category]['count'] += 1
        geom = feature.geometry()
        area_sqm = geom.area()
        category_stats[category]['area_sqm'] += area_sqm
        category_stats[category]['area_pyeong'] += area_sqm * 0.3025

# 렌더러 가져오기
renderer = layer.renderer()
root_rule = renderer.rootRule()

# 각 규칙의 라벨 업데이트
for rule in root_rule.children():
    filter_expr = rule.filterExpression()

    if 'GREEN' in filter_expr:
        count = category_stats['GREEN']['count']
        area_sqm = category_stats['GREEN']['area_sqm']
        area_pyeong = category_stats['GREEN']['area_pyeong']
        rule.setLabel(f'GREEN ({count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평)\n19.2-24억, 채무 부담 낮음')
        print(f"✅ GREEN 라벨 업데이트: {count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평")

    elif 'BLUE' in filter_expr:
        count = category_stats['BLUE']['count']
        area_sqm = category_stats['BLUE']['area_sqm']
        area_pyeong = category_stats['BLUE']['area_pyeong']
        rule.setLabel(f'BLUE ({count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평)\n44.4-48억, 중간')
        print(f"✅ BLUE 라벨 업데이트: {count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평")

    elif 'RED' in filter_expr:
        count = category_stats['RED']['count']
        area_sqm = category_stats['RED']['area_sqm']
        area_pyeong = category_stats['RED']['area_pyeong']
        rule.setLabel(f'RED ({count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평)\n52억, 채무 부담 높음')
        print(f"✅ RED 라벨 업데이트: {count}필지, {area_sqm:,.0f}㎡, {area_pyeong:,.2f}평")

# 레이어 새로고침
layer.triggerRepaint()

print("\n✅ 범례 라벨 업데이트 완료!")
print("   이제 조판에 범례를 추가하면 면적 정보가 포함됩니다.")
