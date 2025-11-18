"""
서초구 지적도 + 아파트 웹맵 (완전 수정 버전 v2)
- QVariant 타입 변환 제대로 처리
- 인코딩 UTF-8 보장
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
import json
import os

def safe_str(qvariant_value, default=''):
    """QVariant를 안전하게 문자열로 변환"""
    if qvariant_value is None:
        return default
    try:
        # QVariant가 NULL인 경우 처리
        if hasattr(qvariant_value, 'isNull') and qvariant_value.isNull():
            return default
        return str(qvariant_value)
    except:
        return default

def safe_int(qvariant_value, default=0):
    """QVariant를 안전하게 정수로 변환"""
    if qvariant_value is None:
        return default
    try:
        if hasattr(qvariant_value, 'isNull') and qvariant_value.isNull():
            return default
        return int(qvariant_value)
    except (TypeError, ValueError):
        return default

print("=" * 70)
print("🌐 웹맵 생성 (완전 수정 버전 v2)")
print("=" * 70)

output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'
os.makedirs(output_dir, exist_ok=True)

# 좌표 변환 객체 (지적도용)
transform = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem('EPSG:5186'),
    QgsCoordinateReferenceSystem('EPSG:4326'),
    QgsProject.instance()
)

# 1단계: 서초구 아파트 5개 (이미 EPSG:4326)
print("\n1️⃣  서초구 아파트 5개 추출 중...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if apt_layer.isValid():
    print(f"   원본 CRS: {apt_layer.crs().authid()}")
    apt_layer.setSubsetString("bjd_cd LIKE '1165%'")

    apt_features = []
    for i, feature in enumerate(apt_layer.getFeatures()):
        if i >= 5:
            break

        geom = feature.geometry()
        point = geom.asPoint()

        # QVariant를 Python 네이티브 타입으로 안전하게 변환
        apt_nm = safe_str(feature['apt_nm'])
        rdnmadr = safe_str(feature['rdnmadr'])
        dngct = safe_int(feature['dngct'])

        apt_features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.x(), point.y()]
            },
            'properties': {
                'apt_nm': apt_nm,
                'rdnmadr': rdnmadr,
                'dngct': dngct
            }
        })

        print(f"   {i+1}. {apt_nm}")
        print(f"      주소: {rdnmadr}")
        print(f"      동수: {dngct}개")
        print(f"      좌표: ({point.x():.6f}, {point.y():.6f})")

    apt_geojson = {
        'type': 'FeatureCollection',
        'features': apt_features
    }

    # UTF-8로 저장, ensure_ascii=False로 한글 유지
    with open(f'{output_dir}/apartments.geojson', 'w', encoding='utf-8') as f:
        json.dump(apt_geojson, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 아파트 GeoJSON 생성: {len(apt_features)}개")

# 2단계: 서초구 지적도 100개 (EPSG:5186 → 4326 변환)
print("\n2️⃣  서초구 지적도 100개 변환 중...")
cadastral_zip = 'E:/연속지적도 전국/LSMD_CONT_LDREG_서울_서초구.zip'
cadastral_shp = 'LSMD_CONT_LDREG_11650_202510.shp'
cadastral_path = f'/vsizip/{cadastral_zip}/{cadastral_shp}'

cadastral_layer = QgsVectorLayer(cadastral_path, 'temp', 'ogr')

if cadastral_layer.isValid():
    print(f"   원본 CRS: {cadastral_layer.crs().authid()}")

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

# 3단계: HTML 생성
print("\n3️⃣  HTML 생성 중...")

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
print("💡 브라우저에서 F5 새로고침 하세요!")
print("=" * 70)
