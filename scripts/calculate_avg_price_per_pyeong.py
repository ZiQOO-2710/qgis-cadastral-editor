"""
서초구 아파트 평균 평당가 계산
"""
import csv

csv_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/아파트(매매)_실거래가_20251022152629.csv'

print("=" * 70)
print("📊 서초구 아파트 평균 평당가 계산")
print("=" * 70)

# 서초구 거래 데이터 수집
seocho_transactions = []

with open(csv_path, 'r', encoding='euc-kr') as f:
    # 헤더 스킵
    for _ in range(15):
        f.readline()

    reader = csv.DictReader(f)

    for row in reader:
        district = row.get('시군구', '')

        if '서초구' in district:
            complex_name = row.get('단지명', '')
            area_sqm = float(row.get('전용면적(㎡)', '0') or '0')
            price_10k = int(row.get('거래금액(만원)', '0').replace(',', '') or '0')

            if area_sqm > 0 and price_10k > 0:
                # 평당 가격 계산
                area_pyeong = area_sqm / 3.3058  # 1평 = 3.3058㎡
                price_won = price_10k * 10000  # 만원 → 원
                price_per_pyeong = price_won / area_pyeong

                seocho_transactions.append({
                    'complex_name': complex_name,
                    'area_sqm': area_sqm,
                    'area_pyeong': area_pyeong,
                    'price_10k': price_10k,
                    'price_won': price_won,
                    'price_per_pyeong': price_per_pyeong
                })

print(f"\n✅ 서초구 거래 데이터: {len(seocho_transactions)}건")

if len(seocho_transactions) == 0:
    print("\n⚠️  서초구 거래 데이터가 없습니다!")
else:
    # 평균 평당가 계산
    total_price_per_pyeong = sum(t['price_per_pyeong'] for t in seocho_transactions)
    avg_price_per_pyeong = total_price_per_pyeong / len(seocho_transactions)

    # 최소/최대 평당가
    min_transaction = min(seocho_transactions, key=lambda x: x['price_per_pyeong'])
    max_transaction = max(seocho_transactions, key=lambda x: x['price_per_pyeong'])

    print("\n" + "=" * 70)
    print("📈 서초구 평당가 통계")
    print("=" * 70)

    print(f"\n🎯 평균 평당가: {avg_price_per_pyeong:,.0f}원/평")
    print(f"   (약 {avg_price_per_pyeong/10000:,.0f}만원/평)")

    print(f"\n📉 최저 평당가: {min_transaction['price_per_pyeong']:,.0f}원/평")
    print(f"   - 단지: {min_transaction['complex_name']}")
    print(f"   - 면적: {min_transaction['area_pyeong']:.1f}평 ({min_transaction['area_sqm']:.2f}㎡)")
    print(f"   - 거래가: {min_transaction['price_10k']:,}만원")

    print(f"\n📈 최고 평당가: {max_transaction['price_per_pyeong']:,.0f}원/평")
    print(f"   - 단지: {max_transaction['complex_name']}")
    print(f"   - 면적: {max_transaction['area_pyeong']:.1f}평 ({max_transaction['area_sqm']:.2f}㎡)")
    print(f"   - 거래가: {max_transaction['price_10k']:,}만원")

    # 단지별 평균 평당가 (거래 건수가 있는 단지만)
    from collections import defaultdict

    complex_prices = defaultdict(list)
    for t in seocho_transactions:
        complex_prices[t['complex_name']].append(t['price_per_pyeong'])

    complex_avg = {}
    for complex_name, prices in complex_prices.items():
        complex_avg[complex_name] = sum(prices) / len(prices)

    # 평당가 높은 순으로 정렬
    sorted_complexes = sorted(complex_avg.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "=" * 70)
    print("🏢 단지별 평균 평당가 (상위 10개)")
    print("=" * 70)

    for i, (complex_name, avg_price) in enumerate(sorted_complexes[:10], 1):
        count = len(complex_prices[complex_name])
        print(f"\n{i}. {complex_name}")
        print(f"   평균 평당가: {avg_price:,.0f}원/평 ({avg_price/10000:,.0f}만원/평)")
        print(f"   거래 건수: {count}건")

print("\n" + "=" * 70)
