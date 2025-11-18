"""
Shapefile 필드 구조 분석 스크립트
QGIS Python으로 실행
"""

import sys
import os

# QGIS 경로 설정
qgis_path = r'C:\Program Files\QGIS 3.40.11\apps\qgis\python'
sys.path.append(qgis_path)

from qgis.core import QgsApplication, QgsVectorLayer

# QGIS 초기화
QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.40.11\apps\qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Shapefile 경로
shapefile_path = r'C:\Users\ksj27\PROJECTS\QGIS\data\AL_D160_50_20250924\AL_D160_50_20250924.shp'

# 레이어 로드
layer = QgsVectorLayer(shapefile_path, "cadastral", "ogr")

if not layer.isValid():
    print("❌ 레이어 로드 실패!")
    sys.exit(1)

print("✅ 레이어 로드 성공!")
print(f"\n📊 총 피처 수: {layer.featureCount():,}")
print(f"🗺️  좌표계: {layer.crs().authid()}")
print(f"📐 지오메트리 타입: {layer.geometryType()}")

# 필드 정보 출력
print("\n" + "="*60)
print("📋 필드 구조")
print("="*60)

fields = layer.fields()
for idx, field in enumerate(fields):
    print(f"{idx+1:2d}. {field.name():20s} | {field.typeName():15s} | 길이: {field.length()}")

# 샘플 데이터 출력
print("\n" + "="*60)
print("📄 샘플 데이터 (처음 5개)")
print("="*60)

features = layer.getFeatures()
for i, feature in enumerate(features):
    if i >= 5:
        break

    print(f"\n--- 피처 {i+1} ---")
    for field in fields:
        value = feature[field.name()]
        print(f"  {field.name():20s}: {value}")

# 지번 관련 필드 찾기
print("\n" + "="*60)
print("🔍 지번 관련 필드 검색")
print("="*60)

jibun_keywords = ['지번', 'JIBUN', 'PNU', '번지', 'BEONJI', 'BON', 'BUN', 'ADDR']
potential_fields = []

for field in fields:
    field_name = field.name().upper()
    for keyword in jibun_keywords:
        if keyword.upper() in field_name:
            potential_fields.append(field.name())
            break

if potential_fields:
    print("✅ 지번 관련 가능성 있는 필드:")
    for pf in potential_fields:
        print(f"   - {pf}")
else:
    print("⚠️  자동 감지 실패. 모든 필드를 확인하세요.")

# QGIS 종료
qgs.exitQgis()
