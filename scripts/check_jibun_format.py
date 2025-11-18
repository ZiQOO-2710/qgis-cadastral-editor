#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 필지의 실제 JIBUN 형식 확인
"""

import struct
from pathlib import Path

def read_dbf(dbf_path, encoding='cp949'):
    """DBF 파일 파싱"""
    with open(dbf_path, 'rb') as f:
        dbf_data = f.read()

    # Header
    header = struct.unpack('<BBBBIHH20x', dbf_data[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    # Field descriptors
    fields = []
    pos = 32
    while dbf_data[pos] != 0x0D:
        field_info = struct.unpack('<11sc4xBB14x', dbf_data[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        fields.append((field_name, field_type, field_len))
        pos += 32

    # Records
    records = []
    data_start = header_len
    for i in range(num_records):
        record_start = data_start + i * record_len
        record = {}
        offset = 1  # Skip deletion marker

        for field_name, field_type, field_len in fields:
            value_bytes = dbf_data[record_start + offset:record_start + offset + field_len]

            if field_type == 'C':  # Character
                try:
                    value = value_bytes.decode(encoding).strip()
                except:
                    value = value_bytes.decode('utf-8', errors='ignore').strip()
            elif field_type == 'N':  # Numeric
                value = value_bytes.decode('ascii').strip()
            elif field_type == 'D':  # Date
                value = value_bytes.decode('ascii', errors='ignore').strip()
            else:
                value = value_bytes.decode('ascii', errors='ignore').strip()

            record[field_name] = value
            offset += field_len

        records.append(record)

    return fields, records

# Paths
dbf_path = Path('/mnt/c/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41461_202510.dbf')

# Read DBF
print("📖 DBF 파일 읽는 중...")
fields, records = read_dbf(str(dbf_path))
print(f"✅ {len(records):,}개 레코드 로드\n")

# Filter Jubulli
jubulli_pnu = '41461101001'
jubulli_records = [r for r in records if str(r.get('PNU', '')).startswith(jubulli_pnu)]
print(f"✅ 주북리 필지: {len(jubulli_records):,}개\n")

# Sample first 30 Jubulli parcels to see format
print("📋 주북리 필지 샘플 (첫 30개):")
for idx, r in enumerate(jubulli_records[:30], 1):
    jibun = r.get('JIBUN', '')
    pnu = r.get('PNU', '')
    print(f"{idx:3}. JIBUN: '{jibun}' | PNU: {pnu}")

# Check for any 8xx parcels
print("\n📋 8로 시작하는 본번 검색:")
sample_8xx = [r for r in jubulli_records if r.get('JIBUN', '').startswith('8')]
print(f"발견: {len(sample_8xx)}개")
for r in sample_8xx[:20]:
    print(f"  JIBUN: '{r.get('JIBUN')}' | PNU: {r.get('PNU')}")
