#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지번 라벨 추가 (숫자만 표시, 한글 제외)
"""

from qgis.core import (
    QgsProject, QgsPalLayerSettings, QgsTextFormat,
    QgsVectorLayerSimpleLabeling, QgsTextBufferSettings
)
from qgis.PyQt.QtGui import QFont, QColor

project = QgsProject.instance()

# jubulli_categorized 레이어에 지번 라벨 추가
layers = project.mapLayersByName('jubulli_categorized')
if layers:
    layer = layers[0]

    # 라벨 설정 - PNU 필드 사용 (또는 expression으로 JIBUN에서 숫자만 추출)
    label_settings = QgsPalLayerSettings()

    # JIBUN 필드에서 숫자 부분만 추출하는 expression
    # 예: "821전" -> "821", "827-1대" -> "827-1"
    label_settings.fieldName = "regexp_replace(\"JIBUN\", '[^0-9-]', '')"
    label_settings.isExpression = True
    label_settings.enabled = True

    # 텍스트 포맷
    text_format = QgsTextFormat()
    text_format.setFont(QFont('Arial', 10))  # 영문 폰트로 변경
    text_format.setSize(10)
    text_format.setColor(QColor(0, 0, 0))  # 검정색

    # 텍스트 외곽선 (가독성 향상)
    buffer_settings = QgsTextBufferSettings()
    buffer_settings.setEnabled(True)
    buffer_settings.setSize(1.5)
    buffer_settings.setColor(QColor(255, 255, 255))  # 흰색 외곽선
    text_format.setBuffer(buffer_settings)

    label_settings.setFormat(text_format)

    # 라벨 적용
    layer.setLabelsEnabled(True)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
    layer.triggerRepaint()

    print("✅ 지번 라벨 추가 완료 (숫자만)")
else:
    print("❌ jubulli_categorized 레이어를 찾을 수 없습니다")

# 지도 새로고침
from qgis.utils import iface
iface.mapCanvas().refresh()

print("✅ 라벨 추가 완료! (821, 822-2, 827-1 등)")
