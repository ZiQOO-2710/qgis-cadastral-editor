"""
QGIS 맵을 PNG 이미지로 저장

사용법:
1. QGIS에서 원하는 지도 뷰로 확대/축소
2. Python Console에서 실행
"""

from qgis.core import (
    QgsProject,
    QgsMapSettings,
    QgsMapRendererParallelJob,
    QgsLayoutExporter,
    QgsRectangle
)
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QImage, QPainter, QColor
import os

# 출력 설정 - 최대 고해상도
output_path = r'C:\Users\ksj27\PROJECTS\QGIS\output\haengwonri_map_high_res.png'
dpi = 600  # 해상도 (600 DPI = 매우 고품질, 인쇄용)
width = 8000  # 픽셀 (A0 크기 수준)
height = 6000  # 픽셀

print("🗺️  지도를 PNG로 저장 중...")
print(f"출력 경로: {output_path}")
print(f"해상도: {width}x{height} px, {dpi} DPI")

# 현재 맵 캔버스 설정 가져오기
canvas = iface.mapCanvas()
extent = canvas.extent()

# 맵 설정
settings = QgsMapSettings()
settings.setExtent(extent)
settings.setOutputSize(QSize(width, height))
settings.setOutputDpi(dpi)
settings.setDestinationCrs(canvas.mapSettings().destinationCrs())
settings.setBackgroundColor(QColor(255, 255, 255))  # 흰색 배경

# 레이어 추가
layers = []
for layer in QgsProject.instance().mapLayers().values():
    if layer.isValid():
        layers.append(layer)

settings.setLayers(layers)

# 이미지 생성
image = QImage(QSize(width, height), QImage.Format_ARGB32)
image.setDotsPerMeterX(int(dpi / 25.4 * 1000))
image.setDotsPerMeterY(int(dpi / 25.4 * 1000))
image.fill(QColor(255, 255, 255))  # 흰색으로 채우기

# 렌더링
painter = QPainter(image)
render = QgsMapRendererParallelJob(settings)

def finished():
    painter.end()
    image.save(output_path)

    file_size = os.path.getsize(output_path) / 1024 / 1024  # MB

    print("\n" + "="*60)
    print("✅ 저장 완료!")
    print("="*60)
    print(f"\n📂 파일 정보:")
    print(f"  경로: {output_path}")
    print(f"  크기: {file_size:.2f} MB")
    print(f"  해상도: {width} x {height} px ({dpi} DPI)")
    print(f"\n💡 Windows 탐색기에서 확인하세요!")

render.finished.connect(finished)
render.start()
render.waitForFinished()

# 동기 렌더링 (간단한 방법)
painter.setRenderHint(QPainter.Antialiasing)
render = QgsMapRendererParallelJob(settings)

render.start()
render.waitForFinished()

painter.begin(image)
painter.drawImage(0, 0, render.renderedImage())
painter.end()

# 저장
image.save(output_path)

file_size = os.path.getsize(output_path) / 1024 / 1024  # MB

print("\n" + "="*60)
print("✅ 저장 완료!")
print("="*60)
print(f"\n📂 파일 정보:")
print(f"  경로: {output_path}")
print(f"  크기: {file_size:.2f} MB")
print(f"  해상도: {width} x {height} px ({dpi} DPI)")
print(f"\n💡 Windows 탐색器에서 확인하세요!")
print(f"   또는 QGIS 메뉴: Project → Import/Export → Export Map to Image")
