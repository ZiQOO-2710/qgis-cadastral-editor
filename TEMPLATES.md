# 지적도 자동화 템플릿 가이드

프로젝트별 스타일로 지적도 웹맵을 자동 생성하는 템플릿 모음입니다.

## 사용 가능한 템플릿

### 1. 무릉리 스타일 (muneung_style)

**특징:**
- 위성 이미지 배경 (Esri World Imagery)
- 노란색 필지 강조 (#FFFF00)
- 흰색 지번 라벨 (각 필지 위 표시)
- 실제 면적 값 (㎡ + 평)
- 레이어 전환 기능

**사용 사례:**
- 단일 색상으로 필지 현황 표시
- 토지조서 기반 지적도 시각화
- 위성 이미지 위에 필지 경계 표시

**빠른 시작:**
```bash
python templates/muneung_style/quick_start.py \
    --name "프로젝트명" \
    --csv "토지조서.csv" \
    --shapefile "원본.shp" \
    --pnu "PNU코드" \
    --display "표시명" \
    --location "위치"
```

**상세 문서:** `templates/muneung_style/README.md`

## 템플릿 디렉토리 구조

```
templates/
├── TEMPLATES.md                 # 이 문서
└── muneung_style/              # 무릉리 스타일 템플릿
    ├── README.md               # 상세 사용 설명서
    ├── config_template.yaml    # 설정 템플릿
    ├── webmap_template.html    # 웹맵 HTML 템플릿
    └── quick_start.py          # 원클릭 자동화 스크립트
```

## 새 템플릿 추가 방법

### 1. 템플릿 디렉토리 생성

```bash
mkdir -p templates/새템플릿명
```

### 2. 필수 파일 작성

```bash
templates/새템플릿명/
├── README.md                # 템플릿 설명 및 사용법
├── config_template.yaml     # YAML 설정 템플릿
├── webmap_template.html     # 웹맵 HTML 템플릿 (선택)
└── quick_start.py           # 자동화 스크립트 (선택)
```

### 3. config_template.yaml 작성

```yaml
project:
  name: "프로젝트명"
  display_name: "표시 이름"
  location: "위치"

input:
  source_shapefile: "data/원본_shapefile/경로.shp"
  pnu_filter: "PNU코드"

  parcel_lists:
    green: "input/green_list.txt"
    blue: "input/blue_list.txt"
    red: "input/red_list.txt"

output:
  directory: "output"
  formats:
    - shapefile
    - csv
    - qml
    - webmap

processing:
  clean_jibun: true

style:
  categories:
    GREEN:
      color: "#색상코드"
      label: "라벨"
    BLUE:
      color: "#색상코드"
      label: "라벨"
    RED:
      color: "#색상코드"
      label: "라벨"

crs:
  source: "EPSG:5186"
  target: "EPSG:4326"

encoding:
  dbf: "cp949"
  csv: "utf-8"
```

### 4. webmap_template.html 작성

플레이스홀더 사용:
- `{{DISPLAY_NAME}}` - 프로젝트 표시명
- `{{LOCATION}}` - 위치
- `{{CATEGORY_LABEL}}` - 범례 라벨

**예시:**
```html
<h3>{{DISPLAY_NAME}}</h3>
<div class="location">📍 {{LOCATION}}</div>
```

### 5. quick_start.py 작성 (선택)

전체 워크플로우를 자동화하는 스크립트:

```python
#!/usr/bin/env python3
import argparse

def main():
    parser = argparse.ArgumentParser()
    # 인자 정의
    args = parser.parse_args()

    # 1. 입력 데이터 처리
    # 2. config.yaml 생성
    # 3. 자동화 실행
    # 4. 웹맵 커스터마이즈
    # 5. HTTP 서버 시작

if __name__ == '__main__':
    main()
```

## 템플릿 선택 가이드

### 무릉리 스타일을 사용해야 하는 경우:

✅ 단일 색상으로 모든 필지 표시
✅ 위성 이미지 위에 필지 경계 보기
✅ 토지조서 CSV 파일이 입력
✅ 빠른 시각화 필요

### 새 템플릿이 필요한 경우:

🔨 3개 카테고리 색상 구분 필요 (GREEN/BLUE/RED)
🔨 도로지도 배경 선호
🔨 특수한 범례나 정보 표시 필요
🔨 다른 스타일의 라벨/팝업 필요

## 예시 프로젝트

### 무릉리 프로젝트 (2025)

```bash
python templates/muneung_style/quick_start.py \
    --name muneung \
    --csv "/mnt/c/Users/ksj27/PROJECTS/autooffice/서귀포시 대정읍 무릉리 토지조서.csv" \
    --shapefile "data/원본_shapefile/서귀포시/LSMD_CONT_LDREG_50130_202510.shp" \
    --pnu "5013010600" \
    --display "무릉리 필지 현황" \
    --location "제주특별자치도 서귀포시 대정읍 무릉리"
```

**결과:**
- 119개 지번 추출
- 40개 필지 매칭 (167,604㎡)
- 웹맵 생성: `http://localhost:8888/index.html`

## 공통 작업 흐름

### 모든 템플릿의 기본 흐름:

```
1. 입력 데이터 준비
   ├── 토지조서 CSV 또는 지번 목록
   ├── 원본 shapefile
   └── PNU 필터 코드

2. 설정 파일 생성
   └── config.yaml (템플릿 기반)

3. 자동화 실행
   └── scripts/cadastral_auto.py

4. 웹맵 커스터마이즈 (선택)
   └── webmap_template.html 적용

5. 결과 확인
   └── HTTP 서버로 웹맵 열기
```

## 문제 해결

### 템플릿 실행 오류

**증상:**
```
ModuleNotFoundError: No module named 'yaml'
```

**해결:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 웹맵 표시 오류

**증상:** CORS 에러, ERR_FILE_NOT_FOUND

**해결:**
```bash
cd output/webmap
python3 -m http.server 8888
# http://localhost:8888/index.html 접속
```

### PNU 필터링 문제

**증상:** 필지가 너무 많거나 적게 추출됨

**해결:**
- 읍면동리 단위 (10자리) 사용
- 예: `5013010600` (O), `501301` (X)

## 추가 자료

- **프로젝트 개요**: `README.md`
- **개발 가이드**: `CLAUDE.md`
- **자동화 스크립트**: `scripts/cadastral_auto.py`
- **테스트 가이드**: `TEST_GUIDE.md`
