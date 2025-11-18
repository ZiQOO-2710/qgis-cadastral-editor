#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoJSON 데이터 무결성 검증 및 필터 시나리오 예상값 계산
"""

import json
import math
from collections import defaultdict

def validate_geojson():
    """GeoJSON 데이터 무결성 검증"""
    geojson_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_prices.geojson'

    print("=" * 80)
    print("GeoJSON 데이터 무결성 검증")
    print("=" * 80)
    print()

    # 1. 파일 로드
    print("1️⃣  GeoJSON 파일 로드 중...")
    with open(geojson_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    features = data.get('features', [])
    print(f"   ✅ 총 {len(features)}개 아파트 로드 완료")
    print()

    # 2. 필수 필드 검증
    print("2️⃣  필수 필드 검증 중...")
    errors = []
    field_stats = defaultdict(int)

    for i, feature in enumerate(features):
        # Geometry 검증
        if feature.get('geometry', {}).get('type') != 'Point':
            errors.append(f"Feature {i}: geometry.type이 'Point'가 아님")

        coords = feature.get('geometry', {}).get('coordinates', [])
        if len(coords) != 2:
            errors.append(f"Feature {i}: coordinates가 [경도, 위도] 형식이 아님")

        # Properties 검증
        props = feature.get('properties', {})

        # apt_nm (필수)
        if 'apt_nm' in props and props['apt_nm']:
            field_stats['apt_nm'] += 1
        else:
            errors.append(f"Feature {i}: apt_nm 없음")

        # dong (필수)
        if 'dong' in props and props['dong']:
            field_stats['dong'] += 1
        else:
            errors.append(f"Feature {i}: dong 없음")

        # avg_price (선택, 실거래가 있는 경우만)
        if 'avg_price' in props and props['avg_price']:
            field_stats['avg_price'] += 1

        # price_per_pyeong (선택)
        if 'price_per_pyeong' in props and props['price_per_pyeong']:
            field_stats['price_per_pyeong'] += 1

        # transaction_count (선택)
        if 'transaction_count' in props and props['transaction_count']:
            field_stats['transaction_count'] += 1

    if errors:
        print(f"   ❌ {len(errors)}개 오류 발견:")
        for err in errors[:10]:  # 처음 10개만 출력
            print(f"      - {err}")
        if len(errors) > 10:
            print(f"      ... 외 {len(errors) - 10}개")
    else:
        print("   ✅ 모든 필수 필드 검증 통과")

    print(f"   📊 필드 통계:")
    print(f"      - apt_nm: {field_stats['apt_nm']}개 ({field_stats['apt_nm']/len(features)*100:.1f}%)")
    print(f"      - dong: {field_stats['dong']}개 ({field_stats['dong']/len(features)*100:.1f}%)")
    print(f"      - avg_price: {field_stats['avg_price']}개 ({field_stats['avg_price']/len(features)*100:.1f}%)")
    print(f"      - price_per_pyeong: {field_stats['price_per_pyeong']}개 ({field_stats['price_per_pyeong']/len(features)*100:.1f}%)")
    print(f"      - transaction_count: {field_stats['transaction_count']}개 ({field_stats['transaction_count']/len(features)*100:.1f}%)")
    print()

    # 3. 법정동별 분포
    print("3️⃣  법정동별 아파트 분포...")
    dong_dist = defaultdict(int)
    dong_with_tx = defaultdict(int)

    for feature in features:
        dong = feature['properties'].get('dong', '기타')
        dong_dist[dong] += 1

        if feature['properties'].get('transaction_count', 0) > 0:
            dong_with_tx[dong] += 1

    print(f"   📊 법정동별 분포:")
    for dong in sorted(dong_dist.keys()):
        tx_count = dong_with_tx.get(dong, 0)
        print(f"      - {dong}: {dong_dist[dong]}개 (실거래 {tx_count}개)")
    print()

    # 4. 평균가/평당가 범위 확인
    print("4️⃣  평균가/평당가 범위 확인...")
    avg_prices = [f['properties']['avg_price'] for f in features
                  if f['properties'].get('avg_price')]

    pyeong_prices = [f['properties']['price_per_pyeong'] / 10000 for f in features
                     if f['properties'].get('price_per_pyeong')]

    tx_counts = [f['properties']['transaction_count'] for f in features
                 if f['properties'].get('transaction_count')]

    if avg_prices:
        print(f"   💰 평균가 범위:")
        print(f"      - 최소: {min(avg_prices):,}만원")
        print(f"      - 최대: {max(avg_prices):,}만원")
        print(f"      - 평균: {sum(avg_prices)/len(avg_prices):,.0f}만원")

    if pyeong_prices:
        min_pyeong = math.floor(min(pyeong_prices))
        max_pyeong = math.ceil(max(pyeong_prices))
        print(f"   💰 평당가 범위:")
        print(f"      - 최소: {min_pyeong:,}만원/평 (실제: {min(pyeong_prices):,.1f})")
        print(f"      - 최대: {max_pyeong:,}만원/평 (실제: {max(pyeong_prices):,.1f})")
        print(f"      - 평균: {sum(pyeong_prices)/len(pyeong_prices):,.0f}만원/평")

    if tx_counts:
        print(f"   📊 거래건수 범위:")
        print(f"      - 최소: {min(tx_counts)}건")
        print(f"      - 최대: {max(tx_counts)}건")
        print(f"      - 평균: {sum(tx_counts)/len(tx_counts):.1f}건")
    print()

    return features


def calculate_filter_scenarios(features):
    """필터 시나리오별 예상값 계산"""
    print("=" * 80)
    print("필터 시나리오별 예상값 계산")
    print("=" * 80)
    print()

    scenarios = []

    # 시나리오 1: 법정동 필터
    print("📌 시나리오 1: 법정동 필터")
    for dong in ['반포동', '방배동', '서초동', '잠원동']:
        count = len([f for f in features if f['properties'].get('dong') == dong])
        scenarios.append({
            'name': f"법정동: {dong}",
            'filter': {'dong': [dong]},
            'expected_count': count
        })
        print(f"   {dong}: {count}개 아파트")
    print()

    # 시나리오 2: 실거래가 있는 아파트만
    print("📌 시나리오 2: 실거래가 있는 아파트만")
    with_tx = len([f for f in features if f['properties'].get('transaction_count', 0) > 0])
    scenarios.append({
        'name': "실거래가 있는 아파트만",
        'filter': {'has_transactions': True},
        'expected_count': with_tx
    })
    print(f"   실거래가 있는 아파트: {with_tx}개")
    print()

    # 시나리오 3: 평균가 범위
    print("📌 시나리오 3: 평균가 범위 필터")
    price_ranges = [
        (100000, 200000),
        (200000, 300000),
        (300000, 622833)
    ]

    for min_price, max_price in price_ranges:
        count = len([f for f in features
                     if f['properties'].get('avg_price')
                     and min_price <= f['properties']['avg_price'] <= max_price])
        scenarios.append({
            'name': f"평균가 {min_price:,}~{max_price:,}만원",
            'filter': {'avg_price': [min_price, max_price]},
            'expected_count': count
        })
        print(f"   {min_price:,}~{max_price:,}만원: {count}개")
    print()

    # 시나리오 4: 복합 필터 (AND 로직)
    print("📌 시나리오 4: 복합 필터 (AND 로직)")

    # 반포동 + 평균가 100,000 이상
    count = len([f for f in features
                 if f['properties'].get('dong') == '반포동'
                 and f['properties'].get('avg_price', 0) >= 100000])
    scenarios.append({
        'name': "반포동 + 평균가 100,000만원 이상",
        'filter': {'dong': ['반포동'], 'avg_price': [100000, 622833]},
        'expected_count': count
    })
    print(f"   반포동 + 평균가 100,000만원 이상: {count}개")

    # 반포동 + 실거래가 있는 아파트만
    count = len([f for f in features
                 if f['properties'].get('dong') == '반포동'
                 and f['properties'].get('transaction_count', 0) > 0])
    scenarios.append({
        'name': "반포동 + 실거래가 있는 아파트만",
        'filter': {'dong': ['반포동'], 'has_transactions': True},
        'expected_count': count
    })
    print(f"   반포동 + 실거래가 있는 아파트만: {count}개")

    # 서초동 + 평균가 200,000 이상 + 실거래가 있음
    count = len([f for f in features
                 if f['properties'].get('dong') == '서초동'
                 and f['properties'].get('avg_price', 0) >= 200000
                 and f['properties'].get('transaction_count', 0) > 0])
    scenarios.append({
        'name': "서초동 + 평균가 200,000만원 이상 + 실거래가 있음",
        'filter': {'dong': ['서초동'], 'avg_price': [200000, 622833], 'has_transactions': True},
        'expected_count': count
    })
    print(f"   서초동 + 평균가 200,000만원 이상 + 실거래가 있음: {count}개")
    print()

    # 시나리오 5: 아파트 이름 검색
    print("📌 시나리오 5: 아파트 이름 검색")
    search_terms = ['래미안', '아크로', '자이', '푸르지오']

    for term in search_terms:
        count = len([f for f in features if term in f['properties'].get('apt_nm', '')])
        scenarios.append({
            'name': f"아파트 이름: {term}",
            'filter': {'apt_nm': term},
            'expected_count': count
        })
        print(f"   '{term}' 포함: {count}개")
    print()

    return scenarios


def generate_test_checklist(scenarios):
    """상세 테스트 체크리스트 생성"""
    output_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/TEST_CHECKLIST.md'

    content = """# 웹맵 필터 시스템 테스트 체크리스트

