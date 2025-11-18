"""
서초구 지적도 + 아파트 5개만 테스트
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFillSymbol, QgsMarkerSymbol,
    QgsSingleSymbolRenderer, QgsVectorFileWriter, QgsCoordinateReferenceSystem
)
from qgis.PyQt.QtGui import QColor

print("=" * 70)
print("🏗️  서초구 지적도 + 아파트 5개 테스트")
print("=" * 70)

# 1단계: 서초구 지적도 로드
print("\n1️⃣  서초구 지적도 로드 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, '서초구_지적도', 'ogr')

if cadastral_layer.isValid():
    QgsProject.instance().addMapLayer(cadastral_layer)
    print(f"✅ 지적도 로드 완료: {cadastral_layer.featureCount():,}개 필지")
    
    # 연한 회색 스타일
    symbol = QgsFillSymbol.createSimple({
        'color': '240,240,240,255',
        'outline_color': '180,180,180,255',
        'outline_width': '0.2'
    })
    cadastral_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    cadastral_layer.triggerRepaint()

# 2단계: 전국 아파트 데이터 로드
print("\n2️⃣  전국 아파트 데이터에서 서초구 아파트 추출 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

temp_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if temp_layer.isValid():
    # 서초구 법정동 코드로 필터링 후 처음 5개만 추출
    temp_layer.setSubsetString("bjd_cd LIKE '1165%'")
    
    # 메모리 레이어 생성 (5개만)
    apt_layer = QgsVectorLayer(f"Point?crs={temp_layer.crs().authid()}", '서초구_아파트_5개', 'memory')
    apt_provider = apt_layer.dataProvider()
    
    # 필드 복사
    apt_provider.addAttributes(temp_layer.fields())
    apt_layer.updateFields()
    
    # 처음 5개 피처만 복사
    features = list(temp_layer.getFeatures())[:5]
    apt_provider.addFeatures(features)
    
    print(f"✅ 아파트 5개 추출 완료")
    
    # 아파트 정보 출력
    print(f"\n📝 선택된 아파트:")
    for i, feature in enumerate(features, 1):
        apt_nm = feature['apt_nm']
        rdnmadr = feature['rdnmadr']
        dngct = feature['dngct'] if feature['dngct'] else 0
        geom = feature.geometry()
        x, y = geom.asPoint().x(), geom.asPoint().y()
        
        print(f"\n   {i}. {apt_nm}")
        print(f"      주소: {rdnmadr}")
        print(f"      동수: {dngct}개")
        print(f"      좌표: ({x:.1f}, {y:.1f})")
    
    # 빨간색 포인트 스타일
    symbol = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': 'red',
        'size': '5',
        'outline_color': 'darkred',
        'outline_width': '1'
    })
    apt_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    
    QgsProject.instance().addMapLayer(apt_layer)
    apt_layer.triggerRepaint()

# 3단계: 서초구 범위로 확대
print("\n3️⃣  서초구 범위로 확대 중...")
if cadastral_layer.isValid():
    extent = cadastral_layer.extent()
    iface.mapCanvas().setExtent(extent)
    iface.mapCanvas().refresh()
    print("✅ 지도 확대 완료")

print("\n" + "=" * 70)
print("🎉 완료! 지적도 위에 빨간 점 5개로 아파트 단지가 표시됩니다.")
print("=" * 70)
