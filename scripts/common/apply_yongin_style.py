#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
용인시 주북리 매매목록 QGIS 스타일 적용 스크립트

QGIS Python 콘솔에서 실행:
exec(open('C:/Users/ksj27/PROJECTS/QGIS/scripts/apply_yongin_style.py', encoding='utf-8').read())
"""

from qgis.core import (
    QgsProject, QgsVectorLayer, QgsRuleBasedRenderer,
    QgsFillSymbol, QgsLineSymbol, QgsSimpleFillSymbolLayer,
    QgsSimpleLineSymbolLayer
)
from qgis.PyQt.QtGui import QColor
from pathlib import Path

# 파일 경로
OUTPUT_DIR = Path(r'C:\Users\ksj27\PROJECTS\QGIS\output\yongin_sales')
SHAPEFILE = OUTPUT_DIR / 'LSMD_CONT_LDREG_41800.shp'  # 실제 파일명으로 수정 필요

def apply_sales_style():
    """매매목록 강조 스타일 적용"""

    # Shapefile 로드
    layer = QgsVectorLayer(str(SHAPEFILE), '용인시 주북리 매매목록', 'ogr')

    if not layer.isValid():
        print(f"❌ 레이어 로드 실패: {SHAPEFILE}")
        print("   파일 경로를 확인하세요.")
        return

    print(f"✅ 레이어 로드 성공: {layer.name()}")
    print(f"   레코드 수: {layer.featureCount()}")

    # Rule-based 렌더러 생성
    symbol = QgsFillSymbol.createSimple({})
    renderer = QgsRuleBasedRenderer(symbol)
    root_rule = renderer.rootRule()
    root_rule.removeChildrenIf(lambda rule: True)  # 기본 룰 제거

    # SALES (매매목록) - 빨간색 강조
    sales_symbol = QgsFillSymbol()
    sales_symbol.setColor(QColor(255, 100, 100, 180))  # 밝은 빨간색, 반투명
    sales_symbol.symbolLayer(0).setStrokeColor(QColor(200, 0, 0))  # 진한 빨간 테두리
    sales_symbol.symbolLayer(0).setStrokeWidth(0.8)

    sales_rule = root_rule.children()[0].clone() if root_rule.children() else root_rule.appendChild(QgsRuleBasedRenderer.Rule(None))
    sales_rule.setSymbol(sales_symbol)
    sales_rule.setFilterExpression('"CATEGORY" = \'SALES\'')
    sales_rule.setLabel('매매목록')
    root_rule.appendChild(sales_rule)

    # OTHER (나머지 필지) - 투명 회색
    other_symbol = QgsFillSymbol()
    other_symbol.setColor(QColor(200, 200, 200, 50))  # 옅은 회색, 매우 투명
    other_symbol.symbolLayer(0).setStrokeColor(QColor(150, 150, 150))
    other_symbol.symbolLayer(0).setStrokeWidth(0.3)

    other_rule = root_rule.children()[0].clone() if len(root_rule.children()) > 0 else root_rule.appendChild(QgsRuleBasedRenderer.Rule(None))
    other_rule.setSymbol(other_symbol)
    other_rule.setFilterExpression('"CATEGORY" = \'OTHER\' OR "CATEGORY" IS NULL')
    other_rule.setLabel('기타 필지')
    root_rule.appendChild(other_rule)

    # 렌더러 적용
    layer.setRenderer(renderer)
    layer.triggerRepaint()

    # 프로젝트에 추가
    QgsProject.instance().addMapLayer(layer)

    # 레이어 확대
    iface.mapCanvas().setExtent(layer.extent())
    iface.mapCanvas().refresh()

    print("\n✅ 스타일 적용 완료!")
    print("   - 빨간색: 매매목록 필지")
    print("   - 회색: 기타 필지")

    # 통계 출력
    sales_count = sum(1 for f in layer.getFeatures() if f['CATEGORY'] == 'SALES')
    other_count = layer.featureCount() - sales_count

    print(f"\n📊 필지 현황:")
    print(f"   매매목록: {sales_count}개")
    print(f"   기타 필지: {other_count}개")
    print(f"   전체: {layer.featureCount()}개")


if __name__ == '__main__' or __name__ == '__console__':
    apply_sales_style()
