#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
양지면의 모든 리 코드 찾기
"""

import struct
from pathlib import Path
from collections import defaultdict

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
        offset = 1

        for field_name, field_type, field_len in fields:
            value_bytes = dbf_data[record_start + offset:record_start + offset + field_len]

            if field_type == 'C':
                try:
                    value = value_bytes.decode(encoding).strip()
                except:
                    value = value_bytes.decode('utf-8', errors='ignore').strip()
            else:
                value = value_bytes.decode('ascii', errors='ignore').strip()

            record[field_name] = value
            offset += field_len

        records.append(record)

    return records

# Paths
dbf_path = Path('/mnt/c/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41461_202510.dbf')

# Read DBF
print("📖 DBF 파일 읽는 중...")
records = read_dbf(str(dbf_path))
print(f"✅ {len(records):,}개 레코드 로드\n")

# Find all Yangji-myeon (101) PNU codes
yangji_pnu_prefix = '41461101'
yangji_records = [r for r in records if str(r.get('PNU', '')).startswith(yangji_pnu_prefix)]
print(f"✅ 양지면 필지: {len(yangji_records):,}개\n")

# Group by 리 code (3 digits after myeon code)
ri_codes = defaultdict(list)
for r in yangji_records:
    pnu = r.get('PNU', '')
    if len(pnu) >= 11:
        ri_code = pnu[5:8]  # Extract 리 code
        ri_codes[ri_code].append(r)

print("📋 양지면 리 코드 목록:")
print(f"{'리코드':<10} {'필지수':>10} {'샘플 지번':<30}")
print("-" * 55)
for ri_code in sorted(ri_codes.keys()):
    parcels = ri_codes[ri_code]
    sample_jibun = parcels[0].get('JIBUN', '') if parcels else ''
    sample_pnu = parcels[0].get('PNU', '') if parcels else ''
    print(f"{ri_code:<10} {len(parcels):>10,}개  {sample_jibun:<15} (PNU: {sample_pnu})")

# Search for 821 parcels in all ri codes
print("\n" + "=" * 60)
print("🔍 821번지 검색 (모든 리 코드)")
print("=" * 60)
found_821 = []
for ri_code, parcels in ri_codes.items():
    for p in parcels:
        jibun = p.get('JIBUN', '')
        if jibun.startswith('821'):
            found_821.append((ri_code, p))

if found_821:
    print(f"✅ 821번지 발견: {len(found_821)}개")
    for ri_code, p in found_821[:20]:
        print(f"  리코드: {ri_code} | JIBUN: {p.get('JIBUN')} | PNU: {p.get('PNU')}")
else:
    print("❌ 821번지를 찾을 수 없습니다.")

# Search for 833 parcels
print("\n🔍 833번지 검색:")
found_833 = []
for ri_code, parcels in ri_codes.items():
    for p in parcels:
        jibun = p.get('JIBUN', '')
        if jibun.startswith('833'):
            found_833.append((ri_code, p))

if found_833:
    print(f"✅ 833번지 발견: {len(found_833)}개")
    for ri_code, p in found_833[:20]:
        print(f"  리코드: {ri_code} | JIBUN: {p.get('JIBUN')} | PNU: {p.get('PNU')}")
else:
    print("❌ 833번지를 찾을 수 없습니다.")