## 🎯 테스트 목적
동적 필터 시스템이 의도대로 동작하는지 검증

## 🌐 테스트 환경
- URL: http://localhost:8000
- 브라우저: Chrome/Edge/Firefox (최신 버전)
- 필수 파일: apartments_with_prices.geojson (538KB)

---

## ✅ 기본 로딩 테스트

### 1.1 페이지 로딩
- [ ] 페이지가 정상적으로 로드되는가?
- [ ] 지도(Kakao Maps)가 표시되는가?
- [ ] Console 에러가 없는가? (F12 → Console 탭 확인)
- [ ] 우측 사이드바 필터 UI가 보이는가?

### 1.2 데이터 로딩
- [ ] 814개 아파트 마커가 지도에 표시되는가?
- [ ] 통계 섹션에 "총 814개" 표시되는가?
- [ ] 실거래가 있는 아파트: 271개 표시되는가?

---

## 🔧 개별 필터 테스트

"""

    # 시나리오별 테스트 케이스 추가
    for i, scenario in enumerate(scenarios, 1):
        content += f"""### 2.{i} {scenario['name']}
- [ ] 필터 적용
- [ ] 예상 결과: **{scenario['expected_count']}개 아파트**
- [ ] 실제 결과: ______개 (통계 섹션 확인)
- [ ] 일치 여부: ⬜ 일치 / ⬜ 불일치

