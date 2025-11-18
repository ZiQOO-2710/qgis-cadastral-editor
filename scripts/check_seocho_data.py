"""
실거래가 CSV에 서초구 데이터가 있는지 확인
"""
import csv

csv_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/아파트(매매)_실거래가_20251022152629.csv'

print("=" * 70)
print("🔍 서초구 실거래가 데이터 확인")
print("=" * 70)

with open(csv_path, 'r', encoding='euc-kr') as f:
    # 헤더까지 스킵
    for _ in range(15):
        f.readline()

    reader = csv.DictReader(f)

    seocho_count = 0
    seocho_complexes = set()

    for row in reader:
        district = row.get('시군구', '')

        if '서초구' in district:
            seocho_count += 1
            complex_name = row.get('단지명', '')
            if complex_name:
                seocho_complexes.add(complex_name)

print(f"\n✅ 서초구 거래 건수: {seocho_count:,}건")
print(f"✅ 서초구 아파트 단지: {len(seocho_complexes)}개")

if seocho_complexes:
    print(f"\n📋 서초구 아파트 단지 목록 (상위 20개):")
    for i, name in enumerate(sorted(seocho_complexes)[:20], 1):
        print(f"   {i}. {name}")

    if len(seocho_complexes) > 20:
        print(f"   ... 외 {len(seocho_complexes) - 20}개")
else:
    print("\n⚠️  서초구 데이터가 없습니다!")
    print("💡 서울 서초구 실거래가 데이터를 다운로드해주세요.")

print("=" * 70)
