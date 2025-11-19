# CLAUDE.md

이 파일은 Claude Code가 이 저장소에서 작업할 때 참고할 가이드입니다.

## 프로젝트 개요

QGIS 기반 한국 지적도(필지) 데이터 처리 및 시각화 도구입니다. 필지 분석, 카테고리별 스타일 적용, 웹맵 내보내기 등의 워크플로우를 자동화합니다.

## 빠른 참조

### 핵심 설정
- **좌표계**: EPSG:5186 (입력) → EPSG:4326 (웹 출력)
- **인코딩**: CP949 (한글 DBF)
- **경로 관리**: `config.py` 사용

### 자주 쓰는 명령
```bash
# 가상환경 활성화
source venv/bin/activate

# 독립 스크립트 실행
python scripts/jubulli/extract_52_areas_direct.py

# QGIS 콘솔에서 실행
exec(open('/path/to/script.py', encoding='utf-8').read())
```

---

## 멀티 에이전트 시스템

사용자 요청에 따라 최적의 에이전트 조합을 자동 선택합니다.

### 에이전트 목록

| 에이전트 | 역할 | 활성화 키워드 |
|---------|------|--------------|
| **Context7** | 라이브러리 문서 검색 | 사용법, API, 문서, 예제 |
| **Sequential** | 복잡한 분석/설계 | 왜, 원인, 분석, 구조 |
| **Codex** | GPT 기반 코드 검증 | Codex, GPT, 검증, 리뷰 |
| **Claude Code** | 코드 작성/실행 | 만들어, 수정, 추가, 코드 |

### 사용 방법

수동 명령 불필요 - 평소처럼 요청하면 자동으로 에이전트가 선택됩니다:
- ✅ "QGIS에서 좌표계 변환하는 방법 알려줘" → Context7 자동 사용
- ✅ "새 기능 만들고 Codex로 검증해줘" → Codex 자동 사용

**설정 파일**: `.claude/agents.md`, `.claude/auto-agent.md`, `.claude/pipeline.md`

### 멀티 AI 협업

코드 검증 요청 시 자동으로 협업:
1. **Claude Code** - 코드 작성
2. **Codex (GPT)** - 품질/버그/보안 검증
3. **Claude Code** - 피드백 반영하여 수정

예시: "새 기능 만들고 Codex로 검증해줘"

### MCP 서버

```bash
# 설치된 서버 확인
claude mcp list

# 서버 추가
claude mcp add [이름] -- [명령어]
```

**설치됨**: Context7, Sequential Thinking
**선택**: OpenAI Codex (API 키 필요)

---

## 환경 설정

### 사전 요구사항
- **QGIS**: 3.40.11-Brailslava
- **Python**: 3.12+ (가상환경)
- **의존성**: `korea-cadastral-tools`

### 초기 설정

```bash
source venv/bin/activate
pip install -r requirements.txt
cd ../korea-cadastral-tools && pip install -e . && cd -
```

### 전국 지적도 데이터

**위치**: `E:\연속지적도 전국`

전국 모든 시/군/구의 연속지적도 shapefile이 저장되어 있음. 지번만 알면 해당 지역 shapefile을 찾아서 지적도 생성 가능.

### 프로젝트 구조

```
qgis-cadastral-editor/
├── config.py              # 경로/설정 관리
├── .claude/               # 에이전트 설정
├── data/                  # 원본 shapefile (1.2GB)
├── input/                 # 필지 목록, PDF
├── output/                # 처리된 파일, 웹맵
├── scripts/               # Python 스크립트
│   ├── common/            # 공통 유틸리티
│   ├── haengwonri/        # 행원리 프로젝트
│   └── jubulli/           # 주북리 프로젝트
└── templates/             # 재사용 템플릿

E:\연속지적도 전국/           # 전국 지적도 데이터
└── [시도]/[시군구]/         # 지역별 shapefile
```

### 경로 관리