"""

    content += """---

## 🔀 복합 필터 테스트 (AND 로직)

### 3.1 2개 필터 조합
- [ ] 반포동 체크 + 평균가 100,000만원 이상
- [ ] 지도에 표시된 마커 개수 확인
- [ ] 통계 수치와 일치하는가?

### 3.2 3개 필터 조합
- [ ] 서초동 체크 + 평균가 200,000만원 이상 + 실거래가 있는 아파트만 체크
- [ ] 모든 조건을 만족하는 아파트만 표시되는가?

---

## 🏷️ 활성 필터 관리 테스트

### 4.1 필터 태그 생성
- [ ] 필터 적용 시 상단에 "🏷️ 활성 필터" 섹션이 나타나는가?
- [ ] 각 필터별로 태그가 생성되는가?
- [ ] 태그에 ❌ 버튼이 있는가?

### 4.2 개별 필터 제거
- [ ] 태그의 ❌ 버튼 클릭
- [ ] 해당 필터만 해제되는가?
- [ ] 다른 필터는 유지되는가?

### 4.3 전체 필터 초기화
- [ ] "🔄 모든 필터 초기화" 버튼 클릭
- [ ] 모든 필터가 해제되는가?
- [ ] 814개 아파트가 다시 표시되는가?
- [ ] 활성 필터 섹션이 사라지는가?

