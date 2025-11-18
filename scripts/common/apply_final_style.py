"""
최종 스타일 적용 (검증됨)
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsSymbol, QgsFillSymbol,
    QgsRuleBasedRenderer, QgsSingleSymbolRenderer,
    QgsTextFormat, QgsVectorLayerSimpleLabeling, QgsPalLayerSettings
)
from qgis.PyQt.QtGui import QColor
from qgis.utils import iface

# 1. 기존 레이어 제거
project = QgsProject.instance()
layers_to_remove = []
for layer in project.mapLayers().values():
    if '모듈러' in layer.name() or '사업지' in layer.name():
        layers_to_remove.append(layer.id())

for layer_id in layers_to_remove:
    project.removeMapLayer(layer_id)

print("기존 레이어 제거 완료")

# 2. 새 shapefile 로드 (65개만 있는 파일)
shp_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/haengwonri_final.shp'
layer = QgsVectorLayer(shp_path, '모듈러주택 사업지', 'ogr')

if not layer.isValid():
    print("❌ 레이어 로드 실패!")
    print(f"경로: {shp_path}")
else:
    print(f"✅ 레이어 로드 성공 ({layer.featureCount()}개 필지)")

    # 3. Rule-based renderer 설정
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    renderer = QgsRuleBasedRenderer(symbol)
    root_rule = renderer.rootRule()

    # 초록색 규칙
    green_symbol = QgsFillSymbol.createSimple({
        'color': '34,139,34,180',
        'outline_color': '0,100,0,255',
        'outline_width': '0.8',
        'outline_style': 'solid',
        'style': 'solid'
    })
    green_rule = root_rule.children()[0].clone()
    green_rule.setSymbol(green_symbol)
    green_rule.setFilterExpression('"CATEGORY" = \'GREEN\'')
    green_rule.setLabel('제주시추천+국공유지')
    root_rule.appendChild(green_rule)

    # 파란색 규칙
    blue_symbol = QgsFillSymbol.createSimple({
        'color': '65,105,225,180',
        'outline_color': '0,0,139,255',
        'outline_width': '0.8',
        'outline_style': 'solid',
        'style': 'solid'
    })
    blue_rule = root_rule.children()[0].clone()
    blue_rule.setSymbol(blue_symbol)
    blue_rule.setFilterExpression('"CATEGORY" = \'BLUE\'')
    blue_rule.setLabel('일반 사유지')
    root_rule.appendChild(blue_rule)

    # 빨간색 규칙
    red_symbol = QgsFillSymbol.createSimple({
        'color': '220,20,60,180',
        'outline_color': '139,0,0,255',
        'outline_width': '0.8',
        'outline_style': 'solid',
        'style': 'solid'
    })
    red_rule = root_rule.children()[0].clone()
    red_rule.setSymbol(red_symbol)
    red_rule.setFilterExpression('"CATEGORY" = \'RED\'')
    red_rule.setLabel('기개발 사유지')
    root_rule.appendChild(red_rule)

    # 기본 규칙 제거
    root_rule.removeChildAt(0)

    # renderer 적용
    layer.setRenderer(renderer)

    # 4. 레이블 설정
    text_format = QgsTextFormat()
    text_format.setSize(10)
    text_format.setColor(QColor(0, 0, 0))

    label_settings = QgsPalLayerSettings()
    label_settings.fieldName = '"A5" || \'\\n\' || format_number("A22", 0) || \'㎡\''
    label_settings.isExpression = True
    label_settings.enabled = True
    label_settings.setFormat(text_format)

    labeling = QgsVectorLayerSimpleLabeling(label_settings)
    layer.setLabeling(labeling)
    layer.setLabelsEnabled(True)

    # 5. 프로젝트에 레이어 추가
    project.addMapLayer(layer)
    print("✅ 메인 레이어 추가 완료")

    # 6. 노란색 테두리 레이어
    border_layer = QgsVectorLayer(shp_path, '사업지 전체 테두리', 'ogr')

    if border_layer.isValid():
        border_symbol = QgsFillSymbol.createSimple({
            'color': '0,0,0,0',
            'outline_color': '255,215,0,255',
            'outline_width': '3.0',
            'outline_style': 'solid',
            'style': 'solid'
        })

        border_renderer = QgsSingleSymbolRenderer(border_symbol)
        border_layer.setRenderer(border_renderer)

        project.addMapLayer(border_layer)
        print("✅ 테두리 레이어 추가 완료")

        # 7. 범위 조정
        extent = layer.extent()
        print(f"\n레이어 범위: {extent.toString()}")
        iface.mapCanvas().setExtent(extent)
        iface.mapCanvas().zoomByFactor(1.2)
        iface.mapCanvas().refresh()

    print("\n" + "="*60)
    print("🎨 스타일 적용 완료!")
    print("="*60)
    print("🟢 초록색: 제주시추천 + 국공유지")
    print("🔵 파란색: 일반 사유지")
    print("🔴 빨간색: 기개발 사유지")
    print("🟡 노란색: 전체 사업지 테두리")
    print("="*60)
