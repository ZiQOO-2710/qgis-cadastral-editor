# 무릉리 스타일 지적도 자동화 템플릿

토지조서 CSV 파일을 입력받아 위성 이미지 기반 지적도 웹맵을 자동 생성하는 템플릿입니다.

## 특징

- ✅ **위성 이미지 배경** - Esri World Imagery
- ✅ **노란색 필지 강조** - #FFFF00
- ✅ **흰색 지번 라벨** - 각 필지 위에 표시
- ✅ **실제 면적 값** - ㎡와 평 단위 모두 표시
- ✅ **레이어 전환** - 위성/거리 지도 전환 가능
- ✅ **완전 자동화** - CSV → 웹맵까지 원클릭

## 사용법

### 방법 1: 빠른 시작 스크립트 (권장)

```bash
# 가상환경 활성화
source venv/bin/activate

# 스크립트 실행
python templates/muneung_style/quick_start.py \
    --name "프로젝트명" \
    --csv "토지조서.csv 경로" \
    --shapefile "원본_shapefile 경로" \
    --pnu "PNU코드" \
    --display "표시명" \
    --location "위치"
```

**예시 (무릉리 프로젝트):**
```bash
python templates/muneung_style/quick_start.py \
    --name muneung \
    --csv "/mnt/c/Users/ksj27/PROJECTS/autooffice/서귀포시 대정읍 무릉리 토지조서.csv" \
    --shapefile "data/원본_shapefile/서귀포시/LSMD_CONT_LDREG_50130_202510.shp" \
    --pnu "5013010600" \
    --display "무릉리 필지 현황" \
    --location "제주특별자치도 서귀포시 대정읍 무릉리"
```

### 방법 2: 수동 설정

1. **프로젝트 디렉토리 생성**
   ```bash
   mkdir -p projects/프로젝트명
   ```

2. **config.yaml 복사 및 수정**
   ```bash
   cp templates/muneung_style/config_template.yaml projects/프로젝트명/config.yaml
   # config.yaml 파일을 열어 프로젝트 정보 수정
   ```

3. **토지조서에서 지번 추출**
   ```python
   import csv

   jibun_list = []
   with open('토지조서.csv', 'r', encoding='utf-8-sig') as f:
       reader = csv.DictReader(f)
       for row in reader:
           bon = row['본번'].strip()
           bu = row.get('부번', '').strip()
           jibun = f"{bon}-{bu}" if bu else bon
           jibun_list.append(jibun)

   with open('input/프로젝트명_list.txt', 'w') as f:
       f.write('\n'.join(jibun_list))
   ```

4. **자동화 실행**
   ```bash
   python scripts/cadastral_auto.py --config projects/프로젝트명/config.yaml
   ```

5. **웹맵 커스터마이즈**
   ```bash
   # 템플릿 복사
   cp templates/muneung_style/webmap_template.html output/webmap/index.html

   # HTML 파일에서 {{플레이스홀더}} 수동 치환
   # {{DISPLAY_NAME}} → 프로젝트 표시명
   # {{LOCATION}} → 위치
   # {{CATEGORY_LABEL}} → 범례 라벨
   ```

6. **HTTP 서버 시작**
   ```bash
   cd output/webmap
   python3 -m http.server 8888
   ```

## 입력 파일 형식

### 토지조서 CSV

```csv
소재지,본번,부번,면적,지목,지역지구,개별공시지가(25년)
제주 서귀포시 대정읍 무릉리,2024,,,,,
제주 서귀포시 대정읍 무릉리,2427,1,,,,
제주 서귀포시 대정읍 무릉리,2536,임,,,,
```

**필수 컬럼:**
- `소재지` - 위치 정보 (검증용)
- `본번` - 필지 본번
- `부번` - 필지 부번 (없으면 빈칸)

### PNU 코드 찾는 방법

PNU (Parcel Number Unique)는 19자리 필지 고유번호입니다:

```
PNU 구조: AABBCCDDDEEEEEFFFFF
AA     - 시도 코드 (2자리)
BB     - 시군구 코드 (2자리)
CCC    - 읍면동 코드 (3자리)
DDD    - 리 코드 (3자리)
EEEEE  - 본번 (5자리)
FFFFF  - 부번 (5자리)
```

