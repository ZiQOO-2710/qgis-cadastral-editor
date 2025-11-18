"""
QGIS Python 콘솔에서 실행하여 생성된 shapefile 테스트

사용법:
1. QGIS 실행
2. Python 콘솔 열기 (Ctrl+Alt+P)
3. 다음 명령 실행:
   exec(open(r'C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/test_in_qgis.py', encoding='utf-8').read())
"""

from pathlib import Path
from qgis.core import QgsVectorLayer, QgsProject

# 프로젝트 경로
project_dir = Path(r'C:/Users/ksj27/PROJECTS/qgis-cadastral-editor')
shapefile = project_dir / 'output' / 'jubulli_categorized.shp'

print("=" * 60)
print("주북리 필지 Shapefile 테스트")
print("=" * 60)

# Shapefile 로드
layer = QgsVectorLayer(str(shapefile), '주북리 필지', 'ogr')

if not layer.isValid():
    print("❌ Shapefile 로드 실패!")
    print(f"   경로: {shapefile}")
else:
    print(f"✅ Shapefile 로드 성공")
    print(f"   경로: {shapefile}")
    print(f"   필지 개수: {layer.featureCount()}개")
    print(f"   좌표계: {layer.crs().authid()}")

    # 필드 확인
    print(f"\n📋 필드 목록:")
    for field in layer.fields():
        print(f"   - {field.name()} ({field.typeName()})")

    # CATEGORY 필드 확인
    if 'CATEGORY' in [f.name() for f in layer.fields()]:
        print(f"\n✅ CATEGORY 필드 존재")

        # 카테고리별 개수
        categories = {}
        for feature in layer.getFeatures():
            cat = feature['CATEGORY']
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\n📊 카테고리별 필지 개수:")
        for cat, count in sorted(categories.items()):
            print(f"   {cat}: {count}개")
    else:
        print(f"\n❌ CATEGORY 필드 없음")

    # 프로젝트에 레이어 추가
    QgsProject.instance().addMapLayer(layer)
    print(f"\n✅ 레이어를 QGIS 프로젝트에 추가했습니다")

    # 레이어로 화면 이동
    canvas = iface.mapCanvas()
    canvas.setExtent(layer.extent())
    canvas.refresh()
    print(f"✅ 레이어 범위로 화면 이동")

print("=" * 60)
print("테스트 완료!")
print("=" * 60)
