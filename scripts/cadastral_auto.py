#!/usr/bin/env python3
"""
지적도 자동화 스크립트
QGIS 기반 한국 지적도 데이터 처리 및 시각화 자동화

사용법:
    python scripts/cadastral_auto.py --config projects/my_project/config.yaml

또는:
    python scripts/cadastral_auto.py --project-name myproject --parcels input/parcels.txt --output output/myproject
"""

import sys
import argparse
from pathlib import Path
import yaml
from typing import Dict, List, Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import (
    get_data_path,
    get_input_path,
    get_output_path,
    DEFAULT_CRS,
    OUTPUT_CRS,
    DBF_ENCODING
)


class CadastralAutomation:
    """지적도 자동화 클래스"""

    def __init__(self, config_path: str):
        """
        초기화

        Args:
            config_path: YAML 설정 파일 경로
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.project_name = self.config['project']['name']

    def _load_config(self) -> Dict:
        """YAML 설정 파일 로드"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"✓ 설정 파일 로드: {self.config_path}")
        print(f"  프로젝트: {config['project']['display_name']}")
        print(f"  위치: {config['project']['location']}")

        return config

    def _read_parcel_list(self, file_path: str) -> List[str]:
        """필지 목록 파일 읽기"""
        path = Path(file_path)
        if not path.exists():
            print(f"⚠ 필지 목록 파일 없음: {file_path}")
            return []

        with open(path, 'r', encoding='utf-8') as f:
            parcels = [line.strip() for line in f if line.strip()]

        print(f"✓ {path.name}: {len(parcels)}개 필지")
        return parcels

    def _clean_jibun(self, jibun: str) -> str:
        """
        지번 정리 (토지 용도 접미사 제거)
        예: "123전" → "123"
        """
        suffixes = ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목']
        for suffix in suffixes:
            if jibun.endswith(suffix):
                return jibun[:-1]
        return jibun

    def step1_extract_parcels(self):
        """1단계: 원본 shapefile에서 필지 추출 및 카테고리 분류"""
        print("\n" + "="*60)
        print("1단계: 필지 추출 및 카테고리 분류")
        print("="*60)

        from korea_cadastral import read_dbf, parse_shapefile_geometry
        import struct

        # 원본 shapefile 경로
        source_shp = self.config['input']['source_shapefile']
        source_path = Path(source_shp)

        if not source_path.exists():
            raise FileNotFoundError(f"원본 shapefile을 찾을 수 없습니다: {source_shp}")

        print(f"✓ 원본 shapefile: {source_shp}")

        # 필지 목록 읽기
        parcel_lists = self.config['input'].get('parcel_lists', {})
        categories = {}

        if parcel_lists:
            # 카테고리별 필지 목록
            for category, file_path in parcel_lists.items():
                parcels = self._read_parcel_list(file_path)
                categories[category.upper()] = parcels
        else:
            # 단일 필지 목록 (카테고리 없음)
            all_parcels_file = self.config['input'].get('all_parcels')
            if all_parcels_file:
                parcels = self._read_parcel_list(all_parcels_file)
                categories['ALL'] = parcels

        total_parcels = sum(len(p) for p in categories.values())
        print(f"총 {total_parcels}개 필지 처리 예정")

        # DBF 파일 읽기
        dbf_path = source_path.with_suffix('.dbf')
        records = read_dbf(str(dbf_path), encoding=DBF_ENCODING)
        print(f"✓ DBF 레코드: {len(records)}개")

        # 필지 매칭 및 추출
        matched_records = []
        matched_indices = []

        # PNU 필터 적용 (옵션)
        pnu_filter = self.config.get('input', {}).get('pnu_filter', None)

        for idx, record in records.items():
            # PNU 필터링 (설정된 경우)
            if pnu_filter:
                pnu = record.get('PNU', '')
                if not pnu.startswith(pnu_filter):
                    continue  # PNU가 일치하지 않으면 건너뛰기

            jibun = record.get('JIBUN', '')

            if self.config['processing'].get('clean_jibun', True):
                jibun_clean = self._clean_jibun(jibun)
            else:
                jibun_clean = jibun

            # 카테고리 찾기
            category = None
            for cat, parcel_list in categories.items():
                if jibun_clean in parcel_list or jibun in parcel_list:
                    category = cat
                    break

            if category:
                # 카테고리 정보 추가
                record['CATEGORY'] = category
                matched_records.append(record)
                matched_indices.append(idx)

        print(f"✓ 매칭된 필지: {len(matched_records)}개")

        # 지오메트리 파싱 (실제 바이트 읽기)
        shp_path = source_path
        matched_geometries = self._read_geometries(shp_path, matched_indices)
        print(f"✓ 지오메트리 추출 완료")

        # 출력 shapefile 생성
        output_dir = Path(self.config['output']['directory'])
        output_dir.mkdir(parents=True, exist_ok=True)

        output_name = f"{self.project_name}_categorized"
        output_path = output_dir / f"{output_name}.shp"

        self._write_shapefile(
            output_path,
            matched_records,
            matched_geometries,
            source_path
        )

        print(f"✓ 출력: {output_path}")

        return output_path, matched_records

    def _read_geometries(self, shp_path: Path, indices: List[int]) -> Dict[int, tuple]:
        """SHP 파일에서 특정 인덱스의 지오메트리 바이트 읽기"""
        import struct

        geometries = {}
        indices_set = set(indices)

        with open(shp_path, 'rb') as f:
            # 헤더 건너뛰기 (100 bytes)
            f.seek(100)

            current_idx = 0
            while True:
                # Record Header (8 bytes)
                record_header = f.read(8)
                if len(record_header) < 8:
                    break

                record_number, content_length = struct.unpack('>II', record_header)

                # Content (2 * content_length bytes)
                content = f.read(content_length * 2)

                # 필요한 레코드만 저장
                if current_idx in indices_set:
                    geometries[current_idx] = (record_header, content)

                current_idx += 1

                if len(geometries) >= len(indices):
                    break

        return geometries

    def _write_shapefile(self, output_path: Path, records: List[Dict],
                        geometries: Dict[int, tuple], source_path: Path):
        """Shapefile 작성"""
        import struct

        # 원본 파일에서 헤더 정보 복사
        with open(source_path.with_suffix('.shp'), 'rb') as f:
            shp_header = f.read(100)

        with open(source_path.with_suffix('.shx'), 'rb') as f:
            shx_header = f.read(100)

        with open(source_path.with_suffix('.dbf'), 'rb') as f:
            dbf_header_data = f.read(32)  # DBF 파일 헤더

        # SHP 파일 작성
        with open(output_path, 'wb') as f_shp, open(output_path.with_suffix('.shx'), 'wb') as f_shx:
            # SHP 헤더 작성
            f_shp.write(shp_header[:100])

            # SHX 헤더 작성
            f_shx.write(shx_header[:100])

            offset = 50  # 헤더 이후 시작 (words)

            # 지오메트리 레코드 작성
            for idx in sorted(geometries.keys()):
                record_header, content = geometries[idx]

                # SHP에 레코드 작성 (header + content)
                f_shp.write(record_header)
                f_shp.write(content)

                # SHX에 인덱스 작성 (offset + content_length)
                content_length = len(content) // 2
                f_shx.write(struct.pack('>I', offset))
                f_shx.write(struct.pack('>I', content_length))

                offset += 4 + content_length  # 헤더(4 words) + 콘텐츠

        # DBF 파일 작성 (CATEGORY 필드 추가)
        self._write_dbf(output_path.with_suffix('.dbf'), records, dbf_header_data)

        # PRJ 파일 복사
        prj_source = source_path.with_suffix('.prj')
        if prj_source.exists():
            import shutil
            shutil.copy(prj_source, output_path.with_suffix('.prj'))

    def _write_dbf(self, output_path: Path, records: List[Dict], header_data: bytes):
        """DBF 파일 작성 (CATEGORY 필드 포함)"""
        import struct

        # 원본 필드 구조 파싱 (CATEGORY 필드 제외)
        fields = []

        # 간단히 하드코딩된 주요 필드 사용 (실제로는 원본 DBF에서 파싱)
        # 한국 지적도 shapefile의 표준 필드 구조
        standard_fields = [
            {'name': 'PNU', 'type': 'C', 'length': 19, 'decimal': 0},
            {'name': 'JIBUN', 'type': 'C', 'length': 10, 'decimal': 0},
            {'name': 'BCHK', 'type': 'C', 'length': 1, 'decimal': 0},
            {'name': 'SGG_OID', 'type': 'N', 'length': 10, 'decimal': 0},
            {'name': 'COL_ADM_SE', 'type': 'C', 'length': 10, 'decimal': 0},
            {'name': 'JIBUN_AREA', 'type': 'N', 'length': 19, 'decimal': 9},
            # CATEGORY 필드 추가
            {'name': 'CATEGORY', 'type': 'C', 'length': 10, 'decimal': 0}
        ]

        fields = standard_fields
        num_records = len(records)

        with open(output_path, 'wb') as f:
            # DBF 헤더 (32 bytes)
            header_length = 32 + len(fields) * 32 + 1
            record_length = 1 + sum(field['length'] for field in fields)

            dbf_header = bytearray(32)
            dbf_header[0] = 0x03  # Version (dBASE III)
            dbf_header[4:8] = struct.pack('<I', num_records)
            dbf_header[8:10] = struct.pack('<H', header_length)
            dbf_header[10:12] = struct.pack('<H', record_length)

            f.write(dbf_header)

            # 필드 디스크립터 (각 필드당 32 bytes)
            for field in fields:
                field_desc = bytearray(32)

                field_name_bytes = field['name'].encode('ascii')[:11]
                field_desc[0:len(field_name_bytes)] = field_name_bytes
                field_desc[11] = ord(field['type'])
                field_desc[16] = field['length']
                field_desc[17] = field.get('decimal', 0)

                f.write(field_desc)

            # 헤더 종료 마커
            f.write(b'\r')

            # 레코드 작성
            for record_data in records:
                # 삭제 마커 (공백 = 활성 레코드)
                f.write(b' ')

                # 각 필드 값
                for field in fields:
                    value = str(record_data.get(field['name'], ''))

                    if field['type'] == 'C':
                        # Character 필드
                        value_bytes = value.encode(DBF_ENCODING, errors='ignore')[:field['length']]
                    elif field['type'] == 'N':
                        # Numeric 필드 (우측 정렬)
                        if value:
                            value = value.rjust(field['length'])
                        value_bytes = value.encode('ascii', errors='ignore')[:field['length']]
                    else:
                        value_bytes = value.encode('ascii', errors='ignore')[:field['length']]

                    # 패딩 (Character는 공백, Numeric는 공백)
                    padded = value_bytes + b' ' * (field['length'] - len(value_bytes))
                    f.write(padded)

            # 파일 종료 마커
            f.write(b'\x1A')

        print(f"  ✅ DBF 파일 작성 완료 ({num_records}개 레코드)")

    def step2_calculate_areas(self, shapefile_path: Path, records: List[Dict]):
        """2단계: 면적 계산 및 통계 생성"""
        print("\n" + "="*60)
        print("2단계: 면적 계산 및 통계")
        print("="*60)

        from korea_cadastral import sqm_to_pyeong, parse_shapefile_geometry
        import csv

        # 출력 shapefile에서 면적 계산 (실제 저장된 geometries로부터)
        geometries = parse_shapefile_geometry(str(shapefile_path))

        # 면적 계산
        stats = []
        category_totals = {}

        for idx, record in enumerate(records):
            # 지오메트리 딕셔너리에서 면적 추출
            area_sqm = geometries.get(idx, 0)

            if self.config['processing'].get('convert_to_pyeong', True):
                area_pyeong = sqm_to_pyeong(area_sqm)
            else:
                area_pyeong = None

            category = record.get('CATEGORY', 'UNKNOWN')

            stats.append({
                'jibun': record.get('JIBUN', ''),
                'pnu': record.get('PNU', ''),
                'category': category,
                'area_sqm': area_sqm,
                'area_pyeong': area_pyeong
            })

            # 카테고리별 합계
            if category not in category_totals:
                category_totals[category] = {'count': 0, 'area_sqm': 0, 'area_pyeong': 0}

            category_totals[category]['count'] += 1
            category_totals[category]['area_sqm'] += area_sqm
            if area_pyeong:
                category_totals[category]['area_pyeong'] += area_pyeong

        # CSV 출력
        output_dir = Path(self.config['output']['directory'])
        csv_path = output_dir / f"{self.project_name}_areas.csv"

        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['jibun', 'pnu', 'category', 'area_sqm', 'area_pyeong'])
            writer.writeheader()
            writer.writerows(stats)

        print(f"✓ 면적 통계 CSV: {csv_path}")

        # 카테고리별 통계 출력
        print("\n카테고리별 통계:")
        for category, totals in category_totals.items():
            print(f"  {category}: {totals['count']}필지, "
                  f"{totals['area_sqm']:,.0f}㎡ ({totals['area_pyeong']:,.2f}평)")

        return stats

    def step3_create_webmap(self, shapefile_path: Path, records: List[Dict]):
        """3단계: 웹맵 생성 (Leaflet)"""
        if 'webmap' not in self.config['output']['formats']:
            print("\n웹맵 생성 건너뛰기 (설정에서 비활성화됨)")
            return

        print("\n" + "="*60)
        print("3단계: 웹맵 생성")
        print("="*60)

        try:
            from pyproj import Transformer
            import json
        except ImportError as e:
            print(f"⚠ 필수 라이브러리 미설치: {e}")
            print("  웹맵 생성을 건너뜁니다. (pyproj 설치 필요: pip install pyproj)")
            return

        # 좌표 변환기 (EPSG:5186 → EPSG:4326)
        transformer = Transformer.from_crs(DEFAULT_CRS, OUTPUT_CRS, always_xy=True)

        # 지오메트리 바이트 읽기 (모든 레코드에 대해)
        all_indices = list(range(len(records)))
        geometries_dict = self._read_geometries(shapefile_path, all_indices)

        # GeoJSON 생성
        features = []

        for idx, record in enumerate(records):
            # 지오메트리 바이트 가져오기
            if idx not in geometries_dict:
                continue

            geom_header, geom_content = geometries_dict[idx]

            # Shapefile 지오메트리에서 좌표 추출
            try:
                import struct

                # Shape type (4 bytes, 지오메트리 content 시작부분)
                geom_data = geom_content

                # Shape type (4 bytes)
                shape_type = struct.unpack('<i', geom_data[0:4])[0]

                if shape_type == 5:  # Polygon
                    # Bounding box 건너뛰기 (32 bytes)
                    num_parts = struct.unpack('<i', geom_data[36:40])[0]
                    num_points = struct.unpack('<i', geom_data[40:44])[0]

                    # Parts array 건너뛰기
                    points_start = 44 + num_parts * 4

                    # Points array 읽기
                    coords = []
                    for i in range(num_points):
                        offset = points_start + i * 16
                        x = struct.unpack('<d', geom_data[offset:offset+8])[0]
                        y = struct.unpack('<d', geom_data[offset+8:offset+16])[0]

                        # 좌표 변환
                        lon, lat = transformer.transform(x, y)
                        coords.append([lon, lat])

                    # GeoJSON Feature 생성
                    feature = {
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [coords]
                        },
                        'properties': {
                            'jibun': record.get('JIBUN', ''),
                            'pnu': record.get('PNU', ''),
                            'category': record.get('CATEGORY', 'UNKNOWN'),
                            'area_sqm': record.get('JIBUN_AREA', 0)
                        }
                    }

                    features.append(feature)

            except Exception as e:
                print(f"  ⚠ 지오메트리 {idx} 파싱 실패: {e}")
                continue

        # GeoJSON 저장
        output_dir = Path(self.config['output']['directory']) / 'webmap'
        output_dir.mkdir(parents=True, exist_ok=True)

        geojson_path = output_dir / 'parcels.geojson'

        geojson_data = {
            'type': 'FeatureCollection',
            'features': features
        }

        with open(geojson_path, 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f, ensure_ascii=False, indent=2)

        print(f"✓ GeoJSON 생성: {geojson_path} ({len(features)}개 필지)")

        # HTML 생성
        html_path = output_dir / 'index.html'
        self._create_webmap_html(html_path)

        print(f"✓ 웹맵 HTML: {html_path}")
        print(f"\n💡 웹맵 확인: file://{html_path.absolute()}")

    def _create_webmap_html(self, output_path: Path):
        """Leaflet 웹맵 HTML 생성"""
        import json

        style_config = self.config.get('style', {}).get('categories', {})
        project_name = self.config['project']['display_name']
        location = self.config['project']['location']

        # 카테고리별 색상 매핑
        category_colors = {}
        for category, style in style_config.items():
            category_colors[category.upper()] = {
                'color': style.get('color', '#CCCCCC'),
                'label': style.get('label', category)
            }

        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{project_name} - 지적도 웹맵</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: 'Malgun Gothic', sans-serif; }}
        #map {{ width: 100%; height: 100vh; }}
        .info-box {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            z-index: 1000;
            max-width: 300px;
        }}
        .info-box h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
        }}
        .info-box .location {{
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
        }}
        .legend {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 8px;
            border: 1px solid #333;
        }}
    </style>
