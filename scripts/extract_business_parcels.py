#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업지 필지 추출 (분할 목록 기준)
본번: 821, 822, 827, 828, 829, 830, 831, 832, 833, 834
"""

from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsVectorFileWriter, QgsFeatureRequest,
    QgsFillSymbol, QgsSimpleFillSymbolLayer
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface
import csv
import re

# 1. 주북리 전체 레이어 가져오기
layers = QgsProject.instance().mapLayersByName('주북리_전체')
if not layers:
    print("❌ '주북리_전체' 레이어를 찾을 수 없습니다")
    print("   먼저 filter_jubulli_by_pnu.py를 실행하세요")
    exit(1)

jubulli_layer = layers[0]
print(f"✅ 주북리 전체 레이어 로드: {jubulli_layer.featureCount()}개 필지")

# 2. 사업지 본번 목록 (분할 목록 기준)
business_bonbuns = ['821', '822', '827', '828', '829', '830', '831', '832', '833', '834']

print(f"\n🎯 사업지 본번: {', '.join(business_bonbuns)}")

# 3. 사업지 필지 추출
business_features = []
business_jibuns = []

for feature in jubulli_layer.getFeatures():
    jibun = feature['JIBUN']

    # 지번에서 본번 추출 (예: "821-2전" → "821")
    match = re.match(r'^(\d+)', jibun)
    if match:
        bonbun = match.group(1)

        if bonbun in business_bonbuns:
            business_features.append(feature)
            business_jibuns.append(jibun)

print(f"\n✅ 사업지 필지 발견: {len(business_features)}개")

if len(business_features) == 0:
    print("❌ 사업지 필지를 찾을 수 없습니다")
    print("\n샘플 지번 (처음 20개):")
    for i, feature in enumerate(jubulli_layer.getFeatures()):
        if i >= 20:
            break
        print(f"   {feature['JIBUN']}")
    exit(1)

# 4. 본번별 통계
bonbun_counts = {}
for jibun in business_jibuns:
    match = re.match(r'^(\d+)', jibun)
    if match:
        bonbun = match.group(1)
        bonbun_counts[bonbun] = bonbun_counts.get(bonbun, 0) + 1

print("\n📊 본번별 필지 수:")
for bonbun in sorted(bonbun_counts.keys(), key=int):
    print(f"   {bonbun}번: {bonbun_counts[bonbun]}개")

# 5. 사업지 레이어 생성 및 QGIS에 추가
# 기존 레이어 제거
existing = QgsProject.instance().mapLayersByName('사업지_필지')
for layer in existing:
    QgsProject.instance().removeMapLayer(layer.id())

# 새 메모리 레이어 생성
business_layer = QgsVectorLayer(
    f"Polygon?crs={jubulli_layer.crs().authid()}",
    "사업지_필지",
    "memory"
)

provider = business_layer.dataProvider()

# 필드 복사
provider.addAttributes(jubulli_layer.fields())
business_layer.updateFields()

# Feature 추가
provider.addFeatures(business_features)

# 레이어 스타일 (빨간색 테두리)
symbol = QgsFillSymbol()
fill_layer = QgsSimpleFillSymbolLayer()
fill_layer.setFillColor(QColor(255, 255, 0, 0))  # 투명
fill_layer.setStrokeColor(QColor(255, 0, 0))  # 빨간색
fill_layer.setStrokeWidth(2)
symbol.changeSymbolLayer(0, fill_layer)
business_layer.renderer().setSymbol(symbol)

QgsProject.instance().addMapLayer(business_layer)

print(f"\n✅ QGIS에 '사업지_필지' 레이어 추가 완료")

# 6. 사업지 범위로 확대
extent = business_layer.extent()
extent.scale(1.2)  # 20% 여유
iface.mapCanvas().setExtent(extent)
iface.mapCanvas().refresh()

print(f"\n📍 사업지 범위:")
print(f"   X: {extent.xMinimum():.0f} ~ {extent.xMaximum():.0f}")
print(f"   Y: {extent.yMinimum():.0f} ~ {extent.yMaximum():.0f}")

# 7. 사업지 필지 목록 CSV 저장
output_csv = 'C:/Users/ksj27/PROJECTS/QGIS/output/business_area_parcels.csv'

with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['본번', '지번', '면적(㎡)', '면적(평)', 'PNU'])

    # 정렬: 본번 → 부번 순
    sorted_features = sorted(business_features, key=lambda f: (
        int(re.match(r'^(\d+)', f['JIBUN']).group(1)),
        f['JIBUN']
    ))

    for feature in sorted_features:
        jibun = feature['JIBUN']
        pnu = feature['PNU']
        geom = feature.geometry()
        area_sqm = geom.area()
        area_pyeong = area_sqm * 0.3025

        # 본번 추출
        match = re.match(r'^(\d+)', jibun)
        bonbun = match.group(1) if match else ''

        writer.writerow([
            bonbun,
            jibun,
            f"{area_sqm:.2f}",
            f"{area_pyeong:.2f}",
            pnu
        ])

print(f"\n✅ 사업지 필지 목록 저장: {output_csv}")
print(f"   총 {len(business_features)}개 필지")

# 8. 사업지 Shapefile 저장
output_shp = 'C:/Users/ksj27/PROJECTS/QGIS/output/business_area.shp'
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "ESRI Shapefile"
options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV3(
    business_layer,
    output_shp,
    QgsProject.instance().transformContext(),
    options
)

if error[0] == QgsVectorFileWriter.NoError:
    print(f"\n✅ 사업지 Shapefile 저장: {output_shp}")
else:
    print(f"\n⚠️ Shapefile 저장 실패: {error}")

# 9. 총 면적 계산
total_area_sqm = sum(f.geometry().area() for f in business_features)
total_area_pyeong = total_area_sqm * 0.3025

print(f"\n📊 사업지 총 면적:")
print(f"   {total_area_sqm:,.0f}㎡ ({total_area_pyeong:,.2f}평)")

print("\n" + "="*70)
print("✅ 사업지 필지 추출 완료!")
print(f"   - 레이어: '사업지_필지' (빨간색 테두리)")
print(f"   - CSV: {output_csv}")
print(f"   - Shapefile: {output_shp}")
print("="*70)
