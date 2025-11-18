"""
레이어 상태 확인
"""
from qgis.core import QgsProject

# 레이어 확인
layer = QgsProject.instance().mapLayersByName('모듈러주택 사업지')[0]
border_layer = QgsProject.instance().mapLayersByName('사업지 전체 테두리')[0]

print(f"메인 레이어 전체 피처 수: {layer.featureCount()}")
print(f"테두리 레이어 피처 수: {border_layer.featureCount()}")

# 지번 목록 읽기
with open('C:/Users/ksj27/PROJECTS/QGIS/input/green_list.txt', 'r', encoding='utf-8') as f:
    green_list = set(line.strip() for line in f if line.strip())

with open('C:/Users/ksj27/PROJECTS/QGIS/input/blue_list.txt', 'r', encoding='utf-8') as f:
    blue_list = set(line.strip() for line in f if line.strip())

with open('C:/Users/ksj27/PROJECTS/QGIS/input/red_list.txt', 'r', encoding='utf-8') as f:
    red_list = set(line.strip() for line in f if line.strip())

# 실제 매칭 확인
green_count = 0
blue_count = 0
red_count = 0

print("\n매칭된 필지:")
for feature in layer.getFeatures():
    jibun = feature['A5']
    if jibun in green_list:
        green_count += 1
        print(f"🟢 {jibun}")
    elif jibun in blue_list:
        blue_count += 1
        print(f"🔵 {jibun}")
    elif jibun in red_list:
        red_count += 1
        print(f"🔴 {jibun}")

print(f"\n실제 매칭 결과:")
print(f"🟢 초록: {green_count}개")
print(f"🔵 파랑: {blue_count}개")
print(f"🔴 빨강: {red_count}개")
print(f"📊 총: {green_count + blue_count + red_count}개")
