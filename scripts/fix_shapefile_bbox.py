#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shapefile 바운딩 박스 수정
"""

import struct

def fix_shapefile_bbox(shp_path):
    """SHP 파일의 바운딩 박스를 실제 지오메트리로부터 계산하여 수정"""

    print(f"📖 {shp_path} 읽는 중...")

    with open(shp_path, 'rb') as f:
        # 헤더 읽기
        header = bytearray(f.read(100))

        # 현재 바운딩 박스 확인
        old_xmin = struct.unpack('<d', header[36:44])[0]
        old_ymin = struct.unpack('<d', header[44:52])[0]
        old_xmax = struct.unpack('<d', header[52:60])[0]
        old_ymax = struct.unpack('<d', header[60:68])[0]

        print(f"현재 바운딩 박스:")
        print(f"  X: {old_xmin} ~ {old_xmax}")
        print(f"  Y: {old_ymin} ~ {old_ymax}")

        # 모든 레코드 읽어서 실제 바운딩 박스 계산
        xmin, ymin, xmax, ymax = float('inf'), float('inf'), float('-inf'), float('-inf')

        record_count = 0
        while True:
            record_header = f.read(8)
            if len(record_header) < 8:
                break

            content_length = struct.unpack('>I', record_header[4:8])[0]
            content = f.read(content_length * 2)

            if len(content) >= 36:
                # 각 레코드의 바운딩 박스 읽기
                box_xmin = struct.unpack('<d', content[4:12])[0]
                box_ymin = struct.unpack('<d', content[12:20])[0]
                box_xmax = struct.unpack('<d', content[20:28])[0]
                box_ymax = struct.unpack('<d', content[28:36])[0]

                xmin = min(xmin, box_xmin)
                ymin = min(ymin, box_ymin)
                xmax = max(xmax, box_xmax)
                ymax = max(ymax, box_ymax)

                record_count += 1

        print(f"\n계산된 바운딩 박스 ({record_count}개 레코드):")
        print(f"  X: {xmin} ~ {xmax}")
        print(f"  Y: {ymin} ~ {ymax}")

        # 바운딩 박스 업데이트
        header[36:44] = struct.pack('<d', xmin)
        header[44:52] = struct.pack('<d', ymin)
        header[52:60] = struct.pack('<d', xmax)
        header[60:68] = struct.pack('<d', ymax)

    # 파일 다시 쓰기
    print(f"\n💾 바운딩 박스 업데이트 중...")

    with open(shp_path, 'r+b') as f:
        f.seek(0)
        f.write(header)

    print("✅ 완료!")

    return xmin, ymin, xmax, ymax

# Shapefile 수정
shp_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_categorized.shp'
bbox = fix_shapefile_bbox(shp_path)

print(f"\n수정된 파일: {shp_path}")
print(f"새 바운딩 박스: ({bbox[0]:.2f}, {bbox[1]:.2f}) - ({bbox[2]:.2f}, {bbox[3]:.2f})")
