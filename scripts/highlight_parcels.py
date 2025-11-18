"""
필지 하이라이트 스크립트
행원리 지번 목록에 해당하는 필지를 지도에 표시

사용법:
1. QGIS 프로그램 열기
2. Python Console (Ctrl+Alt+P) 열기
3. 이 스크립트 로드하여 실행
"""

import sys
import csv
import os

# QGIS 라이브러리
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsFields,
    QgsWkbTypes,
    QgsSymbol,
    QgsSingleSymbolRenderer,
    QgsFillSymbol,
    QgsCoordinateReferenceSystem
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor

# =============================================================================
# 설정
# =============================================================================

# 파일 경로
SHAPEFILE_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\data\AL_D160_50_20250924\AL_D160_50_20250924.shp'
CSV_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\input\행원리 지번.csv'
OUTPUT_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\output\행원리_selected.shp'

# 필드 설정
JIBUN_FIELD = 'A5'  # 지번 필드
ADDR_FIELD = 'A2'   # 주소 필드

# 검색 키워드
LOCATION_KEYWORD = '행원리'

# =============================================================================
# 함수
# =============================================================================

def read_jibun_list(csv_path):
    """CSV에서 지번 목록 읽기"""
    jibun_list = []

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)

            # 헤더 건너뛰기
            next(reader, None)

            for row in reader:
                if row and row[0].strip():
                    jibun = row[0].strip()
                    jibun_list.append(jibun)

        print(f"✅ 지번 목록 읽기 완료: {len(jibun_list)}개")
        return jibun_list

    except Exception as e:
        print(f"❌ 지번 목록 읽기 오류: {e}")
        return []


def filter_and_highlight_parcels(shapefile_path, jibun_list, location_keyword):
    """필지 필터링 및 하이라이트"""

    # 1. 레이어 로드
    print(f"\n🔍 Shapefile 로드 중: {shapefile_path}")
    layer = QgsVectorLayer(shapefile_path, "cadastral_all", "ogr")

    if not layer.isValid():
        print("❌ 레이어 로드 실패!")
        return None

    print(f"✅ 레이어 로드 성공 (총 {layer.featureCount():,}개 필지)")

    # 2. 필드 확인
    field_names = [field.name() for field in layer.fields()]
    print(f"\n📋 사용 가능한 필드: {', '.join(field_names)}")

    if JIBUN_FIELD not in field_names:
        print(f"❌ '{JIBUN_FIELD}' 필드를 찾을 수 없습니다!")
        return None

    # 3. 매칭된 필지 찾기
    print(f"\n🔍 '{location_keyword}' 지역에서 지번 매칭 중...")

    matched_features = []
    matched_jibun = set()

    for feature in layer.getFeatures():
        addr = feature[ADDR_FIELD]
        jibun = feature[JIBUN_FIELD]

        # 주소에 지역 키워드가 있고, 지번이 목록에 있는 경우
        if addr and location_keyword in addr:
            # 지번 매칭 (공백 제거 후 비교)
            jibun_clean = jibun.strip() if jibun else ""

            for target_jibun in jibun_list:
                if jibun_clean == target_jibun:
                    matched_features.append(feature)
                    matched_jibun.add(jibun_clean)
                    print(f"  ✓ 발견: {addr} - {jibun}")
                    break

    print(f"\n📊 매칭 결과:")
    print(f"  - 매칭된 필지: {len(matched_features)}개")
    print(f"  - 매칭된 고유 지번: {len(matched_jibun)}개")
    print(f"  - 입력 지번: {len(jibun_list)}개")

    # 매칭되지 않은 지번 출력
    unmatched = set(jibun_list) - matched_jibun
    if unmatched:
        print(f"\n⚠️  매칭되지 않은 지번 ({len(unmatched)}개):")
        for jibun in sorted(unmatched):
            print(f"  - {jibun}")

    return matched_features, layer


def create_highlighted_layer(matched_features, source_layer, output_path):
    """매칭된 필지로 새 레이어 생성"""

    if not matched_features:
        print("\n❌ 매칭된 필지가 없습니다!")
        return None

    print(f"\n💾 결과 레이어 생성 중: {output_path}")

    # 1. 필드 정의 (원본 레이어와 동일)
    fields = source_layer.fields()

    # 2. 레이어 생성
    crs = source_layer.crs()
    geometry_type = source_layer.geometryType()

    # 3. Shapefile 작성
    writer = QgsVectorFileWriter.create(
        output_path,
        fields,
        QgsWkbTypes.Polygon,
        crs,
        QgsCoordinateTransformContext(),
        QgsVectorFileWriter.SaveVectorOptions()
    )

    if writer.hasError():
        print(f"❌ 레이어 생성 오류: {writer.errorMessage()}")
        return None

    # 4. 피처 추가
    for feature in matched_features:
        writer.addFeature(feature)

    del writer  # 파일 닫기

    print(f"✅ 레이어 생성 완료: {len(matched_features)}개 필지")

    # 5. QGIS에 레이어 추가
    result_layer = QgsVectorLayer(output_path, "행원리_선택필지", "ogr")

    if result_layer.isValid():
        # 스타일 설정 (빨간색 하이라이트)
        symbol = QgsFillSymbol.createSimple({
            'color': '255,0,0,80',  # 반투명 빨간색
            'outline_color': '255,0,0,255',  # 진한 빨간색 테두리
            'outline_width': '0.5'
        })

        renderer = QgsSingleSymbolRenderer(symbol)
        result_layer.setRenderer(renderer)

        # 프로젝트에 추가
        QgsProject.instance().addMapLayer(result_layer)

        print("✅ QGIS 프로젝트에 레이어 추가 완료!")
        return result_layer
    else:
        print("❌ 결과 레이어 로드 실패!")
        return None


# =============================================================================
# 메인 실행
# =============================================================================

def main():
    """메인 실행 함수"""

    print("="*70)
    print("🗺️  필지 하이라이트 스크립트")
    print("="*70)

    # 1. 지번 목록 읽기
    jibun_list = read_jibun_list(CSV_PATH)

    if not jibun_list:
        print("❌ 지번 목록이 비어있습니다!")
        return

    # 2. 필지 필터링
    result = filter_and_highlight_parcels(SHAPEFILE_PATH, jibun_list, LOCATION_KEYWORD)

    if not result:
        return

    matched_features, source_layer = result

    # 3. 결과 레이어 생성
    result_layer = create_highlighted_layer(matched_features, source_layer, OUTPUT_PATH)

    if result_layer:
        print("\n" + "="*70)
        print("✅ 모든 작업 완료!")
        print("="*70)
        print(f"\n📍 결과:")
        print(f"  - 레이어 이름: 행원리_선택필지")
        print(f"  - 필지 수: {result_layer.featureCount()}개")
        print(f"  - 저장 위치: {OUTPUT_PATH}")
        print(f"\n💡 QGIS 맵 캔버스에서 빨간색으로 하이라이트된 필지를 확인하세요!")


# 스크립트 실행
if __name__ == '__main__' or __name__ == '__console__':
    main()
