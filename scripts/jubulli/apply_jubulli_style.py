#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 지적도 QGIS 스타일 적용
채권최고액 기준 3색 분류:
- GREEN: 19.2-24억 (채무 부담 낮음)
- BLUE: 44.4-48억 (중간)
- RED: 52억 (채무 부담 높음)
"""

from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsRuleBasedRenderer, QgsFillSymbol,
    QgsSimpleLineSymbolLayer, QgsSimpleFillSymbolLayer
)
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt

# Shapefile 경로
shapefile_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_categorized.shp'

# 레이어 로드 (이미 로드되어 있으면 재사용)
layers = QgsProject.instance().mapLayersByName('jubulli_categorized')
if layers:
    layer = layers[0]
    print("✅ 기존 레이어 사용: jubulli_categorized")
else:
    layer = QgsVectorLayer(shapefile_path, 'jubulli_categorized', 'ogr')
    if not layer.isValid():
        print(f"❌ 레이어 로드 실패: {shapefile_path}")
        exit(1)
    QgsProject.instance().addMapLayer(layer)
    print("✅ 새 레이어 로드 완료: jubulli_categorized")

# Rule-based renderer 생성
symbol = QgsFillSymbol.createSimple({})
renderer = QgsRuleBasedRenderer(symbol)
root_rule = renderer.rootRule()

# 기본 룰 제거
for child in root_rule.children():
    root_rule.removeChild(child)

# GREEN 룰 (19.2-24억 - 채무 부담 낮음)
green_symbol = QgsFillSymbol()
green_symbol.deleteSymbolLayer(0)

green_fill = QgsSimpleFillSymbolLayer()
green_fill.setColor(QColor(152, 251, 152))  # Light green
green_fill.setStrokeColor(QColor(34, 139, 34))  # Forest green border
green_fill.setStrokeWidth(0.5)
green_fill.setStrokeStyle(Qt.SolidLine)
green_symbol.appendSymbolLayer(green_fill)

green_rule = root_rule.children()[0].clone() if root_rule.children() else root_rule.children()
green_rule = QgsRuleBasedRenderer.Rule(green_symbol)
green_rule.setLabel('GREEN (19.2-24억, 채무 부담 낮음)')
green_rule.setFilterExpression('"CATEGORY" = \'GREEN\'')
root_rule.appendChild(green_rule)

# BLUE 룰 (44.4-48억 - 중간)
blue_symbol = QgsFillSymbol()
blue_symbol.deleteSymbolLayer(0)

blue_fill = QgsSimpleFillSymbolLayer()
blue_fill.setColor(QColor(173, 216, 230))  # Light blue
blue_fill.setStrokeColor(QColor(0, 0, 139))  # Dark blue border
blue_fill.setStrokeWidth(0.5)
blue_fill.setStrokeStyle(Qt.SolidLine)
blue_symbol.appendSymbolLayer(blue_fill)

blue_rule = QgsRuleBasedRenderer.Rule(blue_symbol)
blue_rule.setLabel('BLUE (44.4-48억, 중간)')
blue_rule.setFilterExpression('"CATEGORY" = \'BLUE\'')
root_rule.appendChild(blue_rule)

# RED 룰 (52억 - 채무 부담 높음)
red_symbol = QgsFillSymbol()
red_symbol.deleteSymbolLayer(0)

red_fill = QgsSimpleFillSymbolLayer()
red_fill.setColor(QColor(255, 182, 193))  # Light pink
red_fill.setStrokeColor(QColor(139, 0, 0))  # Dark red border
red_fill.setStrokeWidth(0.5)
red_fill.setStrokeStyle(Qt.SolidLine)
red_symbol.appendSymbolLayer(red_fill)

red_rule = QgsRuleBasedRenderer.Rule(red_symbol)
red_rule.setLabel('RED (52억, 채무 부담 높음)')
red_rule.setFilterExpression('"CATEGORY" = \'RED\'')
root_rule.appendChild(red_rule)

# 렌더러 적용
layer.setRenderer(renderer)
layer.triggerRepaint()

print("✅ 스타일 적용 완료:")
print("   - GREEN: 19.2-24억 (채무 부담 낮음) - 연한 초록색")
print("   - BLUE: 44.4-48억 (중간) - 연한 파란색")
print("   - RED: 52억 (채무 부담 높음) - 연한 분홍색")

# 레이어 범위로 지도 확대
iface.mapCanvas().setExtent(layer.extent())
iface.mapCanvas().refresh()

print("✅ 지도 확대 완료")
