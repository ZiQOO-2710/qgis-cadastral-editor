#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 20개 필지 필터링 및 CATEGORY 필드 추가
채권최고액 기준 분류:
- GREEN: 19.2-24억 (채무 부담 낮음)
- BLUE: 44.4-48억 (중간)
- RED: 52억 (채무 부담 높음)
"""

import struct
import shutil
from pathlib import Path

# 파일 경로 설정
indices_file = '/tmp/jubulli_indices.txt'
source_dir = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/원본_shapefile/용인시_처인구'
source_base = 'LSMD_CONT_LDREG_41461_202510'
output_dir = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output'
output_base = 'jubulli_categorized'

# 채권최고액 기준 카테고리 매핑
category_mapping = {
    '821': 'RED',       # 52억
    '822-2': 'RED',     # 52억
    '827-1': 'BLUE',    # 48억
    '827-3': 'BLUE',    # 44.4억
    '827-4': 'BLUE',    # 44.4억
    '828-1': 'GREEN',   # 24억
    '828-2': 'BLUE',    # 48억
    '828-3': 'BLUE',    # 48억
    '829': 'BLUE',      # 48억
    '830': 'BLUE',      # 48억
    '831': 'BLUE',      # 48억
    '832': 'GREEN',     # 24억
    '833-1': 'GREEN',   # 19.2억
    '833-2': 'GREEN',   # 24억
    '833-3': 'GREEN',   # 19.2억
    '833-4': 'GREEN',   # 19.2억
    '834-2': 'BLUE',    # 44.4억
    '834-4': 'BLUE',    # 48억
    '834-6': 'BLUE',    # 44.4억
    '834-7': 'BLUE',    # 48억
}

def extract_jibun_number(jibun_full):
    """Extract numeric part from JIBUN like '827-1전' -> '827-1'"""
    import re
    match = re.match(r'(\d+-?\d*)', jibun_full.strip())
    if match:
        return match.group(1)
    return None

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

def write_dbf_with_category(source_dbf_path, output_dbf_path, selected_indices, jibun_to_category):
    """CATEGORY 필드를 추가한 새 DBF 파일 생성"""
    with open(source_dbf_path, 'rb') as f:
        dbf_bytes = f.read()

    num_records, header_len, record_len, fields = read_dbf_header(dbf_bytes)

    # 새 필드 정의: CATEGORY (Character, 10 bytes)
    new_field = ('CATEGORY', 'C', 10, 0)
    new_fields = fields + [new_field]
    new_record_len = record_len + 10

    # 새 DBF 헤더 작성
    new_dbf = bytearray()

    # 헤더 레코드 (32 bytes)
    header_struct = struct.pack('<BBBBIHH20x',
        dbf_bytes[0],  # Version
        dbf_bytes[1],  # Last update year
        dbf_bytes[2],  # Last update month
        dbf_bytes[3],  # Last update day
        len(selected_indices),  # Number of records
        32 + len(new_fields) * 32 + 1,  # Header length
        new_record_len,  # Record length
    )
    new_dbf.extend(header_struct)

    # 필드 정보 (각 32 bytes)
    for field_name, field_type, field_len, field_decimal in new_fields:
        field_struct = struct.pack('<11sc4xBB14x',
            field_name.encode('ascii').ljust(11, b'\x00'),
            field_type.encode('ascii'),
            field_len,
            field_decimal
        )
        new_dbf.extend(field_struct)

    # Header terminator
    new_dbf.append(0x0D)

    # 레코드 데이터 복사 및 CATEGORY 추가
    for idx in selected_indices:
        record_start = header_len + idx * record_len
        original_record = dbf_bytes[record_start:record_start + record_len]

        # JIBUN 값 읽어서 카테고리 결정
        record_data = read_dbf_record(dbf_bytes, record_start, fields)
        jibun_num = extract_jibun_number(record_data.get('JIBUN', ''))
        category = jibun_to_category.get(jibun_num, 'UNKNOWN')

        # 원본 레코드 + CATEGORY 필드
        new_dbf.extend(original_record)
        new_dbf.extend(category.encode('ascii').ljust(10, b' '))

    # EOF marker
    new_dbf.append(0x1A)

    # 파일 저장
    with open(output_dbf_path, 'wb') as f:
        f.write(new_dbf)

    print(f"✅ DBF 파일 생성 완료: {output_dbf_path}")
    print(f"   - 레코드 수: {len(selected_indices)}")
    print(f"   - 필드 수: {len(new_fields)} (CATEGORY 추가됨)")

def filter_shp_by_indices(source_shp_path, output_shp_path, selected_indices):
    """SHP 파일에서 선택된 레코드만 추출"""
    with open(source_shp_path, 'rb') as f:
        shp_bytes = bytearray(f.read())

    # SHP 헤더 (100 bytes)
    header = shp_bytes[:100]

    # 새 SHP 파일 생성
    new_shp = bytearray(header)

    # 레코드 읽기 위치 추적
    pos = 100
    record_number = 0
    new_record_number = 1

    while pos < len(shp_bytes):
        # 레코드 헤더 (8 bytes)
        if pos + 8 > len(shp_bytes):
            break

        record_num_bytes = shp_bytes[pos:pos+4]
        content_len_bytes = shp_bytes[pos+4:pos+8]

        record_num = struct.unpack('>I', record_num_bytes)[0]
        content_len = struct.unpack('>I', content_len_bytes)[0]

        # 레코드 전체 길이 (헤더 8 bytes + 내용)
        total_len = 8 + content_len * 2

        if record_number in selected_indices:
            # 선택된 레코드 복사 (레코드 번호는 순차적으로 재지정)
            new_record_header = struct.pack('>I', new_record_number) + content_len_bytes
            new_shp.extend(new_record_header)
            new_shp.extend(shp_bytes[pos+8:pos+total_len])
            new_record_number += 1

        pos += total_len
        record_number += 1

    # 파일 길이 업데이트 (헤더의 24-27 바이트, big-endian, 16-bit words)
    file_length_words = len(new_shp) // 2
    new_shp[24:28] = struct.pack('>I', file_length_words)

    # 파일 저장
    with open(output_shp_path, 'wb') as f:
        f.write(new_shp)

    print(f"✅ SHP 파일 생성 완료: {output_shp_path}")
    print(f"   - 레코드 수: {len(selected_indices)}")

def main():
    # 출력 디렉토리 생성
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 선택된 레코드 인덱스 읽기
    with open(indices_file, 'r') as f:
        selected_indices = [int(line.strip()) for line in f if line.strip()]

    print(f"📋 선택된 레코드 인덱스 수: {len(selected_indices)}")

    # DBF 파일 처리
    source_dbf = f"{source_dir}/{source_base}.dbf"
    output_dbf = f"{output_dir}/{output_base}.dbf"
    write_dbf_with_category(source_dbf, output_dbf, selected_indices, category_mapping)

    # SHP 파일 처리
    source_shp = f"{source_dir}/{source_base}.shp"
    output_shp = f"{output_dir}/{output_base}.shp"
    filter_shp_by_indices(source_shp, output_shp, selected_indices)

    # SHX 파일 복사 후 인덱스 재생성
    source_shx = f"{source_dir}/{source_base}.shx"
    output_shx = f"{output_dir}/{output_base}.shx"

    # SHX는 레코드 오프셋 인덱스이므로 새로 생성해야 함
    # 단순 복사 대신 SHP에서 다시 계산
    with open(output_shp, 'rb') as f:
        shp_bytes = f.read()

    # SHX 생성
    shx = bytearray(shp_bytes[:100])  # 헤더 복사

    pos = 100
    while pos < len(shp_bytes):
        if pos + 8 > len(shp_bytes):
            break

        # 오프셋 (16-bit words 단위)
        offset_words = pos // 2

        # 레코드 길이
        content_len = struct.unpack('>I', shp_bytes[pos+4:pos+8])[0]

        # SHX 엔트리 추가 (오프셋 + 길이, 각 4 bytes, big-endian)
        shx.extend(struct.pack('>I', offset_words))
        shx.extend(struct.pack('>I', content_len))

        pos += 8 + content_len * 2

    # SHX 파일 길이 업데이트
    shx_length_words = len(shx) // 2
    shx[24:28] = struct.pack('>I', shx_length_words)

    with open(output_shx, 'wb') as f:
        f.write(shx)

    print(f"✅ SHX 파일 생성 완료: {output_shx}")

    # PRJ 파일 복사
    source_prj = f"{source_dir}/{source_base}.prj"
    output_prj = f"{output_dir}/{output_base}.prj"
    if Path(source_prj).exists():
        shutil.copy2(source_prj, output_prj)
        print(f"✅ PRJ 파일 복사 완료: {output_prj}")

    print("\n🎉 주북리 필터링 및 카테고리 분류 완료!")
    print(f"   - 출력 경로: {output_dir}/{output_base}.*")
    print(f"   - GREEN (19.2-24억): 6개 필지")
    print(f"   - BLUE (44.4-48억): 12개 필지")
    print(f"   - RED (52억): 2개 필지")

if __name__ == '__main__':
    main()
