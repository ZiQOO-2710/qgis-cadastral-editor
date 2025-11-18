"""
카테고리별 면적 통계 계산
"""
from qgis.core import QgsProject

# 레이어 가져오기
layer = QgsProject.instance().mapLayersByName('모듈러주택 사업지')[0]

# 카테고리별 통계
stats = {
    'GREEN': {'count': 0, 'area': 0, 'label': '제주시추천+국공유지'},
    'BLUE': {'count': 0, 'area': 0, 'label': '일반 사유지'},
    'RED': {'count': 0, 'area': 0, 'label': '기개발 사유지'}
}

# 피처별로 집계
for feature in layer.getFeatures():
    category = feature['CATEGORY']
    area = float(feature['A22']) if feature['A22'] else 0  # A22는 면적(㎡)

    if category in stats:
        stats[category]['count'] += 1
        stats[category]['area'] += area

# 결과 출력
print("=" * 70)
print("📊 카테고리별 면적 통계")
print("=" * 70)

total_area = 0
total_count = 0

for category in ['GREEN', 'BLUE', 'RED']:
    data = stats[category]
    emoji = '🟢' if category == 'GREEN' else '🔵' if category == 'BLUE' else '🔴'

    area_pyeong = data['area'] / 3.3058  # 평으로 환산

    print(f"\n{emoji} {data['label']}")
    print(f"   필지 수: {data['count']:3}개")
    print(f"   면적(㎡): {data['area']:12,.0f} ㎡")
    print(f"   면적(평): {area_pyeong:12,.0f} 평")

    total_area += data['area']
    total_count += data['count']

total_pyeong = total_area / 3.3058

print("\n" + "=" * 70)
print(f"📍 전체 합계")
print(f"   필지 수: {total_count:3}개")
print(f"   면적(㎡): {total_area:12,.0f} ㎡")
print(f"   면적(평): {total_pyeong:12,.0f} 평")
print("=" * 70)

# 비율 계산
print(f"\n📈 면적 비율")
for category in ['GREEN', 'BLUE', 'RED']:
    data = stats[category]
    emoji = '🟢' if category == 'GREEN' else '🔵' if category == 'BLUE' else '🔴'
    ratio = (data['area'] / total_area * 100) if total_area > 0 else 0
    print(f"   {emoji} {data['label']}: {ratio:5.1f}%")
