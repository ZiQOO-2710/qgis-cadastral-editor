#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selected_parcels.csv의 PNU 코드로 면적 추출
"""

import struct
import csv
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
    records = {}  # PNU를 키로 사용
    data_start = header_len
    for i in range(num_records):
        record_start = data_start + i * record_len
        record = {'_idx': i}
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

        pnu = record.get('PNU', '')
        if pnu:
            records[pnu] = record

    return records

def parse_shapefile_geometry(shp_path):
    """Shapefile geometry에서 면적 계산"""
    geometries = {}

    with open(shp_path, 'rb') as f:
        # Skip header (100 bytes)
        f.seek(100)

        record_num = 0
        while True:
            # Record header
            header_bytes = f.read(8)
            if len(header_bytes) < 8:
                break

            record_number, content_length = struct.unpack('>II', header_bytes)
            content_length *= 2

            # Shape type
            shape_type_bytes = f.read(4)
            if len(shape_type_bytes) < 4:
                break
            shape_type = struct.unpack('<I', shape_type_bytes)[0]

            if shape_type == 5:  # Polygon
                # Bounding box
                bbox = struct.unpack('<4d', f.read(32))

                # Number of parts and points
                num_parts, num_points = struct.unpack('<II', f.read(8))

                # Parts array
                parts = struct.unpack(f'<{num_parts}I', f.read(4 * num_parts))

                # Points array
                points = []
                for _ in range(num_points):
                    x, y = struct.unpack('<2d', f.read(16))
                    points.append((x, y))

                # Calculate area using shoelace formula
                area = 0
                for i in range(len(points) - 1):
                    area += points[i][0] * points[i+1][1]
                    area -= points[i+1][0] * points[i][1]
                area = abs(area) / 2.0

                geometries[record_num] = area
            else:
                # Skip unsupported shape types
                remaining = content_length - 4
                f.read(remaining)

            record_num += 1

    return geometries

# Read selected PNU codes from CSV
input_csv = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/selected_parcels.csv'
selected_pnus = []

print("📖 선택된 필지 CSV 읽는 중...")
with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pnu = row.get('PNU', '').strip().strip('"')
        jibun = row.get('JIBUN', '').strip().strip('"')
        if pnu:
            selected_pnus.append({'pnu': pnu, 'jibun': jibun})

print(f"✅ {len(selected_pnus)}개 필지 PNU 로드\n")

# Load shapefile
base_path = Path('/mnt/c/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구')
dbf_path = base_path / 'LSMD_CONT_LDREG_41461_202510.dbf'
shp_path = base_path / 'LSMD_CONT_LDREG_41461_202510.shp'

print("📖 DBF 파일 읽는 중...")
dbf_records = read_dbf(str(dbf_path))
print(f"✅ {len(dbf_records):,}개 레코드 로드\n")

print("📐 Shapefile geometry 읽는 중...")
geometries = parse_shapefile_geometry(str(shp_path))
print(f"✅ {len(geometries):,}개 geometry 로드\n")

# Match and extract areas
results = []
for item in selected_pnus:
    pnu = item['pnu']
    jibun_from_csv = item['jibun']

    if pnu in dbf_records:
        record = dbf_records[pnu]
        idx = record['_idx']
        area_sqm = geometries.get(idx, 0)
        area_pyeong = area_sqm * 0.3025

        jibun_from_dbf = record.get('JIBUN', '')

        results.append({
            'pnu': pnu,
            'jibun': jibun_from_dbf or jibun_from_csv,
            'area_sqm': area_sqm,
            'area_pyeong': area_pyeong
        })
    else:
        print(f"⚠️ PNU 미발견: {pnu} ({jibun_from_csv})")

# Sort by jibun
def sort_key(r):
    jibun = r['jibun']
    # Remove land type and spaces
    for suffix in ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목', '체', '묘', '장', '?']:
        jibun = jibun.replace(suffix, '')
    jibun = jibun.strip()

    parts = jibun.split('-')
    bonbun = int(parts[0]) if parts[0].isdigit() else 0
    bubun = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    return (bonbun, bubun)

results.sort(key=sort_key)

# Calculate totals
total_sqm = sum(r['area_sqm'] for r in results)
total_pyeong = sum(r['area_pyeong'] for r in results)

# Save CSV
output_csv = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/jubulli_52_parcels_area_final.csv'
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

    # Add total row
    writer.writerow(['', '합계', '', f"{total_sqm:.2f}", f"{total_pyeong:.2f}"])

print(f"✅ CSV 저장: {output_csv}\n")

# Summary
print("=" * 65)
print("📊 52개 필지 면적 요약")
print("=" * 65)
print(f"발견된 필지: {len(results)}개")
print(f"총 면적: {total_sqm:,.2f}㎡ ({total_pyeong:,.2f}평)")
print("=" * 65)

# Display results
print("\n📋 필지별 면적 상세:")
print(f"{'No.':<4} {'지번':<15} {'면적(㎡)':>15} {'면적(평)':>15}")
print("-" * 55)
for idx, r in enumerate(results, 1):
    print(f"{idx:<4} {r['jibun']:<15} {r['area_sqm']:>15,.2f} {r['area_pyeong']:>15,.2f}")
print("-" * 55)
print(f"{'합계':<4} {'':<15} {total_sqm:>15,.2f} {total_pyeong:>15,.2f}")
