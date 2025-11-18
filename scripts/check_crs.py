"""
CRS 확인 및 수정
"""
from qgis.core import QgsProject
from qgis.utils import iface

# CRS 확인
main_layer = QgsProject.instance().mapLayersByName('모듈러주택 사업지')[0]
canvas_crs = iface.mapCanvas().mapSettings().destinationCrs()

print(f"레이어 CRS: {main_layer.crs().authid()}")
print(f"캔버스 CRS: {canvas_crs.authid()}")

# CRS가 다르면 캔버스를 레이어에 맞춤
if main_layer.crs().authid() != canvas_crs.authid():
    print("\n⚠️ CRS가 다릅니다! 캔버스 CRS를 레이어에 맞춥니다...")
    iface.mapCanvas().setDestinationCrs(main_layer.crs())
    iface.mapCanvas().refresh()
    print("✅ CRS 변경 완료!")
else:
    print("\n✅ CRS가 일치합니다.")
