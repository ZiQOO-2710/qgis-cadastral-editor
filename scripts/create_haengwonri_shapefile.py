"""
행원리 필지만 추출하여 새 Shapefile 생성
Python + shapefile 라이브러리 사용

실행: python3 scripts/create_haengwonri_shapefile.py
"""

import struct
import os

def read_dbf_structure(dbf_path):
    """DBF 구조 읽기"""
    with open(dbf_path, 'rb') as f:
        # 헤더
        dbf_header = f.read(32)

        num_records = struct.unpack('<I', dbf_header[4:8])[0]
        header_length = struct.unpack('<H', dbf_header[8:10])[0]
        record_length = struct.unpack('<H', dbf_header[10:12])[0]

        # 필드 정보
        num_fields = (header_length - 33) // 32

        fields = []
        for i in range(num_fields):
            field_desc = f.read(32)

            field_name = field_desc[0:11].decode('cp949', errors='ignore').rstrip('\x00')
            field_type = chr(field_desc[11])
            field_length = field_desc[16]
            field_decimal = field_desc[17]

            fields.append({
                'name': field_name,
                'type': field_type,
                'length': field_length,
                'decimal': field_decimal
            })

        return num_records, header_length, record_length, fields


def read_shp_header(shp_path):
    """SHP 헤더 읽기"""
    with open(shp_path, 'rb') as f:
        # 파일 헤더 (100 bytes)
        header = f.read(100)

        # Shape Type (byte 32-35, little endian)
        shape_type = struct.unpack('<i', header[32:36])[0]

        # Bounding Box
        xmin = struct.unpack('<d', header[36:44])[0]
        ymin = struct.unpack('<d', header[44:52])[0]
        xmax = struct.unpack('<d', header[52:60])[0]
        ymax = struct.unpack('<d', header[60:68])[0]

        return shape_type, (xmin, ymin, xmax, ymax)


def extract_haengwonri_data(input_shp, input_dbf, location_keyword='행원리'):
    """행원리 데이터 추출"""

    print(f"🔍 '{location_keyword}' 데이터 추출 중...\n")

    # DBF 구조 읽기
    num_records, header_length, record_length, fields = read_dbf_structure(input_dbf)

    print(f"총 레코드: {num_records:,}개")
    print(f"필드 수: {len(fields)}개")

    # SHP 헤더 읽기
    shape_type, bbox = read_shp_header(input_shp)

    print(f"Shape 타입: {shape_type}")
    print(f"Bounding Box: {bbox}\n")

    # 행원리 레코드 인덱스 찾기
    print("행원리 레코드 검색 중...")

    haengwonri_indices = []
    haengwonri_data = []

    with open(input_dbf, 'rb') as f:
        f.seek(header_length)

        for rec_idx in range(num_records):
            record = f.read(record_length)

            if record[0:1] == b' ':  # 삭제되지 않은 레코드
                pos = 1

                record_dict = {}
                for field in fields:
                    field_data = record[pos:pos + field['length']]

                    try:
                        if field['type'] == 'C':
                            value = field_data.decode('cp949', errors='ignore').strip()
                        else:
                            value = field_data.decode('ascii', errors='ignore').strip()

                        record_dict[field['name']] = value
                    except:
                        record_dict[field['name']] = ''

                    pos += field['length']

                # A2 필드에 '행원리'가 있으면 저장
                if location_keyword in record_dict.get('A2', ''):
                    haengwonri_indices.append(rec_idx)
                    haengwonri_data.append(record_dict)

            # 진행 상황
            if (rec_idx + 1) % 100000 == 0:
                print(f"  진행: {rec_idx + 1:,} / {num_records:,} ({(rec_idx+1)/num_records*100:.1f}%) - 발견: {len(haengwonri_indices):,}개")

    print(f"\n✅ 추출 완료: {len(haengwonri_indices):,}개 레코드")

    return haengwonri_indices, haengwonri_data, fields, shape_type


def read_shp_geometries(shp_path, indices):
    """SHP에서 특정 인덱스의 지오메트리 읽기"""

    print(f"\n📐 지오메트리 읽기 중...")

    geometries = {}

    with open(shp_path, 'rb') as f:
        # 헤더 건너뛰기
        f.seek(100)

        current_idx = 0
        indices_set = set(indices)

        while True:
            # Record Header (8 bytes)
            record_header = f.read(8)

            if len(record_header) < 8:
                break

            record_number = struct.unpack('>i', record_header[0:4])[0]
            content_length = struct.unpack('>i', record_header[4:8])[0]

            # Content (2 * content_length bytes)
            content = f.read(content_length * 2)

            # 필요한 레코드만 저장
            if current_idx in indices_set:
                geometries[current_idx] = (record_header, content)

                if len(geometries) % 100 == 0:
                    print(f"  읽은 지오메트리: {len(geometries):,}개")

            current_idx += 1

            if len(geometries) >= len(indices):
                break

    print(f"✅ 지오메트리 읽기 완료: {len(geometries):,}개")

    return geometries


