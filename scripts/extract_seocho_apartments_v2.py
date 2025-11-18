"""
실거래가 CSV 기반 서초구 아파트 웹맵 생성 (간소화 버전)

CSV → 서초구 아파트 → 좌표 찾기 → 웹맵
"""
import csv
import json
import zipfile
import struct
from collections import defaultdict
from qgis.core import QgsVectorLayer

def read_dbf_with_encoding(dbf_bytes, encoding='euc-kr'):
    """DBF 파일을 지정된 인코딩으로 읽기"""
    header = struct.unpack('<BBBBIHH20x', dbf_bytes[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    fields = []
    pos = 32
    while dbf_bytes[pos] != 0x0D:
        field_info = struct.unpack('<11sc4xBB14x', dbf_bytes[pos:pos+32])
        field_name = field_info[0].rstrip(b'\x00').decode('ascii')
        field_type = field_info[1].decode('ascii')
        field_len = field_info[2]
        fields.append((field_name, field_type, field_len))
        pos += 32

    records = []
    data_start = header_len
    for i in range(num_records):
        record_start = data_start + i * record_len
        record = {}
        offset = 1

        for field_name, field_type, field_len in fields:
            value_bytes = dbf_bytes[record_start + offset:record_start + offset + field_len]

            if field_type == 'C':
                try:
                    value = value_bytes.decode(encoding).strip()
                except:
                    value = value_bytes.decode('utf-8', errors='ignore').strip()
            elif field_type == 'N':
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

def format_price_korean(price_10k):
    """가격을 한국식 표기로 변환"""
    if price_10k is None or price_10k == 0:
        return "정보없음"

    eok = price_10k // 10000
    man = price_10k % 10000

    if eok > 0 and man > 0:
        return f"{eok}억 {man:,}만원"
    elif eok > 0:
        return f"{eok}억"
    else:
        return f"{man:,}만원"

print("=" * 70)
print("🏢 실거래가 기반 서초구 아파트 지도 생성")
print("=" * 70)

csv_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/아파트(매매)_실거래가_20251022152629.csv'
apt_zip = 'C:/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
output_dir = 'C:/Users/ksj27/PROJECTS/QGIS/output/webmap'

# 1단계: CSV에서 서초구 거래 추출 및 그룹화
print("\n1️⃣  CSV에서 서초구 거래 추출 중...")
transactions_by_complex = defaultdict(list)

with open(csv_path, 'r', encoding='euc-kr') as f:
    for _ in range(15):
        f.readline()

    reader = csv.DictReader(f)

    for row in reader:
        district = row.get('시군구', '')

        if '서초구' in district:
            complex_name = row.get('단지명', '')

            if complex_name:
                transaction = {
                    'complex_name': complex_name,
                    'area_sqm': float(row.get('전용면적(㎡)', '0') or '0'),
                    'contract_ym': row.get('계약년월', ''),
                    'contract_day': row.get('계약일', '').strip(),
                    'price_10k': int(row.get('거래금액(만원)', '0').replace(',', '') or '0'),
                    'floor': row.get('층', ''),
                    'road_name': row.get('도로명', '')
                }
                transactions_by_complex[complex_name].append(transaction)

print(f"   ✅ 서초구 아파트 단지: {len(transactions_by_complex)}개")
print(f"   ✅ 총 거래: {sum(len(v) for v in transactions_by_complex.values())}건")

# 2단계: 아파트 마스터에서 좌표 찾기
print("\n2️⃣  아파트 마스터에서 좌표 찾기...")

# DBF 읽기
with zipfile.ZipFile(apt_zip, 'r') as z:
    dbf_bytes = z.read('apt_mst_info_202410.dbf')

all_apt_records = read_dbf_with_encoding(dbf_bytes, 'euc-kr')
seocho_apt_records = [
    r for r in all_apt_records
    if str(r.get('bjd_cd', '')).startswith('1165')
]

print(f"   서초구 아파트 마스터: {len(seocho_apt_records):,}개")

# Shapefile 읽기
apt_shp = 'apt_mst_info_202410.shp'
apt_path = f'/vsizip/{apt_zip}/{apt_shp}'
apt_layer = QgsVectorLayer(apt_path, 'temp', 'ogr')

if not apt_layer.isValid():
    print("   ❌ Shapefile 로드 실패")
    raise Exception("Shapefile load failed")

apt_layer.setSubsetString("bjd_cd LIKE '1165%'")

# 3단계: 매칭 및 GeoJSON 생성
print("\n3️⃣  거래 데이터와 매칭 중...")

apt_features = []
matched_count = 0
unmatched_complexes = set(transactions_by_complex.keys())

for feature in apt_layer.getFeatures():
    # DBF에서 속성 읽기 (인덱스로 접근)
    fid = feature.id()
    if fid < len(seocho_apt_records):
        dbf_record = seocho_apt_records[fid]
        apt_nm = dbf_record.get('apt_nm', '')

        # 좌표
        geom = feature.geometry()
        point = geom.asPoint()

        # 기본 속성
        properties = {
            'apt_nm': apt_nm,
            'rdnmadr': dbf_record.get('rdnmadr', ''),
            'dngct': int(dbf_record.get('dngct', 0))
        }

        # 실거래가 데이터 매칭
        if apt_nm in transactions_by_complex:
            trans_list = transactions_by_complex[apt_nm]

            # 최근 거래 3개
            sorted_trans = sorted(
                trans_list,
                key=lambda x: (x['contract_ym'], x['contract_day']),
                reverse=True
            )[:3]

            # 평균 가격
            avg_price = sum(t['price_10k'] for t in sorted_trans) / len(sorted_trans)

            properties['transaction_count'] = len(trans_list)
            properties['recent_transactions'] = [
                {
                    'date': f"{t['contract_ym'][:4]}-{t['contract_ym'][4:]}-{t['contract_day']}",
                    'price_10k': t['price_10k'],
                    'price_kr': format_price_korean(t['price_10k']),
                    'area_sqm': t['area_sqm'],
                    'floor': t['floor']
                }
                for t in sorted_trans
            ]
            properties['avg_price_10k'] = int(avg_price)
            properties['avg_price_kr'] = format_price_korean(int(avg_price))

            # 평당 가격
            if sorted_trans[0]['area_sqm'] > 0:
                price_per_pyeong = (avg_price * 10000) / (sorted_trans[0]['area_sqm'] / 3.3058)
                properties['price_per_pyeong'] = int(price_per_pyeong)

            matched_count += 1
            unmatched_complexes.discard(apt_nm)

            print(f"   ✅ {apt_nm}: {len(trans_list)}건, 평균 {format_price_korean(int(avg_price))}")

        apt_features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [point.x(), point.y()]
            },
            'properties': properties
        })

