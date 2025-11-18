"""
서초구 지적도 + 아파트 웹맵 프로토타입 생성
GeoJSON 변환 + Leaflet HTML 생성
"""
from qgis.core import QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import json

print("=" * 70)
print("🌐 웹맵 프로토타입 생성")
print("=" * 70)

output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'

# 출력 디렉토리 생성
import os
os.makedirs(output_dir, exist_ok=True)

# 1단계: 서초구 지적도 로드 (샘플 - 100개만)
print("\n1️⃣  서초구 지적도 샘플 100개 추출 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, 'temp', 'ogr')

# EPSG:5186 → EPSG:4326 (WGS84) 변환
source_crs = QgsCoordinateReferenceSystem('EPSG:5186')
dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())

cadastral_features = []
for i, feature in enumerate(cadastral_layer.getFeatures()):
    if i >= 100:  # 100개만
        break
    geom = feature.geometry()
    geom.transform(transform)
    cadastral_features.append({
        'type': 'Feature',
        'geometry': json.loads(geom.asJson()),
        'properties': {'id': i+1}
    })

cadastral_geojson = {
    'type': 'FeatureCollection',
    'features': cadastral_features
}

with open(f'{output_dir}/cadastral.geojson', 'w', encoding='utf-8') as f:
    json.dump(cadastral_geojson, f, ensure_ascii=False)

print(f"✅ 지적도 GeoJSON 생성: {len(cadastral_features)}개")

# 2단계: 서초구 아파트 5개
print("\n2️⃣  서초구 아파트 5개 추출 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')
apt_layer.setSubsetString("bjd_cd LIKE '1165%'")

apt_features = []
for i, feature in enumerate(apt_layer.getFeatures()):
    if i >= 5:  # 5개만
        break
    geom = feature.geometry()
    geom.transform(transform)
    apt_features.append({
        'type': 'Feature',
        'geometry': json.loads(geom.asJson()),
        'properties': {
            'name': feature['apt_nm'],
            'address': feature['rdnmadr'],
            'buildings': feature['dngct'] if feature['dngct'] else 0
        }
    })

apt_geojson = {
    'type': 'FeatureCollection',
    'features': apt_features
}

with open(f'{output_dir}/apartments.geojson', 'w', encoding='utf-8') as f:
    json.dump(apt_geojson, f, ensure_ascii=False)

print(f"✅ 아파트 GeoJSON 생성: {len(apt_features)}개")

# 3단계: HTML 생성
print("\n3️⃣  HTML 웹맵 생성 중...")
html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>서초구 지적도 + 아파트 단지</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; padding: 0; }
        #map { width: 100%; height: 100vh; }
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // 지도 초기화
        var map = L.map('map').setView([37.48, 127.01], 14);
        
        // 베이스맵 (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        
        // 지적도 로드
        fetch('cadastral.geojson')
            .then(r => r.json())
            .then(data => {
                L.geoJSON(data, {
                    style: {
                        fillColor: '#f0f0f0',
                        fillOpacity: 0.5,
                        color: '#b0b0b0',
                        weight: 1
                    }
                }).addTo(map);
            });
        
        // 아파트 로드
        fetch('apartments.geojson')
            .then(r => r.json())
            .then(data => {
                L.geoJSON(data, {
                    pointToLayer: function(feature, latlng) {
                        return L.circleMarker(latlng, {
                            radius: 8,
                            fillColor: 'red',
                            color: 'darkred',
                            weight: 2,
                            fillOpacity: 0.8
                        });
                    },
                    onEachFeature: function(feature, layer) {
                        var props = feature.properties;
                        layer.bindPopup(
                            '<b>' + props.name + '</b><br>' +
                            props.address + '<br>' +
                            '동수: ' + props.buildings + '개'
                        );
                    }
                }).addTo(map);
            });
    </script>
</body>
</html>'''

with open(f'{output_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ HTML 생성 완료")

print("\n" + "=" * 70)
print("🎉 웹맵 생성 완료!")
print("=" * 70)
print(f"\n📂 출력 위치: {output_dir}")
print(f"\n🌐 열어보기:")
print(f"   1. 탐색기에서 {output_dir} 폴더 열기")
print(f"   2. index.html 더블클릭")
print(f"   3. 웹 브라우저에서 확인!")
print("\n💡 아파트 빨간 점 클릭하면 정보 팝업 나옵니다.")
print("=" * 70)
