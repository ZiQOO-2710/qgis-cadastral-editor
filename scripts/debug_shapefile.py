"""
Shapefile 로딩 디버깅
"""
from qgis.core import QgsVectorLayer

apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

print("=" * 70)
print("🔍 Shapefile 디버깅")
print("=" * 70)

print(f"\n경로: {apt_path}")

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

print(f"\n1️⃣  레이어 유효성: {apt_layer.isValid()}")
print(f"2️⃣  전체 Feature 수: {apt_layer.featureCount()}")

# 필터 적용 전
print(f"\n3️⃣  필터 적용 전:")
count = 0
for feature in apt_layer.getFeatures():
    count += 1
    if count <= 3:
        print(f"   Feature {count}: ID={feature.id()}")
        # 속성 출력
        attrs = feature.attributes()
        print(f"      속성 개수: {len(attrs)}")
print(f"   총 순회: {count}개")

# 필터 적용
apt_layer.setSubsetString("bjd_cd LIKE '1165%'")

print(f"\n4️⃣  필터 적용 후 (bjd_cd LIKE '1165%'):")
print(f"   Feature 수: {apt_layer.featureCount()}")

count = 0
for feature in apt_layer.getFeatures():
    count += 1
    if count <= 3:
        print(f"   Feature {count}: ID={feature.id()}")
print(f"   총 순회: {count}개")

print("\n" + "=" * 70)
