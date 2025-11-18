#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 지적도 카테고리별 통계 계산
"""

from qgis.core import QgsProject

# 레이어 가져오기
layers = QgsProject.instance().mapLayersByName('jubulli_categorized')
if not layers:
    print("❌ 레이어를 찾을 수 없습니다: jubulli_categorized")
    print("   먼저 apply_jubulli_style.py를 실행하세요.")
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
        # 필지 개수
        category_stats[category]['count'] += 1

        # 면적 계산 (geometry area, 단위: 제곱미터)
        geom = feature.geometry()
        area_sqm = geom.area()

        category_stats[category]['area_sqm'] += area_sqm
        category_stats[category]['area_pyeong'] += area_sqm * 0.3025

# 합계 계산
total_count = sum(stats['count'] for stats in category_stats.values())
total_area_sqm = sum(stats['area_sqm'] for stats in category_stats.values())
total_area_pyeong = sum(stats['area_pyeong'] for stats in category_stats.values())

# 결과 출력
print("\n📊 주북리 필지 카테고리별 통계\n")
print("=" * 80)
print(f"{'카테고리':<10} {'필지 수':>10} {'면적(㎡)':>15} {'면적(평)':>15} {'설명':<30}")
print("=" * 80)

print(f"{'GREEN':<10} {category_stats['GREEN']['count']:>10} "
      f"{category_stats['GREEN']['area_sqm']:>15,.0f} "
      f"{category_stats['GREEN']['area_pyeong']:>15,.2f} "
      f"{'19.2-24억, 채무 부담 낮음':<30}")

print(f"{'BLUE':<10} {category_stats['BLUE']['count']:>10} "
      f"{category_stats['BLUE']['area_sqm']:>15,.0f} "
      f"{category_stats['BLUE']['area_pyeong']:>15,.2f} "
      f"{'44.4-48억, 중간':<30}")

print(f"{'RED':<10} {category_stats['RED']['count']:>10} "
      f"{category_stats['RED']['area_sqm']:>15,.0f} "
      f"{category_stats['RED']['area_pyeong']:>15,.2f} "
      f"{'52억, 채무 부담 높음':<30}")

print("-" * 80)
print(f"{'합계':<10} {total_count:>10} "
      f"{total_area_sqm:>15,.0f} "
      f"{total_area_pyeong:>15,.2f}")
print("=" * 80)

# 통계 데이터를 CSV로 저장
import csv
csv_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_statistics.csv'

with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['카테고리', '필지 수', '면적(㎡)', '면적(평)', '설명'])
    writer.writerow(['GREEN', category_stats['GREEN']['count'],
                     f"{category_stats['GREEN']['area_sqm']:.0f}",
                     f"{category_stats['GREEN']['area_pyeong']:.2f}",
                     '19.2-24억, 채무 부담 낮음'])
    writer.writerow(['BLUE', category_stats['BLUE']['count'],
                     f"{category_stats['BLUE']['area_sqm']:.0f}",
                     f"{category_stats['BLUE']['area_pyeong']:.2f}",
                     '44.4-48억, 중간'])
    writer.writerow(['RED', category_stats['RED']['count'],
                     f"{category_stats['RED']['area_sqm']:.0f}",
                     f"{category_stats['RED']['area_pyeong']:.2f}",
                     '52억, 채무 부담 높음'])
    writer.writerow(['합계', total_count,
                     f"{total_area_sqm:.0f}",
                     f"{total_area_pyeong:.2f}", ''])

print(f"\n✅ 통계 CSV 저장 완료: {csv_path}")
