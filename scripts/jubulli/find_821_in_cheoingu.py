#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
처인구 전체에서 821번지 검색
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

# Search for 821 parcels in entire Cheoingu
print("🔍 처인구 전체에서 821번지 검색:")
found_821 = [r for r in records if r.get('JIBUN', '').startswith('821')]

if found_821:
    print(f"✅ 821번지 발견: {len(found_821)}개\n")

    # Group by PNU prefix (읍/면/동/리)
    pnu_groups = defaultdict(list)
    for r in found_821:
        pnu = r.get('PNU', '')
        pnu_prefix = pnu[:8] if len(pnu) >= 8 else pnu
        pnu_groups[pnu_prefix].append(r)

    print(f"{'PNU 코드':<12} {'필지수':>8} {'샘플 지번':<20}")
    print("-" * 50)
    for pnu_prefix in sorted(pnu_groups.keys()):
        parcels = pnu_groups[pnu_prefix]
        sample = parcels[0]
        print(f"{pnu_prefix:<12} {len(parcels):>8}개  {sample.get('JIBUN'):<20}")

    print("\n상세 목록 (최대 30개):")
    for idx, r in enumerate(found_821[:30], 1):
        print(f"{idx:3}. JIBUN: {r.get('JIBUN'):<15} PNU: {r.get('PNU')}")
else:
    print("❌ 처인구 전체에서 821번지를 찾을 수 없습니다.")

# Also search for 833
print("\n" + "=" * 60)
print("🔍 처인구 전체에서 833번지 검색:")
found_833 = [r for r in records if r.get('JIBUN', '').startswith('833')]

if found_833:
    print(f"✅ 833번지 발견: {len(found_833)}개\n")

    pnu_groups = defaultdict(list)
    for r in found_833:
        pnu = r.get('PNU', '')
        pnu_prefix = pnu[:8] if len(pnu) >= 8 else pnu
        pnu_groups[pnu_prefix].append(r)

    print(f"{'PNU 코드':<12} {'필지수':>8} {'샘플 지번':<20}")
    print("-" * 50)
    for pnu_prefix in sorted(pnu_groups.keys()):
        parcels = pnu_groups[pnu_prefix]
        sample = parcels[0]
        print(f"{pnu_prefix:<12} {len(parcels):>8}개  {sample.get('JIBUN'):<20}")

    print("\n상세 목록 (최대 30개):")
    for idx, r in enumerate(found_833[:30], 1):
        print(f"{idx:3}. JIBUN: {r.get('JIBUN'):<15} PNU: {r.get('PNU')}")
else:
    print("❌ 처인구 전체에서 833번지를 찾을 수 없습니다.")
