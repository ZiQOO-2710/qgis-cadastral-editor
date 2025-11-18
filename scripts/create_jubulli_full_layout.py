#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 지적도 전체 프로세스 자동화
1. 스타일 적용 (GREEN/BLUE/RED)
2. 통계 계산 및 CSV 저장
3. 조판 레이아웃 생성
4. PNG 내보내기
"""

import sys
import os

# 스크립트 디렉토리
script_dir = 'C:/Users/ksj27/PROJECTS/QGIS/scripts'

print("=" * 80)
print("주북리 사업지 지적도 생성 프로세스 시작")
print("=" * 80)

# Step 1: 스타일 적용
print("\n[1/3] 스타일 적용 중...")
print("-" * 80)
exec(open(f'{script_dir}/apply_jubulli_style.py', encoding='utf-8').read())

# Step 2: 통계 계산
print("\n[2/3] 통계 계산 중...")
print("-" * 80)
exec(open(f'{script_dir}/calculate_jubulli_statistics.py', encoding='utf-8').read())

# Step 3: 조판 레이아웃 생성 및 PNG 내보내기
print("\n[3/3] 조판 레이아웃 생성 및 PNG 내보내기 중...")
print("-" * 80)
exec(open(f'{script_dir}/create_jubulli_layout.py', encoding='utf-8').read())

print("\n" + "=" * 80)
print("🎉 전체 프로세스 완료!")
print("=" * 80)
print("\n출력 파일:")
print(f"  - Shapefile: C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_categorized.*")
print(f"  - 통계 CSV: C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_statistics.csv")
print(f"  - 지도 PNG: C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_map.png")
print("\nQGIS 조판 보기:")
print(f"  프로젝트(P) → 조판 관리자(N)... → '주북리_사업지_지도' → 보기(S)")
