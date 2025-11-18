"""
서초구 지적도 + 아파트 단지 오버레이 테스트
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsFillSymbol, QgsMarkerSymbol,
    QgsSingleSymbolRenderer, QgsRuleBasedRenderer
)
from qgis.PyQt.QtGui import QColor

print("=" * 70)
print("🏗️  서초구 지적도 + 아파트 단지 오버레이 테스트")
print("=" * 70)

# 1단계: 서초구 지적도 로드
print("\n1️⃣  서초구 지적도 로드 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, '서초구_지적도', 'ogr')

if not cadastral_layer.isValid():
    print("❌ 지적도 로드 실패")
else:
    QgsProject.instance().addMapLayer(cadastral_layer)
    print(f"✅ 지적도 로드 완료: {cadastral_layer.featureCount():,}개 필지")
    
    # 지적도 스타일: 연한 회색 채우기, 진한 회색 테두리
    symbol = QgsFillSymbol.createSimple({
        'color': '240,240,240,255',
        'outline_color': '180,180,180,255',
        'outline_width': '0.2'
    })
    cadastral_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    cadastral_layer.triggerRepaint()

# 2단계: 전국 아파트 데이터 로드
print("\n2️⃣  전국 아파트 데이터 로드 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, '전국_아파트_단지', 'ogr')

if not apt_layer.isValid():
    print("❌ 아파트 데이터 로드 실패")
else:
    print(f"✅ 아파트 데이터 로드 완료: {apt_layer.featureCount():,}개 단지")
    
    # 3단계: 서초구 아파트만 필터링
    print("\n3️⃣  서초구 아파트 필터링 중...")
    # 서초구 법정동 코드: 1165로 시작
    apt_layer.setSubsetString("bjd_cd LIKE '1165%'")
    
    seocho_apt_count = apt_layer.featureCount()
    print(f"✅ 서초구 아파트: {seocho_apt_count:,}개")
    
    # 아파트 스타일: 빨간색 포인트
    symbol = QgsMarkerSymbol.createSimple({
        'name': 'circle',
        'color': 'red',
        'size': '3',
        'outline_color': 'darkred',
        'outline_width': '0.5'
    })
    apt_layer.setRenderer(QgsSingleSymbolRenderer(symbol))
    apt_layer.triggerRepaint()
    
    QgsProject.instance().addMapLayer(apt_layer)
    
    # 4단계: 샘플 아파트 정보 출력
    print(f"\n📝 서초구 아파트 샘플 (처음 5개):")
    features = list(apt_layer.getFeatures())[:5]
    for i, feature in enumerate(features, 1):
        apt_nm = feature['apt_nm']
        rdnmadr = feature['rdnmadr']
        dngct = feature['dngct']
        print(f"   {i}. {apt_nm}")
        print(f"      {rdnmadr}")
        print(f"      동수: {dngct}개")

# 5단계: 확대
print("\n5️⃣  서초구 범위로 확대 중...")
if cadastral_layer.isValid():
    extent = cadastral_layer.extent()
    iface.mapCanvas().setExtent(extent)
    iface.mapCanvas().refresh()
    print("✅ 지도 확대 완료")

print("\n" + "=" * 70)
print("🎉 완료! 지적도 위에 빨간색 점으로 아파트 단지가 표시됩니다.")
print("=" * 70)
