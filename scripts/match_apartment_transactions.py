"""
아파트 단지와 실거래가 매칭 스크립트 (프로토타입)

CSV 구조:
- 인코딩: EUC-KR
- 헤더 라인: 16
- 주요 필드: 시군구, 단지명, 전용면적(㎡), 계약년월, 거래금액(만원), 층, 도로명
"""
import csv
import json
from collections import defaultdict
from difflib import SequenceMatcher

def clean_apartment_name(name):
    """아파트 이름 정규화 (매칭 정확도 향상)"""
    # 공백 제거, 소문자 변환
    cleaned = name.replace(' ', '').lower()
    # 일반적인 접미사 제거 (선택적)
    # cleaned = cleaned.replace('아파트', '').replace('단지', '')
    return cleaned

def fuzzy_match_score(str1, str2):
    """두 문자열의 유사도 점수 (0.0 ~ 1.0)"""
    return SequenceMatcher(None, str1, str2).ratio()

def parse_price(price_str):
    """가격 문자열을 숫자로 변환 (만원 단위)"""
    try:
        # "57,300" → 57300
        return int(price_str.replace(',', ''))
    except:
        return None

def format_price_korean(price_10k):
    """가격을 한국식 표기로 변환 (억, 만원)"""
    if price_10k is None:
        return "정보없음"

    eok = price_10k // 10000
    man = price_10k % 10000

    if eok > 0 and man > 0:
        return f"{eok}억 {man:,}만원"
    elif eok > 0:
        return f"{eok}억"
    else:
        return f"{man:,}만원"

def read_transaction_csv(csv_path):
    """실거래가 CSV 읽기"""
    transactions = []

    with open(csv_path, 'r', encoding='euc-kr') as f:
        # 헤더까지 스킵 (15줄)
        for _ in range(15):
            f.readline()

        # CSV 파싱
        reader = csv.DictReader(f)

        for row in reader:
            transaction = {
                'district': row.get('시군구', ''),
                'complex_name': row.get('단지명', ''),
                'area_sqm': float(row.get('전용면적(㎡)', '0') or '0'),
                'contract_ym': row.get('계약년월', ''),
                'contract_day': row.get('계약일', '').strip(),
                'price_10k': parse_price(row.get('거래금액(만원)', '')),
                'floor': row.get('층', ''),
                'build_year': row.get('건축년도', ''),
                'road_name': row.get('도로명', '')
            }

            # 유효한 거래만 추가
            if transaction['price_10k'] is not None:
                transactions.append(transaction)

    print(f"✅ 총 {len(transactions):,}개 거래 데이터 읽기 완료")
    return transactions

def group_transactions_by_complex(transactions):
    """단지명별로 거래 데이터 그룹화"""
    grouped = defaultdict(list)

    for trans in transactions:
        complex_name = trans['complex_name']
        if complex_name:
            grouped[complex_name].append(trans)

    print(f"✅ {len(grouped)}개 아파트 단지 식별")
    return grouped