def write_shapefile(output_base, data_records, geometries, fields, shape_type):
    """새 Shapefile 작성"""

    print(f"\n💾 Shapefile 생성 중: {output_base}")

    output_shp = output_base + '.shp'
    output_shx = output_base + '.shx'
    output_dbf = output_base + '.dbf'

    num_records = len(data_records)

    # 1. SHP 파일 작성
    print("  .shp 파일 작성 중...")

    with open(output_shp, 'wb') as f_shp, open(output_shx, 'wb') as f_shx:
        # SHP 헤더 (나중에 업데이트)
        shp_header = bytearray(100)
        f_shp.write(shp_header)

        # SHX 헤더 (나중에 업데이트)
        shx_header = bytearray(100)
        f_shx.write(shx_header)

        # 레코드 작성
        file_length = 50  # 헤더 길이 (words)

        for idx, (rec_idx, record_data) in enumerate(zip(sorted(geometries.keys()), data_records)):
            record_header, content = geometries[rec_idx]

            # SHP에 레코드 작성
            offset = f_shp.tell() // 2  # offset in words
            f_shp.write(record_header)
            f_shp.write(content)

            # SHX에 인덱스 작성
            content_length = len(content) // 2
            f_shx.write(struct.pack('>i', offset))
            f_shx.write(struct.pack('>i', content_length))

            file_length += 4 + content_length  # 헤더(4) + 내용

        # SHP 헤더 업데이트
        f_shp.seek(0)
        shp_header[0:4] = struct.pack('>i', 9994)  # File Code
        shp_header[24:28] = struct.pack('>i', file_length)  # File Length
        shp_header[28:32] = struct.pack('<i', 1000)  # Version
        shp_header[32:36] = struct.pack('<i', shape_type)  # Shape Type
        f_shp.write(shp_header)

        # SHX 헤더 업데이트
        f_shx.seek(0)
        shx_header[0:4] = struct.pack('>i', 9994)
        shx_header[24:28] = struct.pack('>i', 50 + num_records * 4)
        shx_header[28:32] = struct.pack('<i', 1000)
        shx_header[32:36] = struct.pack('<i', shape_type)
        f_shx.write(shx_header)

    print(f"  ✅ .shp, .shx 작성 완료")

    # 2. DBF 파일 작성
    print("  .dbf 파일 작성 중...")

    with open(output_dbf, 'wb') as f:
        # DBF 헤더
        header_length = 32 + len(fields) * 32 + 1
        record_length = 1 + sum(field['length'] for field in fields)

        dbf_header = bytearray(32)
        dbf_header[0] = 0x03  # Version
        dbf_header[4:8] = struct.pack('<I', num_records)
        dbf_header[8:10] = struct.pack('<H', header_length)
        dbf_header[10:12] = struct.pack('<H', record_length)

        f.write(dbf_header)

        # 필드 디스크립터
        for field in fields:
            field_desc = bytearray(32)

            field_name_bytes = field['name'].encode('cp949')[:11]
            field_desc[0:len(field_name_bytes)] = field_name_bytes
            field_desc[11] = ord(field['type'])
            field_desc[16] = field['length']
            field_desc[17] = field.get('decimal', 0)

            f.write(field_desc)

        # 헤더 종료 마커
        f.write(b'\r')

        # 레코드 작성
        for record_data in data_records:
            # 삭제 마커
            f.write(b' ')

            # 각 필드 값
            for field in fields:
                value = record_data.get(field['name'], '')

                if field['type'] == 'C':
                    value_bytes = value.encode('cp949', errors='ignore')[:field['length']]
                else:
                    value_bytes = value.encode('ascii', errors='ignore')[:field['length']]

                # 패딩
                padded = value_bytes + b' ' * (field['length'] - len(value_bytes))
                f.write(padded)

        # 파일 종료 마커
        f.write(b'\x1A')

    print(f"  ✅ .dbf 작성 완료")

    print(f"\n✅ Shapefile 생성 완료: {num_records:,}개 레코드")


def main():
    """메인 실행"""

    print("="*70)
    print("🗺️  행원리 Shapefile 추출기")
    print("="*70)
    print()

    # 경로
    input_shp = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.shp'
    input_dbf = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.dbf'
    output_base = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/haengwonri_all'

    # 1. 행원리 데이터 추출
    indices, data_records, fields, shape_type = extract_haengwonri_data(input_shp, input_dbf, '행원리')

    if not indices:
        print("❌ 행원리 데이터를 찾을 수 없습니다!")
        return

    # 2. 지오메트리 읽기
    geometries = read_shp_geometries(input_shp, indices)

    # 3. 새 Shapefile 작성
    write_shapefile(output_base, data_records, geometries, fields, shape_type)

    # 4. PRJ 파일 복사
    input_prj = input_shp.replace('.shp', '.prj')
    output_prj = output_base + '.prj'

    try:
        with open(input_prj, 'r') as f_in:
            prj_content = f_in.read()

        with open(output_prj, 'w') as f_out:
            f_out.write(prj_content)

        print(f"  ✅ .prj 파일 복사 완료")
    except Exception as e:
        print(f"  ⚠️  .prj 파일 복사 실패: {e}")

    print("\n" + "="*70)
    print("✅ 모든 작업 완료!")
    print("="*70)
    print(f"\n📂 결과 파일:")
    print(f"  {output_base}.shp")
    print(f"  {output_base}.shx")
    print(f"  {output_base}.dbf")
    print(f"  {output_base}.prj")
    print(f"\n💡 QGIS에서 '{output_base}.shp' 파일을 열어보세요!")


if __name__ == '__main__':
    main()
