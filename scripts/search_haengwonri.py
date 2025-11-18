"""
Shapefile에서 행원리 데이터 검색
"""

import struct

def search_location(dbf_path, search_keyword='행원리'):
    """특정 지역 데이터 검색"""

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

                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'length': field_length
                })

            # 헤더 종료 마커로 이동
            f.seek(header_length)

            print(f"🔍 '{search_keyword}' 검색 중...")
            print(f"총 {num_records:,}개 레코드 검색\n")

            found_count = 0
            matched_records = []

            # 모든 레코드 검색
            for rec_idx in range(num_records):
                record = f.read(record_length)

                if record[0:1] == b' ':  # 삭제되지 않은 레코드
                    pos = 1

                    record_data = {}
                    for field in fields:
                        field_data = record[pos:pos + field['length']]

                        try:
                            if field['type'] == 'C':
                                value = field_data.decode('cp949', errors='ignore').strip()
                            else:
                                value = field_data.decode('ascii', errors='ignore').strip()

                            record_data[field['name']] = value
                        except:
                            record_data[field['name']] = ''

                        pos += field['length']

                    # A2 필드 (주소)에서 검색
                    if search_keyword in record_data.get('A2', ''):
                        found_count += 1
                        matched_records.append(record_data)

                        # 처음 10개만 출력
                        if found_count <= 10:
                            print(f"--- 발견 #{found_count} ---")
                            print(f"  주소: {record_data.get('A2', '')}")
                            print(f"  지번: {record_data.get('A5', '')}")
                            print(f"  PNU: {record_data.get('A0', '')}")
                            print(f"  지목: {record_data.get('A20', '')}")
                            print(f"  면적: {record_data.get('A22', '')}㎡")
                            print()

                # 진행 상황 표시 (10만 건마다)
                if (rec_idx + 1) % 100000 == 0:
                    print(f"  진행: {rec_idx + 1:,} / {num_records:,} ({(rec_idx+1)/num_records*100:.1f}%)")

            print("="*70)
            print(f"✅ 검색 완료!")
            print(f"총 발견: {found_count:,}개 레코드")
            print("="*70)

            return matched_records

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == '__main__':
    dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.dbf'

    results = search_location(dbf_path, '행원리')

    if results:
        print(f"\n💡 '{results[0].get('A2', '')}' 데이터 발견!")
    else:
        print("\n⚠️  '행원리' 데이터를 찾을 수 없습니다.")
        print("다른 검색어를 시도하거나 Shapefile이 올바른지 확인하세요.")
