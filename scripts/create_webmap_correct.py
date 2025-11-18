"""
서초구 지적도 + 아파트 웹맵 (완전 수정 버전)
- QgsVectorFileWriter로 직접 GeoJSON 저장
- UTF-8 인코딩
- 올바른 좌표계 변환
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsVectorFileWriter, 
    QgsCoordinateReferenceSystem, QgsCoordinateTransformContext
)
import os
import json

print("=" * 70)
print("🌐 웹맵 생성 (완전 수정 버전)")
print("=" * 70)

output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'
os.makedirs(output_dir, exist_ok=True)

# 1단계: 서초구 아파트 5개 GeoJSON 생성
print("\n1️⃣  서초구 아파트 5개 GeoJSON 생성 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if apt_layer.isValid():
    print(f"   원본 CRS: {apt_layer.crs().authid()}")
    
    # 서초구만 필터링
    apt_layer.setSubsetString("bjd_cd LIKE '1165%'")
    
    # 처음 5개만 선택
    feature_ids = [f.id() for f in apt_layer.getFeatures()][:5]
    apt_layer.selectByIds(feature_ids)
    
    # GeoJSON 저장 옵션
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = 'GeoJSON'
    save_options.fileEncoding = 'UTF-8'
    save_options.ct = QgsCoordinateTransformContext()
    save_options.onlySelectedFeatures = True
    
    # EPSG:4326으로 변환하여 저장
    dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    
    result = QgsVectorFileWriter.writeAsVectorFormatV3(
        apt_layer,
        f'{output_dir}/apartments.geojson',
        QgsCoordinateTransformContext(),
        save_options,
        destCRS=dest_crs
    )
    
    if result[0] == QgsVectorFileWriter.NoError:
        print("✅ 아파트 GeoJSON 생성 완료")
        
        # 샘플 좌표 출력
        for i, feature in enumerate(apt_layer.getSelectedFeatures()):
            geom = feature.geometry()
            print(f"   {i+1}. {feature['apt_nm']}")
            print(f"      원본 좌표: {geom.asPoint()}")
    else:
        print(f"❌ 아파트 GeoJSON 생성 실패: {result}")

# 2단계: 서초구 지적도 100개 GeoJSON 생성
print("\n2️⃣  서초구 지적도 100개 GeoJSON 생성 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, 'temp', 'ogr')

if cadastral_layer.isValid():
    print(f"   원본 CRS: {cadastral_layer.crs().authid()}")
    
    # 처음 100개만 선택
    feature_ids = [f.id() for f in cadastral_layer.getFeatures()][:100]
    cadastral_layer.selectByIds(feature_ids)
    
    # GeoJSON 저장
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = 'GeoJSON'
    save_options.fileEncoding = 'UTF-8'
    save_options.onlySelectedFeatures = True
    
    dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
    
    result = QgsVectorFileWriter.writeAsVectorFormatV3(
        cadastral_layer,
        f'{output_dir}/cadastral.geojson',
        QgsCoordinateTransformContext(),
        save_options,
        destCRS=dest_crs
    )
    
    if result[0] == QgsVectorFileWriter.NoError:
        print("✅ 지적도 GeoJSON 생성 완료")
    else:
        print(f"❌ 지적도 GeoJSON 생성 실패: {result}")

# 3단계: HTML 생성 (OpenStreetMap 베이스맵)
print("\n3️⃣  HTML 생성 중 (OpenStreetMap 베이스맵)...")

html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>서초구 지적도 + 아파트 단지</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; font-family: 'Malgun Gothic', sans-serif; }
        #map { width: 100%; height: 100vh; }
        .info-box {
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="info-box">
        <h3 style="margin:0 0 10px 0;">서초구 지적도 + 아파트</h3>
        <div>📍 아파트: <span id="apt-count">-</span>개</div>
        <div>📦 필지: <span id="parcel-count">-</span>개</div>
    </div>
    <div id="map"></div>
    <script>
        // 지도 초기화 (서초구 중심: 127.03, 37.48)
        var map = L.map('map').setView([37.48, 127.03], 14);
        
        // OpenStreetMap 베이스맵
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
        
        var aptCount = 0;
        var parcelCount = 0;
        
        // 지적도 로드
        fetch('cadastral.geojson')
            .then(r => r.json())
            .then(data => {
                parcelCount = data.features.length;
                document.getElementById('parcel-count').innerText = parcelCount;
                
                var cadastralLayer = L.geoJSON(data, {
                    style: {
                        fillColor: '#ffff00',
                        fillOpacity: 0.2,
                        color: '#ff0000',
                        weight: 1
                    }
                }).addTo(map);
                
                // 지적도 범위로 확대
                map.fitBounds(cadastralLayer.getBounds());
                
                console.log('지적도 로드 완료:', parcelCount, '개');
            })
            .catch(err => console.error('지적도 로드 실패:', err));
        
        // 아파트 로드
        fetch('apartments.geojson')
            .then(r => r.json())
            .then(data => {
                aptCount = data.features.length;
                document.getElementById('apt-count').innerText = aptCount;
                
                L.geoJSON(data, {
                    pointToLayer: function(feature, latlng) {
                        console.log('아파트:', feature.properties.apt_nm, latlng);
                        return L.circleMarker(latlng, {
                            radius: 10,
                            fillColor: 'red',
                            color: 'darkred',
                            weight: 2,
                            fillOpacity: 0.8
                        });
                    },
                    onEachFeature: function(feature, layer) {
                        var props = feature.properties;
                        layer.bindPopup(
                            '<div style="min-width:200px;">' +
                            '<h4 style="margin:0 0 5px 0;">' + props.apt_nm + '</h4>' +
                            '<div><b>주소:</b> ' + props.rdnmadr + '</div>' +
                            '<div><b>동수:</b> ' + props.dngct + '개</div>' +
                            '</div>'
                        );
                    }
                }).addTo(map);
                
                console.log('아파트 로드 완료:', aptCount, '개');
            })
            .catch(err => console.error('아파트 로드 실패:', err));
    </script>
</body>
</html>'''

with open(f'{output_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ HTML 생성 완료")

print("\n" + "=" * 70)
print("🎉 웹맵 생성 완료!")
print("=" * 70)
print(f"\n📂 위치: {output_dir}")
print(f"\n🌐 접속: http://localhost:8000")
print("=" * 70)
