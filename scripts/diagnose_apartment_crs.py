"""
아파트 shapefile CRS 진단 및 좌표 검증
"""
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem
import struct

print("=" * 70)
print("🔍 아파트 데이터 CRS 진단")
print("=" * 70)

# 1. QGIS로 읽기
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if layer.isValid():
    print(f"\n📊 레이어 정보:")
    print(f"   CRS authid: {layer.crs().authid()}")
    print(f"   CRS description: {layer.crs().description()}")
    print(f"   총 피처 수: {layer.featureCount():,}")

    # 서초구 필터링
    layer.setSubsetString("bjd_cd LIKE '1165%'")
    print(f"   서초구 피처 수: {layer.featureCount()}")

    # 처음 5개 좌표 출력
    print(f"\n📍 서초구 아파트 좌표 (처음 5개):")
    for i, feature in enumerate(layer.getFeatures()):
        if i >= 5:
            break

        geom = feature.geometry()
        point = geom.asPoint()

        apt_nm = feature['apt_nm']
        rdnmadr = feature['rdnmadr']

        print(f"\n   {i+1}. {apt_nm}")
        print(f"      주소: {rdnmadr}")
        print(f"      X: {point.x():.10f}")
        print(f"      Y: {point.y():.10f}")

        # 좌표 범위 체크
        if 126.5 <= point.x() <= 127.5 and 37.0 <= point.y() <= 38.0:
            print(f"      ✅ 좌표 정상 (서울 범위)")
        else:
            print(f"      ❌ 좌표 이상! (서울 범위 벗어남)")

# 2. .prj 파일 직접 읽기
print(f"\n📄 .prj 파일 내용:")
import zipfile
with zipfile.ZipFile('C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip', 'r') as z:
    prj_content = z.read('apt_mst_info_202410.prj').decode('utf-8')
    print(f"   {prj_content}")

# 3. 인코딩 체크
print(f"\n📝 인코딩 체크:")
with zipfile.ZipFile('C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip', 'r') as z:
    # .cpg 파일이 있는지 체크
    if 'apt_mst_info_202410.cpg' in z.namelist():
        cpg_content = z.read('apt_mst_info_202410.cpg').decode('utf-8').strip()
        print(f"   .cpg 파일 존재: {cpg_content}")
    else:
        print(f"   .cpg 파일 없음 (기본 인코딩 사용)")

    # DBF 헤더에서 인코딩 정보 읽기
    dbf_data = z.read('apt_mst_info_202410.dbf')
    # DBF 헤더 29번째 바이트가 language driver ID
    ldid = dbf_data[29]
    encoding_map = {
        0x00: 'ASCII',
        0x01: 'DOS USA (437)',
        0x02: 'DOS Multilingual (850)',
        0x03: 'Windows ANSI (1252)',
        0x57: 'Windows ANSI (1252)',
        0x64: 'EUC-KR',
        0x65: 'EUC-KR',
        0x66: 'Russian (866)'
    }
    encoding = encoding_map.get(ldid, f'Unknown (0x{ldid:02X})')
    print(f"   DBF LDID: 0x{ldid:02X} → {encoding}")

print("\n" + "=" * 70)
print("✅ 진단 완료")
print("=" * 70)
