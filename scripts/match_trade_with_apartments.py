#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아파트 실거래가 데이터와 아파트 위치 데이터를 매칭하여 GeoJSON 생성
"""

import json
import zipfile
import struct
from collections import defaultdict

def load_trade_data():
    """실거래가 데이터 로드 (3개월치)"""
    all_trades = []

    for month in ['202410', '202409', '202408']:
        json_file = f'/mnt/c/Users/ksj27/PROJECTS/QGIS/data/apt_trade_{month}.json'
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                trades = json.load(f)
                all_trades.extend(trades)
                print(f"✅ {month}: {len(trades)}건 로드")
        except Exception as e:
            print(f"❌ {month} 로드 실패: {e}")

    return all_trades

def aggregate_trades_by_apartment(trades):
    """아파트별로 거래 데이터 집계"""
    apt_trades = defaultdict(list)

    for trade in trades:
        apt_name = trade.get('아파트', '').strip()
        if apt_name:
            # 거래금액을 숫자로 변환 (쉼표 제거 후 정수 변환)
            price_str = trade.get('거래금액', '0').replace(',', '').strip()
            try:
                price = int(price_str)
            except:
                price = 0

            area_raw = trade.get('전용면적', '')
            try:
                area_sqm = float(area_raw) if area_raw else None
            except ValueError:
                area_sqm = None

            apt_trades[apt_name].append({
                '거래금액': price,
                '거래금액_원본': trade.get('거래금액', ''),
                '거래일': f"{trade.get('년', '')}-{trade.get('월', '').zfill(2)}-{trade.get('일', '').zfill(2)}",
                '전용면적': area_sqm,
                '전용면적_원본': area_raw,
                '층': trade.get('층', ''),
                '법정동': trade.get('법정동', ''),
                '지번': trade.get('지번', ''),
                '건축년도': trade.get('건축년도', ''),
            })

    return apt_trades


def load_apartment_attributes():
    """Shapefile DBF에서 단지 메타데이터 읽기 (세대수 등)"""
    zip_path = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/apt_mst_info_202410_shp.zip'
    attributes = {}

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            dbf_bytes = zf.read('apt_mst_info_202410.dbf')
    except Exception as e:
        print(f"⚠️  아파트 DBF 로드 실패: {e}")
        return attributes

    header = struct.unpack('<BBBBIHH20x', dbf_bytes[:32])
    num_records = header[4]
    header_len = header[5]
    record_len = header[6]

    fields = []
    pos = 32
    while dbf_bytes[pos] != 0x0D:
        name = dbf_bytes[pos:pos+11].rstrip(b'\x00').decode('ascii')
        f_type = chr(dbf_bytes[pos+11])
        length = dbf_bytes[pos+16]
        fields.append((name, f_type, length))
        pos += 32

    name_to_idx = {name: idx for idx, (name, _, _) in enumerate(fields)}

    def get_value(raw, f_type):
        if f_type == 'C':
            try:
                return raw.decode('cp949').strip()
            except UnicodeDecodeError:
                return raw.decode('latin-1', errors='ignore').strip()
        else:
            text = raw.decode('ascii', errors='ignore').strip()
            if not text:
                return None
            if text == '*********':
                return None
            try:
                return float(text) if '.' in text else int(text)
            except ValueError:
                return None

    for i in range(num_records):
        rec = dbf_bytes[header_len + i * record_len: header_len + (i + 1) * record_len]
        if rec[0:1] != b' ':
            continue

        values = []
        offset = 1
        for name, f_type, length in fields:
            raw = rec[offset:offset+length]
            offset += length
            values.append(get_value(raw, f_type))

        bjd_cd = values[name_to_idx.get('bjd_cd', -1)]
        apt_name = values[name_to_idx.get('apt_nm', -1)]

        if not apt_name or not bjd_cd:
            continue

        # 서초구만 필터링
        if not str(bjd_cd).startswith('1165'):
            continue

        household = values[name_to_idx.get('elcty_capa', -1)]
        dong_count = values[name_to_idx.get('dngct', -1)]

        key = (apt_name, str(bjd_cd))
        attributes[key] = {
            'household_count': int(household) if isinstance(household, (int, float)) else None,
            'dngct': int(dong_count) if isinstance(dong_count, (int, float)) else None,
        }

    print(f"✅ DBF 속성 로드: {len(attributes)}개 단지")
    return attributes

def calculate_statistics(apt_trades):
    """아파트별 거래 통계 계산"""
    apt_stats = {}

    for apt_name, trades in apt_trades.items():
        prices = [t['거래금액'] for t in trades if t['거래금액'] > 0]

        if not prices:
            continue

        # 전용면적(㎡) 리스트
        areas_sqm = [t.get('전용면적') for t in trades if isinstance(t.get('전용면적'), (int, float)) and t['전용면적'] > 0]

        avg_area_sqm = sum(areas_sqm) / len(areas_sqm) if areas_sqm else None
        avg_area_pyeong = (avg_area_sqm / 3.3058) if avg_area_sqm else None

        # 건축년도(가장 빈도 높은 값 사용, 없으면 None)
        build_years = []
        for t in trades:
            by = t.get('건축년도')
            if by and by.isdigit():
                build_years.append(int(by))

        build_year = None
        if build_years:
            from collections import Counter
            build_year = Counter(build_years).most_common(1)[0][0]

        apt_stats[apt_name] = {
            '거래건수': len(trades),
            '최고가': max(prices),
            '최저가': min(prices),
            '평균가': int(sum(prices) / len(prices)),
            '거래내역': trades[:5],  # 최근 5건만 저장
            '건축년도': build_year,
            '평균면적_㎡': avg_area_sqm,
            '평균면적_평': avg_area_pyeong
        }

    return apt_stats

def match_with_geojson(apt_stats):
    """아파트 위치 데이터(GeoJSON)와 매칭"""
    geojson_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments.geojson'

    with open(geojson_file, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    print(f"\n📍 기존 아파트 위치 데이터: {len(geojson_data['features'])}개")

    attribute_map = load_apartment_attributes()

    matched = 0
    unmatched_apartments = []

    for feature in geojson_data['features']:
        apt_nm = feature['properties']['apt_nm']
        bjd_cd = str(feature['properties'].get('bjd_cd', ''))

        # 아파트 이름으로 직접 매칭 시도
        if apt_nm in apt_stats:
            feature['properties']['거래통계'] = apt_stats[apt_nm]
            matched += 1
        else:
            # 부분 매칭 시도 (예: "서초꽃마을1502" -> "서초꽃마을")
            matched_any = False
            for trade_apt_nm in apt_stats.keys():
                if trade_apt_nm in apt_nm or apt_nm in trade_apt_nm:
                    feature['properties']['거래통계'] = apt_stats[trade_apt_nm]
                    matched += 1
                    matched_any = True
                    break

            if not matched_any:
                unmatched_apartments.append(apt_nm)

        # 세대수 / 동수 보강
        attr_key = (apt_nm, bjd_cd)
        if attr_key in attribute_map:
            attr = attribute_map[attr_key]
            if attr.get('household_count') is not None:
                feature['properties']['household_count'] = attr['household_count']
            if attr.get('dngct') is not None:
                feature['properties']['dngct'] = attr['dngct']

    print(f"✅ 매칭 성공: {matched}개")
    print(f"❌ 매칭 실패: {len(unmatched_apartments)}개")

    if unmatched_apartments[:10]:
        print(f"\n매칭 실패한 아파트 샘플 (상위 10개):")
        for apt in unmatched_apartments[:10]:
            print(f"  - {apt}")

    return geojson_data

def save_result(geojson_data):
    """결과 저장"""
    output_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/output/webmap/apartments_with_real_prices.geojson'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 저장 완료: {output_file}")
    return output_file

if __name__ == "__main__":
    print("=" * 70)
    print("아파트 실거래가 데이터 매칭 및 GeoJSON 생성")
    print("=" * 70)

    # 1. 실거래가 데이터 로드
    print("\n[1/5] 실거래가 데이터 로드 중...")
    trades = load_trade_data()
    print(f"총 {len(trades)}건의 거래 데이터 로드 완료")

    # 2. 아파트별 집계
    print("\n[2/5] 아파트별 거래 집계 중...")
    apt_trades = aggregate_trades_by_apartment(trades)
    print(f"총 {len(apt_trades)}개 아파트의 거래 데이터 집계 완료")

    # 3. 통계 계산
    print("\n[3/5] 통계 계산 중...")
    apt_stats = calculate_statistics(apt_trades)
    print(f"총 {len(apt_stats)}개 아파트의 통계 계산 완료")

    # 상위 10개 아파트 출력
    print("\n거래가 가장 많은 아파트 TOP 10:")
    sorted_apts = sorted(apt_stats.items(), key=lambda x: x[1]['거래건수'], reverse=True)
    for i, (apt_name, stats) in enumerate(sorted_apts[:10], 1):
        print(f"{i:2d}. {apt_name}: {stats['거래건수']}건 (평균 {stats['평균가']:,}만원)")

    # 4. GeoJSON과 매칭
    print("\n[4/5] 아파트 위치 데이터와 매칭 중...")
    geojson_data = match_with_geojson(apt_stats)

    # 5. 결과 저장
    print("\n[5/5] 결과 저장 중...")
    output_file = save_result(geojson_data)

    print("\n" + "=" * 70)
    print("✅ 완료!")
    print("=" * 70)
