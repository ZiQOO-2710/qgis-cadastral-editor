#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아파트 단지 Shapefile에서 서초구 아파트만 추출하여 GeoJSON 생성
PyQGIS 없이 순수 Python으로 동작
"""

import zipfile
import struct
import json

def read_dbf_with_encoding(dbf_bytes, encoding='euc-kr'):
    """DBF 파일을 지정된 인코딩으로 직접 파싱"""
    # DBF 헤더 파싱
    header = struct.unpack('<BBBBIHH20x', dbf_bytes[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    print(f"   레코드 수: {num_records:,}개")
    print(f"   레코드 길이: {record_len} bytes")

    # 필드 정보 읽기
    fields = []
    pos = 32
    while dbf_bytes[pos] != 0x0D:
        field_info = struct.unpack('<11sc4xBB14x', dbf_bytes[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        fields.append((field_name, field_type, field_len))
        pos += 32

    print(f"   필드 수: {len(fields)}개")

    # 레코드 읽기 - Character 필드를 EUC-KR로 디코딩
    records = []
    data_start = header_len
    for i in range(num_records):
        record_start = data_start + i * record_len
        record = {}
        offset = 1  # 삭제 마커 건너뛰기

        for field_name, field_type, field_len in fields:
            value_bytes = dbf_bytes[record_start + offset:record_start + offset + field_len]

            if field_type == 'C':  # Character - 한글 필드
                try:
                    value = value_bytes.decode(encoding).strip()
                except:
                    value = value_bytes.decode('utf-8', errors='ignore').strip()
            elif field_type == 'N':  # Numeric
                value_str = value_bytes.decode('ascii').strip()
                if '.' in value_str:
                    try:
                        value = float(value_str)
                    except:
                        value = 0.0
                else:
                    try:
                        value = int(value_str)
                    except:
                        value = 0
            elif field_type == 'D':  # Date
                value = value_bytes.decode('ascii').strip()
            else:
                value = value_bytes.decode('ascii', errors='ignore').strip()

            record[field_name] = value
            offset += field_len

        records.append(record)

    return records

def read_shp_geometry(shp_bytes):
    """Shapefile 지오메트리 읽기 (Point 타입만 지원)"""
    # SHP 파일 헤더 (100 bytes)
    shape_type = struct.unpack('<i', shp_bytes[32:36])[0]
    print(f"   Shape Type: {shape_type}")

    if shape_type != 1:  # Point가 아니면 에러
        print(f"   경고: Point 타입이 아닙니다 (type={shape_type})")

    # 레코드 읽기
    geometries = []
    offset = 100

    while offset < len(shp_bytes):
        if offset + 8 > len(shp_bytes):
            break

        # 레코드 헤더
        content_len = struct.unpack('>i', shp_bytes[offset+4:offset+8])[0]
        offset += 8

        if content_len == 0:
            break

        # Shape 타입 (4 bytes)
        rec_shape_type = struct.unpack('<i', shp_bytes[offset:offset+4])[0]
        offset += 4

        if rec_shape_type == 1:  # Point
            x, y = struct.unpack('<2d', shp_bytes[offset:offset+16])
            geometries.append({'type': 'Point', 'coordinates': [x, y]})
            offset += 16
        else:
            # 다른 타입은 스킵
            offset += (content_len * 2 - 4)

    return geometries

def extract_seocho_apartments():
    """서초구 아파트 추출"""
    apt_zip = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'

    print("1️⃣  아파트 Shapefile 로드 중...")
    with zipfile.ZipFile(apt_zip, 'r') as z:
        # DBF 읽기
        print("   DBF 읽는 중...")
        dbf_bytes = z.read('apt_mst_info_202410.dbf')
        dbf_records = read_dbf_with_encoding(dbf_bytes, 'euc-kr')

        # SHP 읽기
        print("\n   SHP 읽는 중...")
        shp_bytes = z.read('apt_mst_info_202410.shp')
        geometries = read_shp_geometry(shp_bytes)

    print(f"\n   총 아파트 수: {len(dbf_records):,}개")
    print(f"   총 지오메트리 수: {len(geometries):,}개")

    # 서초구 필터링 (bjd_cd가 11650으로 시작)
    print("\n2️⃣  서초구 아파트 필터링 중...")
    seocho_features = []

    for i, (record, geom) in enumerate(zip(dbf_records, geometries)):
        bjd_cd = str(record.get('bjd_cd', ''))

        if bjd_cd.startswith('11650'):  # 서초구
            feature = {
                'type': 'Feature',
                'geometry': geom,
                'properties': {
                    'apt_nm': record.get('apt_nm', ''),
                    'rdnmadr': record.get('rdnmadr', ''),
                    'lnmadr': record.get('lnmadr', ''),
                    'dngct': record.get('dngct', 0),
                    'hshldco': record.get('hshldco', 0),
                    'bjd_cd': record.get('bjd_cd', ''),
                }
            }
            seocho_features.append(feature)

    print(f"   서초구 아파트: {len(seocho_features):,}개")

    # GeoJSON 생성
    print("\n3️⃣  GeoJSON 생성 중...")
    geojson = {
        'type': 'FeatureCollection',
        'features': seocho_features
    }

    # 저장
    output_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments.geojson'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"   저장 완료: {output_file}")

    # 샘플 출력
    print("\n샘플 아파트 (처음 5개):")
    for i, feature in enumerate(seocho_features[:5], 1):
        props = feature['properties']
        coords = feature['geometry']['coordinates']
        print(f"{i}. {props['apt_nm']}")
        print(f"   주소: {props['rdnmadr']}")
        print(f"   동수: {props['dngct']}, 세대수: {props['hshldco']}")
        print(f"   좌표: ({coords[0]:.6f}, {coords[1]:.6f})")

    return len(seocho_features)

if __name__ == "__main__":
    print("=" * 70)
    print("서초구 아파트 추출 (DBF 직접 파싱)")
    print("=" * 70)
    print()

    count = extract_seocho_apartments()

    print("\n" + "=" * 70)
    print(f"✅ 완료! 총 {count:,}개 아파트 추출")
    print("=" * 70)
