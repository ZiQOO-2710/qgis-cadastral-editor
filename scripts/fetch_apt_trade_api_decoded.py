#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국토교통부 아파트 매매 실거래가 상세 자료 API
서초구 아파트 실거래가 조회 - Decoding 키 버전
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json

# API 설정 - Decoding 버전 사용
SERVICE_KEY_DECODED = "UTbePYIP4ncyCP2hgiw146sprZ18xCv7Ca5xxNf0CNR1tM3PI7Rldtr08mQQ1a4htR/PhCPWLdAbidhgI7IDIQ=="
BASE_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

# 지역코드
LAWD_CD_SEOCHO = "11650"  # 서울특별시 서초구

def fetch_apartment_trades(lawd_cd=LAWD_CD_SEOCHO, deal_ymd="202410", page_no=1, num_of_rows=10):
    """
    아파트 매매 실거래가 조회

    Args:
        lawd_cd: 지역코드 (11650=서초구)
        deal_ymd: 계약년월 (YYYYMM)
        page_no: 페이지번호
        num_of_rows: 한 페이지 결과 수
    """

    # 모든 파라미터를 urlencode로 처리 (serviceKey 포함)
    params = {
        'serviceKey': SERVICE_KEY_DECODED,
        'LAWD_CD': lawd_cd,
        'DEAL_YMD': deal_ymd,
        'pageNo': str(page_no),
        'numOfRows': str(num_of_rows)
    }

    query_string = urllib.parse.urlencode(params)
    full_url = f"{BASE_URL}?{query_string}"

    print(f"📡 API 호출 중...")
    print(f"지역: 서초구 ({lawd_cd})")
    print(f"기간: {deal_ymd}")
    print(f"페이지: {page_no}, 결과수: {num_of_rows}")
    print(f"URL 앞부분: {full_url[:120]}...")

    try:
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            print(f"\n✅ 응답 코드: {status_code}")

            if status_code == 200:
                # XML 파싱
                response_data = response.read()
                xml_content = response_data.decode('utf-8')

                # XML 저장
                xml_file = f'/mnt/c/Users/ksj27/PROJECTS/QGIS/data/apt_trade_{deal_ymd}_raw.xml'
                with open(xml_file, 'w', encoding='utf-8') as f:
                    f.write(xml_content)
                print(f"💾 XML 저장: {xml_file}")

                # XML 파싱
                root = ET.fromstring(response_data)

                # 응답 헤더 확인
                result_code = root.findtext('.//resultCode')
                result_msg = root.findtext('.//resultMsg')

                print(f"\n결과 코드: {result_code}")
                print(f"결과 메시지: {result_msg}")

                if result_code == "00":  # 정상
                    # 데이터 파싱
                    items = root.findall('.//item')
                    print(f"\n📊 조회 결과: {len(items)}건")

                    trades = []
                    for item in items:
                        trade = {
                            '아파트': item.findtext('아파트', ''),
                            '법정동': item.findtext('법정동', ''),
                            '거래금액': item.findtext('거래금액', '').strip(),
                            '건축년도': item.findtext('건축년도', ''),
                            '년': item.findtext('년', ''),
                            '월': item.findtext('월', ''),
                            '일': item.findtext('일', ''),
                            '전용면적': item.findtext('전용면적', ''),
                            '지번': item.findtext('지번', ''),
                            '지역코드': item.findtext('지역코드', ''),
                            '층': item.findtext('층', ''),
                            '도로명': item.findtext('도로명', ''),
                            '해제사유발생일': item.findtext('해제사유발생일', ''),
                        }
                        trades.append(trade)

                    # JSON 저장
                    json_file = f'/mnt/c/Users/ksj27/PROJECTS/QGIS/data/apt_trade_{deal_ymd}.json'
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(trades, f, ensure_ascii=False, indent=2)
                    print(f"💾 JSON 저장: {json_file}")

                    # 샘플 출력
                    if trades:
                        print(f"\n샘플 데이터 (첫 3건):")
                        for i, trade in enumerate(trades[:3], 1):
                            print(f"\n{i}. {trade['아파트']}")
                            print(f"   위치: {trade['법정동']} {trade['지번']}")
                            print(f"   거래금액: {trade['거래금액']}만원")
                            print(f"   면적: {trade['전용면적']}㎡")
                            print(f"   층: {trade['층']}층")
                            print(f"   거래일: {trade['년']}-{trade['월']}-{trade['일']}")

                    return trades
                else:
                    print(f"❌ API 오류: {result_msg}")
                    return None
            else:
                print(f"❌ HTTP 오류: {status_code}")
                return None

    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP 오류: {e.code}")
        print(f"응답 내용: {e.read().decode('utf-8')[:500]}")
        return None
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 70)
    print("서초구 아파트 매매 실거래가 조회 (Decoding 키 테스트)")
    print("=" * 70)

    # 2024년 10월 데이터만 테스트
    result = fetch_apartment_trades(deal_ymd="202410", num_of_rows=10)

    if result:
        print(f"\n✅ 성공: {len(result)}건 조회")
    else:
        print(f"\n❌ 실패")