def match_apartments_with_transactions(apartment_geojson_path, transactions):
    """아파트 GeoJSON과 실거래가 매칭"""

    # GeoJSON 읽기
    with open(apartment_geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # 거래 데이터를 단지명별로 그룹화
    trans_by_complex = group_transactions_by_complex(transactions)

    print(f"\n📊 매칭 시작...")
    print(f"   아파트: {len(geojson['features'])}개")
    print(f"   거래 데이터: {len(trans_by_complex)}개 단지")

    matched_count = 0

    # 각 아파트 피처에 대해 매칭 시도
    for feature in geojson['features']:
        apt_name = feature['properties']['apt_nm']
        apt_address = feature['properties'].get('rdnmadr', '')

        # 아파트 이름 정규화
        apt_name_clean = clean_apartment_name(apt_name)

        # 최고 매칭 점수 찾기
        best_match = None
        best_score = 0.0

        for complex_name, trans_list in trans_by_complex.items():
            complex_name_clean = clean_apartment_name(complex_name)
            score = fuzzy_match_score(apt_name_clean, complex_name_clean)

            # 주소 기반 추가 검증 (선택적)
            if apt_address and trans_list[0]['road_name']:
                road_in_address = any(
                    road_part in apt_address
                    for road_part in trans_list[0]['road_name'].split()
                )
                if road_in_address:
                    score += 0.1  # 주소 일치 시 보너스

            if score > best_score:
                best_score = score
                best_match = (complex_name, trans_list)

        # 매칭 임계값 (0.7 이상이면 동일 아파트로 간주)
        if best_score >= 0.7 and best_match:
            complex_name, trans_list = best_match

            # 최근 거래 3개만 선택 (날짜 기준 정렬)
            sorted_trans = sorted(
                trans_list,
                key=lambda x: (x['contract_ym'], x['contract_day']),
                reverse=True
            )[:3]

            # 거래 정보 추가
            feature['properties']['transactions'] = [
                {
                    'date': f"{t['contract_ym'][:4]}-{t['contract_ym'][4:]}-{t['contract_day']}",
                    'price_10k': t['price_10k'],
                    'price_kr': format_price_korean(t['price_10k']),
                    'area_sqm': t['area_sqm'],
                    'floor': t['floor']
                }
                for t in sorted_trans
            ]

            # 평균 거래가 계산
            avg_price = sum(t['price_10k'] for t in sorted_trans) / len(sorted_trans)
            feature['properties']['avg_price_10k'] = int(avg_price)
            feature['properties']['avg_price_kr'] = format_price_korean(int(avg_price))

            # 평당 가격 (평 = 3.3058㎡)
            if sorted_trans[0]['area_sqm'] > 0:
                price_per_pyeong = (avg_price * 10000) / (sorted_trans[0]['area_sqm'] / 3.3058)
                feature['properties']['price_per_pyeong'] = int(price_per_pyeong)

            matched_count += 1

            print(f"   ✅ {apt_name} ↔ {complex_name} (유사도: {best_score:.2f})")
            print(f"      최근 거래: {len(sorted_trans)}개, 평균: {format_price_korean(int(avg_price))}")

    print(f"\n✅ 매칭 완료: {matched_count}/{len(geojson['features'])}개 아파트")

    return geojson

def main():
    print("=" * 70)
    print("🏢 아파트-실거래가 매칭 스크립트")
    print("=" * 70)

    # 파일 경로
    csv_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/아파트(매매)_실거래가_20251022152629.csv'
    geojson_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments.geojson'
    output_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_prices.geojson'

    # 1단계: CSV 읽기
    print("\n1️⃣  실거래가 CSV 읽기...")
    transactions = read_transaction_csv(csv_path)

    # 통계 출력
    if transactions:
        districts = set(t['district'] for t in transactions)
        print(f"   지역: {', '.join(districts)}")

        prices = [t['price_10k'] for t in transactions if t['price_10k']]
        if prices:
            print(f"   가격 범위: {format_price_korean(min(prices))} ~ {format_price_korean(max(prices))}")

    # 2단계: 아파트와 매칭
    print("\n2️⃣  아파트 GeoJSON과 매칭...")
    matched_geojson = match_apartments_with_transactions(geojson_path, transactions)

    # 3단계: 결과 저장
    print("\n3️⃣  결과 저장...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(matched_geojson, f, ensure_ascii=False, indent=2)

    print(f"✅ 저장 완료: {output_path}")

    # 4단계: 매칭 결과 샘플 출력
    print("\n" + "=" * 70)
    print("📋 매칭 결과 샘플 (첫 번째 아파트)")
    print("=" * 70)

    first_apt = matched_geojson['features'][0]
    print(f"\n아파트: {first_apt['properties']['apt_nm']}")
    print(f"주소: {first_apt['properties']['rdnmadr']}")

    if 'transactions' in first_apt['properties']:
        print(f"\n최근 거래 {len(first_apt['properties']['transactions'])}건:")
        for i, trans in enumerate(first_apt['properties']['transactions'], 1):
            print(f"  {i}. {trans['date']} | {trans['price_kr']} | {trans['area_sqm']}㎡ | {trans['floor']}층")

        print(f"\n평균 거래가: {first_apt['properties']['avg_price_kr']}")
        if 'price_per_pyeong' in first_apt['properties']:
            print(f"평당 가격: {first_apt['properties']['price_per_pyeong']:,}원")
    else:
        print("\n⚠️  매칭된 거래 정보 없음")

    print("\n" + "=" * 70)
    print("💡 참고사항")
    print("=" * 70)
    print("- 현재 CSV는 부산 데이터입니다")
    print("- 서울 서초구 데이터로 교체하면 동일한 방식으로 매칭됩니다")
    print("- 매칭 임계값: 0.7 (이름 유사도 70% 이상)")
    print("- 주소 일치 시 매칭 점수 10% 가산")
    print("=" * 70)

if __name__ == '__main__':
    main()