print(f"\n   📊 매칭 결과:")
print(f"      총 아파트: {len(apt_features)}개")
print(f"      실거래가 매칭: {matched_count}개")
print(f"      미매칭: {len(apt_features) - matched_count}개")

if unmatched_complexes:
    print(f"\n   ⚠️  좌표를 찾지 못한 단지 ({len(unmatched_complexes)}개):")
    for name in sorted(list(unmatched_complexes)[:10]):
        print(f"      - {name}")
    if len(unmatched_complexes) > 10:
        print(f"      ... 외 {len(unmatched_complexes) - 10}개")

# 4단계: GeoJSON 저장
print("\n4️⃣  GeoJSON 저장 중...")

apt_geojson = {
    'type': 'FeatureCollection',
    'features': apt_features
}

with open(f'{output_dir}/apartments_with_prices.geojson', 'w', encoding='utf-8') as f:
    json.dump(apt_geojson, f, ensure_ascii=False, indent=2)

print(f"   ✅ 저장 완료: {len(apt_features)}개 아파트")

# 5단계: HTML 업데이트
print("\n5️⃣  HTML 업데이트 중...")

html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>서초구 지적도 + 아파트 실거래가</title>
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
        .transaction-table {
            margin-top: 10px;
            border-collapse: collapse;
            width: 100%;
        }
        .transaction-table th, .transaction-table td {
            border: 1px solid #ddd;
            padding: 5px;
            text-align: left;
            font-size: 12px;
        }
        .transaction-table th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="info-box">
        <h3 style="margin:0 0 10px 0;">서초구 아파트 실거래가</h3>
        <div>🏢 아파트: <span id="apt-count">-</span>개</div>
        <div>💰 실거래가 매칭: <span id="matched-count">-</span>개</div>
        <div>📦 필지: <span id="parcel-count">-</span>개</div>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([37.48, 127.03], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        var aptCount = 0;
        var matchedCount = 0;
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

                console.log('지적도 로드 완료:', parcelCount, '개');
            })
            .catch(err => console.error('지적도 로드 실패:', err));

        fetch('apartments_with_prices.geojson')
            .then(r => r.json())
            .then(data => {
                aptCount = data.features.length;
                document.getElementById('apt-count').innerText = aptCount;

                data.features.forEach(function(feature) {
                    if (feature.properties.transaction_count) {
                        matchedCount++;
                    }
                });
                document.getElementById('matched-count').innerText = matchedCount;

                L.geoJSON(data, {
                    pointToLayer: function(feature, latlng) {
                        var hasTransactions = feature.properties.transaction_count;
                        return L.circleMarker(latlng, {
                            radius: hasTransactions ? 8 : 5,
                            fillColor: hasTransactions ? '#0066ff' : '#cccccc',
                            color: hasTransactions ? '#003366' : '#666666',
                            weight: 2,
                            fillOpacity: hasTransactions ? 0.8 : 0.5
                        });
                    },
                    onEachFeature: function(feature, layer) {
                        var props = feature.properties;
                        var popupContent = '<div style="min-width:250px;">';
                        popupContent += '<h4 style="margin:0 0 5px 0;">' + props.apt_nm + '</h4>';
                        popupContent += '<div><b>주소:</b> ' + props.rdnmadr + '</div>';
                        popupContent += '<div><b>동수:</b> ' + props.dngct + '개</div>';

                        if (props.transaction_count) {
                            popupContent += '<hr style="margin:10px 0;">';
                            popupContent += '<div style="background:#f0f8ff; padding:5px; border-radius:3px;">';
                            popupContent += '<b>평균 거래가:</b> ' + props.avg_price_kr + '<br>';
                            popupContent += '<b>총 거래:</b> ' + props.transaction_count + '건<br>';
                            if (props.price_per_pyeong) {
                                popupContent += '<b>평당 가격:</b> ' + props.price_per_pyeong.toLocaleString() + '원';
                            }
                            popupContent += '</div>';

                            popupContent += '<div style="margin-top:10px;"><b>최근 거래:</b></div>';
                            popupContent += '<table class="transaction-table">';
                            popupContent += '<tr><th>날짜</th><th>가격</th><th>면적</th><th>층</th></tr>';

                            props.recent_transactions.forEach(function(trans) {
                                popupContent += '<tr>';
                                popupContent += '<td>' + trans.date + '</td>';
                                popupContent += '<td>' + trans.price_kr + '</td>';
                                popupContent += '<td>' + trans.area_sqm.toFixed(1) + '㎡</td>';
                                popupContent += '<td>' + trans.floor + '</td>';
                                popupContent += '</tr>';
                            });
                            popupContent += '</table>';
                        } else {
                            popupContent += '<hr style="margin:10px 0;">';
                            popupContent += '<div style="color:#999;">실거래가 정보 없음</div>';
                        }

                        popupContent += '</div>';
                        layer.bindPopup(popupContent);
                    }
                }).addTo(map);

                console.log('아파트 로드 완료:', aptCount, '개 (실거래가:', matchedCount, '개)');
            })
            .catch(err => console.error('아파트 로드 실패:', err));
    </script>
</body>
</html>'''

with open(f'{output_dir}/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("   ✅ HTML 생성 완료")

print("\n" + "=" * 70)
print("🎉 완료!")
print("=" * 70)
print(f"📂 위치: {output_dir}")
print(f"🌐 브라우저에서 Ctrl+Shift+Delete로 캐시 삭제 후")
print(f"   http://localhost:8000 새로고침 (Ctrl+F5)")
print("=" * 70)
