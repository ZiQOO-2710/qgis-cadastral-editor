"""
행원리 Shapefile에서 CSV 지번 목록에 해당하는 필지만 선택하여 새 파일 생성
Python 스크립트 (QGIS 불필요)

실행: python3 scripts/filter_by_csv.py
"""

import struct
import csv

def read_csv_jibun(csv_path):
    """CSV에서 지번 목록 읽기"""
    jibun_list = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)

        # 헤더 건너뛰기
        next(reader, None)

        for row in reader:
            if row and row[0].strip():
                jibun_list.append(row[0].strip())

    return jibun_list


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
        header = f.read(100)
        shape_type = struct.unpack('<i', header[32:36])[0]

        return shape_type


def filter_by_jibun(input_shp, input_dbf, jibun_list, jibun_field='A5'):
    """지번 목록으로 필터링"""

    print(f"\n🔍 CSV 지번 목록으로 필터링 중...")
    print(f"대상 지번: {len(jibun_list)}개")

    # DBF 구조 읽기
    num_records, header_length, record_length, fields = read_dbf_structure(input_dbf)

    # SHP 헤더
    shape_type = read_shp_header(input_shp)

    # 지번 세트
    jibun_set = set(jibun_list)

    # 매칭되는 레코드 찾기
    matched_indices = []
    matched_data = []
    matched_jibun = set()

    with open(input_dbf, 'rb') as f:
        f.seek(header_length)

        for rec_idx in range(num_records):
            record = f.read(record_length)

            if record[0:1] == b' ':
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

                # 지번 매칭
                jibun = record_dict.get(jibun_field, '').strip()

                if jibun in jibun_set:
                    matched_indices.append(rec_idx)
                    matched_data.append(record_dict)
                    matched_jibun.add(jibun)

                    print(f"  ✓ 매칭: 지번 {jibun} (#{len(matched_indices)})")

    print(f"\n📊 매칭 결과:")
    print(f"  매칭된 필지: {len(matched_indices)}개")
    print(f"  매칭된 고유 지번: {len(matched_jibun)}개")

    # 매칭되지 않은 지번
    unmatched = jibun_set - matched_jibun
    if unmatched:
        print(f"\n⚠️  매칭되지 않은 지번 ({len(unmatched)}개):")
        for jb in sorted(unmatched):
            print(f"  - {jb}")

    return matched_indices, matched_data, fields, shape_type


def read_shp_geometries(shp_path, indices):
    """SHP에서 특정 인덱스의 지오메트리 읽기"""

    print(f"\n📐 지오메트리 읽기 중...")

    geometries = {}

    with open(shp_path, 'rb') as f:
        f.seek(100)

        current_idx = 0
        indices_set = set(indices)

        while True:
            record_header = f.read(8)

            if len(record_header) < 8:
                break

            record_number = struct.unpack('>i', record_header[0:4])[0]
            content_length = struct.unpack('>i', record_header[4:8])[0]

            content = f.read(content_length * 2)

            if current_idx in indices_set:
                geometries[current_idx] = (record_header, content)

            current_idx += 1

            if len(geometries) >= len(indices):
                break

    print(f"✅ 지오메트리 읽기 완료: {len(geometries)}개")

    return geometries


