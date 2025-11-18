"""
내부 필지 경계선 제거, 전체 사업지 외곽선만 노란색으로 표시
"""
from qgis.core import QgsProject, QgsFillSymbol
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
import processing

layer = QgsProject.instance().mapLayersByName('모듈러주택 사업지')[0]

# 1. 각 카테고리 심볼의 테두리를 투명하게 설정
renderer = layer.renderer()
for rule in renderer.rootRule().children():
    symbol = rule.symbol()
    symbol_layer = symbol.symbolLayer(0)
    # 채우기 색상은 유지, 테두리만 투명
    symbol_layer.setStrokeColor(QColor(255, 255, 255, 0))  # 완전 투명
    symbol_layer.setStrokeWidth(0)

layer.triggerRepaint()

# 2. Processing으로 전체 필지를 하나로 합치기 (Dissolve)
result = processing.run("native:dissolve", {
    'INPUT': layer,
    'FIELD': [],
    'OUTPUT': 'memory:'
})

dissolved_layer = result['OUTPUT']
dissolved_layer.setName('사업지 외곽선')

# 3. Dissolve된 레이어에 노란색 외곽선 스타일 적용
symbol = QgsFillSymbol.createSimple({
    'color': '255,255,255,0',  # 채우기 투명
    'outline_color': 'yellow',  # 노란색 외곽선
    'outline_width': '1.5',
    'outline_style': 'solid'
})

from qgis.core import QgsSingleSymbolRenderer
dissolved_layer.setRenderer(QgsSingleSymbolRenderer(symbol))

# 4. 프로젝트에 추가
QgsProject.instance().addMapLayer(dissolved_layer)

print("✅ 내부 경계선 제거, 외곽선만 노란색으로 표시 완료!")
