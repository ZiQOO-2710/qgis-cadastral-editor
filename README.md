# QGIS Cadastral Editor

> QGIS 기반 대한민국 지적도 편집 및 시각화 도구

## 소개

QGIS Python 콘솔에서 실행하는 지적도 처리 스크립트 모음입니다.

**주요 기능:**
- ✅ 지적도 Shapefile 로드 및 카테고리별 색상 스타일 적용
- ✅ 필지별 면적 자동 계산 (㎡, 평)
- ✅ 인쇄용 레이아웃 자동 생성
- ✅ 웹맵용 GeoJSON 변환
- ✅ DBF 바이너리 직접 파싱 (한글 인코딩 보장)

## 시스템 요구사항

- **QGIS**: 3.40.11+ (한글판 권장)
- **Python**: 3.12+ (QGIS에 포함된 Python 사용)
- **좌표계**: EPSG:5186 (Korea 2000 / Central Belt)

## 설치

```bash
# 1. korea-cadastral-tools 패키지 설치 (필수)
cd ../korea-cadastral-tools
pip install -e .

# 2. QGIS 실행
# QGIS를 실행하면 자동으로 PyQGIS 환경이 설정됨
```

## 프로젝트 구조

```
qgis-cadastral-editor/
├── scripts/
│   ├── haengwonri/     # 제주 행원리 프로젝트 (6 scripts)
│   ├── jubulli/        # 용인 주북리 프로젝트 (12 scripts)
│   └── common/         # 공통 스타일/레이아웃 (30 scripts)
├── input/              # 필지 목록 및 문서
│   ├── green_list.txt  # 카테고리별 필지 목록
│   ├── blue_list.txt
│   ├── red_list.txt
│   └── *.pdf          # 토지 등기부등본 (30개)
├── docs/
├── requirements.txt
└── README.md
```

## 빠른 시작

### 1. 행원리 프로젝트 (제주 모듈러주택)

**올인원 자동화:**
```python
# QGIS Python 콘솔에서 실행
exec(open('C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/scripts/haengwonri/create_full_layout.py', encoding='utf-8').read())
```

### 2. 주북리 프로젝트 (용인 사업부지)

**52개 필지 면적 추출:**
```python
# QGIS Python 콘솔에서 실행
exec(open('C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/scripts/jubulli/extract_52_areas_direct.py', encoding='utf-8').read())
```

### 3. 공통 스타일 적용

**카테고리별 색상 스타일:**
```python
# 3색 카테고리 + 노란 외곽선
exec(open('C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/scripts/common/apply_categorized_style.py', encoding='utf-8').read())
```

## 주요 스크립트

### haengwonri/ (행원리 프로젝트)
- `add_category_field.py` - CATEGORY 필드 추가
- `create_haengwonri_shapefile.py` - Shapefile 생성
- `check_haengwonri_jibun.py` - 지번 검증
- `search_haengwonri.py` - 필지 검색

### jubulli/ (주북리 프로젝트)
- `extract_52_areas_direct.py` - **52개 필지 면적 추출 (핵심)**
- `create_jubulli_full_layout.py` - 인쇄 레이아웃 생성
- `apply_jubulli_style.py` - 스타일 적용

### common/ (공통 유틸리티)
- `apply_categorized_style.py` - 카테고리별 색상 적용
- `create_full_layout.py` - 인쇄 레이아웃 생성
- `create_webmap_dbf_direct.py` - 웹맵용 GeoJSON 생성
- `export_map_to_png.py` - PNG 이미지 내보내기

## 데이터 형식

### 필지 목록 (input/*.txt)
```
# green_list.txt
821
822-2
827-1
...
```

### Shapefile 구조
- **좌표계**: EPSG:5186
- **필드**: PNU, JIBUN, JIMOK, AREA 등
- **CATEGORY 필드**: GREEN, BLUE, RED (스크립트로 추가)

## 개발 워크플로우

1. **데이터 준비**: input/ 폴더에 필지 목록 작성
2. **Shapefile 생성**: CATEGORY 필드 추가
3. **QGIS 시각화**: 스타일 적용 및 레이아웃 생성
4. **결과 추출**: 면적 계산 또는 웹맵 변환

## 기술 세부사항

### DBF 인코딩 처리
```python
# PyQGIS의 QVariant는 한글 인코딩 손실 가능
# korea-cadastral-tools로 DBF 직접 파싱

from korea_cadastral import read_dbf

records = read_dbf('cadastral.dbf', encoding='cp949', index_by='PNU')
parcel = records['4146136029108210000']
```

### 좌표계 변환
```python
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem

src_crs = QgsCoordinateReferenceSystem('EPSG:5186')  # 미터
dst_crs = QgsCoordinateReferenceSystem('EPSG:4326')  # 위경도
transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())
```

### 면적 계산
```python
from korea_cadastral import parse_shapefile_geometry, sqm_to_pyeong

geometries = parse_shapefile_geometry('cadastral.shp')
area_sqm = geometries[0]
area_pyeong = sqm_to_pyeong(area_sqm)
```

## 프로젝트 히스토리

### Phase 1: 행원리 (2024년)
- **위치**: 제주시 구좌읍 행원리
- **목적**: 모듈러주택 시범사업 구역 시각화
- **성과**: 65개 필지 3색 분류 + 인쇄 레이아웃

### Phase 2: 주북리 (2025년 1월)
- **위치**: 경기도 용인시 처인구 양지면 주북리
- **목적**: 사업부지 52개 필지 면적 조사
- **성과**: 총 면적 52,357.15㎡ (15,838.04평)

## 관련 프로젝트

- [korea-cadastral-tools](https://github.com/yourusername/korea-cadastral-tools) - 공유 Python 라이브러리
- [korean-apartment-viewer](https://github.com/yourusername/korean-apartment-viewer) - 아파트 웹 지도 뷰어

## 라이선스

Internal use only

## 기여

프로젝트 내부 사용 목적
