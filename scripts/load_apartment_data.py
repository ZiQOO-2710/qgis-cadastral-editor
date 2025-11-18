"""
전국 아파트 단지 정보 로드 및 분석
"""
from qgis.core import QgsVectorLayer, QgsProject

# ZIP 파일 직접 로드
zip_path = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
shp_file = 'apt_mst_info_202410.shp'

layer_path = f'/vsizip/{zip_path}/{shp_file}'
layer = QgsVectorLayer(layer_path, '전국_아파트_단지_202410', 'ogr')

if layer.isValid():
    QgsProject.instance().addMapLayer(layer)
    
    print("=" * 70)
    print("✅ 아파트 단지 데이터 로드 완료!")
    print("=" * 70)
    
    feature_count = layer.featureCount()
    extent = layer.extent()
    fields = layer.fields()
    
    print(f"\n📊 기본 정보:")
    print(f"   - 총 아파트 단지 수: {feature_count:,}개")
    print(f"   - 좌표계: {layer.crs().authid()}")
    print(f"   - 필드 수: {fields.count()}개")
    
    print(f"\n📍 공간 범위:")
    print(f"   - X: {extent.xMinimum():.1f} ~ {extent.xMaximum():.1f}")
    print(f"   - Y: {extent.yMinimum():.1f} ~ {extent.yMaximum():.1f}")
    
    print(f"\n🏢 주요 필드:")
    key_fields = ['uid', 'apt_cd', 'apt_nm', 'rdnmadr', 'bjd_cd', 'ltno_addr', 
                  'jibun_addr', 'dngct', 'totprk_cnt', 'cctv_cnt']
    for field_name in key_fields:
        field = fields.field(field_name)
        if field:
            print(f"   - {field_name}: {field.typeName()}")
    
    # 샘플 데이터 3개 출력
    print(f"\n📝 샘플 데이터:")
    features = list(layer.getFeatures())[:3]
    for i, feature in enumerate(features, 1):
        print(f"\n   {i}. {feature['apt_nm']}")
        print(f"      주소: {feature['rdnmadr']}")
        print(f"      동수: {feature['dngct']}, 주차: {feature['totprk_cnt']}대")
    
else:
    print(f"❌ 레이어 로드 실패")
    print(f"🔍 시도한 경로: {layer_path}")