</head>
<body>
    <div class="info-box">
        <h3>{project_name}</h3>
        <div class="location">📍 {location}</div>
        <div>📦 필지 수: <span id="parcel-count">-</span>개</div>
        <div class="legend">
            <div style="font-weight: bold; margin-bottom: 5px;">범례</div>
'''

        # 범례 항목 추가
        for category, colors in category_colors.items():
            html_content += f'''            <div class="legend-item">
                <div class="legend-color" style="background-color: {colors['color']};"></div>
                <span>{colors['label']}</span>
            </div>
'''

        html_content += '''        </div>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map');

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);

        var categoryColors = ''' + json.dumps(category_colors) + ''';

        fetch('parcels.geojson')
            .then(r => r.json())
            .then(data => {
                var parcelCount = data.features.length;
                document.getElementById('parcel-count').innerText = parcelCount;

                var parcelLayer = L.geoJSON(data, {
                    style: function(feature) {
                        var category = feature.properties.category || 'UNKNOWN';
                        var colorInfo = categoryColors[category] || {color: '#CCCCCC'};

                        return {
                            fillColor: colorInfo.color,
                            fillOpacity: 0.6,
                            color: '#333',
                            weight: 1
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        var props = feature.properties;
                        var category = props.category || 'UNKNOWN';
                        var categoryLabel = (categoryColors[category] || {}).label || category;

                        var popupContent = '<div style="min-width:200px;">' +
                            '<h4 style="margin:0 0 5px 0;">필지: ' + props.jibun + '</h4>' +
                            '<div><b>PNU:</b> ' + props.pnu + '</div>' +
                            '<div><b>카테고리:</b> ' + categoryLabel + '</div>' +
                            '<div><b>면적:</b> ' + Number(props.area_sqm).toLocaleString() + ' ㎡</div>' +
                            '</div>';

                        layer.bindPopup(popupContent);
                    }
                }).addTo(map);

                map.fitBounds(parcelLayer.getBounds());
                console.log('필지 로드 완료:', parcelCount, '개');
            })
            .catch(err => console.error('GeoJSON 로드 실패:', err));
    </script>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        import json

    def step4_create_qgis_outputs(self, shapefile_path: Path):
        """4단계: QGIS 출력물 생성 (QML, PNG, PDF)"""
        qgis_formats = {'qml', 'png', 'pdf'} & set(self.config['output']['formats'])

        if not qgis_formats:
            print("\nQGIS 출력물 생성 건너뛰기 (설정에서 비활성화됨)")
            return

        print("\n" + "="*60)
        print("4단계: QGIS 출력물 생성")
        print("="*60)

        print("⚠ QGIS 출력물은 QGIS Python 콘솔에서 수동으로 실행하거나,")
        print("  Claude Desktop의 QGIS MCP를 통해 생성할 수 있습니다.")

        # PyQGIS 스크립트 생성
        script_path = self._generate_qgis_script(shapefile_path)
        print(f"\n생성된 PyQGIS 스크립트: {script_path}")
        print("\nQGIS Python 콘솔에서 다음 명령으로 실행:")
        print(f"  exec(open(r'{script_path}', encoding='utf-8').read())")

    def _generate_qgis_script(self, shapefile_path: Path) -> Path:
        """PyQGIS 스크립트 자동 생성"""
        output_dir = Path(self.config['output']['directory'])
        script_path = output_dir / f"{self.project_name}_qgis_script.py"

        style_config = self.config.get('style', {}).get('categories', {})

        script_content = f'''"""
자동 생성된 QGIS 스크립트
프로젝트: {self.config['project']['display_name']}
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRuleBasedRenderer,
    QgsFillSymbol, QgsRendererCategory
)
from qgis.PyQt.QtGui import QColor

# 레이어 로드
layer_path = r"{shapefile_path.absolute()}"
layer = QgsVectorLayer(layer_path, "{self.project_name}", "ogr")

if not layer.isValid():
    print("❌ 레이어 로드 실패")
else:
    # 프로젝트에 추가
    QgsProject.instance().addMapLayer(layer)
    print("✓ 레이어 추가:", layer.name())

    # 카테고리별 스타일 적용
    categories = []
'''

        # 카테고리별 스타일 추가
        for category, style in style_config.items():
            color = style.get('color', '#CCCCCC')
            label = style.get('label', category)
            opacity = style.get('opacity', 0.6)

            script_content += f'''
    # {category.upper()} 카테고리
    symbol_{category} = QgsFillSymbol.createSimple({{
        'color': '{color}',
        'style': 'solid',
        'outline_color': 'black',
        'outline_style': 'solid',
        'outline_width': '0.26'
    }})
    symbol_{category}.setOpacity({opacity})
    cat_{category} = QgsRendererCategory('{category.upper()}', symbol_{category}, '{label}')
    categories.append(cat_{category})
'''

        script_content += '''
    # 렌더러 적용
    renderer = QgsCategorizedSymbolRenderer('CATEGORY', categories)
    layer.setRenderer(renderer)
    layer.triggerRepaint()

    print("✓ 스타일 적용 완료")

    # 레이어로 줌
    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()
    print("✓ 레이어로 줌 완료")
'''

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        return script_path

    def run(self):
        """전체 워크플로우 실행"""
        print("\n" + "🚀 "*20)
        print(f"지적도 자동화 시작: {self.config['project']['display_name']}")
        print("🚀 "*20 + "\n")

        try:
            # 1단계: 필지 추출
            shapefile_path, records = self.step1_extract_parcels()

            # 2단계: 면적 계산
            stats = self.step2_calculate_areas(shapefile_path, records)

            # 3단계: 웹맵 생성
            self.step3_create_webmap(shapefile_path, records)

            # 4단계: QGIS 출력물
            self.step4_create_qgis_outputs(shapefile_path)

            print("\n" + "✅ "*20)
            print("자동화 완료!")
            print("✅ "*20 + "\n")

            print(f"출력 디렉토리: {self.config['output']['directory']}")

        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return 1

        return 0


def main():
    """CLI 진입점"""
    parser = argparse.ArgumentParser(
        description='QGIS 기반 한국 지적도 자동화 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예시:
  # 설정 파일로 실행
  %(prog)s --config projects/myproject/config.yaml

  # 빠른 실행 (간단한 옵션)
  %(prog)s --project-name myproject --parcels input/parcels.txt --source data/source.shp

자세한 설정은 config.example.yaml 참조
        '''
    )

    parser.add_argument(
        '--config', '-c',
        help='YAML 설정 파일 경로'
    )

    parser.add_argument(
        '--project-name', '-p',
        help='프로젝트 이름 (영문)'
    )

    parser.add_argument(
        '--parcels',
        help='필지 목록 파일 경로'
    )

    parser.add_argument(
        '--source', '-s',
        help='원본 shapefile 경로'
    )

    args = parser.parse_args()

    if args.config:
        # 설정 파일로 실행
        automation = CadastralAutomation(args.config)
        return automation.run()

    elif args.project_name and args.parcels and args.source:
        # TODO: 간단한 옵션으로 임시 설정 생성 후 실행
        print("❌ 빠른 실행 모드는 추후 구현 예정")
        print("현재는 --config 옵션을 사용하세요")
        return 1

    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
