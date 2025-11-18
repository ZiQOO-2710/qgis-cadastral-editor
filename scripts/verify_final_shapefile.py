#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 shapefile 검증
"""

import struct

def read_shp_header(shp_path):
    """SHP 헤더 읽기"""
    with open(shp_path, 'rb') as f:
        header = f.read(100)
        xmin = struct.unpack('<d', header[36:44])[0]
        ymin = struct.unpack('<d', header[44:52])[0]
        xmax = struct.unpack('<d', header[52:60])[0]
        ymax = struct.unpack('<d', header[60:68])[0]
        return xmin, ymin, xmax, ymax

def read_dbf_simple(dbf_path):
    """DBF 레코드 개수와 필드 확인"""
    with open(dbf_path, 'rb') as f:
        header = f.read(32)
        num_records = struct.unpack('<I', header[4:8])[0]
        header_length = struct.unpack('<H', header[8:10])[0]

        num_fields = (header_length - 33) // 32
        fields = []
        for i in range(num_fields):
            field_info = f.read(32)
            field_name = field_info[:11].rstrip(b'\x00').decode('ascii')
            fields.append(field_name)

        return num_records, fields

# 검증
shp_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_final.shp'
dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_final.dbf'

print("="*60)
print("📋 최종 Shapefile 검증")
print("="*60)

# SHP 확인
print("\n1. SHP 파일:")
xmin, ymin, xmax, ymax = read_shp_header(shp_path)
print(f"   바운딩 박스: ({xmin:.2f}, {ymin:.2f}) - ({xmax:.2f}, {ymax:.2f})")

if xmin == 0 and xmax == 0:
    print("   ❌ 바운딩 박스가 (0,0)입니다!")
else:
    print("   ✅ 바운딩 박스 정상")

# DBF 확인
print("\n2. DBF 파일:")
num_records, fields = read_dbf_simple(dbf_path)
print(f"   레코드 개수: {num_records}")
print(f"   필드 목록: {', '.join(fields)}")

if 'CATEGORY' in fields:
    print("   ✅ CATEGORY 필드 존재")
else:
    print("   ❌ CATEGORY 필드 없음!")

if num_records == 65:
    print("   ✅ 레코드 개수 정상 (65개)")
else:
    print(f"   ❌ 레코드 개수 오류 (예상: 65, 실제: {num_records})")

print("\n" + "="*60)
print("검증 완료!")
print("="*60)
