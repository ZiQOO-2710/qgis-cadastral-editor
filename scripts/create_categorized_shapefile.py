#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카테고리별로 분류된 shapefile 생성
"""

import struct
import shutil

def read_dbf(dbf_path, encoding='cp949'):
    """DBF 파일 읽기"""
    with open(dbf_path, 'rb') as f:
        # 헤더 읽기
        header = f.read(32)
        num_records = struct.unpack('<I', header[4:8])[0]
        header_length = struct.unpack('<H', header[8:10])[0]
        record_length = struct.unpack('<H', header[10:12])[0]

        # 필드 정보 읽기
        num_fields = (header_length - 33) // 32
        fields = []
        for i in range(num_fields):
            field_info = f.read(32)
            field_name = field_info[:11].rstrip(b'\x00').decode('ascii')
            field_type = chr(field_info[11])
            field_length = field_info[16]
            fields.append((field_name, field_type, field_length))

        f.read(1)  # 헤더 종료 바이트

        # 레코드 읽기
        records = []
        for i in range(num_records):
            record = f.read(record_length)
            if record[0:1] == b' ':  # 삭제되지 않은 레코드
                record_data = {}
                offset = 1
                for field_name, field_type, field_length in fields:
                    field_value = record[offset:offset+field_length]
                    try:
                        if field_type == 'C':
                            record_data[field_name] = field_value.decode(encoding).strip()
                        elif field_type == 'N':
                            record_data[field_name] = field_value.decode('ascii').strip()
                    except:
                        record_data[field_name] = ''
                    offset += field_length
                records.append(record_data)

        return fields, records

def read_shp(shp_path):
    """SHP 파일 읽기"""
    with open(shp_path, 'rb') as f:
        # 헤더 읽기 (100 bytes)
        header = f.read(100)

        # 지오메트리 읽기
        geometries = {}
        rec_idx = 0
        while True:
            record_header = f.read(8)
            if len(record_header) < 8:
                break

            record_number = struct.unpack('>I', record_header[0:4])[0]
            content_length = struct.unpack('>I', record_header[4:8])[0]
            content = f.read(content_length * 2)

            geometries[rec_idx] = (record_header, content)
            rec_idx += 1

        return header, geometries

def write_dbf(dbf_path, fields, records, encoding='cp949'):
    """DBF 파일 쓰기"""
    num_records = len(records)
    num_fields = len(fields)
    header_length = 32 + num_fields * 32 + 1
    record_length = 1 + sum(f[2] for f in fields)

    with open(dbf_path, 'wb') as f:
        # 헤더 작성
        header = bytearray(32)
        header[0] = 0x03  # DBF version
        header[4:8] = struct.pack('<I', num_records)
        header[8:10] = struct.pack('<H', header_length)
        header[10:12] = struct.pack('<H', record_length)
        f.write(header)

        # 필드 정보 작성
        for field_name, field_type, field_length in fields:
            field_info = bytearray(32)
            field_info[:len(field_name)] = field_name.encode('ascii')
            field_info[11] = ord(field_type)
            field_info[16] = field_length
            f.write(field_info)

        f.write(b'\r')  # 헤더 종료

        # 레코드 작성
        for record in records:
            f.write(b' ')  # 삭제 플래그
            for field_name, field_type, field_length in fields:
                value = record.get(field_name, '')
                if field_type == 'C':
                    f.write(value.encode(encoding, errors='ignore').ljust(field_length)[:field_length])
                elif field_type == 'N':
                    f.write(str(value).encode('ascii').rjust(field_length)[:field_length])

        f.write(b'\x1a')  # 파일 종료

def write_shp(shp_path, header, geometries):
    """SHP 파일 쓰기"""
    with open(shp_path, 'wb') as f:
        # Bounding Box 계산
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')

        for rec_idx in geometries.keys():
            record_header, content = geometries[rec_idx]
            if len(content) >= 36:
                box_xmin = struct.unpack('<d', content[4:12])[0]
                box_ymin = struct.unpack('<d', content[12:20])[0]
                box_xmax = struct.unpack('<d', content[20:28])[0]
                box_ymax = struct.unpack('<d', content[28:36])[0]
                xmin = min(xmin, box_xmin)
                ymin = min(ymin, box_ymin)
                xmax = max(xmax, box_xmax)
                ymax = max(ymax, box_ymax)

        # 헤더 업데이트
        new_header = bytearray(header)
        new_header[36:44] = struct.pack('<d', xmin)
        new_header[44:52] = struct.pack('<d', ymin)
        new_header[52:60] = struct.pack('<d', xmax)
        new_header[60:68] = struct.pack('<d', ymax)

        # 파일 길이 업데이트
        file_length = 50 + sum(4 + len(geometries[i][1])//2 for i in geometries.keys())
        new_header[24:28] = struct.pack('>I', file_length)

        f.write(new_header)

        # 지오메트리 작성
        for rec_idx in sorted(geometries.keys()):
            record_header, content = geometries[rec_idx]
            f.write(record_header)
            f.write(content)

# 원본 shapefile 읽기
input_shp = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/haengwonri_all.shp'
output_shp = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shp'

print("📖 원본 shapefile 읽는 중...")
shp_header, shp_geometries = read_shp(input_shp)
dbf_fields, dbf_records = read_dbf(input_shp.replace('.shp', '.dbf'))

# 지번 목록 읽기
with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/green_list.txt', 'r', encoding='utf-8') as f:
    green_list = [line.strip() for line in f]

with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/blue_list.txt', 'r', encoding='utf-8') as f:
    blue_list = [line.strip() for line in f]

with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/red_list.txt', 'r', encoding='utf-8') as f:
    red_list = [line.strip() for line in f]

# 카테고리 필드 추가
new_fields = dbf_fields + [('CATEGORY', 'C', 20)]

# 매칭되는 레코드 필터링 및 카테고리 추가
new_records = []
new_geometries = {}
new_idx = 0

for i, record in enumerate(dbf_records):
    jibun = record.get('A5', '').strip()

    if jibun in green_list:
        new_record = record.copy()
        new_record['CATEGORY'] = 'GREEN'
        new_records.append(new_record)
        new_geometries[new_idx] = shp_geometries[i]
        new_idx += 1
        print(f"🟢 {jibun}")
    elif jibun in blue_list:
        new_record = record.copy()
        new_record['CATEGORY'] = 'BLUE'
        new_records.append(new_record)
        new_geometries[new_idx] = shp_geometries[i]
        new_idx += 1
        print(f"🔵 {jibun}")
    elif jibun in red_list:
        new_record = record.copy()
        new_record['CATEGORY'] = 'RED'
        new_records.append(new_record)
        new_geometries[new_idx] = shp_geometries[i]
        new_idx += 1
        print(f"🔴 {jibun}")

print(f"\n📊 매칭 결과: {len(new_records)}개 필지")

# 새 shapefile 작성
print(f"\n💾 새 shapefile 저장 중: {output_shp}")
write_shp(output_shp, shp_header, new_geometries)
write_dbf(output_shp.replace('.shp', '.dbf'), new_fields, new_records)

# SHX, PRJ 파일 복사
shutil.copy(input_shp.replace('.shp', '.shx'), output_shp.replace('.shp', '.shx'))
shutil.copy(input_shp.replace('.shp', '.prj'), output_shp.replace('.shp', '.prj'))

print("✅ 완료!")
print(f"\n결과 파일: {output_shp}")
print(f"  - 🟢 초록색: {len([r for r in new_records if r['CATEGORY'] == 'GREEN'])}필지")
print(f"  - 🔵 파란색: {len([r for r in new_records if r['CATEGORY'] == 'BLUE'])}필지")
print(f"  - 🔴 빨간색: {len([r for r in new_records if r['CATEGORY'] == 'RED'])}필지")
