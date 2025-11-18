#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 categorized shapefile 검증
"""

import struct

dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/jubulli_categorized.dbf'

def read_dbf_header(dbf_bytes):
    """DBF 헤더 파싱"""
    header = struct.unpack('<BBBBIHH20x', dbf_bytes[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    # 필드 정보 읽기
    fields = []
    pos = 32
    while dbf_bytes[pos] != 0x0D:
        field_info = struct.unpack('<11sc4xBB14x', dbf_bytes[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        field_decimal = field_info[3]
        fields.append((field_name, field_type, field_len, field_decimal))
        pos += 32

    return num_records, header_len, record_len, fields

def read_dbf_record(dbf_bytes, record_start, fields):
    """DBF 레코드 읽기"""
    record = {}
    offset = 1  # Skip deletion flag

    for field_name, field_type, field_len, field_decimal in fields:
        value_bytes = dbf_bytes[record_start + offset:record_start + offset + field_len]

        if field_type == 'C':  # Character
            value = value_bytes.decode('cp949', errors='ignore').strip()
        elif field_type == 'N':  # Numeric
            value = value_bytes.decode('ascii', errors='ignore').strip()
        elif field_type == 'D':  # Date
            value = value_bytes.decode('ascii', errors='ignore').strip()
        else:
            value = value_bytes.decode('cp949', errors='ignore').strip()

        record[field_name] = value
        offset += field_len

    return record

def extract_jibun_number(jibun_full):
    """Extract numeric part from JIBUN"""
    import re
    match = re.match(r'(\d+-?\d*)', jibun_full.strip())
    if match:
        return match.group(1)
    return None

with open(dbf_path, 'rb') as f:
    dbf_bytes = f.read()

num_records, header_len, record_len, fields = read_dbf_header(dbf_bytes)

print(f"📊 DBF 파일 정보:")
print(f"   - 레코드 수: {num_records}")
print(f"   - 필드 수: {len(fields)}")
print(f"   - 레코드 길이: {record_len} bytes\n")

print("📋 필드 구조:")
for field_name, field_type, field_len, field_decimal in fields:
    print(f"   - {field_name:12s} ({field_type}) {field_len:3d} bytes")

print("\n📝 카테고리별 필지 목록:\n")

category_counts = {'GREEN': [], 'BLUE': [], 'RED': []}

for i in range(num_records):
    record_start = header_len + i * record_len
    record = read_dbf_record(dbf_bytes, record_start, fields)

    jibun_num = extract_jibun_number(record.get('JIBUN', ''))
    category = record.get('CATEGORY', '').strip()

    if category in category_counts:
        category_counts[category].append(jibun_num)

# 출력
for category in ['GREEN', 'BLUE', 'RED']:
    parcels = category_counts[category]
    print(f"{category:6s} ({len(parcels):2d}개): {', '.join(sorted(parcels, key=lambda x: (int(x.split('-')[0]), int(x.split('-')[1]) if '-' in x else 0)))}")

print("\n✅ 검증 완료!")
