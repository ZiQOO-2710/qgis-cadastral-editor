"""
서초구 지적도 + 아파트 웹맵 (수정버전)
- 브이월드 베이스맵
- 좌표계 변환 수정
- UTF-8 인코딩 수정
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform, QgsVectorFileWriter, QgsWkbTypes
)
import json
import os

print("=" * 70)
print("🌐 웹맵 생성 (수정버전)")
print("=" * 70)

output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'
os.makedirs(output_dir, exist_ok=True)

# 좌표계 변환 객체
source_crs = QgsCoordinateReferenceSystem('EPSG:5186')
dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
transform = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())

# 1단계: 아파트 먼저 (5개)
print("\n1️⃣  서초구 아파트 5개 변환 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if apt_layer.isValid():
    # 서초구만 필터링
    apt_layer.setSubsetString("bjd_cd LIKE '1165%'")
    
    apt_features = []
    for i, feature in enumerate(apt_layer.getFeatures()):
        if i >= 5:
            break
        
        # 좌표 변환
        geom = feature.geometry()
        geom.transform(transform)
        
        # 좌표 확인
        point = geom.asPoint()
        
        apt_features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.x(), point.y()]
            },
            'properties': {
                'name': str(feature['apt_nm'] or ''),
                'address': str(feature['rdnmadr'] or ''),
                'buildings': int(feature['dngct']) if feature['dngct'] else 0
            }
        })
        
        print(f"   {i+1}. {feature['apt_nm']} → ({point.x():.6f}, {point.y():.6f})")
    
    apt_geojson = {
        'type': 'FeatureCollection',
        'features': apt_features
    }
    
    with open(f'{output_dir}/apartments.geojson', 'w', encoding='utf-8') as f:
        json.dump(apt_geojson, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 아파트 GeoJSON 생성: {len(apt_features)}개")

# 2단계: 지적도 (100개)
print("\n2️⃣  서초구 지적도 100개 변환 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, 'temp', 'ogr')

if cadastral_layer.isValid():
    cadastral_features = []
    
    for i, feature in enumerate(cadastral_layer.getFeatures()):
        if i >= 100:
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
        json.dump(cadastral_geojson, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 지적도 GeoJSON 생성: {len(cadastral_features)}개")

# 3단계: HTML 생성 (브이월드 지도)
print("\n3️⃣  HTML 생성 중 (브이월드 베이스맵)...")

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
        // 지도 초기화 (서초구 중심)
        var map = L.map('map').setView([37.48, 127.03], 14);
        
        // 브이월드 베이스맵 (배경지도 - 하이브리드)
        L.tileLayer('http://api.vworld.kr/req/wmts/1.0.0/CEB245F0-4A30-396E-A5DF-77739FB90870/Hybrid/{z}/{y}/{x}.png', {
            attribution: '© VWorld',
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
                
                L.geoJSON(data, {
                    style: {
                        fillColor: '#ffff00',
                        fillOpacity: 0.1,
                        color: '#ff0000',
                        weight: 1
                    }
                }).addTo(map);
                
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
                        console.log('아파트:', feature.properties.name, latlng);
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
                            '<h4 style="margin:0 0 5px 0;">' + props.name + '</h4>' +
                            '<div><b>주소:</b> ' + props.address + '</div>' +
                            '<div><b>동수:</b> ' + props.buildings + '개</div>' +
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
print(f"\n🌐 실행 방법:")
print(f"   1. 탐색기에서 {output_dir} 폴더 열기")
print(f"   2. index.html 더블클릭")
print(f"   3. 웹 브라우저에서 확인")
print("\n💡 브라우저 개발자도구(F12) 콘솔에서 에러 확인 가능")
print("=" * 70)
