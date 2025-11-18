#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
국토교통부 아파트 매매 실거래가 상세 자료 API
서초구 아파트 실거래가 조회
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

# API 설정 - 개인 통합 API 인증키 (Encoding 버전)
SERVICE_KEY = "UTbePYIP4ncyCPzhgiw146sprZ18xCv7Ca5xxNf0CNR1tM3Pl7Rldtr08mQQ1a4htR%2FPhCPWLdAbIdhgl7IDlQ%3D%3D"
BASE_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

# 지역코드
LAWD_CD_SEOCHO = "11650"  # 서울특별시 서초구

def fetch_apartment_trades(lawd_cd=LAWD_CD_SEOCHO, deal_ymd="202410", page_no=1, num_of_rows=999):
    """
    아파트 매매 실거래가 조회

    Args:
        lawd_cd: 지역코드 (11650=서초구)
        deal_ymd: 계약년월 (YYYYMM)
        page_no: 페이지번호
        num_of_rows: 한 페이지 결과 수
    """

    # serviceKey를 첫 번째 파라미터로 배치 (이미 인코딩되어 있음)
    params = {
        'LAWD_CD': lawd_cd,
        'DEAL_YMD': deal_ymd,
        'pageNo': str(page_no),
        'numOfRows': str(num_of_rows)
    }

    query_string = urllib.parse.urlencode(params)
    full_url = f"{BASE_URL}?serviceKey={SERVICE_KEY}&{query_string}"

    print(f"📡 API 호출 중...")
    print(f"지역: 서초구 ({lawd_cd})")
    print(f"기간: {deal_ymd}")
    print(f"페이지: {page_no}, 결과수: {num_of_rows}")
    print(f"URL: {full_url[:150]}...")  # URL 첫 150자 출력

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

                if result_code == "000":  # 정상 (API 응답 코드가 000)
                    # 데이터 파싱
                    items = root.findall('.//item')
                    print(f"\n📊 조회 결과: {len(items)}건")

                    trades = []
                    for item in items:
                        trade = {
                            '아파트': item.findtext('aptNm', ''),
                            '법정동': item.findtext('umdNm', ''),
                            '거래금액': item.findtext('dealAmount', '').strip(),
                            '건축년도': item.findtext('buildYear', ''),
                            '년': item.findtext('dealYear', ''),
                            '월': item.findtext('dealMonth', ''),
                            '일': item.findtext('dealDay', ''),
                            '전용면적': item.findtext('excluUseAr', ''),
                            '지번': item.findtext('jibun', ''),
                            '지역코드': item.findtext('sggCd', ''),
                            '층': item.findtext('floor', ''),
                            '도로명': item.findtext('roadNm', ''),
                            '해제사유발생일': item.findtext('cdealDay', ''),
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
    print("서초구 아파트 매매 실거래가 조회 (국토교통부 API)")
    print("=" * 70)

    # 2024년 최근 3개월 데이터 조회
    months = ["202410", "202409", "202408"]  # 2024년 10월, 9월, 8월

    for deal_ymd in months:
        print(f"\n\n{'=' * 70}")
        print(f"📅 {deal_ymd} 데이터 조회")
        print("=" * 70)

        result = fetch_apartment_trades(deal_ymd=deal_ymd)

        if result:
            print(f"\n✅ {deal_ymd}: {len(result)}건 조회 성공")
        else:
            print(f"\n❌ {deal_ymd}: 조회 실패")
