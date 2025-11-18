"""
올인원 자동화 스크립트
- 스타일 적용 → 라벨 제거 → 외곽선 표시 → 레이아웃 생성 → PNG 자동 내보내기
"""
from qgis.core import (
    QgsProject, QgsRuleBasedRenderer, QgsFillSymbol, QgsSymbol,
    QgsPrintLayout, QgsLayoutExporter, QgsLayoutItemMap, QgsLayoutItemLabel,
    QgsLayoutItemLegend, QgsLayoutPoint, QgsLayoutSize, QgsLayoutMeasurement,
    QgsUnitTypes, QgsSingleSymbolRenderer
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QRectF, Qt
import processing

print("=" * 70)
print("🚀 올인원 자동화 시작")
print("=" * 70)

# =============================================================================
# 1단계: 레이어 가져오기
# =============================================================================
project = QgsProject.instance()
layer = project.mapLayersByName('모듈러주택 사업지')[0]
print("✅ 1단계: 레이어 로드 완료")

# =============================================================================
# 2단계: 카테고리별 스타일 적용 (3색 + 테두리 투명)
# =============================================================================
# GREEN 심볼
green_symbol = QgsFillSymbol.createSimple({
    'color': '144,238,144,255',
    'outline_color': '255,255,255,0',
    'outline_width': '0'
})

# BLUE 심볼
blue_symbol = QgsFillSymbol.createSimple({
    'color': '135,206,250,255',
    'outline_color': '255,255,255,0',
    'outline_width': '0'
})

# RED 심볼
red_symbol = QgsFillSymbol.createSimple({
    'color': '255,99,71,255',
    'outline_color': '255,255,255,0',
    'outline_width': '0'
})

# 기본 심볼 (매칭 안되는 것)
default_symbol = QgsFillSymbol.createSimple({
    'color': '200,200,200,255',
    'outline_color': '255,255,255,0',
    'outline_width': '0'
})

# Rule-based renderer 생성
renderer = QgsRuleBasedRenderer(default_symbol)
root_rule = renderer.rootRule()

# GREEN 룰
green_rule = root_rule.children()[0].clone()
green_rule.setFilterExpression('"CATEGORY" = \'GREEN\'')
green_rule.setLabel('제주시추천+국공유지')
green_rule.setSymbol(green_symbol)
root_rule.appendChild(green_rule)

# BLUE 룰
blue_rule = root_rule.children()[0].clone()
blue_rule.setFilterExpression('"CATEGORY" = \'BLUE\'')
blue_rule.setLabel('일반 사유지')
blue_rule.setSymbol(blue_symbol)
root_rule.appendChild(blue_rule)

# RED 룰
red_rule = root_rule.children()[0].clone()
red_rule.setFilterExpression('"CATEGORY" = \'RED\'')
red_rule.setLabel('기개발 사유지')
red_rule.setSymbol(red_symbol)
root_rule.appendChild(red_rule)

# 기본 룰 제거
root_rule.removeChildAt(0)

layer.setRenderer(renderer)
layer.triggerRepaint()
print("✅ 2단계: 카테고리별 스타일 적용 완료")

# =============================================================================
# 3단계: 라벨 제거
# =============================================================================
layer.setLabelsEnabled(False)
layer.triggerRepaint()
print("✅ 3단계: 라벨 제거 완료")

# =============================================================================
# 4단계: 외곽선 레이어 생성
# =============================================================================
result = processing.run("native:dissolve", {
    'INPUT': layer,
    'FIELD': [],
    'OUTPUT': 'memory:'
})

dissolved_layer = result['OUTPUT']
dissolved_layer.setName('사업지 외곽선')

# 노란색 외곽선 스타일
outline_symbol = QgsFillSymbol.createSimple({
    'color': '255,255,255,0',
    'outline_color': 'yellow',
    'outline_width': '1.5',
    'outline_style': 'solid'
})

dissolved_layer.setRenderer(QgsSingleSymbolRenderer(outline_symbol))
project.addMapLayer(dissolved_layer)
print("✅ 4단계: 외곽선 레이어 생성 완료")

# =============================================================================
# 5단계: 통계 계산
# =============================================================================
stats = {
    'GREEN': {'count': 0, 'area': 0, 'label': '제주시추천+국공유지'},
    'BLUE': {'count': 0, 'area': 0, 'label': '일반 사유지'},
    'RED': {'count': 0, 'area': 0, 'label': '기개발 사유지'}
}

for feature in layer.getFeatures():
    category = feature['CATEGORY']
    area = float(feature['A22']) if feature['A22'] else 0

    if category in stats:
        stats[category]['count'] += 1
        stats[category]['area'] += area

total_area = sum(s['area'] for s in stats.values())
total_count = sum(s['count'] for s in stats.values())
print("✅ 5단계: 통계 계산 완료")

# =============================================================================
# 6단계: Print Layout 생성
# =============================================================================
layout_manager = project.layoutManager()
layout_name = '모듈러주택_사업지_지도'

# 기존 레이아웃 제거
existing_layout = layout_manager.layoutByName(layout_name)
if existing_layout:
    layout_manager.removeLayout(existing_layout)

# 새 레이아웃 생성
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName(layout_name)
layout_manager.addLayout(layout)

# 6-1. 제목
title_item = QgsLayoutItemLabel(layout)
title_item.attemptSetSceneRect(QRectF(10, 5, 190, 8))
title_item.setText('제주시 구좌읍 행원리 모듈러주택 시범사업 구역')

title_font = QFont('맑은 고딕', 14)
title_font.setBold(True)
title_item.setFont(title_font)
title_item.setHAlign(Qt.AlignCenter)

layout.addLayoutItem(title_item)

# 6-2. 지도 프레임
map_item = QgsLayoutItemMap(layout)
map_item.attemptSetSceneRect(QRectF(10, 15, 190, 185))
map_item.setFrameEnabled(True)
map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

extent = layer.extent()
extent.scale(1.1)
map_item.setExtent(extent)

layout.addLayoutItem(map_item)

# 6-3. 통계 표 (QgsLayoutItemLabel 그리드)
table_data = [
    ['구분', '필지수', '면적(㎡)', '면적(평)', '비율'],
    [f"제주시\n추천+국공유지",
     str(stats['GREEN']['count']),
     f"{stats['GREEN']['area']:,.0f}",
     f"{stats['GREEN']['area']/3.3058:,.0f}",
     f"{stats['GREEN']['area']/total_area*100:.1f}%"],
    [f"일반\n사유지",
     str(stats['BLUE']['count']),
     f"{stats['BLUE']['area']:,.0f}",
     f"{stats['BLUE']['area']/3.3058:,.0f}",
     f"{stats['BLUE']['area']/total_area*100:.1f}%"],
    [f"기개발\n사유지",
     str(stats['RED']['count']),
     f"{stats['RED']['area']:,.0f}",
     f"{stats['RED']['area']/3.3058:,.0f}",
     f"{stats['RED']['area']/total_area*100:.1f}%"],
    ['합계',
     str(total_count),
     f"{total_area:,.0f}",
     f"{total_area/3.3058:,.0f}",
     '100.0%']
]

start_x = 205
start_y = 30
col_widths = [25, 12, 16, 16, 16]
row_height = 20

for row_idx, row_data in enumerate(table_data):
    y_pos = start_y + (row_idx * row_height)
    x_pos = start_x

    for col_idx, cell_text in enumerate(row_data):
        cell = QgsLayoutItemLabel(layout)
        cell.attemptSetSceneRect(QRectF(x_pos, y_pos, col_widths[col_idx], row_height))
        cell.setText(cell_text)

        if row_idx == 0:  # 헤더
            cell_font = QFont('맑은 고딕', 9)
            cell_font.setBold(True)
            cell.setFont(cell_font)
            cell.setBackgroundEnabled(True)
            cell.setBackgroundColor(QColor(230, 230, 230))
            cell.setHAlign(Qt.AlignCenter)
        else:  # 데이터 행
            cell_font = QFont('맑은 고딕', 8)
            cell.setFont(cell_font)
            if col_idx == 0:
                cell.setHAlign(Qt.AlignLeft)
            else:
                cell.setHAlign(Qt.AlignRight)

        cell.setVAlign(Qt.AlignVCenter)
        cell.setFrameEnabled(True)
        cell.setFrameStrokeWidth(QgsLayoutMeasurement(0.3, QgsUnitTypes.LayoutMillimeters))
        cell.setMargin(1)

        layout.addLayoutItem(cell)
        x_pos += col_widths[col_idx]

# 6-4. 범례
legend_item = QgsLayoutItemLegend(layout)
legend_item.attemptSetSceneRect(QRectF(205, 135, 85, 40))
legend_item.setTitle('범례')
legend_item.setFrameEnabled(True)
legend_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

layout.addLayoutItem(legend_item)

# 6-5. 날짜/출처
footer_item = QgsLayoutItemLabel(layout)
footer_item.attemptSetSceneRect(QRectF(205, 180, 85, 15))
footer_item.setText('제주시\n2025년 10월')

footer_font = QFont('맑은 고딕', 8)
footer_item.setFont(footer_font)
footer_item.setHAlign(Qt.AlignCenter)

layout.addLayoutItem(footer_item)

print("✅ 6단계: Print Layout 생성 완료")

# =============================================================================
# 7단계: PNG로 자동 내보내기
# =============================================================================
exporter = QgsLayoutExporter(layout)

export_settings = QgsLayoutExporter.ImageExportSettings()
export_settings.dpi = 300  # 고해상도

output_path = 'C:/Users/ksj27/모듈러주택_사업지_지도.png'

result = exporter.exportToImage(output_path, export_settings)

if result == QgsLayoutExporter.Success:
    print(f"✅ 7단계: PNG 내보내기 완료")
    print(f"📁 저장 경로: {output_path}")
else:
    print(f"❌ PNG 내보내기 실패: {result}")

# =============================================================================
# 완료
# =============================================================================
print("=" * 70)
print("🎉 올인원 자동화 완료!")
print("=" * 70)
print(f"\n📊 통계:")
print(f"🟢 제주시추천+국공유지: {stats['GREEN']['count']}개, {stats['GREEN']['area']:,.0f}㎡")
print(f"🔵 일반 사유지: {stats['BLUE']['count']}개, {stats['BLUE']['area']:,.0f}㎡")
print(f"🔴 기개발 사유지: {stats['RED']['count']}개, {stats['RED']['area']:,.0f}㎡")
print(f"📍 합계: {total_count}개, {total_area:,.0f}㎡ ({total_area/3.3058:,.0f}평)")
print("=" * 70)
