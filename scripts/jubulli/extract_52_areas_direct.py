#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF 파일 직접 파싱으로 52개 필지 면적 추출
"""

import csv
from pathlib import Path
from korea_cadastral import read_dbf, parse_shapefile_geometry, sqm_to_pyeong

# 52개 필지 목록
target_jibuns = [
    '821', '821-1',
    '822-2',
    '827-1', '827-3', '827-4', '827-5', '827-6',
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

print(f"검색 대상: {len(target_jibuns)}개 필지\n")

# Paths
base_path = Path('/mnt/c/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구')
dbf_path = base_path / 'LSMD_CONT_LDREG_41461_202510.dbf'
shp_path = base_path / 'LSMD_CONT_LDREG_41461_202510.shp'

# Read DBF
print("📖 DBF 파일 읽는 중...")
records_dict = read_dbf(str(dbf_path))
# Convert dict to list while preserving order
records = [records_dict[i] for i in sorted(records_dict.keys())]
print(f"✅ {len(records):,}개 레코드 로드\n")

# Read geometries
print("📐 Shapefile geometry 읽는 중...")
geometries = parse_shapefile_geometry(str(shp_path))
print(f"✅ {len(geometries):,}개 geometry 로드\n")

# Filter by correct PNU (41461360291)
target_pnu = '41461360291'
target_records = []
for idx, record in enumerate(records):
    pnu = str(record.get('PNU', ''))
    if pnu.startswith(target_pnu):
        record['_idx'] = idx
        record['_area_sqm'] = geometries.get(idx, 0)
        target_records.append(record)

print(f"✅ 대상 지역 필지: {len(target_records):,}개\n")

# Find target parcels
results = []
found_jibuns = set()

for record in target_records:
    jibun = record.get('JIBUN', '')

    # Clean jibun (remove land type suffix)
    jibun_clean = jibun
    for suffix in ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목']:
        if jibun.endswith(suffix):
            jibun_clean = jibun[:-1]
            break

    if jibun_clean in target_jibuns or jibun in target_jibuns:
        area_sqm = record['_area_sqm']
        area_pyeong = sqm_to_pyeong(area_sqm)

        results.append({
            'jibun': jibun,
            'pnu': record.get('PNU', ''),
            'area_sqm': area_sqm,
            'area_pyeong': area_pyeong
        })

        found_jibuns.add(jibun_clean if jibun_clean in target_jibuns else jibun)

# Sort by jibun
def sort_key(r):
    jibun = r['jibun']
    # Remove land type suffix
    for suffix in ['전', '답', '대', '임', '잡']:
        jibun = jibun.replace(suffix, '')

    parts = jibun.split('-')
    bonbun = int(parts[0])
    bubun = int(parts[1]) if len(parts) > 1 else 0
    return (bonbun, bubun)

results.sort(key=sort_key)

# Calculate totals
total_sqm = sum(r['area_sqm'] for r in results)
total_pyeong = sum(r['area_pyeong'] for r in results)

# Save CSV
output_csv = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/jubulli_52_parcels_area.csv'
with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['No.', '지번', 'PNU', '면적(㎡)', '면적(평)'])

    for idx, r in enumerate(results, 1):
        writer.writerow([
            idx,
            r['jibun'],
            r['pnu'],
            f"{r['area_sqm']:.2f}",
            f"{r['area_pyeong']:.2f}"
        ])

print(f"✅ CSV 저장: {output_csv}\n")

# Summary
print("=" * 60)
print("📊 52개 필지 면적 요약")
print("=" * 60)
print(f"검색 대상: {len(target_jibuns)}개 필지")
print(f"발견된 필지: {len(results)}개")
print(f"총 면적: {total_sqm:,.2f}㎡ ({total_pyeong:,.2f}평)")
print("=" * 60)

# Missing parcels
missing = set(target_jibuns) - found_jibuns
if missing:
    print(f"\n⚠️ 미발견 필지 ({len(missing)}개):")
    for jibun in sorted(missing):
        print(f"  - {jibun}")
    print()

# Display results
print("\n📋 필지별 면적 상세:")
print(f"{'No.':<4} {'지번':<15} {'면적(㎡)':>15} {'면적(평)':>15}")
print("-" * 55)
for idx, r in enumerate(results, 1):
    print(f"{idx:<4} {r['jibun']:<15} {r['area_sqm']:>15,.2f} {r['area_pyeong']:>15,.2f}")
print("-" * 55)
print(f"{'합계':<4} {'':<15} {total_sqm:>15,.2f} {total_pyeong:>15,.2f}")
