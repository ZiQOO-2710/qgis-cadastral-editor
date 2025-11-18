"""
필지 하이라이트 스크립트 (디버그 버전)
"""

import sys
import csv
import os

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

SHAPEFILE_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\data\AL_D160_50_20250924\AL_D160_50_20250924.shp'
CSV_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\input\행원리 지번.csv'
OUTPUT_PATH = r'C:\Users\ksj27\PROJECTS\QGIS\output\행원리_selected.shp'

JIBUN_FIELD = 'A5'
ADDR_FIELD = 'A2'
LOCATION_KEYWORD = '행원리'

# =============================================================================
# 함수
# =============================================================================

def read_jibun_list(csv_path):
    """CSV에서 지번 목록 읽기 (디버그 출력 포함)"""
    jibun_list = []

    try:
        print(f"\n📂 CSV 파일 읽기: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            print(f"파일 내용 (처음 200자):\n{repr(content[:200])}\n")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)

            # 헤더
            header = next(reader, None)
            print(f"헤더: {repr(header)}")

            # 데이터
            for i, row in enumerate(reader):
                if row and row[0].strip():
                    jibun = row[0].strip()
                    jibun_list.append(jibun)

                    if i < 5:  # 처음 5개만 출력
                        print(f"  {i+1}. '{jibun}' (len={len(jibun)}, repr={repr(jibun)})")

        print(f"\n✅ 지번 목록 읽기 완료: {len(jibun_list)}개")
        return jibun_list

    except Exception as e:
        print(f"❌ 지번 목록 읽기 오류: {e}")
        import traceback
        traceback.print_exc()
        return []


def filter_and_highlight_parcels(shapefile_path, jibun_list, location_keyword):
    """필지 필터링 (디버그 버전)"""

    # 1. 레이어 로드
    print(f"\n🔍 Shapefile 로드 중: {shapefile_path}")
    layer = QgsVectorLayer(shapefile_path, "cadastral_all", "ogr")

    if not layer.isValid():
        print("❌ 레이어 로드 실패!")
        return None

    print(f"✅ 레이어 로드 성공 (총 {layer.featureCount():,}개 필지)")

    # 2. 행원리 데이터 샘플 확인
    print(f"\n🔍 '{location_keyword}' 필지 샘플 확인:")

    sample_count = 0
    for feature in layer.getFeatures():
        addr = feature[ADDR_FIELD]
        jibun = feature[JIBUN_FIELD]

        if addr and location_keyword in addr:
            if sample_count < 5:
                print(f"  샘플 {sample_count+1}:")
                print(f"    주소: '{addr}'")
                print(f"    지번: '{jibun}' (len={len(jibun) if jibun else 0}, repr={repr(jibun)})")
                print(f"    매칭 테스트: '{jibun}' in {jibun_list[:3]}... = {jibun in jibun_list if jibun else False}")

            sample_count += 1

            if sample_count >= 5:
                break

    # 3. 매칭
    print(f"\n🔍 지번 매칭 시작...")

    matched_features = []
    matched_jibun = set()
    debug_count = 0

    for feature in layer.getFeatures():
        addr = feature[ADDR_FIELD]
        jibun = feature[JIBUN_FIELD]

        if addr and location_keyword in addr:
            jibun_clean = jibun.strip() if jibun else ""

            for target_jibun in jibun_list:
                if jibun_clean == target_jibun:
                    matched_features.append(feature)
                    matched_jibun.add(jibun_clean)

                    if debug_count < 10:
                        print(f"  ✓ 매칭 #{debug_count+1}: '{jibun_clean}' == '{target_jibun}'")
                        debug_count += 1

                    break

    print(f"\n📊 매칭 결과:")
    print(f"  - 매칭된 필지: {len(matched_features)}개")
    print(f"  - 매칭된 고유 지번: {len(matched_jibun)}개")

    if matched_jibun:
        print(f"\n매칭된 지번 샘플 (처음 20개):")
        for i, jb in enumerate(sorted(matched_jibun)[:20], 1):
            print(f"  {i}. {jb}")

    # 매칭되지 않은 지번
    unmatched = set(jibun_list) - matched_jibun
    if unmatched:
        print(f"\n⚠️  매칭되지 않은 지번 ({len(unmatched)}개, 처음 20개만 표시):")
        for i, jibun in enumerate(sorted(unmatched)[:20], 1):
            print(f"  {i}. {jibun}")

    return matched_features, layer


def create_highlighted_layer(matched_features, source_layer, output_path):
    """결과 레이어 생성"""

    if not matched_features:
        print("\n❌ 매칭된 필지가 없습니다!")
        return None

    print(f"\n💾 결과 레이어 생성 중: {output_path}")

    fields = source_layer.fields()
    crs = source_layer.crs()

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

    for feature in matched_features:
        writer.addFeature(feature)

    del writer

    print(f"✅ 레이어 생성 완료: {len(matched_features)}개 필지")

    # QGIS에 추가
    result_layer = QgsVectorLayer(output_path, "행원리_선택필지", "ogr")

    if result_layer.isValid():
        symbol = QgsFillSymbol.createSimple({
            'color': '255,0,0,80',
            'outline_color': '255,0,0,255',
            'outline_width': '0.5'
        })

        renderer = QgsSingleSymbolRenderer(symbol)
        result_layer.setRenderer(renderer)

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
    print("🗺️  필지 하이라이트 스크립트 (디버그 버전)")
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
    if matched_features:
        result_layer = create_highlighted_layer(matched_features, source_layer, OUTPUT_PATH)

        if result_layer:
            print("\n" + "="*70)
            print("✅ 모든 작업 완료!")
            print("="*70)
            print(f"\n📍 결과:")
            print(f"  - 레이어 이름: 행원리_선택필지")
            print(f"  - 필지 수: {result_layer.featureCount()}개")
            print(f"  - 저장 위치: {OUTPUT_PATH}")
    else:
        print("\n" + "="*70)
        print("⚠️  매칭된 필지가 없습니다!")
        print("="*70)
        print("\n원인 분석:")
        print("  1. CSV 지번과 Shapefile 지번 형식이 다를 수 있습니다")
        print("  2. 주소 필드에 '행원리'가 정확히 포함되지 않을 수 있습니다")
        print("  3. 지번에 보이지 않는 특수문자나 공백이 있을 수 있습니다")


if __name__ == '__main__' or __name__ == '__console__':
    main()
