#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoJSON 데이터를 웹맵 형식으로 변환
"""

import json

def transform_geojson():
    """웹맵에 맞는 형식으로 GeoJSON 변환"""
    input_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_real_prices.geojson'
    output_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_prices.geojson'

    # 법정동코드 매핑
    bjd_map = {
        '1165010100': '방배동',
        '1165010200': '방배동',
        '1165010300': '방배동',
        '1165010400': '방배동',
        '1165010500': '서초동',
        '1165010600': '서초동',
        '1165010700': '서초동',
        '1165010800': '서초동',
        '1165010900': '잠원동',
        '1165011000': '반포동',
        '1165011100': '반포동',
        '1165011200': '반포동',
        '1165011300': '반포동',
        '1165011400': '양재동',
        '1165011500': '내곡동',
        '1165011600': '내곡동',
    }

    print("📂 GeoJSON 데이터 로드 중...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"   총 아파트: {len(data['features'])}개")

    transformed_features = []
    matched_count = 0

    for feature in data['features']:
        props = feature['properties']
        bjd_cd = props.get('bjd_cd', '')
        dong = bjd_map.get(bjd_cd[:10], '기타')

        household_count = props.get('household_count')
        if household_count in (None, '', 0):
            household_count = props.get('hshldco', 0)

        try:
            household_count = int(household_count) if household_count not in (None, '') else None
        except (TypeError, ValueError):
            household_count = None

        new_props = {
            'apt_nm': props.get('apt_nm', ''),
            'rdnmadr': props.get('rdnmadr', ''),
            'lnmadr': props.get('lnmadr', ''),
            'dngct': props.get('dngct', 0),
            'household_count': household_count,
            'bjd_cd': props.get('bjd_cd', ''),
            'dong': dong,
        }

        # 거래통계가 있는 경우 변환
        if '거래통계' in props and props['거래통계']:
            stats = props['거래통계']
            matched_count += 1

            # 평균가를 10억 단위와 만원 단위로 변환
            avg_price = stats.get('평균가', 0)
            if avg_price >= 10000:
                avg_price_kr = f"{avg_price // 10000}억 {avg_price % 10000:,}만원"
            else:
                avg_price_kr = f"{avg_price:,}만원"

            new_props['transaction_count'] = stats.get('거래건수', 0)
            new_props['avg_price_kr'] = avg_price_kr
            new_props['max_price'] = stats.get('최고가', 0)
            new_props['min_price'] = stats.get('최저가', 0)
            new_props['avg_price'] = avg_price

            build_year = stats.get('건축년도')
            new_props['build_year'] = build_year if isinstance(build_year, int) else None

            avg_area_sqm = stats.get('평균면적_㎡')
            avg_area_pyeong = stats.get('평균면적_평')
            if avg_area_sqm:
                new_props['avg_area_sqm'] = round(avg_area_sqm, 2)
            if avg_area_pyeong:
                new_props['avg_area_pyeong'] = round(avg_area_pyeong, 2)

            if avg_area_pyeong and avg_area_pyeong > 0:
                price_per_pyeong = int((avg_price * 10000) / avg_area_pyeong)
                new_props['price_per_pyeong'] = price_per_pyeong

            # 최근 거래 내역 변환
            new_props['recent_transactions'] = []
            recent_trades = stats.get('거래내역', [])
            for trans in recent_trades[:5]:  # 최근 5건만
                price = trans.get('거래금액', 0)
                if price >= 10000:
                    price_kr = f"{price // 10000}억 {price % 10000:,}만원"
                else:
                    price_kr = f"{price:,}만원"

                area_sqm = trans.get('전용면적') if isinstance(trans.get('전용면적'), (int, float)) else None
                if area_sqm is None:
                    try:
                        raw = trans.get('전용면적_원본')
                        area_sqm = float(raw) if raw else None
                    except (TypeError, ValueError):
                        area_sqm = None
                area_pyeong = (area_sqm / 3.3058) if area_sqm else None

                area_label = None
                if area_sqm:
                    area_label = f"{area_sqm:.1f}㎡"
                elif trans.get('전용면적_원본'):
                    area_label = f"{trans.get('전용면적_원본')}㎡"

                new_props['recent_transactions'].append({
                    'date': trans.get('거래일', ''),
                    'price_kr': price_kr,
                    'price': price,
                    'area_sqm': round(area_sqm, 2) if area_sqm else None,
                    'area_pyeong': round(area_pyeong, 2) if area_pyeong else None,
                    'area_label': area_label,
                    'floor': trans.get('층', '')
                })

        transformed_features.append({
            'type': 'Feature',
            'geometry': feature['geometry'],
            'properties': new_props
        })

    # 변환된 GeoJSON 저장
    output_data = {
        'type': 'FeatureCollection',
        'features': transformed_features
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 변환 완료!")
    print(f"   저장 위치: {output_file}")
    print(f"   총 아파트: {len(transformed_features):,}개")
    print(f"   실거래가 매칭: {matched_count:,}개 ({matched_count/len(transformed_features)*100:.1f}%)")

    # 샘플 출력
    print(f"\n📊 변환된 데이터 샘플:")
    for i, feature in enumerate(transformed_features[:3], 1):
        props = feature['properties']
        print(f"\n{i}. {props['apt_nm']}")
        print(f"   주소: {props['rdnmadr']}")
        if props.get('transaction_count'):
            print(f"   거래건수: {props['transaction_count']}건")
            print(f"   평균가: {props['avg_price_kr']}")
            if props.get('price_per_pyeong'):
                print(f"   평당가: {props['price_per_pyeong']:,}원")

if __name__ == "__main__":
    print("=" * 70)
    print("웹맵용 GeoJSON 데이터 변환")
    print("=" * 70)
    print()

    transform_geojson()

    print("\n" + "=" * 70)
    print("✅ 변환 작업 완료")
    print("=" * 70)
