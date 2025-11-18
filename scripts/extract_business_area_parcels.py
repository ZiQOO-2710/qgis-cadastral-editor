#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업지 범위 내 필지 추출
방법: 이미지 좌표계 기준으로 경계 폴리곤 생성 → Spatial Intersection
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsVectorFileWriter
)
import csv

# 1. 연속지적도 로드
cadastral_path = 'C:/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41461_202510.shp'
cadastral_layer = QgsVectorLayer(cadastral_path, 'cadastral', 'ogr')

if not cadastral_layer.isValid():
    print("❌ 연속지적도를 로드할 수 없습니다")
    exit(1)

print(f"✅ 연속지적도 로드 완료: {cadastral_layer.featureCount()}개 필지")

# 2. 양지면 주북리 필지 필터링 (먼저 리/동 필드 확인 필요)
fields = cadastral_layer.fields()
print("\n📋 필드 목록:")
for i, field in enumerate(fields):
    print(f"  {i}: {field.name()} ({field.typeName()})")

# 리 이름 필드 찾기 (보통 A2, A3, 또는 리명 관련 필드)
li_field = None
jibun_field = None

for field in fields:
    name = field.name().upper()
    if '리' in field.name() or 'RI' in name or 'DONG' in name:
        li_field = field.name()
        print(f"\n🔍 리/동 필드 발견: {li_field}")
    if '지번' in field.name() or 'JIBUN' in name or 'PNU' in name or 'A7' in name:
        jibun_field = field.name()
        print(f"🔍 지번 필드 발견: {jibun_field}")

# 3. 주북리 필지만 필터링
if li_field:
    # 주북리 필터 표현식
    filter_expr = f'"{li_field}" LIKE \'%주북%\' OR "{li_field}" LIKE \'%JUBOK%\''
    cadastral_layer.setSubsetString(filter_expr)
    print(f"\n✅ 주북리 필터 적용: {cadastral_layer.featureCount()}개 필지 발견")
else:
    print("\n⚠️ 리/동 필드를 찾을 수 없습니다. 전체 데이터에서 수동 확인 필요")
    # 샘플 데이터 출력
    print("\n📊 샘플 데이터 (처음 5개):")
    for i, feature in enumerate(cadastral_layer.getFeatures()):
        if i >= 5:
            break
        print(f"  Feature {i}:")
        for field in fields:
            value = feature[field.name()]
            if value and str(value).strip():
                print(f"    {field.name()}: {value}")

# 4. 주북리 필지 범위 확인
extent = cadastral_layer.extent()
print(f"\n📍 주북리 필지 범위:")
print(f"  최소 X: {extent.xMinimum():.2f}")
print(f"  최대 X: {extent.xMaximum():.2f}")
print(f"  최소 Y: {extent.yMinimum():.2f}")
print(f"  최대 Y: {extent.yMaximum():.2f}")
print(f"  중심: ({extent.center().x():.2f}, {extent.center().y():.2f})")

# 5. CRS 정보
crs = cadastral_layer.crs()
print(f"\n🌐 좌표계: {crs.authid()} - {crs.description()}")

# 6. 주북리 필지 목록 CSV 저장 (지번 기준)
if jibun_field:
    output_csv = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_all_parcels.csv'

    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['지번', '면적(㎡)', 'PNU', '좌표X', '좌표Y'])

        for feature in cadastral_layer.getFeatures():
            jibun = feature[jibun_field] if jibun_field else ''
            area = feature.geometry().area()
            centroid = feature.geometry().centroid().asPoint()

            # PNU 필드 찾기
            pnu = ''
            for field in fields:
                if 'PNU' in field.name().upper():
                    pnu = feature[field.name()]
                    break

            writer.writerow([
                jibun,
                f"{area:.2f}",
                pnu,
                f"{centroid.x():.2f}",
                f"{centroid.y():.2f}"
            ])

    print(f"\n✅ 주북리 전체 필지 목록 저장: {output_csv}")
    print(f"   총 {cadastral_layer.featureCount()}개 필지")

print("\n" + "="*60)
print("📋 다음 단계:")
print("1. QGIS에서 이 레이어 열기")
print("2. 사업지 이미지 지오레퍼런싱")
print("3. 경계 폴리곤 digitizing")
print("4. Spatial intersection 실행")
print("="*60)
