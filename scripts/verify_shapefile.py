"""
Shapefile 검증 스크립트
"""

import struct

def verify_shp_file(shp_path):
    """SHP 파일 검증"""

    print(f"🔍 SHP 파일 검증: {shp_path}\n")

    try:
        with open(shp_path, 'rb') as f:
            # 헤더 읽기
            header = f.read(100)

            file_code = struct.unpack('>i', header[0:4])[0]
            file_length = struct.unpack('>i', header[24:28])[0]  # in words
            version = struct.unpack('<i', header[28:32])[0]
            shape_type = struct.unpack('<i', header[32:36])[0]

            xmin = struct.unpack('<d', header[36:44])[0]
            ymin = struct.unpack('<d', header[44:52])[0]
            xmax = struct.unpack('<d', header[52:60])[0]
            ymax = struct.unpack('<d', header[60:68])[0]

            print("📋 SHP 헤더 정보:")
            print(f"  File Code: {file_code} (should be 9994)")
            print(f"  File Length: {file_length} words ({file_length * 2} bytes)")
            print(f"  Version: {version}")
            print(f"  Shape Type: {shape_type} (5 = Polygon)")
            print(f"  Bounding Box:")
            print(f"    X: {xmin:.6f} ~ {xmax:.6f}")
            print(f"    Y: {ymin:.6f} ~ {ymax:.6f}")

            # 레코드 읽기
            print("\n📊 레코드 정보:")
            record_count = 0
            total_points = 0

            while True:
                record_header = f.read(8)

                if len(record_header) < 8:
                    break

                record_number = struct.unpack('>i', record_header[0:4])[0]
                content_length = struct.unpack('>i', record_header[4:8])[0]  # in words

                content = f.read(content_length * 2)

                if len(content) < 4:
                    break

                shape_type_rec = struct.unpack('<i', content[0:4])[0]

                record_count += 1

                # 첫 5개만 상세 출력
                if record_count <= 5:
                    print(f"\n  레코드 #{record_number}:")
                    print(f"    Content Length: {content_length} words ({content_length * 2} bytes)")
                    print(f"    Shape Type: {shape_type_rec}")

                    if shape_type_rec == 5 and len(content) >= 44:  # Polygon
                        box_xmin = struct.unpack('<d', content[4:12])[0]
                        box_ymin = struct.unpack('<d', content[12:20])[0]
                        box_xmax = struct.unpack('<d', content[20:28])[0]
                        box_ymax = struct.unpack('<d', content[28:36])[0]
                        num_parts = struct.unpack('<i', content[36:40])[0]
                        num_points = struct.unpack('<i', content[40:44])[0]

                        print(f"    Box: ({box_xmin:.2f}, {box_ymin:.2f}) - ({box_xmax:.2f}, {box_ymax:.2f})")
                        print(f"    Parts: {num_parts}, Points: {num_points}")

                        total_points += num_points

            print(f"\n✅ 총 {record_count}개 레코드")
            print(f"✅ 총 {total_points}개 포인트")

            if record_count == 0:
                print("\n❌ 경고: 레코드가 없습니다!")
            elif total_points == 0:
                print("\n❌ 경고: 지오메트리 포인트가 없습니다!")

            return record_count > 0 and total_points > 0

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_dbf_file(dbf_path):
    """DBF 파일 검증"""

    print(f"\n\n🔍 DBF 파일 검증: {dbf_path}\n")

    try:
        with open(dbf_path, 'rb') as f:
            # 헤더
            dbf_header = f.read(32)

            version = dbf_header[0]
            num_records = struct.unpack('<I', dbf_header[4:8])[0]
            header_length = struct.unpack('<H', dbf_header[8:10])[0]
            record_length = struct.unpack('<H', dbf_header[10:12])[0]

            num_fields = (header_length - 33) // 32

            print("📋 DBF 헤더 정보:")
            print(f"  Version: {version}")
            print(f"  레코드 수: {num_records}")
            print(f"  헤더 길이: {header_length}")
            print(f"  레코드 길이: {record_length}")
            print(f"  필드 수: {num_fields}")

            # 필드 읽기
            fields = []
            for i in range(num_fields):
                field_desc = f.read(32)

                field_name = field_desc[0:11].decode('cp949', errors='ignore').rstrip('\x00')
                field_type = chr(field_desc[11])
                field_length = field_desc[16]

                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'length': field_length
                })

            print(f"\n필드 목록:")
            for field in fields[:10]:  # 처음 10개만
                print(f"  - {field['name']:15s} ({field['type']}, {field['length']})")

            # 샘플 레코드
            f.seek(header_length)

            print(f"\n샘플 레코드 (처음 3개):")

            for i in range(min(3, num_records)):
                record = f.read(record_length)

                if record[0:1] == b' ':
                    pos = 1

                    print(f"\n  레코드 {i+1}:")

                    for field in fields:
                        field_data = record[pos:pos + field['length']]

                        try:
                            if field['type'] == 'C':
                                value = field_data.decode('cp949', errors='ignore').strip()
                            else:
                                value = field_data.decode('ascii', errors='ignore').strip()

                            if value and field['name'] in ['A2', 'A5', 'A6']:  # 주요 필드만
                                print(f"    {field['name']:10s}: {value}")

                        except:
                            pass

                        pos += field['length']

            return num_records > 0

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    shp_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.shp'
    dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/haengwonri_selected.dbf'

    print("="*70)
    print("🗺️  Shapefile 검증 도구")
    print("="*70)

    shp_valid = verify_shp_file(shp_path)
    dbf_valid = verify_dbf_file(dbf_path)

    print("\n" + "="*70)
    if shp_valid and dbf_valid:
        print("✅ Shapefile이 유효합니다!")
    else:
        print("❌ Shapefile에 문제가 있습니다!")
    print("="*70)
