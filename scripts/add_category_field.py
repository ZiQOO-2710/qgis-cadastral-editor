#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 shapefile에 CATEGORY 필드 추가
"""

import struct
import shutil

# 지번 목록 읽기
with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/green_list.txt', 'r', encoding='utf-8') as f:
    green_list = set(line.strip() for line in f if line.strip())

with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/blue_list.txt', 'r', encoding='utf-8') as f:
    blue_list = set(line.strip() for line in f if line.strip())

with open('/mnt/c/Users/ksj27/PROJECTS/QGIS/input/red_list.txt', 'r', encoding='utf-8') as f:
    red_list = set(line.strip() for line in f if line.strip())

def read_dbf(dbf_path, encoding='cp949'):
    """DBF 파일 읽기"""
    with open(dbf_path, 'rb') as f:
        header = f.read(32)
        num_records = struct.unpack('<I', header[4:8])[0]
        header_length = struct.unpack('<H', header[8:10])[0]
        record_length = struct.unpack('<H', header[10:12])[0]

        num_fields = (header_length - 33) // 32
        fields = []
        for i in range(num_fields):
            field_info = f.read(32)
            field_name = field_info[:11].rstrip(b'\x00').decode('ascii')
            field_type = chr(field_info[11])
            field_length = field_info[16]
            fields.append((field_name, field_type, field_length))

        f.read(1)

        records = []
        for i in range(num_records):
            record = f.read(record_length)
            if record[0:1] == b' ':
                record_data = {}
                offset = 1
                for field_name, field_type, field_length in fields:
                    field_value = record[offset:offset+field_length]
                    try:
                        if field_type == 'C':
                            record_data[field_name] = field_value.decode(encoding).strip()
                        elif field_type == 'N':
                            record_data[field_name] = field_value.decode('ascii').strip()
                        elif field_type == 'D':
                            record_data[field_name] = field_value.decode('ascii').strip()
                    except:
                        record_data[field_name] = ''
                    offset += field_length
                records.append(record_data)

        return fields, records

def write_dbf(dbf_path, fields, records, encoding='cp949'):
    """DBF 파일 쓰기"""
    num_records = len(records)
    num_fields = len(fields)
    header_length = 32 + num_fields * 32 + 1
    record_length = 1 + sum(f[2] for f in fields)

    print(f"[DEBUG] write_dbf 시작:")
    print(f"  - 필드 수: {num_fields}")
    print(f"  - 레코드 수: {num_records}")
    print(f"  - 레코드 길이: {record_length}")

    with open(dbf_path, 'wb') as f:
        header = bytearray(32)
        header[0] = 0x03
        header[4:8] = struct.pack('<I', num_records)
        header[8:10] = struct.pack('<H', header_length)
        header[10:12] = struct.pack('<H', record_length)
        f.write(header)

        for field_name, field_type, field_length in fields:
            field_info = bytearray(32)
            field_info[:len(field_name)] = field_name.encode('ascii')
            field_info[11] = ord(field_type)
            field_info[16] = field_length
            f.write(field_info)

        f.write(b'\r')

        record_count = 0
        for record in records:
            f.write(b' ')
            for field_name, field_type, field_length in fields:
                value = record.get(field_name, '')
                if field_type == 'C':
                    # CATEGORY 필드는 ASCII, 나머지는 cp949
                    if field_name == 'CATEGORY':
                        if record_count < 3:
                            print(f"[DEBUG] 레코드 {record_count+1} CATEGORY: '{value}'")
                        encoded = value.encode('ascii', errors='ignore')
                        f.write(encoded + b' ' * (field_length - len(encoded)))
                    else:
                        encoded = value.encode(encoding, errors='ignore')
                        f.write(encoded + b' ' * (field_length - len(encoded)))
                elif field_type == 'N':
                    encoded = str(value).encode('ascii')
                    f.write(b' ' * (field_length - len(encoded)) + encoded)
                elif field_type == 'D':
                    # 날짜 필드 (YYYYMMDD 형식)
                    encoded = str(value).encode('ascii', errors='ignore')
                    f.write(encoded + b' ' * (field_length - len(encoded)))
            record_count += 1

        f.write(b'\x1a')

# 원본 파일 읽기
input_dbf = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.dbf'
output_dbf = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.dbf'

print("📖 DBF 파일 읽는 중...")
fields, records = read_dbf(input_dbf)
print(f"✅ 읽은 필드 개수: {len(fields)}")
print(f"✅ 읽은 레코드 개수: {len(records)}")

# CATEGORY 필드 추가
new_fields = fields + [('CATEGORY', 'C', 10)]

# 각 레코드에 카테고리 추가
new_records = []
for record in records:
    jibun = record.get('A5', '').strip()
    new_record = record.copy()

    if jibun in green_list:
        new_record['CATEGORY'] = 'GREEN'
        print(f"🟢 {jibun}")
    elif jibun in blue_list:
        new_record['CATEGORY'] = 'BLUE'
        print(f"🔵 {jibun}")
    elif jibun in red_list:
        new_record['CATEGORY'] = 'RED'
        print(f"🔴 {jibun}")
    else:
        new_record['CATEGORY'] = 'OTHER'
        print(f"⚪ {jibun}")

    new_records.append(new_record)

print(f"\n💾 새 DBF 파일 저장 중...")
print(f"📊 저장할 필드: {len(new_fields)}개")
print(f"📊 저장할 레코드: {len(new_records)}개")

# 처음 3개 레코드의 CATEGORY 확인
print("\n처음 3개 레코드 CATEGORY 확인:")
for i, rec in enumerate(new_records[:3]):
    print(f"  {i+1}. {rec.get('A5', '')} -> {rec.get('CATEGORY', 'MISSING')}")

write_dbf(output_dbf, new_fields, new_records)

# SHP, SHX, PRJ 파일 복사
shutil.copy('/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.shp',
            '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shp')
shutil.copy('/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.shx',
            '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shx')
shutil.copy('/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.prj',
            '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.prj')

print("✅ 완료!")
print(f"\n파일: /mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shp")
print(f"  - 🟢 초록: {sum(1 for r in new_records if r['CATEGORY'] == 'GREEN')}개")
print(f"  - 🔵 파랑: {sum(1 for r in new_records if r['CATEGORY'] == 'BLUE')}개")
print(f"  - 🔴 빨강: {sum(1 for r in new_records if r['CATEGORY'] == 'RED')}개")
