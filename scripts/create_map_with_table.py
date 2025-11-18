"""
지도 + 면적 통계 표 레이아웃 생성
"""
from qgis.core import (
    QgsProject, QgsLayoutExporter, QgsPrintLayout,
    QgsLayoutItemMap, QgsLayoutItemLabel, QgsLayoutItemLegend,
    QgsLayoutPoint, QgsLayoutSize, QgsLayoutMeasurement, QgsUnitTypes
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import QRectF, Qt

# 프로젝트 가져오기
project = QgsProject.instance()
layer = project.mapLayersByName('모듈러주택 사업지')[0]

# 카테고리별 통계 계산
stats = {
    'GREEN': {'count': 0, 'area': 0, 'label': '제주시추천+국공유지', 'color': '초록색'},
    'BLUE': {'count': 0, 'area': 0, 'label': '일반 사유지', 'color': '파란색'},
    'RED': {'count': 0, 'area': 0, 'label': '기개발 사유지', 'color': '빨간색'}
}

for feature in layer.getFeatures():
    category = feature['CATEGORY']
    area = float(feature['A22']) if feature['A22'] else 0

    if category in stats:
        stats[category]['count'] += 1
        stats[category]['area'] += area

total_area = sum(s['area'] for s in stats.values())
total_count = sum(s['count'] for s in stats.values())

print("=" * 70)
print("📊 카테고리별 면적 통계")
print("=" * 70)

# Print Layout 생성
layout_manager = project.layoutManager()
layout_name = '모듈러주택_사업지_지도'

# 기존 레이아웃 제거
existing_layout = layout_manager.layoutByName(layout_name)
if existing_layout:
    layout_manager.removeLayout(existing_layout)

# 새 레이아웃 생성 (A4 가로)
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName(layout_name)
layout_manager.addLayout(layout)

# 페이지 설정 (A4 가로, mm 단위)
page_width = 297
page_height = 210

# 1. 지도 프레임 추가 (왼쪽)
map_item = QgsLayoutItemMap(layout)
map_item.attemptSetSceneRect(QRectF(10, 10, 190, 190))  # x, y, width, height (mm)
map_item.setFrameEnabled(True)
map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

# 현재 지도 범위 설정
extent = layer.extent()
extent.scale(1.1)  # 10% 여유
map_item.setExtent(extent)

layout.addLayoutItem(map_item)

# 2. 제목 추가
title_item = QgsLayoutItemLabel(layout)
title_item.attemptSetSceneRect(QRectF(10, 5, 190, 8))
title_item.setText('제주시 구좌군 행원리 모듈러주택 시범사업 구역')

title_font = QFont('맑은 고딕', 14)
title_font.setBold(True)
title_item.setFont(title_font)
title_item.setHAlign(Qt.AlignCenter)

layout.addLayoutItem(title_item)

# 3. 면적 통계 표 추가 (오른쪽) - QgsLayoutItemLabel 그리드 방식
# 표 데이터 준비
table_data = [
    ['구분', '필지수', '면적(㎡)', '면적(평)', '비율'],
    [f"초록색\n{stats['GREEN']['label']}",
     str(stats['GREEN']['count']),
     f"{stats['GREEN']['area']:,.0f}",
     f"{stats['GREEN']['area']/3.3058:,.0f}",
     f"{stats['GREEN']['area']/total_area*100:.1f}%"],
    [f"파란색\n{stats['BLUE']['label']}",
     str(stats['BLUE']['count']),
     f"{stats['BLUE']['area']:,.0f}",
     f"{stats['BLUE']['area']/3.3058:,.0f}",
     f"{stats['BLUE']['area']/total_area*100:.1f}%"],
    [f"빨간색\n{stats['RED']['label']}",
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

# 표 설정
start_x = 205  # mm
start_y = 30   # mm
col_widths = [25, 12, 16, 16, 16]  # mm (총 85mm)
row_height = 20  # mm

# 각 셀을 QgsLayoutItemLabel로 생성
for row_idx, row_data in enumerate(table_data):
    y_pos = start_y + (row_idx * row_height)
    x_pos = start_x

    for col_idx, cell_text in enumerate(row_data):
        # 라벨 생성
        cell = QgsLayoutItemLabel(layout)
        cell.attemptSetSceneRect(QRectF(x_pos, y_pos, col_widths[col_idx], row_height))
        cell.setText(cell_text)

        # 폰트 설정
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
            # 첫 번째 열(구분)은 좌측 정렬, 나머지는 우측 정렬
            if col_idx == 0:
                cell.setHAlign(Qt.AlignLeft)
            else:
                cell.setHAlign(Qt.AlignRight)

        # 세로 정렬
        cell.setVAlign(Qt.AlignVCenter)

        # 테두리
        cell.setFrameEnabled(True)
        cell.setFrameStrokeWidth(QgsLayoutMeasurement(0.3, QgsUnitTypes.LayoutMillimeters))

        # 여백 (padding)
        cell.setMargin(1)

        layout.addLayoutItem(cell)
        x_pos += col_widths[col_idx]

# 4. 범례 추가 (표 아래)
legend_item = QgsLayoutItemLegend(layout)
legend_item.attemptSetSceneRect(QRectF(205, 135, 85, 40))
legend_item.setTitle('범례')
legend_item.setFrameEnabled(True)
legend_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.5, QgsUnitTypes.LayoutMillimeters))

layout.addLayoutItem(legend_item)

# 5. 날짜/출처 추가
footer_item = QgsLayoutItemLabel(layout)
footer_item.attemptSetSceneRect(QRectF(205, 180, 85, 15))
footer_item.setText('제주시\n2025년 10월')

footer_font = QFont('맑은 고딕', 8)
footer_item.setFont(footer_font)
footer_item.setHAlign(Qt.AlignCenter)

layout.addLayoutItem(footer_item)

print(f"\n✅ Print Layout 생성 완료: '{layout_name}'")
print(f"\n📊 통계:")
for category in ['GREEN', 'BLUE', 'RED']:
    data = stats[category]
    emoji = '🟢' if category == 'GREEN' else '🔵' if category == 'BLUE' else '🔴'
    print(f"{emoji} {data['color']} {data['label']}")
    print(f"   필지: {data['count']}개")
    print(f"   면적: {data['area']:,.0f} ㎡ ({data['area']/3.3058:,.0f} 평)")
    print(f"   비율: {data['area']/total_area*100:.1f}%")

print(f"\n📍 합계: {total_count}개 필지, {total_area:,.0f} ㎡ ({total_area/3.3058:,.0f} 평)")

print("\n" + "=" * 70)
print("📋 다음 단계:")
print("1. 상단 메뉴: '프로젝트' → '레이아웃' → '모듈러주택_사업지_지도'")
print("2. 레이아웃 창에서 확인 및 조정")
print("3. 레이아웃 메뉴: '내보내기' → '이미지로 내보내기'")
print("=" * 70)
