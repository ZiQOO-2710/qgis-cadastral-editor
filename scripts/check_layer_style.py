"""
레이어 스타일 확인
"""
from qgis.core import QgsProject

layer = QgsProject.instance().mapLayersByName('모듈러주택 사업지')[0]

print(f"레이어 이름: {layer.name()}")
print(f"레이어 타입: {layer.type()}")
print(f"피처 개수: {layer.featureCount()}")
print(f"렌더러 타입: {type(layer.renderer()).__name__}")

# CATEGORY 필드 값 확인
print("\nCATEGORY 값 확인:")
green_count = 0
blue_count = 0
red_count = 0
other_count = 0

for feature in layer.getFeatures():
    category = feature['CATEGORY']
    if category == 'GREEN':
        green_count += 1
    elif category == 'BLUE':
        blue_count += 1
    elif category == 'RED':
        red_count += 1
    else:
        other_count += 1
        print(f"  기타: {feature['A5']} = '{category}'")

print(f"\n🟢 GREEN: {green_count}")
print(f"🔵 BLUE: {blue_count}")
print(f"🔴 RED: {red_count}")
print(f"⚪ OTHER: {other_count}")

# 렌더러 규칙 확인
if hasattr(layer.renderer(), 'rootRule'):
    root_rule = layer.renderer().rootRule()
    print(f"\n규칙 개수: {len(root_rule.children())}")
    for i, rule in enumerate(root_rule.children()):
        print(f"  규칙 {i+1}: {rule.label()} - {rule.filterExpression()}")
