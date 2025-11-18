#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHX 파일 재생성
"""

import struct

def rebuild_shx(shp_path):
    """SHP 파일로부터 SHX 인덱스 파일 재생성"""

    shx_path = shp_path.replace('.shp', '.shx')

    print(f"📖 {shp_path} 읽는 중...")

    # SHP 파일 읽어서 각 레코드의 오프셋 수집
    offsets = []

    with open(shp_path, 'rb') as f:
        # 헤더 건너뛰기
        header = f.read(100)

        current_offset = 50  # 헤더는 50 워드 (100 바이트)

        while True:
            record_header = f.read(8)
            if len(record_header) < 8:
                break

            record_number = struct.unpack('>I', record_header[0:4])[0]
            content_length = struct.unpack('>I', record_header[4:8])[0]

            offsets.append((current_offset, content_length))

            # 레코드 내용 건너뛰기
            f.read(content_length * 2)

            # 다음 레코드 오프셋 (헤더 4워드 + 내용)
            current_offset += 4 + content_length

    print(f"📊 레코드 개수: {len(offsets)}")

    # SHX 파일 생성
    print(f"💾 {shx_path} 생성 중...")

    with open(shx_path, 'wb') as f:
        # SHP 헤더 복사
        f.write(header)

        # 각 레코드의 오프셋과 길이 작성
        for offset, length in offsets:
            f.write(struct.pack('>I', offset))
            f.write(struct.pack('>I', length))

    print("✅ SHX 파일 재생성 완료!")
    return len(offsets)

# SHX 재생성
shp_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shp'
count = rebuild_shx(shp_path)

print(f"\n✅ 완료: {count}개 레코드")