```python
from config import get_data_path, get_output_path, DEFAULT_CRS

shapefile = get_data_path('원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41460.shp')
output = get_output_path('result.shp')
```

---

## 핵심 패턴

### 한글 인코딩

```python
# ❌ PyQGIS - 한글 깨짐 가능
feature['JIBUN']

# ✅ 직접 파싱 - 한글 보존
from korea_cadastral import read_dbf
records = read_dbf('file.dbf', encoding='cp949')
```

### 좌표계 변환

```python
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem

transform = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem('EPSG:5186'),
    QgsCoordinateReferenceSystem('EPSG:4326'),
    QgsProject.instance()
)
geom.transform(transform)
```

### 지번 정리

```python
# 토지 용도 접미사 제거
for suffix in ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목']:
    if jibun.endswith(suffix):
        jibun = jibun[:-1]
        break
```

---

## 주요 스크립트

### 면적 추출
```bash
python scripts/jubulli/extract_52_areas_direct.py
```

### 카테고리별 Shapefile 생성
```bash
python scripts/haengwonri/create_haengwonri_shapefile.py
```

### 스타일 적용 (QGIS 콘솔)
```python
exec(open('.../scripts/common/apply_categorized_style.py', encoding='utf-8').read())
```

### 웹맵 생성
```bash
python scripts/common/create_webmap_dbf_direct.py
# 출력: output/webmap/index.html
```

---

## 프로젝트별 정보

### 행원리 (제주, 2024)
- 65개 필지, 3개 카테고리
- 출력: `output/haengwonri_categorized.shp`

### 주북리 (용인, 2025)
- 52개 필지, 52,357㎡ (15,838평)
- GREEN: 6필지 / BLUE: 12필지 / RED: 2필지
- 출력: `output/jubulli_52_parcels_area.csv`

---

## 문제 해결

| 문제 | 원인 | 해결 |
|-----|------|------|
| 한글 깨짐 | CP949 vs UTF-8 | `korea_cadastral.read_dbf()` 사용 |
| `No module 'qgis'` | QGIS 외부 실행 | QGIS 콘솔에서 실행 |
| `No module 'korea_cadastral'` | 미설치 | `pip install -e ../korea-cadastral-tools` |
| 웹맵 좌표 불일치 | EPSG:5186 그대로 사용 | EPSG:4326으로 변환 |
| 경로 오류 | 하드코딩 | `config.py` 사용 |

---

## 개발 가이드라인

### 새 스크립트 작성 시

1. **경로**: `config.py` 사용
2. **인코딩**: `korea_cadastral.read_dbf()` 사용
3. **좌표계**: 변환 확인
4. **모듈화**: `exec()` 대신 import 사용
5. **문서화**: 용도/사용법 주석

### 정보 검색

1. **Context7** - 공식 문서 (QGIS, PyQGIS, Leaflet)
2. **웹 검색** - 최신 솔루션, 버그 수정

---

## 설치된 도구

### MCP 서버
- **Context7** - 라이브러리 문서
- **Sequential** - 복잡한 분석
- **QGIS MCP** - QGIS 원격 제어 (Claude Desktop용)

### Python 패키지
- **qgis-stubs** - IDE 자동완성
- **qgis-plugin-manager** - 플러그인 CLI

### QGIS MCP 사용법

1. QGIS에서 `플러그인 → QGIS MCP → Start Server`
2. Claude Desktop에서 QGIS 작업 요청
3. 연결 확인: "QGIS에 연결되었는지 확인해줘"

---

## 관련 프로젝트

- **korea-cadastral-tools** - DBF 파싱, 면적 변환 라이브러리
- **korean-apartment-viewer** - 아파트 웹맵 뷰어

## 추가 리소스

- [QGIS 공식 문서](https://docs.qgis.org/)
- [PyQGIS Cookbook](https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/)
- [EPSG:5186](https://epsg.io/5186)
