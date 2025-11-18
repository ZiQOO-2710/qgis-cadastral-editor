#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공공데이터 포털 API를 사용하여 서초구 아파트 단지 정보 가져오기
한국부동산원_공동주택 단지 식별정보 조회 서비스
"""

import urllib.request
import urllib.parse
import json
import sys

# API 설정 (Decoding 버전 사용 - urllib이 자동 인코딩)
SERVICE_KEY = "UTbePYIP4ncyCP2hgiw146sprZ18xCv7Ca5xxNf0CNR1tM3PI7Rldtr08mQQ1a4htR/PhCPWLdAbidhgI7IDIQ=="
BASE_URL = "https://api.odcloud.kr/api"

# Swagger 문서에서 확인한 엔드포인트
ENDPOINT = "/AptIdInfoSvc/v1/getAptInfo"

def fetch_apartments(address="서초", page=1, per_page=1000):
    """
    아파트 단지 정보 조회

    Args:
        address: 주소 검색어 (서초)
        page: 페이지 번호
        per_page: 페이지당 데이터 수
    """

    url = f"{BASE_URL}{ENDPOINT}"

    # 기술문서대로 정확한 파라미터 구성
    params = {
        'page': str(page),
        'perPage': str(per_page),
        'cond[ADRES::LIKE]': address,
        'serviceKey': SERVICE_KEY
    }

    # URL 파라미터 인코딩
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    print(f"📡 API 호출 중...")
    print(f"URL: {url}")
    print(f"파라미터: page={page}, perPage={per_page}, address={address}")
    print(f"인증: serviceKey (Query parameter)")

    try:
        req = urllib.request.Request(full_url)

        with urllib.request.urlopen(req, timeout=30) as response:
            status_code = response.getcode()
            print(f"\n✅ 응답 코드: {status_code}")

            if status_code == 200:
                # JSON 파싱
                response_data = response.read()
                data = json.loads(response_data.decode('utf-8'))

                # 응답 구조 확인
                print(f"\n📊 응답 데이터 구조:")
                preview = json.dumps(data, ensure_ascii=False, indent=2)
                print(preview[:500] + "...")

                # 데이터 저장
                output_file = '/mnt/c/Users/ksj27/PROJECTS/QGIS/data/api_apartments_raw.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print(f"\n💾 데이터 저장 완료: {output_file}")

                return data
            else:
                print(f"\n❌ API 호출 실패 (HTTP {status_code})")
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
    print("=" * 60)
    print("서초구 아파트 단지 정보 조회 (공공데이터 포털 API)")
    print("=" * 60)

    result = fetch_apartments()

    if result:
        print("\n✅ API 호출 성공!")
    else:
        print("\n❌ API 호출 실패")
        sys.exit(1)
