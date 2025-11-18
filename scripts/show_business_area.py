#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업지 필지 표시 (필터 방식 - 안전)
"""

from qgis.core import QgsProject
from qgis.utils import iface
import re

print("=" * 70)
print("사업지 필지 표시")
print("=" * 70)

# 1. 주북리 전체 레이어 가져오기
layers = QgsProject.instance().mapLayersByName('주북리_전체')
if not layers:
    print("❌ '주북리_전체' 레이어를 찾을 수 없습니다")
    exit(1)

jubulli_layer = layers[0]
print(f"✅ 주북리 전체: {jubulli_layer.featureCount()}개 필지")

# 2. 사업지 본번으로 필터 표현식 생성
business_bonbuns = ['821', '822', '827', '828', '829', '830', '831', '832', '833', '834']
print(f"\n사업지 본번: {', '.join(business_bonbuns)}")

# 필터 표현식: "JIBUN" LIKE '821%' OR "JIBUN" LIKE '822%' OR ...
filter_parts = [f'"JIBUN" LIKE \'{bonbun}%\'' for bonbun in business_bonbuns]
filter_expr = ' OR '.join(filter_parts)

print(f"\n필터 표현식: {filter_expr[:100]}...")

# 3. 필터 적용
jubulli_layer.setSubsetString(filter_expr)

filtered_count = jubulli_layer.featureCount()
print(f"\n✅ 사업지 필지: {filtered_count}개")

if filtered_count == 0:
    print("\n❌ 필터링된 필지가 없습니다")
    print("샘플 지번:")
    jubulli_layer.setSubsetString('')  # 필터 해제
    for i, feature in enumerate(jubulli_layer.getFeatures()):
        if i >= 10:
            break
        print(f"   {feature['JIBUN']}")
    exit(1)

# 4. 사업지 범위로 확대
extent = jubulli_layer.extent()
extent.scale(1.2)  # 20% 여유
iface.mapCanvas().setExtent(extent)
iface.mapCanvas().refresh()

print(f"\n📍 사업지 범위:")
print(f"   X: {extent.xMinimum():.0f} ~ {extent.xMaximum():.0f}")
print(f"   Y: {extent.yMinimum():.0f} ~ {extent.yMaximum():.0f}")

# 5. 본번별 통계
bonbun_counts = {}
total_area_sqm = 0

for feature in jubulli_layer.getFeatures():
    jibun = feature['JIBUN']
    match = re.match(r'^(\d+)', jibun)
    if match:
        bonbun = match.group(1)
        bonbun_counts[bonbun] = bonbun_counts.get(bonbun, 0) + 1
        total_area_sqm += feature.geometry().area()

print(f"\n📊 본번별 필지 수:")
for bonbun in sorted(bonbun_counts.keys(), key=int):
    print(f"   {bonbun}번: {bonbun_counts[bonbun]}개")

total_area_pyeong = total_area_sqm * 0.3025
print(f"\n📊 사업지 총 면적:")
print(f"   {total_area_sqm:,.0f}㎡ ({total_area_pyeong:,.2f}평)")

print("\n" + "=" * 70)
print("✅ 사업지 필지 표시 완료!")
print("\n참고:")
print("   - '주북리_전체' 레이어에 필터가 적용되었습니다")
print("   - 사업지 필지만 화면에 표시됩니다")
print("   - 전체 보기: 레이어 우클릭 → 필터 해제")
print("=" * 70)
