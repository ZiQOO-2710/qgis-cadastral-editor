"""
ZIP 압축 파일 직접 로드 테스트 - 서울 서초구
"""
from qgis.core import QgsVectorLayer, QgsProject

# /vsizip/ 프리픽스로 ZIP 내부 SHP 파일 직접 접근
zip_path = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
shp_file = 'LSMD_CONT_LDREG_11650_202510.shp'

# GDAL의 /vsizip/ 가상 파일 시스템 사용
layer_path = f'/vsizip/{zip_path}/{shp_file}'
layer = QgsVectorLayer(layer_path, '서울_서초구_지적도', 'ogr')

if layer.isValid():
    QgsProject.instance().addMapLayer(layer)
    feature_count = layer.featureCount()
    extent = layer.extent()
    print(f"✅ ZIP 직접 로드 성공!")
    print(f"📊 필지 수: {feature_count:,}개")
    print(f"📍 범위: {extent.xMinimum():.1f}, {extent.yMinimum():.1f} ~ {extent.xMaximum():.1f}, {extent.yMaximum():.1f}")
    print(f"🗺️  좌표계: {layer.crs().authid()}")
else:
    print(f"❌ 레이어 로드 실패")
    print(f"🔍 시도한 경로: {layer_path}")
