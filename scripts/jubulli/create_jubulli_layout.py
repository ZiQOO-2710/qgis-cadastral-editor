#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주북리 지적도 조판 레이아웃 생성
지도 + 통계표 + 범례 포함
"""

from qgis.core import (
    QgsProject, QgsPrintLayout, QgsLayoutExporter,
    QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutItemLegend,
    QgsLayoutPoint, QgsLayoutSize, QgsLayoutMeasurement, QgsUnitTypes
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QRectF, Qt

# 레이어 가져오기
layers = QgsProject.instance().mapLayersByName('jubulli_categorized')
if not layers:
    print("❌ 레이어를 찾을 수 없습니다: jubulli_categorized")
    print("   먼저 apply_jubulli_style.py를 실행하세요.")
    exit(1)

layer = layers[0]

# 기존 레이아웃 삭제
project = QgsProject.instance()
layout_manager = project.layoutManager()
existing_layout = layout_manager.layoutByName('주북리_사업지_지도')
if existing_layout:
    layout_manager.removeLayout(existing_layout)
    print("✅ 기존 레이아웃 삭제 완료")

# 새 레이아웃 생성
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName('주북리_사업지_지도')

# A4 가로 (297mm x 210mm)
page = layout.pageCollection().pages()[0]
page.setPageSize('A4', QgsLayoutItemPage.Landscape)

# 1. 지도 추가 (왼쪽)
map_item = QgsLayoutItemMap(layout)
map_item.attemptSetSceneRect(QRectF(10, 20, 180, 170))  # x, y, width, height (mm)
map_item.setFrameEnabled(True)
map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

# 레이어 범위로 설정
map_item.setExtent(layer.extent())
layout.addLayoutItem(map_item)

print("✅ 지도 추가 완료 (180mm x 170mm)")

# 2. 제목 추가
title = QgsLayoutItemLabel(layout)
title.attemptSetSceneRect(QRectF(10, 5, 280, 12))
title.setText('용인시 처인구 양지면 주북리 사업 대상 필지 현황')
title.setFont(QFont('맑은 고딕', 14, QFont.Bold))
title.setHAlign(Qt.AlignCenter)
title.setVAlign(Qt.AlignVCenter)
title.setFrameEnabled(False)
layout.addLayoutItem(title)

print("✅ 제목 추가 완료")

# 3. 통계표 추가 (오른쪽 상단)
table_x = 200
table_y = 30
table_width = 85
row_height = 8

# 통계 데이터 계산
category_stats = {
    'GREEN': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0},
    'BLUE': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0},
    'RED': {'count': 0, 'area_sqm': 0, 'area_pyeong': 0}
}

for feature in layer.getFeatures():
    category = feature['CATEGORY']
    if category in category_stats:
        category_stats[category]['count'] += 1
        geom = feature.geometry()
        area_sqm = geom.area()
        category_stats[category]['area_sqm'] += area_sqm
        category_stats[category]['area_pyeong'] += area_sqm * 0.3025

total_count = sum(stats['count'] for stats in category_stats.values())
total_area_sqm = sum(stats['area_sqm'] for stats in category_stats.values())
total_area_pyeong = sum(stats['area_pyeong'] for stats in category_stats.values())

# 표 데이터 구성
table_data = [
    ['카테고리', '필지 수', '면적(㎡)', '면적(평)'],
    ['GREEN', str(category_stats['GREEN']['count']),
     f"{category_stats['GREEN']['area_sqm']:.0f}",
     f"{category_stats['GREEN']['area_pyeong']:.2f}"],
    ['BLUE', str(category_stats['BLUE']['count']),
     f"{category_stats['BLUE']['area_sqm']:.0f}",
     f"{category_stats['BLUE']['area_pyeong']:.2f}"],
    ['RED', str(category_stats['RED']['count']),
     f"{category_stats['RED']['area_sqm']:.0f}",
     f"{category_stats['RED']['area_pyeong']:.2f}"],
    ['합계', str(total_count),
     f"{total_area_sqm:.0f}",
     f"{total_area_pyeong:.2f}"]
]

# 헤더 폰트
header_font = QFont('맑은 고딕', 9)
header_font.setBold(True)

# 데이터 폰트
data_font = QFont('맑은 고딕', 8)

# 컬럼 너비
col_widths = [20, 15, 25, 25]

# 표 생성 (5x4 그리드)
for row_idx, row_data in enumerate(table_data):
    x_offset = 0

    for col_idx, cell_text in enumerate(row_data):
        cell = QgsLayoutItemLabel(layout)

        cell_x = table_x + x_offset
        cell_y = table_y + row_idx * row_height
        cell_width = col_widths[col_idx]
        cell_height = row_height

        cell.attemptSetSceneRect(QRectF(cell_x, cell_y, cell_width, cell_height))
        cell.setText(cell_text)

        # 헤더 vs 데이터 스타일
        if row_idx == 0:  # 헤더
            cell.setFont(header_font)
            cell.setBackgroundEnabled(True)
            cell.setBackgroundColor(QColor(220, 220, 220))
            cell.setHAlign(Qt.AlignCenter)
        elif row_idx == 4:  # 합계 행
            cell.setFont(header_font)
            cell.setBackgroundEnabled(True)
            cell.setBackgroundColor(QColor(255, 255, 200))
            cell.setHAlign(Qt.AlignCenter if col_idx == 0 else Qt.AlignRight)
        else:  # 데이터 행
            cell.setFont(data_font)
            cell.setHAlign(Qt.AlignCenter if col_idx == 0 else Qt.AlignRight)

        cell.setVAlign(Qt.AlignVCenter)
        cell.setFrameEnabled(True)
        cell.setFrameStrokeWidth(QgsLayoutMeasurement(0.3, QgsUnitTypes.LayoutMillimeters))

        layout.addLayoutItem(cell)

        x_offset += cell_width

print("✅ 통계표 추가 완료 (5행 x 4열)")

# 4. 범례 추가 (오른쪽 중간)
legend = QgsLayoutItemLegend(layout)
legend.attemptSetSceneRect(QRectF(200, 80, 85, 40))
legend.setTitle('범례')

# 범례 제목 폰트
legend_title_font = QFont('맑은 고딕', 10)
legend_title_font.setBold(True)
legend.setStyleFont(QgsLegendStyle.Title, legend_title_font)

# 범례 항목 폰트
legend_item_font = QFont('맑은 고딕', 8)
legend.setStyleFont(QgsLegendStyle.SymbolLabel, legend_item_font)

legend.setFrameEnabled(True)
legend.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
legend.setBackgroundEnabled(True)
legend.setBackgroundColor(QColor(255, 255, 255, 230))

layout.addLayoutItem(legend)

print("✅ 범례 추가 완료")

# 5. 설명 추가 (오른쪽 하단)
description = QgsLayoutItemLabel(layout)
description.attemptSetSceneRect(QRectF(200, 130, 85, 60))
description.setText('''분류 기준: 채권최고액(근저당권)

GREEN: 19.2~24억원
       (채무 부담 낮음)

BLUE: 44.4~48억원
      (중간)

RED: 52억원
     (채무 부담 높음)''')
description.setFont(QFont('맑은 고딕', 8))
description.setHAlign(Qt.AlignLeft)
description.setVAlign(Qt.AlignTop)
description.setFrameEnabled(True)
description.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))
description.setBackgroundEnabled(True)
description.setBackgroundColor(QColor(255, 255, 240))
layout.addLayoutItem(description)

print("✅ 설명 추가 완료")

# 레이아웃 매니저에 추가
layout_manager.addLayout(layout)

print("\n✅ 조판 레이아웃 생성 완료: '주북리_사업지_지도'")
print("   조판 보기: 프로젝트(P) → 조판 관리자(N)... → '주북리_사업지_지도' → 보기(S)")

# PNG 내보내기
output_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_map.png'
exporter = QgsLayoutExporter(layout)

settings = QgsLayoutExporter.ImageExportSettings()
settings.dpi = 300
settings.imageSize = page.pageSize().toQSizeF().toSize() * 300 / 25.4  # 300 DPI

result = exporter.exportToImage(output_path, settings)

if result == QgsLayoutExporter.Success:
    print(f"\n✅ PNG 내보내기 성공: {output_path}")
    print("   해상도: 300 DPI")
else:
    print(f"\n❌ PNG 내보내기 실패: {result}")
