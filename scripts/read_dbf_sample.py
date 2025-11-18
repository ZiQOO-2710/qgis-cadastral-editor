"""
DBF 샘플 데이터 읽기
"""

import struct

def read_dbf_sample(dbf_path, num_samples=10):
    """DBF 파일의 샘플 데이터 읽기"""

    try:
        with open(dbf_path, 'rb') as f:
            # 헤더 읽기
            dbf_header = f.read(32)

            num_records = struct.unpack('<I', dbf_header[4:8])[0]
            header_length = struct.unpack('<H', dbf_header[8:10])[0]
            record_length = struct.unpack('<H', dbf_header[10:12])[0]

            # 필드 정보 읽기
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

            # 헤더 종료 마커로 이동
            f.seek(header_length)

            print("="*100)
            print(f"📄 샘플 데이터 ({num_samples}개)")
            print("="*100)

            # 샘플 레코드 읽기
            for rec_idx in range(min(num_samples, num_records)):
                record = f.read(record_length)

                if record[0:1] == b' ':  # 삭제되지 않은 레코드
                    print(f"\n--- 레코드 {rec_idx + 1} ---")

                    pos = 1  # 첫 바이트는 삭제 마커
                    for field in fields:
                        field_data = record[pos:pos + field['length']]

                        try:
                            if field['type'] == 'C':  # Text
                                value = field_data.decode('cp949', errors='ignore').strip()
                            elif field['type'] == 'N' or field['type'] == 'F':  # Number/Float
                                value = field_data.decode('ascii', errors='ignore').strip()
                            elif field['type'] == 'D':  # Date
                                value = field_data.decode('ascii', errors='ignore').strip()
                            else:
                                value = str(field_data)

                            # 값이 있을 때만 출력
                            if value:
                                print(f"  {field['name']:10s}: {value}")

                        except Exception as e:
                            print(f"  {field['name']:10s}: [읽기 오류: {e}]")

                        pos += field['length']

            print("\n" + "="*100)

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.dbf'

    print("🔍 DBF 샘플 데이터 읽는 중...\n")
    read_dbf_sample(dbf_path, num_samples=5)
    print("\n✅ 완료!")
