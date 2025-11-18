# 지적도 자동화 스크립트 사용 가이드

한국 지적도 데이터를 자동으로 처리하고 시각화하는 스크립트입니다.

## 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 2. 프로젝트 설정 파일 작성

`config.example.yaml`을 복사하여 프로젝트 설정 파일을 만듭니다:

```bash
# 예시: 주북리 프로젝트
mkdir -p projects/my_project
cp config.example.yaml projects/my_project/config.yaml
```

설정 파일을 편집하여 다음 항목을 수정합니다:

- `project.name`: 프로젝트 이름 (영문, 숫자, 언더스코어만)
- `project.display_name`: 한글 표시 이름
- `project.location`: 위치 설명
- `input.source_shapefile`: 원본 지적도 shapefile 경로
- `input.parcel_lists`: 카테고리별 필지 목록 파일 경로

### 3. 필지 목록 파일 준비

카테고리별 필지 목록을 텍스트 파일로 작성합니다 (한 줄에 하나씩):

**input/green_list.txt** (예시):
```
123
124-1
125
```

**input/blue_list.txt** (예시):
```
126
127-2
```

**input/red_list.txt** (예시):
```
128
```

💡 **Tip**: 지번에서 토지 용도 접미사(전, 답, 대 등)는 자동으로 제거됩니다.

### 4. 실행

```bash
python scripts/cadastral_auto.py --config projects/my_project/config.yaml
```

## 출력 결과

자동화 스크립트는 다음 파일들을 생성합니다:

```
output/
├── {project_name}_categorized.shp      # 카테고리화된 shapefile
├── {project_name}_categorized.shx
├── {project_name}_categorized.dbf
├── {project_name}_categorized.prj
├── {project_name}_areas.csv            # 면적 통계 CSV
├── {project_name}_qgis_script.py       # QGIS 스타일링 스크립트
└── webmap/
    ├── parcels.geojson                 # GeoJSON (EPSG:4326)
    └── index.html                      # Leaflet 웹맵
```

### 출력 형식 설명

#### 1. Shapefile (`.shp`)
- CATEGORY 필드가 추가된 지적도 shapefile
- QGIS에서 직접 열어서 사용 가능
- 카테고리: GREEN, BLUE, RED

#### 2. 면적 통계 CSV (`.csv`)
- 각 필지의 지번, PNU, 카테고리, 면적(㎡, 평) 정보
- Excel 또는 스프레드시트로 열기 가능

#### 3. QGIS 스타일 스크립트 (`.py`)
- QGIS Python 콘솔에서 실행하여 자동 스타일링
- 카테고리별 색상 자동 적용

#### 4. 웹맵 (`.html`)
- 브라우저에서 바로 볼 수 있는 인터랙티브 지도
- Leaflet.js 기반
- 좌표계: EPSG:4326 (WGS84)

## 예제: 주북리 프로젝트

주북리 프로젝트 설정이 미리 준비되어 있습니다:

```bash
python scripts/cadastral_auto.py --config projects/jubulli/config.yaml
```

### 주북리 프로젝트 정보
- **위치**: 경기도 용인시 처인구 양지면 주북리
- **필지 수**: 52개
  - GREEN (낮은 채무): 6필지
  - BLUE (중간 채무): 12필지
  - RED (높은 채무): 2필지
- **원본 데이터**: 용인시 처인구 지적도 shapefile

## QGIS에서 스타일 적용

자동 생성된 PyQGIS 스크립트를 QGIS에서 실행합니다:

1. QGIS 실행
2. Python 콘솔 열기 (`Ctrl+Alt+P` 또는 `플러그인 → Python 콘솔`)
3. 다음 명령 실행:

```python
exec(open(r'output/{project_name}_qgis_script.py', encoding='utf-8').read())
```

스크립트는 자동으로:
- Shapefile 레이어 로드
- 카테고리별 색상 스타일 적용
- 범례 생성
- 레이어로 줌

## 웹맵 확인

생성된 웹맵을 브라우저에서 엽니다:

```bash
# 브라우저에서 파일 열기
file:///mnt/c/Users/ksj27/PROJECTS/qgis-cadastral-editor/output/webmap/index.html
```

또는:

```bash
# 간단한 웹 서버 실행
cd output/webmap
python -m http.server 8000

# 브라우저에서 http://localhost:8000 접속
```

## 설정 파일 상세

### 필수 설정

```yaml
project:
  name: "my_project"              # 프로젝트 ID (영문)
  display_name: "내 프로젝트"     # 한글 이름
  location: "경기도 ○○시"        # 위치

input:
  source_shapefile: "data/source.shp"  # 원본 shapefile
  parcel_lists:
    green: "input/green_list.txt"
    blue: "input/blue_list.txt"
    red: "input/red_list.txt"
```

### 선택 설정

```yaml
output:
  formats:
    - shapefile   # 기본
    - csv         # 기본
    - qml         # QGIS 스타일
    - webmap      # 웹맵
    # - png       # 지도 이미지 (QGIS 필요)
    # - pdf       # PDF 출력 (QGIS 필요)

style:
  categories:
    green:
      color: "#90EE90"    # 색상 (Hex)
      label: "낮은 채무"   # 범례 라벨
      opacity: 0.6        # 투명도 (0-1)

processing:
  clean_jibun: true           # 지번 정리 (접미사 제거)
  convert_to_pyeong: true     # 평 단위 변환
  dbf_encoding: "cp949"       # DBF 인코딩
```

## 문제 해결

### pyproj 설치 오류

```bash
pip install pyproj
```

### PyYAML 설치 오류

```bash
pip install PyYAML
```

### 한글 깨짐

- DBF 인코딩이 `cp949`로 설정되어 있는지 확인
- `processing.dbf_encoding: "cp949"` 설정 확인

### 웹맵이 표시되지 않음

- GeoJSON 파일 확인: `output/webmap/parcels.geojson`
- 브라우저 콘솔(F12)에서 오류 메시지 확인
- pyproj 라이브러리 설치 확인

### 원본 shapefile을 찾을 수 없음

- `input.source_shapefile` 경로가 정확한지 확인
- 절대 경로 또는 프로젝트 루트 기준 상대 경로 사용

## 고급 사용

### 카테고리 없이 전체 필지만 추출

```yaml
input:
  source_shapefile: "data/source.shp"
  all_parcels: "input/all_parcels.txt"  # 단일 파일
  # parcel_lists는 주석 처리
```

### 커스텀 색상 설정

```yaml
style:
  categories:
    green:
      color: "#00FF00"    # 순수 녹색
      label: "안전"
      opacity: 0.8
    red:
      color: "#FF0000"    # 순수 빨강
      label: "위험"
      opacity: 0.8
```

### 좌표계 변경

```yaml
crs:
  source: "EPSG:5186"    # 원본 (Korea 2000 Central Belt)
  output: "EPSG:4326"    # 웹맵용 (WGS84)
  # 다른 좌표계: EPSG:5174, EPSG:5179 등
```

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트 환영합니다!
