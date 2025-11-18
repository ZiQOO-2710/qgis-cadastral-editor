#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사업지 필지 추출 (안전 버전)
단계별 오류 체크
"""

from qgis.core import QgsProject
import csv
import re

print("=" * 70)
print("사업지 필지 추출 시작")
print("=" * 70)

# 1. 주북리 전체 레이어 가져오기
print("\n[1/5] 주북리 전체 레이어 로드 중...")
layers = QgsProject.instance().mapLayersByName('주북리_전체')
if not layers:
    print("❌ '주북리_전체' 레이어를 찾을 수 없습니다")
    print("   먼저 filter_jubulli_by_pnu.py를 실행하세요")
    exit(1)

jubulli_layer = layers[0]
print(f"✅ 로드 완료: {jubulli_layer.featureCount()}개 필지")

# 2. 사업지 본번 목록
business_bonbuns = ['821', '822', '827', '828', '829', '830', '831', '832', '833', '834']
print(f"\n[2/5] 사업지 본번: {', '.join(business_bonbuns)}")

# 3. 사업지 필지 찾기
print("\n[3/5] 사업지 필지 검색 중...")
business_features = []
business_jibuns = []

count = 0
for feature in jubulli_layer.getFeatures():
    count += 1
    if count % 1000 == 0:
        print(f"   처리 중: {count}/{jubulli_layer.featureCount()}")

    jibun = feature['JIBUN']

    # 지번에서 본번 추출
    match = re.match(r'^(\d+)', jibun)
    if match:
        bonbun = match.group(1)

        if bonbun in business_bonbuns:
            business_features.append(feature)
            business_jibuns.append(jibun)

print(f"\n✅ 사업지 필지 발견: {len(business_features)}개")

if len(business_features) == 0:
    print("\n❌ 사업지 필지를 찾을 수 없습니다")
    print("\n샘플 지번 (처음 20개):")
    for i, feature in enumerate(jubulli_layer.getFeatures()):
        if i >= 20:
            break
        print(f"   {feature['JIBUN']}")
    exit(1)

# 4. 본번별 통계
print("\n[4/5] 본번별 필지 수:")
bonbun_counts = {}
for jibun in business_jibuns:
    match = re.match(r'^(\d+)', jibun)
    if match:
        bonbun = match.group(1)
        bonbun_counts[bonbun] = bonbun_counts.get(bonbun, 0) + 1

for bonbun in sorted(bonbun_counts.keys(), key=int):
    print(f"   {bonbun}번: {bonbun_counts[bonbun]}개")

# 5. CSV 저장
print("\n[5/5] CSV 파일 저장 중...")
output_csv = 'C:/Users/ksj27/PROJECTS/QGIS/output/business_area_parcels.csv'

try:
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['본번', '지번', '면적(㎡)', '면적(평)', 'PNU', '중심X', '중심Y'])

        # 정렬
        sorted_features = sorted(business_features, key=lambda f: (
            int(re.match(r'^(\d+)', f['JIBUN']).group(1)),
            f['JIBUN']
        ))

        total_area_sqm = 0

        for feature in sorted_features:
            jibun = feature['JIBUN']
            pnu = feature['PNU']
            geom = feature.geometry()
            area_sqm = geom.area()
            area_pyeong = area_sqm * 0.3025
            centroid = geom.centroid().asPoint()

            total_area_sqm += area_sqm

            # 본번 추출
            match = re.match(r'^(\d+)', jibun)
            bonbun = match.group(1) if match else ''

            writer.writerow([
                bonbun,
                jibun,
                f"{area_sqm:.2f}",
                f"{area_pyeong:.2f}",
                pnu,
                f"{centroid.x():.2f}",
                f"{centroid.y():.2f}"
            ])

    print(f"✅ CSV 저장 완료: {output_csv}")

    # 총 면적
    total_area_pyeong = total_area_sqm * 0.3025
    print(f"\n📊 사업지 총 면적:")
    print(f"   {total_area_sqm:,.0f}㎡ ({total_area_pyeong:,.2f}평)")

except Exception as e:
    print(f"❌ CSV 저장 실패: {e}")

print("\n" + "=" * 70)
print("✅ 사업지 필지 목록 추출 완료!")
print(f"   CSV: {output_csv}")
print("\n다음 단계:")
print("   1. CSV 파일을 열어서 필지 목록 확인")
print("   2. 필요하면 레이어 생성 스크립트 별도 실행")
print("=" * 70)
