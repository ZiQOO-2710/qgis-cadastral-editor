"""
QGIS Python Console에서 실행
특정 필지만 빨간색으로 표시

사용법:
1. QGIS Python Console 열기 (Ctrl+Alt+P)
2. 이 스크립트 내용을 복사 붙여넣기
3. Enter!
"""

from qgis.core import (
    QgsProject,
    QgsRuleBasedRenderer,
    QgsSymbol,
    QgsFillSymbol,
    QgsSingleSymbolRenderer
)
from qgis.PyQt.QtGui import QColor

# 현재 선택된 레이어 가져오기
layer = iface.activeLayer()

if not layer:
    print("❌ 레이어가 선택되지 않았습니다!")
    print("왼쪽 레이어 패널에서 'haengwonri_selected' 클릭 후 다시 실행하세요.")
else:
    print(f"✅ 레이어: {layer.name()}")

    # 규칙 기반 렌더러 생성
    root_rule = QgsRuleBasedRenderer.Rule(None)

    # 규칙 1: 빨간색 그룹
    red_filter = """"A5" IN ('1241', '1241-5', '1241-6', '1241-7', '1241-8', '1172-8', '1172-1', '1172-9')"""

    red_symbol = QgsFillSymbol.createSimple({
        'color': '255,0,0,100',  # 빨간색, 투명도 40%
        'outline_color': '255,0,0,255',  # 진한 빨간색 테두리
        'outline_width': '1.0',
        'outline_style': 'solid',
        'style': 'solid'
    })

    red_rule = QgsRuleBasedRenderer.Rule(red_symbol)
    red_rule.setLabel('선택 필지 (빨간색)')
    red_rule.setFilterExpression(red_filter)
    root_rule.appendChild(red_rule)

    print("✅ 빨간색 규칙 추가")

    # 규칙 2: 회색 그룹 (나머지)
    gray_filter = """ELSE"""

    gray_symbol = QgsFillSymbol.createSimple({
        'color': '150,150,150,80',  # 회색, 투명
        'outline_color': '100,100,100,255',  # 진한 회색 테두리
        'outline_width': '0.6',
        'outline_style': 'solid',
        'style': 'solid'
    })

    gray_rule = QgsRuleBasedRenderer.Rule(gray_symbol)
    gray_rule.setLabel('기타 필지 (회색)')
    gray_rule.setFilterExpression(gray_filter)
    root_rule.appendChild(gray_rule)

    print("✅ 회색 규칙 추가")

    # 렌더러 적용
    renderer = QgsRuleBasedRenderer(root_rule)
    layer.setRenderer(renderer)

    # 레이어 새로고침
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())

    print("\n" + "="*50)
    print("✅ 스타일 적용 완료!")
    print("="*50)
    print("\n📊 결과:")
    print("  🔴 빨간색 그룹: 8개 필지")
    print("     - 1241, 1241-5, 1241-6, 1241-7, 1241-8")
    print("     - 1172-8, 1172-1, 1172-9")
    print("  ⚪ 회색 그룹: 나머지 57개 필지")
    print("\n💡 지도를 확인하세요!")
