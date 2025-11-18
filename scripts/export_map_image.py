#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QGIS 지도 이미지 내보내기
"""

from qgis.core import QgsProject
from qgis.utils import iface

# 출력 파일 경로
output_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli_business_area_map.png'

# 현재 맵 캔버스 가져오기
canvas = iface.mapCanvas()

# 이미지로 저장
canvas.saveAsImage(output_path)

print(f"✅ 지도 이미지 저장 완료!")
print(f"📁 경로: {output_path}")

# 선택된 필지 개수 확인
layers = QgsProject.instance().mapLayers().values()
for layer in layers:
    if layer.type() == 0:  # Vector layer
        selected_count = layer.selectedFeatureCount()
        if selected_count > 0:
            print(f"\n레이어: {layer.name()}")
            print(f"선택된 필지: {selected_count}개")
