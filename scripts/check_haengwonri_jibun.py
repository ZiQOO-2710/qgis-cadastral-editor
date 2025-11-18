"""
행원리의 실제 지번 목록 확인
"""

import struct

def get_haengwonri_jibun_list(dbf_path, location_keyword='행원리'):
    """행원리의 모든 지번 목록 추출"""

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

            print(f"🔍 '{location_keyword}' 지번 추출 중...\n")

            jibun_set = set()
            sample_data = []

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
                    addr = record_data.get('A2', '')
                    jibun = record_data.get('A5', '')

                    if location_keyword in addr and jibun:
                        jibun_set.add(jibun)

                        # 샘플 50개만 저장
                        if len(sample_data) < 50:
                            sample_data.append({
                                'addr': addr,
                                'jibun': jibun,
                                'A6': record_data.get('A6', '')
                            })

                # 진행 상황 표시
                if (rec_idx + 1) % 200000 == 0:
                    print(f"  진행: {rec_idx + 1:,} / {num_records:,} ({(rec_idx+1)/num_records*100:.1f}%)")

            print("\n" + "="*70)
            print(f"✅ 추출 완료!")
            print(f"행원리 총 고유 지번: {len(jibun_set)}개")
            print("="*70)

            # 샘플 출력
            print("\n📄 샘플 지번 (처음 30개):")
            for i, data in enumerate(sample_data[:30], 1):
                print(f"{i:3d}. {data['jibun']:15s} | A6: {data['A6']}")

            # 지번 목록 정렬 및 출력
            jibun_list = sorted(jibun_set, key=lambda x: (
                int(x.split('-')[0]) if x.split('-')[0].isdigit() else 999999,
                int(x.split('-')[1]) if len(x.split('-')) > 1 and x.split('-')[1].isdigit() else 0
            ))

            return jibun_list

    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == '__main__':
    dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.dbf'

    jibun_list = get_haengwonri_jibun_list(dbf_path, '행원리')

    if jibun_list:
        print("\n" + "="*70)
        print("📋 행원리 모든 지번 목록:")
        print("="*70)

        # 지번 범위 확인
        print(f"\n첫 30개 지번:")
        for i, jibun in enumerate(jibun_list[:30], 1):
            print(f"  {i:3d}. {jibun}")

        print(f"\n...")
        print(f"\n마지막 30개 지번:")
        for i, jibun in enumerate(jibun_list[-30:], len(jibun_list)-29):
            print(f"  {i:3d}. {jibun}")

        # CSV의 지번과 비교
        csv_jibun = ['1262-11', '1262-12', '924-1', '924-2', '924-3', '924-4', '924',
                     '926-1', '926-2', '926-4', '926-5', '926-7', '926-8', '926-9']

        print("\n" + "="*70)
        print("🔍 CSV 지번 vs Shapefile 지번 비교:")
        print("="*70)

        for csv_j in csv_jibun[:10]:
            if csv_j in jibun_list:
                print(f"  ✅ {csv_j:15s} - 발견")
            else:
                print(f"  ❌ {csv_j:15s} - 없음")

                # 유사한 지번 찾기
                similar = [j for j in jibun_list if csv_j in j or j in csv_j]
                if similar:
                    print(f"      💡 유사: {', '.join(similar[:5])}")
