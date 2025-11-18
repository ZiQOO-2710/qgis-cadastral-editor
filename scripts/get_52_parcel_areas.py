#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
52개 필지의 면적 정보 추출
"""

import sys
import os

# Add QGIS Python path
qgis_path = 'C:/Program Files/QGIS 3.40.11/apps/qgis-ltr/python'
if os.path.exists(qgis_path):
    sys.path.insert(0, qgis_path)

from qgis.core import QgsApplication, QgsVectorLayer
import csv

# Initialize QGIS
QgsApplication.setPrefixPath('C:/Program Files/QGIS 3.40.11/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# 52개 필지 목록 (스크린샷에서 확인)
target_jibuns = [
    '821', '821-1',
    '822-2',
    '827-1', '827-3', '827-4대', '827-5', '827-6',
    '828-1', '828-2', '828-3', '828-4', '828-5', '828-6', '828-7', '828-8',
    '829', '829-1',
    '830',
    '831', '831-1',
    '832', '832-1', '832-2', '832-3',
    '833-1', '833-2', '833-3', '833-4', '833-7', '833-8', '833-9',
    '833-10', '833-11', '833-12', '833-13', '833-14', '833-15', '833-16',
    '833-17', '833-18', '833-19', '833-20', '833-21', '833-22', '833-23',
    '834-7', '834-10', '834-11', '834-12', '834-13', '834-15'
]

print(f"검색 대상 필지: {len(target_jibuns)}개")

# Load shapefile
cadastral_path = 'C:/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41461_202510.shp'
layer = QgsVectorLayer(cadastral_path, 'cadastral', 'ogr')

if not layer.isValid():
    print("❌ Shapefile 로드 실패")
    qgs.exitQgis()
    sys.exit(1)

print(f"✅ Shapefile 로드 성공: {layer.featureCount():,}개 필지")

# Check fields
print("\n📋 필드 목록:")
for field in layer.fields():
    print(f"  - {field.name()} ({field.typeName()})")

# Filter to Jubulli
jubulli_pnu = '41461101001'
layer.setSubsetString(f'"PNU" LIKE \'{jubulli_pnu}%\'')
print(f"\n✅ 주북리 필지: {layer.featureCount():,}개")

# Extract target parcels
results = []
found_jibuns = set()

for feature in layer.getFeatures():
    jibun = feature['JIBUN']

    # Remove land type suffix for matching
    jibun_clean = jibun
    for suffix in ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목']:
        if jibun.endswith(suffix):
            jibun_clean = jibun[:-1]
            break

    if jibun_clean in target_jibuns or jibun in target_jibuns:
        geom = feature.geometry()
        area_sqm = geom.area()
        area_pyeong = area_sqm * 0.3025

        centroid = geom.centroid().asPoint()

        results.append({
            'jibun': jibun,
            'pnu': feature['PNU'],
            'area_sqm': area_sqm,
            'area_pyeong': area_pyeong,
            'center_x': centroid.x(),
            'center_y': centroid.y()
        })

        found_jibuns.add(jibun_clean if jibun_clean in target_jibuns else jibun)

# Sort by jibun
results.sort(key=lambda x: (
    int(x['jibun'].split('-')[0].replace('전','').replace('대','')),
    int(x['jibun'].split('-')[1].replace('전','').replace('대','')) if '-' in x['jibun'] else 0
))

# Calculate totals
total_sqm = sum(r['area_sqm'] for r in results)
total_pyeong = sum(r['area_pyeong'] for r in results)

# Save to CSV
output_csv = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_52_parcels_area.csv'
with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['No.', '지번', 'PNU', '면적(㎡)', '면적(평)', '중심X', '중심Y'])

    for idx, r in enumerate(results, 1):
        writer.writerow([
            idx,
            r['jibun'],
            r['pnu'],
            f"{r['area_sqm']:.2f}",
            f"{r['area_pyeong']:.2f}",
            f"{r['center_x']:.2f}",
            f"{r['center_y']:.2f}"
        ])

print(f"\n✅ CSV 저장 완료: {output_csv}")
print(f"\n📊 결과 요약:")
print(f"  - 검색 대상: {len(target_jibuns)}개 필지")
print(f"  - 발견된 필지: {len(results)}개")
print(f"  - 총 면적: {total_sqm:,.2f}㎡ ({total_pyeong:,.2f}평)")

# Show missing parcels
missing = set(target_jibuns) - found_jibuns
if missing:
    print(f"\n⚠️ 미발견 필지 ({len(missing)}개):")
    for jibun in sorted(missing):
        print(f"  - {jibun}")

# Display results
print("\n📋 필지별 면적:")
print(f"{'No.':<4} {'지번':<12} {'면적(㎡)':>12} {'면적(평)':>12}")
print("-" * 45)
for idx, r in enumerate(results, 1):
    print(f"{idx:<4} {r['jibun']:<12} {r['area_sqm']:>12,.2f} {r['area_pyeong']:>12,.2f}")
print("-" * 45)
print(f"{'합계':<4} {'':<12} {total_sqm:>12,.2f} {total_pyeong:>12,.2f}")

qgs.exitQgis()
