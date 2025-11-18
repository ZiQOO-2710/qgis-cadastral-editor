"""
파일 접근 테스트 (QGIS Python Console용)
"""
import os

print("=" * 70)
print("📁 파일 접근 테스트")
print("=" * 70)

# Windows 경로로 테스트
csv_path = 'C:/Users/ksj27/PROJECTS/QGIS/data/아파트(매매)_실거래가_20251022152629.csv'
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'

print("\n1️⃣  CSV 파일:")
if os.path.exists(csv_path):
    print(f"   ✅ 존재: {csv_path}")
    print(f"   크기: {os.path.getsize(csv_path):,} bytes")
else:
    print(f"   ❌ 없음: {csv_path}")

print("\n2️⃣  아파트 ZIP:")
if os.path.exists(apt_zip):
    print(f"   ✅ 존재: {apt_zip}")
    print(f"   크기: {os.path.getsize(apt_zip):,} bytes")
else:
    print(f"   ❌ 없음: {apt_zip}")

print("\n3️⃣  지적도 ZIP:")
if os.path.exists(cadastral_zip):
    print(f"   ✅ 존재: {cadastral_zip}")
    print(f"   크기: {os.path.getsize(cadastral_zip):,} bytes")
else:
    print(f"   ❌ 없음: {cadastral_zip}")

print("\n" + "=" * 70)
print("테스트 완료")
print("=" * 70)
