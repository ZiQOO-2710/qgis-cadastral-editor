#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
용인시 처인구 양지면 주북리 매매목록 시각화 준비 스크립트

사용 방법:
1. 공간정보 오픈플랫폼(http://data.nsdi.go.kr)에서 용인시 처인구 양지면 지적도 다운로드
2. 다운로드한 shapefile을 data/yongin_yangji/ 폴더에 저장
3. 이 스크립트를 실행하여 매매목록 필터링 및 카테고리 추가
4. QGIS에서 apply_yongin_style.py 실행하여 시각화
"""

import os
import struct
import shutil
from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(r'C:\Users\ksj27\PROJECTS\QGIS')
INPUT_DIR = PROJECT_ROOT / 'input'
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_DIR = PROJECT_ROOT / 'output'

# 용인시 데이터 경로
YONGIN_DATA_DIR = DATA_DIR / 'yongin_yangji'
YONGIN_OUTPUT = OUTPUT_DIR / 'yongin_sales'

# 매매목록 파일
SALES_LIST_FILE = INPUT_DIR / 'yongin_sales_list.txt'


def read_sales_list():
    """매매목록 지번 읽기"""
    with open(SALES_LIST_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def check_data_availability():
    """용인시 지적도 데이터 존재 확인"""
    if not YONGIN_DATA_DIR.exists():
        print("❌ 용인시 지적도 데이터가 없습니다!")
        print("\n📥 데이터 다운로드 방법:")
        print("1. 공간정보 오픈플랫폼 접속: http://data.nsdi.go.kr")
        print("2. 회원가입 및 로그인 (무료)")
        print("3. 검색: '연속지적도' 또는 '용인시 처인구'")
        print("4. 용인시 처인구 양지면 지적도 신청 및 다운로드")
        print("5. 다운로드한 shapefile을 다음 경로에 저장:")
        print(f"   {YONGIN_DATA_DIR}")
        print("\n좌표계: EPSG:5186 (Korea 2000 / Central Belt)")
        return False

    # .shp 파일 찾기
    shp_files = list(YONGIN_DATA_DIR.glob('*.shp'))
    if not shp_files:
        print(f"❌ {YONGIN_DATA_DIR}에 shapefile이 없습니다!")
        return False

    print(f"✅ 지적도 데이터 발견: {shp_files[0].name}")
    return True


def add_sales_category_field(input_shp):
    """
    매매목록 지번에 SALES 카테고리 추가

    CATEGORY 필드:
    - SALES: 매매목록에 포함된 필지
    - OTHER: 그 외 필지
    """
    sales_list = read_sales_list()
    print(f"매매목록 지번 수: {len(sales_list)}")

    # 파일 경로 설정
    dbf_path = input_shp.with_suffix('.dbf')
    output_shp = YONGIN_OUTPUT / input_shp.name
    output_dbf = output_shp.with_suffix('.dbf')

    # 출력 디렉토리 생성
    YONGIN_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Shapefile 복사 (.shp, .shx, .prj)
    for ext in ['.shp', '.shx', '.prj']:
        src = input_shp.with_suffix(ext)
        dst = output_shp.with_suffix(ext)
        if src.exists():
            shutil.copy2(src, dst)
            print(f"복사됨: {src.name}")

    # DBF 파일 처리
    with open(dbf_path, 'rb') as f:
        dbf_data = f.read()

    # DBF 헤더 파싱
    header = struct.unpack('<BBBBIHH20x', dbf_data[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    print(f"\nDBF 정보:")
    print(f"- 레코드 수: {num_records}")
    print(f"- 헤더 길이: {header_len}")
    print(f"- 레코드 길이: {record_len}")

    # 필드 정보 읽기
    fields = []
    pos = 32
    while dbf_data[pos] != 0x0D:
        field_info = struct.unpack('<11sc4xBB14x', dbf_data[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        fields.append((field_name, field_type, field_len))
        pos += 32

    print(f"\n기존 필드: {len(fields)}개")
    for fname, ftype, flen in fields:
        print(f"  {fname} ({ftype}, {flen})")

    # CATEGORY 필드 찾기 또는 추가
    category_exists = any(fname == 'CATEGORY' for fname, _, _ in fields)

    if not category_exists:
        # CATEGORY 필드 추가
        new_field = ('CATEGORY', 'C', 10)
        fields.append(new_field)
        new_record_len = record_len + 10

        # 새 헤더 생성
        new_header_data = bytearray(dbf_data[:32])
        struct.pack_into('<H', new_header_data, 8, header_len + 32)  # 헤더 길이 증가
        struct.pack_into('<H', new_header_data, 10, new_record_len)  # 레코드 길이 증가

        # 필드 정보 추가
        category_field = struct.pack('<11sc4xBB14x',
                                     b'CATEGORY\x00\x00\x00',
                                     b'C',
                                     10,
                                     0)

        # 새 DBF 파일 생성
        with open(output_dbf, 'wb') as f:
            # 헤더 쓰기
            f.write(new_header_data)

            # 기존 필드 정보 쓰기
            f.write(dbf_data[32:pos])

            # CATEGORY 필드 정보 쓰기
            f.write(category_field)

            # 헤더 종료 마커
            f.write(b'\x0D')

            # 레코드 데이터 처리
            data_start = header_len
            for i in range(num_records):
                record_start = data_start + i * record_len
                record_data = dbf_data[record_start:record_start + record_len]

                # 지번 필드 찾기 (PNU, JIBUN 등)
                offset = 1  # 삭제 마커 건너뛰기
                jibun = None

                for fname, ftype, flen in fields[:-1]:  # CATEGORY 제외
                    value_bytes = record_data[offset:offset + flen]

                    if fname in ['JIBUN', 'PNU', 'A2']:
                        if ftype == 'C':
                            jibun = value_bytes.decode('cp949', errors='ignore').strip()

                    offset += flen

                # CATEGORY 값 결정
                category = 'OTHER'
                if jibun:
                    # 지번 매칭 (예: "833-2" 또는 "주북리 833-2")
                    jibun_number = jibun.split()[-1] if ' ' in jibun else jibun
                    if jibun_number in sales_list:
                        category = 'SALES'

                # 새 레코드 쓰기
                f.write(record_data)
                f.write(category.ljust(10).encode('ascii'))

            # EOF 마커
            f.write(b'\x1A')

        print(f"\n✅ CATEGORY 필드 추가 완료")
        print(f"출력: {output_shp}")

    else:
        print("\n⚠️  CATEGORY 필드가 이미 존재합니다.")


def main():
    print("=" * 60)
    print("용인시 주북리 매매목록 시각화 준비")
    print("=" * 60)

    # 데이터 확인
    if not check_data_availability():
        return

    # Shapefile 찾기
    shp_files = list(YONGIN_DATA_DIR.glob('*.shp'))
    input_shp = shp_files[0]

    # CATEGORY 필드 추가
    add_sales_category_field(input_shp)

    print("\n" + "=" * 60)
    print("다음 단계:")
    print("1. QGIS 열기")
    print("2. Python 콘솔에서 다음 실행:")
    print("   exec(open('C:/Users/ksj27/PROJECTS/QGIS/scripts/apply_yongin_style.py', encoding='utf-8').read())")
    print("=" * 60)


if __name__ == '__main__':
    main()
