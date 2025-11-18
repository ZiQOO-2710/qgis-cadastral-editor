#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새로운 CSV 파일에서 지번 추출 및 카테고리 분류
"""

import csv

# CSV 파일 읽기
csv_path = '/mnt/d/OneDrive/행원리 지적도.csv'

# 카테고리별 지번 저장
green_list = []  # 제주시추천 + 국공유지
blue_list = []   # 일반 사유지
red_list = []    # 기개발 사유지

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    lines = list(reader)

    for i, row in enumerate(lines):
        # 헤더와 빈 줄 건너뛰기
        if i < 4 or len(row) < 10:
            continue

        # "소 계" 행 건너뛰기
        if row[0] == '' or '소 계' in str(row[1]) or '총 합계' in str(row[0]):
            continue

        # 본번, 부번, 비고 추출
        try:
            bonbun = row[1].strip() if row[1] else ''
            bubun = row[2].strip() if row[2] else ''
            bigo = row[9].strip() if len(row) > 9 and row[9] else ''

            # 지번 생성
            if bonbun:
                if bubun:
                    jibun = f"{bonbun}-{bubun}"
                else:
                    jibun = bonbun

                # 카테고리 분류
                if '제주시 추천' in bigo or '국공유지' in bigo:
                    green_list.append(jibun)
                    print(f"🟢 초록색: {jibun} ({bigo})")
                elif '기개발' in bigo or (len(row) > 19 and '기개발' in str(row[19])):
                    red_list.append(jibun)
                    print(f"🔴 빨간색: {jibun} (기개발 사유지)")
                elif '사유지' in bigo:
                    blue_list.append(jibun)
                    print(f"🔵 파란색: {jibun} (일반 사유지)")
        except Exception as e:
            continue

# 기개발 사유지 오른쪽 테이블에서 추가 확인
for i, row in enumerate(lines):
    if i < 58 or len(row) < 20:
        continue

    try:
        bonbun = row[12].strip() if len(row) > 12 and row[12] else ''
        bubun = row[13].strip() if len(row) > 13 and row[13] else ''

        if bonbun:
            if bubun:
                jibun = f"{bonbun}-{bubun}"
            else:
                jibun = bonbun

            if jibun not in red_list:
                red_list.append(jibun)
                print(f"🔴 빨간색 추가: {jibun} (기개발 사유지 테이블)")
    except:
        continue

print("\n" + "="*60)
print("📊 분류 결과")
print("="*60)
print(f"🟢 초록색 (제주시추천+국공유지): {len(green_list)}필지")
print(f"🔵 파란색 (일반 사유지): {len(blue_list)}필지")
print(f"🔴 빨간색 (기개발 사유지): {len(red_list)}필지")
print(f"📝 전체: {len(green_list) + len(blue_list) + len(red_list)}필지")

# 지번 목록 파일로 저장
output_dir = '/mnt/c/Users/ksj27/PROJECTS/QGIS/input'

with open(f'{output_dir}/green_list.txt', 'w', encoding='utf-8') as f:
    for jibun in green_list:
        f.write(f"{jibun}\n")

with open(f'{output_dir}/blue_list.txt', 'w', encoding='utf-8') as f:
    for jibun in blue_list:
        f.write(f"{jibun}\n")

with open(f'{output_dir}/red_list.txt', 'w', encoding='utf-8') as f:
    for jibun in red_list:
        f.write(f"{jibun}\n")

with open(f'{output_dir}/all_jibun.txt', 'w', encoding='utf-8') as f:
    all_jibun = green_list + blue_list + red_list
    for jibun in all_jibun:
        f.write(f"{jibun}\n")

print("\n✅ 지번 목록 파일 저장 완료:")
print(f"  - {output_dir}/green_list.txt")
print(f"  - {output_dir}/blue_list.txt")
print(f"  - {output_dir}/red_list.txt")
print(f"  - {output_dir}/all_jibun.txt")
