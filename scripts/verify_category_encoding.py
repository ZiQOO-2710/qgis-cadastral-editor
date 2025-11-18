#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CATEGORY 필드 인코딩 검증
"""

import struct

def read_dbf_categories(dbf_path):
    """DBF 파일에서 CATEGORY 필드 값 읽기"""
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

        # CATEGORY 필드 찾기
        category_idx = None
        jibun_idx = None
        offset_map = {}
        current_offset = 1

        for i, (fname, ftype, flen) in enumerate(fields):
            offset_map[fname] = (current_offset, flen)
            if fname == 'CATEGORY':
                category_idx = i
            if fname == 'A5':
                jibun_idx = i
            current_offset += flen

        if category_idx is None:
            print("❌ CATEGORY 필드를 찾을 수 없습니다!")
            return

        print("=" * 60)
        print("📋 CATEGORY 필드 인코딩 검증")
        print("=" * 60)
        print(f"\n총 레코드: {num_records}")
        print(f"CATEGORY 필드 위치: {offset_map['CATEGORY']}")
        print(f"A5(지번) 필드 위치: {offset_map['A5']}")

        green_count = 0
        blue_count = 0
        red_count = 0
        other_count = 0

        print("\n🔍 각 레코드 검증:")
        for i in range(num_records):
            record = f.read(record_length)
            if record[0:1] == b' ':
                # CATEGORY 값 추출 (ASCII로 디코드)
                cat_offset, cat_len = offset_map['CATEGORY']
                category_bytes = record[cat_offset:cat_offset+cat_len]
                category = category_bytes.decode('ascii', errors='replace').strip()

                # 지번 추출 (cp949로 디코드)
                jibun_offset, jibun_len = offset_map['A5']
                jibun_bytes = record[jibun_offset:jibun_offset+jibun_len]
                jibun = jibun_bytes.decode('cp949', errors='replace').strip()

                # 카테고리별 카운트
                if category == 'GREEN':
                    green_count += 1
                    if green_count <= 3:  # 처음 3개만 출력
                        print(f"  🟢 {jibun}: '{category}' (bytes: {category_bytes.hex()})")
                elif category == 'BLUE':
                    blue_count += 1
                    if blue_count <= 3:
                        print(f"  🔵 {jibun}: '{category}' (bytes: {category_bytes.hex()})")
                elif category == 'RED':
                    red_count += 1
                    if red_count <= 3:
                        print(f"  🔴 {jibun}: '{category}' (bytes: {category_bytes.hex()})")
                else:
                    other_count += 1
                    print(f"  ⚠️ {jibun}: '{category}' (bytes: {category_bytes.hex()})")

        print("\n" + "=" * 60)
        print("📊 최종 집계:")
        print("=" * 60)
        print(f"🟢 GREEN (제주시추천+국공유지): {green_count}개")
        print(f"🔵 BLUE (일반 사유지): {blue_count}개")
        print(f"🔴 RED (기개발 사유지): {red_count}개")
        print(f"⚪ OTHER: {other_count}개")

        expected_green = 31
        expected_blue = 26
        expected_red = 8

        print("\n✅ 예상 개수:")
        print(f"   GREEN: {expected_green}개")
        print(f"   BLUE: {expected_blue}개")
        print(f"   RED: {expected_red}개")

        if green_count == expected_green and blue_count == expected_blue and red_count == expected_red:
            print("\n✅✅✅ 완벽합니다! 모든 CATEGORY 값이 정확합니다!")
        else:
            print("\n⚠️ 개수가 예상과 다릅니다!")

# 검증 실행
dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_final.dbf'
read_dbf_categories(dbf_path)
