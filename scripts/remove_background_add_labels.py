#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배경 레이어 끄고 지번 라벨 추가
"""

from qgis.core import (
    QgsProject, QgsPalLayerSettings, QgsTextFormat,
    QgsVectorLayerSimpleLabeling, QgsTextBufferSettings
)
from qgis.PyQt.QtGui import QFont, QColor

project = QgsProject.instance()

# 1. 배경 레이어 끄기 (Vworld, 항공사진 등)
background_keywords = ['vworld', 'hybrid', 'satellite', '위성', '항공']
for layer in project.mapLayers().values():
    layer_name_lower = layer.name().lower()
    if any(keyword in layer_name_lower for keyword in background_keywords):
        # 레이어 트리에서 체크박스 해제
        root = project.layerTreeRoot()
        tree_layer = root.findLayer(layer.id())
        if tree_layer:
            tree_layer.setItemVisibilityChecked(False)
            print(f"✅ 배경 레이어 끔: {layer.name()}")

# 2. jubulli_categorized 레이어에 지번 라벨 추가
layers = project.mapLayersByName('jubulli_categorized')
if layers:
    layer = layers[0]

    # 라벨 설정
    label_settings = QgsPalLayerSettings()
    label_settings.fieldName = "JIBUN"
    label_settings.enabled = True
    # placement는 기본값 사용 (버전 호환성)

    # 텍스트 포맷
    text_format = QgsTextFormat()
    text_format.setFont(QFont('맑은 고딕', 9))
    text_format.setSize(9)
    text_format.setColor(QColor(0, 0, 0))  # 검정색

    # 텍스트 외곽선 (가독성 향상)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1.0)
    buffer_settings.setColor(QColor(255, 255, 255))  # 흰색 외곽선
    text_format.setBuffer(buffer_settings)

    label_settings.setFormat(text_format)

    # 라벨 적용
    layer.setLabelsEnabled(True)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
    layer.triggerRepaint()

    print("✅ 지번 라벨 추가 완료")
else:
    print("❌ jubulli_categorized 레이어를 찾을 수 없습니다")

# 지도 새로고침
from qgis.utils import iface
iface.mapCanvas().refresh()

print("\n✅ 배경 제거 및 라벨 추가 완료!")
