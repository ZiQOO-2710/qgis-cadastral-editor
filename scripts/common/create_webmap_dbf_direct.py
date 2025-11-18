"""
서초구 지적도 + 아파트 웹맵 (DBF 직접 읽기 버전)
- ZIP에서 DBF 직접 추출하여 EUC-KR로 읽기
- shapefile은 좌표만 사용
"""
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform
)
import json
import os
import zipfile
import struct

def read_dbf_with_encoding(dbf_bytes, encoding='euc-kr'):
    """DBF 파일을 지정된 인코딩으로 읽기"""
    # DBF 헤더 파싱
    header = struct.unpack('<BBBBIHH20x', dbf_bytes[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    # 필드 정보 읽기
    fields = []
    pos = 32
    while dbf_bytes[pos] != 0x0D:  # 필드 종료 마커
        field_info = struct.unpack('<11sc4xBB14x', dbf_bytes[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        fields.append((field_name, field_type, field_len))
        pos += 32

    # 레코드 읽기
    records = []
    data_start = header_len
    for i in range(num_records):
        record_start = data_start + i * record_len
        record = {}
        offset = 1  # 첫 바이트는 삭제 마커

        for field_name, field_type, field_len in fields:
            value_bytes = dbf_bytes[record_start + offset:record_start + offset + field_len]

            if field_type == 'C':  # Character
                try:
                    value = value_bytes.decode(encoding).strip()
                except:
                    value = value_bytes.decode('utf-8', errors='ignore').strip()
            elif field_type == 'N':  # Numeric
                value = value_bytes.decode('ascii').strip()
                if value:
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except:
                        value = 0
                else:
                    value = 0
            else:
                value = value_bytes.decode('ascii', errors='ignore').strip()

            record[field_name] = value
            offset += field_len

        records.append(record)

    return records

print("=" * 70)
print("🌐 웹맵 생성 (DBF 직접 읽기 버전)")
print("=" * 70)

output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'
os.makedirs(output_dir, exist_ok=True)

# 1단계: DBF에서 속성 읽기 (EUC-KR)
print("\n1️⃣  아파트 DBF 직접 읽기 중 (EUC-KR)...")
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'

with zipfile.ZipFile(apt_zip, 'r') as z:
    dbf_bytes = z.read('apt_mst_info_202410.dbf')

dbf_records = read_dbf_with_encoding(dbf_bytes, 'euc-kr')
print(f"   총 레코드: {len(dbf_records):,}개")

# 서초구만 필터링 (bjd_cd LIKE '1165%')
seocho_records = [r for r in dbf_records if str(r.get('bjd_cd', '')).startswith('1165')]
print(f"   서초구 레코드: {len(seocho_records):,}개")

# 처음 5개만
seocho_records = seocho_records[:5]

# 2단계: Shapefile에서 좌표 읽기
print("\n2️⃣  아파트 좌표 읽기 중...")
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'

apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if apt_layer.isValid():
    print(f"   원본 CRS: {apt_layer.crs().authid()}")
    apt_layer.setSubsetString("bjd_cd LIKE '1165%'")

    # DBF 레코드와 shapefile 피처를 매칭
    apt_features = []
    feature_list = list(apt_layer.getFeatures())[:5]

    for i, (feature, dbf_record) in enumerate(zip(feature_list, seocho_records)):
        geom = feature.geometry()
        point = geom.asPoint()

        apt_nm = dbf_record.get('apt_nm', '')
        rdnmadr = dbf_record.get('rdnmadr', '')
        dngct = dbf_record.get('dngct', 0)

        apt_features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.x(), point.y()]
            },
            'properties': {
                'apt_nm': apt_nm,
                'rdnmadr': rdnmadr,
                'dngct': int(dngct) if dngct else 0
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

    # UTF-8로 저장
    with open(f'{output_dir}/apartments.geojson', 'w', encoding='utf-8') as f:
        json.dump(apt_geojson, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 아파트 GeoJSON 생성: {len(apt_features)}개")

# 3단계: 지적도 변환
print("\n3️⃣  서초구 지적도 100개 변환 중...")
transform = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem('EPSG:5186'),
    QgsCoordinateReferenceSystem('EPSG:4326'),
    QgsProject.instance()
)

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

# 4단계: HTML (변경 없음)
print("\n4️⃣  HTML 생성 중...")

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
        var map = L.map('map').setView([37.48, 127.03], 14);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        var aptCount = 0;
        var parcelCount = 0;

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

                map.fitBounds(cadastralLayer.getBounds());
                console.log('지적도 로드 완료:', parcelCount, '개');
            })
            .catch(err => console.error('지적도 로드 실패:', err));

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
print("💡 브라우저에서 Ctrl+Shift+Delete로 캐시 삭제 후 Ctrl+F5!")
print("=" * 70)
