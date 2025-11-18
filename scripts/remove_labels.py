#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지번 라벨 제거
"""

from qgis.core import QgsProject
from qgis.utils import iface

# jubulli_categorized 레이어의 라벨 제거
layers = QgsProject.instance().mapLayersByName('jubulli_categorized')
if layers:
    layer = layers[0]
    layer.setLabelsEnabled(False)
    layer.triggerRepaint()
    print("✅ 라벨 제거 완료")
else:
    print("❌ 레이어를 찾을 수 없습니다")

# 지도 새로고침
iface.mapCanvas().refresh()