**예시:**
- `5013010600` - 제주(50) 서귀포시(13) 대정읍(01) 무릉리(06) 전체
- `50130106` - 대정읍 전체 (너무 넓음, 비추천)

**찾는 방법:**
1. Shapefile DBF 파일 열기
2. `PNU` 컬럼에서 필지 확인
3. 처음 10자리가 읍면동리 코드

## 출력 파일

### 생성되는 파일들

```
output/
├── 프로젝트명_categorized.shp     # 카테고리화된 shapefile
├── 프로젝트명_areas.csv           # 면적 통계 CSV
├── 프로젝트명_style.qml           # QGIS 스타일 파일
└── webmap/
    ├── index.html                 # 웹맵 HTML (무릉리 스타일)
    └── parcels.geojson           # GeoJSON 데이터
```

### 웹맵 접속

```
http://localhost:8888/index.html
```

**기능:**
- 위성 지도 기본 표시
- 노란색 필지 강조 (#FFFF00)
- 각 필지에 흰색 지번 라벨
- 필지 클릭 → 팝업 (지번, PNU, 면적)
- 우측 상단 레이어 전환 버튼

## 검증 체크리스트

자동화 완료 후 다음을 확인하세요:

- [ ] 필지 개수가 맞는가?
- [ ] 총 면적이 예상 범위 내인가?
- [ ] 모든 지번이 올바르게 매칭되었는가?
- [ ] 웹맵에서 위성 이미지가 보이는가?
- [ ] 필지가 노란색으로 표시되는가?
- [ ] 지번 라벨이 각 필지 위에 보이는가?
- [ ] 팝업에 실제 면적 값이 표시되는가?

## 문제 해결

### 필지가 너무 많이 추출됨

**원인:** PNU 필터가 너무 넓음

**해결:**
1. `config.yaml`의 `pnu_filter` 값 확인
2. 10자리 전체 사용 (읍면동리 코드)
3. 예: `"501301"` → `"5013010600"`

### 웹맵에서 CORS 에러

**원인:** `file://` 프로토콜에서 fetch 불가

**해결:**
```bash
cd output/webmap
python3 -m http.server 8888
```

### 면적 값이 0으로 표시됨

**원인:** GeoJSON에 면적 데이터 누락

**해결:**
```python
import json
import csv

# CSV에서 면적 데이터 읽기
areas = {}
with open('output/프로젝트명_areas.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        jibun = row['jibun']
        areas[jibun] = {
            'area_sqm': float(row['area_sqm']),
            'area_pyeong': float(row['area_pyeong'])
        }

# GeoJSON 업데이트
with open('output/webmap/parcels.geojson', 'r', encoding='utf-8') as f:
    geojson = json.load(f)

for feature in geojson['features']:
    jibun = feature['properties']['jibun']
    if jibun in areas:
        feature['properties']['area_sqm'] = areas[jibun]['area_sqm']
        feature['properties']['area_pyeong'] = areas[jibun]['area_pyeong']

with open('output/webmap/parcels.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
```

### 한글이 깨져 보임

**원인:** 인코딩 문제

**해결:**
- DBF 파일: `cp949` 인코딩 사용
- CSV 파일: `utf-8-sig` (BOM 포함) 사용
- Python 파일 읽기: `encoding='utf-8-sig'`

## 프로젝트 예시

### 무릉리 프로젝트 (2025년)

- **위치**: 제주특별자치도 서귀포시 대정읍 무릉리
- **필지**: 119개 → 40개 (PNU 필터링 후)
- **면적**: 167,604㎡ (50,708평)
- **PNU**: 5013010600
- **소요시간**: 약 3분

## 파일 구조

```
templates/muneung_style/
├── README.md                # 이 문서
├── config_template.yaml     # 설정 템플릿
├── webmap_template.html     # 웹맵 HTML 템플릿
└── quick_start.py           # 빠른 시작 스크립트
```

## 라이선스

이 템플릿은 qgis-cadastral-editor 프로젝트의 일부입니다.
