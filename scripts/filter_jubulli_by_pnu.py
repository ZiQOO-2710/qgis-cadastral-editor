#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNU 코드로 주북리 필지 필터링 및 QGIS 표시
"""

from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsVectorFileWriter, QgsCoordinateReferenceSystem
)
from qgis.utils import iface
import csv

# 1. 연속지적도 로드
cadastral_path = 'C:/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41461_202510.shp'
cadastral_layer = QgsVectorLayer(cadastral_path, 'cadastral_temp', 'ogr')

if not cadastral_layer.isValid():
    print("❌ 연속지적도를 로드할 수 없습니다")
    exit(1)

print(f"✅ 연속지적도 로드 완료: {cadastral_layer.featureCount()}개 필지")

# 2. PNU 코드로 주북리 필터링
# PNU 구조: 41461 (처인구) + 101 (양지면) + 00 (주북리) + 1 (지목코드) + ...
# 주북리 PNU 패�n: 41461101001...
jubulli_pnu_prefix = '41461101001'

filter_expr = f'"PNU" LIKE \'{jubulli_pnu_prefix}%\''
cadastral_layer.setSubsetString(filter_expr)

jubulli_count = cadastral_layer.featureCount()
print(f"\n✅ 주북리 필터 적용 (PNU: {jubulli_pnu_prefix}...)")
print(f"   주북리 필지: {jubulli_count}개")

if jubulli_count == 0:
    print("\n❌ 주북리 필지를 찾을 수 없습니다. PNU 패턴 확인 필요")
    print("   샘플 PNU 코드:")
    cadastral_layer.setSubsetString('')  # 필터 해제
    for i, feature in enumerate(cadastral_layer.getFeatures()):
        if i >= 10:
            break
        print(f"     {feature['JIBUN']}: {feature['PNU']}")
    exit(1)

# 3. 주북리 레이어를 QGIS에 추가
# 기존 레이어 제거
existing_layers = QgsProject.instance().mapLayersByName('주북리_전체')
for layer in existing_layers:
    QgsProject.instance().removeMapLayer(layer.id())

# 새 레이어 추가
cadastral_layer.setName('주북리_전체')
QgsProject.instance().addMapLayer(cadastral_layer)

print(f"\n✅ QGIS에 레이어 추가 완료: '주북리_전체'")

# 4. 주북리 범위로 확대
extent = cadastral_layer.extent()
iface.mapCanvas().setExtent(extent)
iface.mapCanvas().refresh()

print(f"\n📍 주북리 필지 범위:")
print(f"   X: {extent.xMinimum():.0f} ~ {extent.xMaximum():.0f}")
print(f"   Y: {extent.yMinimum():.0f} ~ {extent.yMaximum():.0f}")

# 5. 주북리 필지 목록 CSV 저장
output_csv = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_all_parcels.csv'

with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['지번', '면적(㎡)', '면적(평)', 'PNU', '중심X', '중심Y'])

    for feature in cadastral_layer.getFeatures():
        jibun = feature['JIBUN']
        pnu = feature['PNU']
        geom = feature.geometry()
        area_sqm = geom.area()
        area_pyeong = area_sqm * 0.3025
        centroid = geom.centroid().asPoint()

        writer.writerow([
            jibun,
            f"{area_sqm:.2f}",
            f"{area_pyeong:.2f}",
            pnu,
            f"{centroid.x():.2f}",
            f"{centroid.y():.2f}"
        ])

print(f"\n✅ 주북리 전체 필지 목록 저장: {output_csv}")
print(f"   총 {jubulli_count}개 필지")

# 6. 주북리 Shapefile 저장 (나중에 사용)
output_shp = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_all.shp'
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "ESRI Shapefile"
options.fileEncoding = "UTF-8"

error = QgsVectorFileWriter.writeAsVectorFormatV3(
    cadastral_layer,
    output_shp,
    QgsProject.instance().transformContext(),
    options
)

if error[0] == QgsVectorFileWriter.NoError:
    print(f"\n✅ 주북리 Shapefile 저장: {output_shp}")
else:
    print(f"\n⚠️ Shapefile 저장 실패: {error}")

print("\n" + "="*70)
print("✅ 작업 완료!")
print("   다음: 사업지 경계 폴리곤으로 필지 선택")
print("="*70)