def write_shapefile(output_base, data_records, geometries, fields, shape_type):
    """새 Shapefile 작성"""

    print(f"\n💾 Shapefile 생성 중: {output_base}")

    output_shp = output_base + '.shp'
    output_shx = output_base + '.shx'
    output_dbf = output_base + '.dbf'

    num_records = len(data_records)

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

    print(f"  Bounding Box: ({xmin:.2f}, {ymin:.2f}) - ({xmax:.2f}, {ymax:.2f})")

    # SHP 파일 작성
    with open(output_shp, 'wb') as f_shp, open(output_shx, 'wb') as f_shx:
        shp_header = bytearray(100)
        f_shp.write(shp_header)

        shx_header = bytearray(100)
        f_shx.write(shx_header)

        file_length = 50

        for idx, (rec_idx, record_data) in enumerate(zip(sorted(geometries.keys()), data_records)):
            record_header, content = geometries[rec_idx]

            offset = f_shp.tell() // 2
            f_shp.write(record_header)
            f_shp.write(content)

            content_length = len(content) // 2
            f_shx.write(struct.pack('>i', offset))
            f_shx.write(struct.pack('>i', content_length))

            file_length += 4 + content_length

        # 헤더 업데이트
        f_shp.seek(0)
        shp_header[0:4] = struct.pack('>i', 9994)
        shp_header[24:28] = struct.pack('>i', file_length)
        shp_header[28:32] = struct.pack('<i', 1000)
        shp_header[32:36] = struct.pack('<i', shape_type)
        shp_header[36:44] = struct.pack('<d', xmin)
        shp_header[44:52] = struct.pack('<d', ymin)
        shp_header[52:60] = struct.pack('<d', xmax)
        shp_header[60:68] = struct.pack('<d', ymax)
        f_shp.write(shp_header)

        f_shx.seek(0)
        shx_header[0:4] = struct.pack('>i', 9994)
        shx_header[24:28] = struct.pack('>i', 50 + num_records * 4)
        shx_header[28:32] = struct.pack('<i', 1000)
        shx_header[32:36] = struct.pack('<i', shape_type)
        shx_header[36:44] = struct.pack('<d', xmin)
        shx_header[44:52] = struct.pack('<d', ymin)
        shx_header[52:60] = struct.pack('<d', xmax)
        shx_header[60:68] = struct.pack('<d', ymax)
        f_shx.write(shx_header)

    # DBF 파일 작성
    with open(output_dbf, 'wb') as f:
        header_length = 32 + len(fields) * 32 + 1
        record_length = 1 + sum(field['length'] for field in fields)

        dbf_header = bytearray(32)
        dbf_header[0] = 0x03
        dbf_header[4:8] = struct.pack('<I', num_records)
        dbf_header[8:10] = struct.pack('<H', header_length)
        dbf_header[10:12] = struct.pack('<H', record_length)

        f.write(dbf_header)

        for field in fields:
            field_desc = bytearray(32)

            field_name_bytes = field['name'].encode('cp949')[:11]
            field_desc[0:len(field_name_bytes)] = field_name_bytes
            field_desc[11] = ord(field['type'])
            field_desc[16] = field['length']
            field_desc[17] = field.get('decimal', 0)

            f.write(field_desc)

        f.write(b'\r')

        for record_data in data_records:
            f.write(b' ')

            for field in fields:
                value = record_data.get(field['name'], '')

                if field['type'] == 'C':
                    value_bytes = value.encode('cp949', errors='ignore')[:field['length']]
                else:
                    value_bytes = value.encode('ascii', errors='ignore')[:field['length']]

                padded = value_bytes + b' ' * (field['length'] - len(value_bytes))
                f.write(padded)

        f.write(b'\x1A')

    print(f"✅ Shapefile 생성 완료: {num_records}개 레코드")


def main():
    """메인 실행"""

    print("="*70)
    print("🗺️  CSV 지번 필터링 스크립트")
    print("="*70)

    # 경로
    csv_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/input/행원리 지번.csv'
    input_shp = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/haengwonri_all.shp'
    input_dbf = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/haengwonri_all.dbf'
    output_base = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected'

    # 1. CSV 읽기
    print("\n📂 CSV 지번 목록 읽기...")
    jibun_list = read_csv_jibun(csv_path)
    print(f"✅ 읽기 완료: {len(jibun_list)}개 지번")
    print(f"샘플: {jibun_list[:10]}")

    # 2. 필터링
    indices, data_records, fields, shape_type = filter_by_jibun(
        input_shp, input_dbf, jibun_list, jibun_field='A5'
    )

    if not indices:
        print("\n❌ 매칭된 필지가 없습니다!")
        return

    # 3. 지오메트리 읽기
    geometries = read_shp_geometries(input_shp, indices)

    # 4. 새 Shapefile 작성
    write_shapefile(output_base, data_records, geometries, fields, shape_type)

    # 5. PRJ 파일 복사
    input_prj = input_shp.replace('.shp', '.prj')
    output_prj = output_base + '.prj'

    try:
        with open(input_prj, 'r') as f_in:
            prj_content = f_in.read()

        with open(output_prj, 'w') as f_out:
            f_out.write(prj_content)

        print(f"✅ .prj 파일 복사 완료")
    except Exception as e:
        print(f"⚠️  .prj 파일 복사 실패: {e}")

    print("\n" + "="*70)
    print("✅ 모든 작업 완료!")
    print("="*70)
    print(f"\n📂 결과 파일:")
    print(f"  {output_base}.shp")
    print(f"  {output_base}.shx")
    print(f"  {output_base}.dbf")
    print(f"  {output_base}.prj")
    print(f"\n💡 QGIS에서 '{output_base}.shp' 파일을 열어보세요!")
    print(f"   Windows 경로: C:\\Users\\ksj27\\PROJECTS\\QGIS\\output\\haengwonri_selected.shp")


if __name__ == '__main__':
    main()
