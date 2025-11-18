#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
무릉리 필지 데이터 검증 스크립트
CSV 토지조서(119개) vs 출력 결과(890개) 비교
"""

import csv
from collections import defaultdict
from pathlib import Path

# 지목 접미사 목록
LAND_USE_SUFFIXES = ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목', '광', '염', '장', '창', '주', '사', '묘', '체', '양', '공', '수', '학']

def clean_jibun(jibun: str) -> str:
    """지번에서 지목 접미사 제거"""
    for suffix in LAND_USE_SUFFIXES:
        if jibun.endswith(suffix):
            return jibun[:-len(suffix)]
    return jibun

def main():
    project_root = Path(__file__).parent
    csv_path = '/mnt/c/Users/ksj27/PROJECTS/autooffice/서귀포시 대정읍 무릉리 토지조서.csv'
    output_csv = project_root / 'output/muneung_areas.csv'

    print("=" * 80)
    print("📊 무릉리 필지 데이터 검증")
    print("=" * 80)

    # 1. CSV 토지조서의 119개 지번 읽기
    print("\n1️⃣ CSV 토지조서 분석...")
    csv_jibuns = set()
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bon = row.get('본번', '').strip()
            bu = row.get('부번', '').strip()
            if bon:
                jibun = f"{bon}-{bu}" if bu else bon
                csv_jibuns.add(jibun)

    print(f"   📋 입력 CSV: {len(csv_jibuns)}개 지번")

    # 2. 출력 CSV의 890개 필지 읽기
    print("\n2️⃣ 출력 결과 분석...")
    output_records = []
    jibun_to_parcels = defaultdict(list)  # 지번별 필지 목록

    with open(output_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jibun_raw = row['jibun']
            jibun_clean = clean_jibun(jibun_raw)

            output_records.append({
                'jibun_raw': jibun_raw,
                'jibun_clean': jibun_clean,
                'pnu': row['pnu'],
                'category': row['category'],
                'area_sqm': float(row['area_sqm']),
                'area_pyeong': float(row['area_pyeong'])
            })

            jibun_to_parcels[jibun_clean].append(jibun_raw)

    print(f"   📦 출력 결과: {len(output_records)}개 필지")
    print(f"   🏷️  고유 지번: {len(jibun_to_parcels)}개")

    # 3. 비교 분석
    print("\n3️⃣ 비교 분석...")

    output_jibuns = set(jibun_to_parcels.keys())
    matched_jibuns = csv_jibuns & output_jibuns
    missing_jibuns = csv_jibuns - output_jibuns
    extra_jibuns = output_jibuns - csv_jibuns

    print(f"\n   ✅ 매칭된 지번: {len(matched_jibuns)}개 / {len(csv_jibuns)}개 ({len(matched_jibuns)/len(csv_jibuns)*100:.1f}%)")

    if missing_jibuns:
        print(f"\n   ❌ 누락된 지번: {len(missing_jibuns)}개")
        print(f"      {sorted(missing_jibuns)[:10]}")
        if len(missing_jibuns) > 10:
            print(f"      ... 외 {len(missing_jibuns)-10}개")
    else:
        print(f"\n   ✅ 누락된 지번: 없음")

    if extra_jibuns:
        print(f"\n   ⚠️  추가 지번: {len(extra_jibuns)}개 (CSV에 없는 지번)")
        print(f"      {sorted(extra_jibuns)[:10]}")
        if len(extra_jibuns) > 10:
            print(f"      ... 외 {len(extra_jibuns)-10}개")

    # 4. 지목 중복 분석
    print("\n4️⃣ 지목 중복 분석...")

    duplicate_counts = defaultdict(int)
    for jibun, parcels in jibun_to_parcels.items():
        count = len(parcels)
        duplicate_counts[count] += 1

    print(f"\n   📊 지번당 필지 개수 분포:")
    for count in sorted(duplicate_counts.keys()):
        num_jibuns = duplicate_counts[count]
        print(f"      {count}개 필지: {num_jibuns}개 지번")

    # 지목이 많은 상위 10개 지번
    print(f"\n   🔝 지목이 많은 지번 (TOP 10):")
    sorted_jibuns = sorted(jibun_to_parcels.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for jibun, parcels in sorted_jibuns:
        print(f"      {jibun}: {len(parcels)}개 - {', '.join(parcels)}")

    # 5. 총 면적 계산
    print("\n5️⃣ 면적 통계...")
    total_area_sqm = sum(r['area_sqm'] for r in output_records)
    total_area_pyeong = sum(r['area_pyeong'] for r in output_records)

    print(f"   📏 총 면적: {total_area_sqm:,.2f}㎡ ({total_area_pyeong:,.2f}평)")

    # 6. 문제점 및 개선 방안
    print("\n" + "=" * 80)
    print("📋 검증 결과 요약")
    print("=" * 80)

    issues = []
    improvements = []

    if missing_jibuns:
        issues.append(f"❌ {len(missing_jibuns)}개 지번이 shapefile에서 누락됨")
        improvements.append("- shapefile에 해당 지번이 존재하는지 수동 확인 필요")
        improvements.append("- PNU 필터링 로직 재검토")

    if extra_jibuns:
        issues.append(f"⚠️  {len(extra_jibuns)}개의 CSV에 없는 지번이 출력에 포함됨")
        improvements.append("- 지번 매칭 로직의 오차 범위 검토")
        improvements.append("- 유사 지번 필터링 강화")

    avg_duplicates = len(output_records) / len(output_jibuns) if output_jibuns else 0
    if avg_duplicates > 5:
        issues.append(f"⚠️  지번당 평균 {avg_duplicates:.1f}개 필지 (지목 중복 많음)")
        improvements.append("- 단일 지번만 표시하고 지목은 속성으로 통합하는 옵션 고려")

    if not issues:
        print("\n✅ 문제 없음: 모든 지번이 정상적으로 처리됨")
    else:
        print("\n🔍 발견된 문제:")
        for issue in issues:
            print(f"   {issue}")

        print("\n💡 개선 방안:")
        for improvement in improvements:
            print(f"   {improvement}")

    print("\n" + "=" * 80)

    # 7. 상세 결과 CSV 저장
    detail_csv = project_root / 'output/muneung_validation_detail.csv'
    with open(detail_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['지번', '입력CSV', '출력결과', '필지수', '필지목록'])

        all_jibuns = sorted(csv_jibuns | output_jibuns)
        for jibun in all_jibuns:
            in_csv = '✓' if jibun in csv_jibuns else '✗'
            in_output = '✓' if jibun in output_jibuns else '✗'
            parcel_count = len(jibun_to_parcels[jibun]) if jibun in jibun_to_parcels else 0
            parcel_list = ', '.join(jibun_to_parcels[jibun]) if jibun in jibun_to_parcels else ''

            writer.writerow([jibun, in_csv, in_output, parcel_count, parcel_list])

    print(f"\n📄 상세 결과 저장: {detail_csv}")
    print("=" * 80)

if __name__ == '__main__':
    main()