---

## 📊 정렬 기능 테스트

### 5.1 정렬 드롭다운
- [ ] 정렬 옵션이 8개 있는가?
  - [ ] 아파트명 (가나다순)
  - [ ] 아파트명 (역순)
  - [ ] 평균가 (높은순)
  - [ ] 평균가 (낮은순)
  - [ ] 평당가 (높은순)
  - [ ] 평당가 (낮은순)
  - [ ] 거래건수 (많은순)
  - [ ] 거래건수 (적은순)

### 5.2 정렬 동작
- [ ] "평균가 (높은순)" 선택
- [ ] 리스트 상단에 고가 아파트가 표시되는가?
- [ ] "거래건수 (많은순)" 선택
- [ ] 거래가 많은 아파트가 상단에 표시되는가?

---

## ⚡ 성능 최적화 테스트

### 6.1 Debounce (검색 입력)
- [ ] 아파트 이름 검색창에 "래미안" 입력
- [ ] 입력 중에는 필터링되지 않는가?
- [ ] 입력 멈춘 후 약 300ms 후 필터링되는가?

### 6.2 Throttle (슬라이더)
- [ ] 평균가 슬라이더를 빠르게 드래그
- [ ] 드래그 중에도 부드럽게 업데이트되는가?
- [ ] 과도한 리렌더링이 발생하지 않는가?

---

## 🎨 반응형 업데이트 테스트

### 7.1 지도 마커
- [ ] 필터 변경 시 마커가 즉시 업데이트되는가?
- [ ] 줌 레벨 변경 시 마커 크기가 조정되는가?

### 7.2 통계
- [ ] 필터 변경 시 통계가 즉시 업데이트되는가?
- [ ] 총 아파트 수가 정확한가?
- [ ] 실거래가 있는 아파트 수가 정확한가?

---

## 🐛 버그 리포트 양식

발견된 버그가 있다면 아래 양식으로 리포트해주세요:

```
버그 제목:
재현 단계:
1.
2.
3.

예상 동작:

실제 동작:

스크린샷: (선택)

Console 에러: (F12 → Console 탭 내용)
```

---

## ✅ 최종 체크

- [ ] 모든 필터가 정상 동작함
- [ ] 복합 필터 (AND 로직)가 정확함
- [ ] 활성 필터 관리가 정상 동작함
- [ ] 정렬 기능이 정상 동작함
- [ ] 성능 최적화가 체감됨
- [ ] Console 에러 없음
- [ ] UX가 직관적임

---

**검증 완료일**: ________________
**검증자**: ________________
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 테스트 체크리스트 생성 완료: {output_file}")


if __name__ == "__main__":
    # 1. GeoJSON 데이터 무결성 검증
    features = validate_geojson()

    print()

    # 2. 필터 시나리오별 예상값 계산
    scenarios = calculate_filter_scenarios(features)

    print()

    # 3. 상세 테스트 체크리스트 생성
    generate_test_checklist(scenarios)

    print()
    print("=" * 80)
    print("✅ 모든 검증 작업 완료!")
    print("=" * 80)
