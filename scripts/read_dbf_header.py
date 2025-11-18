"""
DBF 파일 헤더 읽기 스크립트 (QGIS 없이 실행 가능)
일반 Python으로 실행 가능
"""

import struct
import sys

def read_dbf_header(dbf_path):
    """DBF 파일의 필드 구조 읽기"""

    try:
        with open(dbf_path, 'rb') as f:
            # DBF 헤더 읽기
            dbf_header = f.read(32)

            # 레코드 수와 헤더 길이
            num_records = struct.unpack('<I', dbf_header[4:8])[0]
            header_length = struct.unpack('<H', dbf_header[8:10])[0]
            record_length = struct.unpack('<H', dbf_header[10:12])[0]

            print("="*70)
            print("📊 DBF 파일 정보")
            print("="*70)
            print(f"총 레코드 수: {num_records:,}")
            print(f"헤더 길이: {header_length} bytes")
            print(f"레코드 길이: {record_length} bytes")

            # 필드 디스크립터 읽기
            num_fields = (header_length - 33) // 32

            print(f"\n총 필드 수: {num_fields}")
            print("\n" + "="*70)
            print("📋 필드 구조")
            print("="*70)
            print(f"{'No':<4} {'필드명':<20} {'타입':<6} {'길이':<6} {'소수점':<6}")
            print("-"*70)

            fields = []
            for i in range(num_fields):
                field_desc = f.read(32)

                # 필드명 (11 bytes, null-terminated)
                field_name = field_desc[0:11].decode('cp949', errors='ignore').rstrip('\x00')

                # 필드 타입 (1 byte)
                field_type = chr(field_desc[11])

                # 필드 길이 (1 byte)
                field_length = field_desc[16]

                # 소수점 자리수 (1 byte)
                field_decimal = field_desc[17]

                type_name = {
                    'C': 'Text',
                    'N': 'Number',
                    'F': 'Float',
                    'L': 'Logical',
                    'D': 'Date',
                    'M': 'Memo'
                }.get(field_type, field_type)

                print(f"{i+1:<4} {field_name:<20} {type_name:<6} {field_length:<6} {field_decimal:<6}")

                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'length': field_length,
                    'decimal': field_decimal
                })

            # 지번 관련 필드 찾기
            print("\n" + "="*70)
            print("🔍 지번 관련 가능성 있는 필드")
            print("="*70)

            jibun_keywords = ['지번', 'JIBUN', 'PNU', '번지', 'BEONJI', 'BON', 'BUN', 'ADDR',
                             'JIMOK', '본번', '부번', 'MAIN', 'SUB', 'LAND']
            potential_fields = []

            for field in fields:
                field_name_upper = field['name'].upper()
                for keyword in jibun_keywords:
                    if keyword.upper() in field_name_upper:
                        potential_fields.append(field['name'])
                        break

            if potential_fields:
                print("✅ 다음 필드들을 확인하세요:")
                for pf in potential_fields:
                    print(f"   - {pf}")
            else:
                print("⚠️  자동 감지 실패")
                print("💡 필드 목록을 직접 확인하여 지번 필드를 찾으세요")
                print("   (보통 'PNU', 'JIBUN', 'BON', 'BUN' 등의 이름)")

            return fields

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    dbf_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/AL_D160_50_20250924/AL_D160_50_20250924.dbf'

    print("🔍 DBF 파일 분석 중...\n")
    fields = read_dbf_header(dbf_path)

    if fields:
        print("\n✅ 분석 완료!")
    else:
        print("\n❌ 분석 실패!")
