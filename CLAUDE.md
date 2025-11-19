# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고할 가이드입니다.

## 프로젝트 개요

QGIS 기반 한국 지적도(필지) 데이터 처리 및 시각화 도구입니다. QGIS Python 콘솔에서 실행되도록 설계되었으며, 필지 분석, 카테고리별 스타일 적용, 인쇄 레이아웃 생성, 웹맵 내보내기 등의 워크플로우를 자동화합니다.

## 멀티 에이전트 시스템

이 프로젝트는 자동 멀티 에이전트 시스템을 사용합니다. 사용자가 요청하면 Claude가 자동으로 최적의 에이전트 조합을 선택하여 실행합니다.

### 주요 작업 우선순위

1. **GeoJSON 생성 및 검증** (가장 많이 사용)
2. **웹 개발 (필터, UI 개선)** (두 번째로 많이 사용)

### 사용 가능한 에이전트

**Context7 Agent** - 라이브러리 문서 검색
- QGIS/PyQGIS API 문서
- Leaflet 지도 라이브러리
- Python 패키지 사용법

**Sequential Thinking Agent** - 복잡한 분석
- 인코딩 문제 분석
- 좌표계 변환 로직
- 시스템 설계 검토

**OpenAI Codex Agent** - GPT 기반 코드 검증
- 코드 품질 분석
- 버그 탐지 및 수정
- 성능 최적화 제안
- 대안 구현 비교

**Claude Code** - 실제 코드 작성
- 파일 읽기/쓰기
- 스크립트 실행
- 검증 및 테스트

### 자동 실행 예시

#### GeoJSON 재생성 요청
```
사용자: "GeoJSON 재생성하고 검증해줘"

자동 실행:
┌─────────────────────────────────────┐
│ 1단계: 병렬 분석 (동시 실행)        │
├─────────────────────────────────────┤
│ ┌─ Context7                         │
│ │   └─ QGIS 문서 검색               │
│ │                                    │
│ └─ Sequential                        │
│     └─ 현재 코드 분석                │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 2단계: 실행 (순차)                  │
├─────────────────────────────────────┤
│ Claude Code                          │
│   └─ QGIS Python 콘솔 실행 안내     │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 3단계: 병렬 검증 (동시 실행)        │
├─────────────────────────────────────┤
│ ┌─ Claude Code                      │
│ │   └─ 파일 존재 확인               │
│ │                                    │
│ └─ Sequential                        │
│     └─ 한글 인코딩 확인              │
└─────────────────────────────────────┘
```

#### 웹 UI 개선 요청
```
사용자: "필터 UI 개선해줘"

자동 실행:
┌─────────────────────────────────────┐
│ 1단계: 병렬 분석                    │
├─────────────────────────────────────┤
│ ┌─ Context7                         │
│ │   └─ Leaflet UI 모범사례 검색    │
│ │                                    │
│ └─ Sequential                        │
│     └─ 현재 필터 구조 분석          │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 2단계: 구현                         │
├─────────────────────────────────────┤
│ Claude Code                          │
│   ├─ index.html 수정                │
│   └─ 로컬 서버로 테스트             │
└─────────────────────────────────────┘
```

#### 멀티 AI 검증 요청
```
사용자: "새 필터 기능 만들고 Codex로 검증해줘"

자동 실행:
┌─────────────────────────────────────┐
│ 1단계: Claude Code가 코드 작성     │
├─────────────────────────────────────┤
│ Claude Code                          │
│   └─ index.html 필터 코드 생성      │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 2단계: Codex (GPT)가 검증          │
├─────────────────────────────────────┤
│ OpenAI Codex                         │
│   ├─ 코드 품질 분석                 │
│   ├─ 버그 탐지                      │
│   ├─ 보안 취약점 검사               │
│   └─ 최적화 제안                    │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ 3단계: Claude Code가 개선           │
├─────────────────────────────────────┤
│ Claude Code                          │
│   └─ Codex 피드백 반영하여 수정    │
└─────────────────────────────────────┘
```

### 자동 선택 규칙

**분석 키워드 감지 시** → Sequential Agent 활성화
- "왜", "원인", "분석", "구조", "설계"

**검색 키워드 감지 시** → Context7 Agent 활성화
- "사용법", "API", "문서", "예제", "라이브러리"

**검증 키워드 감지 시** → OpenAI Codex 활성화
- "Codex", "GPT", "검증", "리뷰", "대안"

**구현 키워드 감지 시** → Claude Code 활성화
- "만들어", "수정", "추가", "삭제", "코드"

**복잡도가 높을 때** → 하이브리드 실행 (병렬 + 순차 조합)
- 여러 파일 수정
- 분석 + 구현
- 검증 포함

### 사용 방법

**수동 명령 불필요** - 그냥 평소처럼 요청하면 됩니다:
- ❌ "Context7로 QGIS 문서 찾아줘" (이렇게 안 해도 됨)
- ✅ "QGIS에서 좌표계 변환하는 방법 알려줘" (자동으로 Context7 사용)
- ✅ "새 기능 만들고 Codex로 검증해줘" (자동으로 Codex 사용)

**상세 설정 파일:**
- `.claude/auto-agent.md` - 자동 선택 로직 정의
- `.claude/agents.md` - 에이전트 역할 설명
- `.claude/pipeline.md` - 워크플로우 템플릿

### MCP 서버 설정

**설치된 MCP 서버 (3개):**

1. **Context7** - 라이브러리 문서
   ```bash
   npx -y @upstash/context7-mcp
   ```

2. **Sequential Thinking** - 복잡한 분석
   ```bash
   npx -y @modelcontextprotocol/server-sequential-thinking
   ```

3. **OpenAI Codex** - GPT 코드 검증
   ```bash
   codex mcp serve
   ```

**MCP 서버 관리:**
```bash
# 서버 목록 확인
claude mcp list

# 서버 추가 (예시)
claude mcp add [이름] -- [명령어]

# 서버 제거
claude mcp remove [이름]
```

**요구사항:**
- OpenAI Codex: OpenAI API 키 필요 (OPENAI_API_KEY)
- Context7: 무료
- Sequential Thinking: 무료

## 환경 설정

### 사전 요구사항
- **QGIS**: 3.40.11-Brailslava (한글판 사용 중)
  - Python: 3.12.11
  - GDAL: 3.11.3 (Eganville)
  - PROJ: 9.6.2
- **Python (venv)**: 3.12+ (가상환경 사용)
- **좌표계**: EPSG:5186 (Korea 2000 / Central Belt)
- **외부 의존성**: `korea-cadastral-tools` 패키지

### 초기 설정

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. korea-cadastral-tools 설치 (editable 모드)
cd ../korea-cadastral-tools
pip install -e .
cd ../qgis-cadastral-editor

# 4. 환경변수 확인
# .env 파일을 열어 경로 설정 확인
cat .env

# 5. 설정 확인
python config.py
```

### 프로젝트 구조

```
qgis-cadastral-editor/
├── .env                    # 환경변수 설정 (실제 사용)
├── .env.example            # 환경변수 템플릿
├── config.py               # 경로 및 설정 관리 모듈
├── requirements.txt        # Python 패키지 목록
├── CLAUDE.md              # 이 문서
├── README.md              # 프로젝트 설명
│
├── data/                  # 원본 데이터 (1.2GB)
│   ├── 원본_shapefile/    # 전국 지적도 shapefile
│   │   └── 용인시_처인구/
│   └── AL_D160_50_20250924/
│
├── input/                 # 입력 파일 (5.3MB)
│   ├── green_list.txt     # 녹색 카테고리 필지 목록
│   ├── blue_list.txt      # 파란색 카테고리 필지 목록
│   ├── red_list.txt       # 빨간색 카테고리 필지 목록
│   └── *.pdf              # 토지 등기부등본 (30개)
│
├── output/                # 출력 파일 (4.1MB)
│   ├── *_categorized.shp  # 카테고리화된 shapefile
│   ├── *.csv              # 면적 통계 CSV
│   ├── *.qml              # QGIS 스타일 파일
│   └── webmap/            # 웹맵 HTML
│
└── scripts/               # Python 스크립트 (940KB, 134개)
    ├── common/            # 공통 유틸리티
    ├── haengwonri/        # 행원리 프로젝트
    └── jubulli/           # 주북리 프로젝트
```

### 경로 관리 (config.py)

프로젝트의 모든 경로는 `config.py`를 통해 관리됩니다:

```python
from config import (
    DATA_DIR,           # data/ 디렉토리
    INPUT_DIR,          # input/ 디렉토리
    OUTPUT_DIR,         # output/ 디렉토리
    DEFAULT_CRS,        # EPSG:5186
    OUTPUT_CRS,         # EPSG:4326
    DBF_ENCODING,       # cp949
    get_data_path,      # 데이터 파일 경로 생성
    get_input_path,     # 입력 파일 경로 생성
    get_output_path     # 출력 파일 경로 생성
)

# 사용 예시
shapefile_path = get_data_path('원본_shapefile/용인시_처인구/LSMD_CONT_LDREG_41460.shp')
output_path = get_output_path('jubulli_categorized.shp')
```

### 환경변수 설정 (.env)

프로젝트 설정은 `.env` 파일에서 관리합니다:

```bash
# 프로젝트 디렉토리
PROJECT_DIR=/mnt/c/Users/ksj27/PROJECTS/qgis-cadastral-editor

# 데이터 디렉토리
DATA_DIR=${PROJECT_DIR}/data
INPUT_DIR=${PROJECT_DIR}/input
OUTPUT_DIR=${PROJECT_DIR}/output

# 좌표계 설정
DEFAULT_CRS=EPSG:5186
OUTPUT_CRS=EPSG:4326

# 인코딩 설정
DBF_ENCODING=cp949
```

## 스크립트 실행 모델

### 두 가지 실행 모드

**1. QGIS Python 콘솔 (주 사용 - PyQGIS API 필요)**
```python
# QGIS Python 콘솔에서 실행
exec(open('/mnt/c/Users/ksj27/PROJECTS/qgis-cadastral-editor/scripts/common/apply_categorized_style.py', encoding='utf-8').read())
```

**2. 독립 Python 실행 (PyQGIS 불필요한 스크립트만)**
```bash
# 가상환경 활성화 후 실행
source venv/bin/activate
python scripts/jubulli/extract_52_areas_direct.py
```

### 스크립트 체이닝 패턴

일부 스크립트는 `exec()`를 사용해 작업을 연결합니다:

```python
# 예시: create_jubulli_full_layout.py
script_dir = Path(__file__).parent
exec(open(f'{script_dir}/apply_jubulli_style.py', encoding='utf-8').read())
exec(open(f'{script_dir}/calculate_jubulli_statistics.py', encoding='utf-8').read())
exec(open(f'{script_dir}/create_jubulli_layout.py', encoding='utf-8').read())
```

**보안 주의**: 새 스크립트 작성 시 `exec()` 대신 모듈 import 사용을 권장합니다.

## 아키텍처

### 데이터 흐름

```
1. 입력 데이터 준비
   input/*.txt → 필지 목록 (지번)
   input/*.pdf → 토지 등기부등본

2. Shapefile 처리
   data/원본_shapefile/ → 원본 지적도 shapefile
   ↓
   korea_cadastral.read_dbf() → CP949 인코딩으로 DBF 파싱
   ↓
   필지 매칭 및 CATEGORY 필드 추가 (GREEN/BLUE/RED)
   ↓
   output/*.shp → 처리된 shapefile

3. 시각화 (QGIS Python 콘솔)
   PyQGIS APIs → 카테고리별 스타일 적용
   ↓
   QgsRuleBasedRenderer → CATEGORY 필드로 스타일링
   ↓
   인쇄 레이아웃 또는 PNG 내보내기

4. 웹 출력
   EPSG:5186 → EPSG:4326 변환
   ↓
   GeoJSON + Leaflet HTML
   ↓
   output/webmap/index.html
```

### 중요 인코딩 패턴

한글 텍스트는 특별한 처리가 필요합니다:

```python
# ❌ 잘못된 방법: PyQGIS QVariant는 한글 문자 손실
feature['JIBUN']  # CP949 텍스트 손상 가능

# ✅ 올바른 방법: DBF 바이너리 직접 파싱
from korea_cadastral import read_dbf
records = read_dbf('file.dbf', encoding='cp949')
jibun = records[idx]['JIBUN']  # 한글 보존
```

**이유**: QGIS의 QVariant는 내부적으로 UTF-8을 사용하여 CP949로 인코딩된 한글이 깨질 수 있습니다.

### 좌표계 워크플로우

모든 스크립트는 다음을 가정합니다:
- **입력**: EPSG:5186 (미터 기반, 한국 최적화)
- **출력(웹)**: EPSG:4326 (위경도, Leaflet용)

변환 패턴:
```python
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem
from config import DEFAULT_CRS, OUTPUT_CRS

transform = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem(DEFAULT_CRS),
    QgsCoordinateReferenceSystem(OUTPUT_CRS),
    QgsProject.instance()
)
geom.transform(transform)
```

## 주요 스크립트 사용법

### 1. 필지 면적 추출

**스크립트**: `scripts/jubulli/extract_52_areas_direct.py`

- `korea_cadastral.read_dbf()`로 DBF 직접 읽기
- `parse_shapefile_geometry()`로 SHP에서 지오메트리 파싱
- `sqm_to_pyeong()`으로 ㎡를 평으로 변환
- 면적 계산 결과를 CSV로 출력

```bash
# 독립 실행 (QGIS 불필요)
source venv/bin/activate
python scripts/jubulli/extract_52_areas_direct.py
```

### 2. 카테고리별 Shapefile 생성

**스크립트**: `scripts/haengwonri/create_haengwonri_shapefile.py`

- 대규모 전국 shapefile에서 특정 필지 추출
- DBF/SHP/SHX 형식의 바이너리 직접 조작
- CP949 인코딩 보존

```bash
# 독립 실행
python scripts/haengwonri/create_haengwonri_shapefile.py
```

### 3. 스타일 적용

**스크립트**: `scripts/common/apply_categorized_style.py`

- 3개 카테고리(GREEN/BLUE/RED)로 규칙 기반 렌더러 생성
- CATEGORY 필드가 있는 레이어에 적용
- `QgsRuleBasedRenderer`와 `QgsFillSymbol` 사용

```python
# QGIS Python 콘솔에서만 실행
exec(open('/mnt/c/.../apply_categorized_style.py', encoding='utf-8').read())
```

### 4. 웹맵 생성

**스크립트**: `scripts/common/create_webmap_dbf_direct.py`

- 올바른 인코딩으로 DBF 읽기 (PyQGIS QVariant 문제 회피)
- 좌표 변환 EPSG:5186 → EPSG:4326
- Leaflet.js를 포함한 독립 실행 HTML 생성

```bash
# 출력: output/webmap/index.html (브라우저에서 열기)
python scripts/common/create_webmap_dbf_direct.py
```

### 5. 인쇄 레이아웃 생성

**스크립트**: `scripts/jubulli/create_jubulli_full_layout.py`

- 카테고리화된 shapefile 로드
- 지도 프레임으로 `QgsPrintLayout` 생성
- 카테고리 개수가 포함된 범례 추가
- 제목과 면적 통계 표 추가
- PNG 또는 PDF로 내보내기

```python
# QGIS Python 콘솔에서만 실행
exec(open('/mnt/c/.../create_jubulli_full_layout.py', encoding='utf-8').read())
```

## 공통 패턴

### CATEGORY 필드 추가

1. `input/green_list.txt`, `blue_list.txt`, `red_list.txt`에서 필지 목록 읽기
2. shapefile 레코드와 지번 매칭
3. DBF에 새 CATEGORY 필드 추가
4. 업데이트된 shapefile 작성

예시: `scripts/haengwonri/add_category_field.py`

### 지번 정리

한국 필지 번호(지번)는 토지 용도 접미사를 제거해야 합니다:

```python
# 접미사 제거: 전(논), 답(밭), 대(대지) 등
jibun_clean = jibun
for suffix in ['전', '답', '대', '임', '잡', '도', '천', '구', '유', '제', '하', '목']:
    if jibun.endswith(suffix):
        jibun_clean = jibun[:-1]
        break
```

## 프로젝트별 컨텍스트

### 행원리 프로젝트 (제주, 2024년)
- **위치**: 제주시 구좌읍 행원리
- **목적**: 모듈러주택 시범사업 구역 시각화
- **필지**: 65개 필지, 3개 카테고리 분류
- **출력**:
  - `output/haengwonri_categorized.shp`
  - `output/haengwonri_style.qml`

### 주북리 프로젝트 (용인, 2025년)
- **위치**: 경기도 용인시 처인구 양지면 주북리
- **목적**: 사업부지 필지 조사
- **필지**: 52개 필지
- **총 면적**: 52,357.15㎡ (15,838.04평)
- **카테고리**:
  - GREEN: 6필지, 4,013㎡ (낮은 채무 부담)
  - BLUE: 12필지, 18,878㎡ (중간)
  - RED: 2필지, 6,297㎡ (높은 채무 부담)
- **출력**:
  - `output/jubulli_52_parcels_area.csv`
  - 토지 등기부등본 PDF: 30개 파일

## 문제 해결

### 한글 텍스트가 깨져 보임

**원인**: DBF 인코딩 불일치 (CP949 vs UTF-8)

**해결법**: PyQGIS 대신 `korea_cadastral.read_dbf()` 사용:
```python
# ❌ 대신에:
layer.getFeatures()

# ✅ 사용:
from korea_cadastral import read_dbf
records = read_dbf('file.dbf', encoding='cp949')
```

### 스크립트 실패: "No module named 'qgis'"

**원인**: QGIS Python 환경 외부에서 실행

**해결법**:
1. PyQGIS API를 사용하는 스크립트는 QGIS Python 콘솔에서만 실행
2. 독립 실행 가능한 스크립트는 `korea_cadastral` 라이브러리 사용

### 스크립트 실패: "No module named 'korea_cadastral'"

**원인**: 의존성 미설치

**해결법**:
```bash
cd ../korea-cadastral-tools
pip install -e .
```

### 스크립트 실패: "No module named 'dotenv'"

**원인**: python-dotenv 미설치

**해결법**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 웹맵에서 좌표 불일치

**원인**: Leaflet에서 EPSG:5186 좌표 사용 (EPSG:4326 필요)

**해결법**: GeoJSON 내보내기 전에 항상 변환:
```python
from config import DEFAULT_CRS, OUTPUT_CRS
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem

transform = QgsCoordinateTransform(
    QgsCoordinateReferenceSystem(DEFAULT_CRS),
    QgsCoordinateReferenceSystem(OUTPUT_CRS),
    QgsProject.instance()
)
geom.transform(transform)
```

### 경로 오류

**원인**: 하드코딩된 절대 경로 사용

**해결법**: `config.py` 사용:
```python
from config import get_data_path, get_output_path

# ❌ 하드코딩된 경로
shp_path = 'C:/Users/ksj27/PROJECTS/QGIS/output/jubulli.shp'

# ✅ config.py 사용
shp_path = get_output_path('jubulli.shp')
```

## 개발 가이드라인

### 정보 검색 및 참조

개발 시 **항상 최신 정보를 활용**하세요:

1. **Context7 MCP 서버 활용**
   - QGIS API, PyQGIS, Python 라이브러리 등의 공식 문서 참조
   - 최신 버전의 API 문서와 모범 사례 확인
   - 예시 코드와 패턴 검색

2. **웹 검색 활용**
   - 최신 버그 수정 및 해결 방법 확인
   - 커뮤니티 솔루션 및 토론 참조
   - 최신 라이브러리 버전 및 변경사항 확인

3. **개발 프로세스**
   ```
   문제 발생 → Context7에서 공식 문서 확인
              → 웹 검색으로 최신 솔루션 탐색
              → 검증된 방법으로 구현
   ```

**중요**: 코드 작성 전에 항상 최신 정보를 확인하여 더 이상 사용되지 않는(deprecated) 방법을 사용하지 않도록 주의하세요.

### 새 스크립트 작성 시

1. **경로 관리**: `config.py` 사용
   ```python
   from config import get_data_path, get_output_path, DEFAULT_CRS
   ```

2. **인코딩**: 한글 처리 시 `korea_cadastral.read_dbf()` 사용

3. **좌표계**: EPSG:5186 → EPSG:4326 변환 확인

4. **모듈화**: `exec()` 대신 함수/클래스로 구조화

5. **문서화**: 스크립트 상단에 용도와 사용법 주석 추가

### Git 워크플로우

```bash
# 변경사항 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "설명"

# (선택) 원격 저장소에 푸시
git push
```

**주의**: `.env` 파일은 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

## 설치된 도구 및 MCP 서버

이 프로젝트는 다음 도구들이 설치되어 있습니다:

### ✅ 설치 완료

#### 1. **QGIS MCP 서버** (Claude AI 통합)
- **위치**: `/mnt/c/Users/ksj27/PROJECTS/qgis_mcp`
- **GitHub**: https://github.com/jjsantos01/qgis_mcp
- **버전**: 최신 (2025년 3월 릴리스)
- **기능**:
  - Claude AI에서 QGIS 프로젝트 생성/로드/저장
  - 벡터/래스터 레이어 추가/제거
  - Processing Toolbox 알고리즘 실행
  - QGIS에서 Python 코드 직접 실행

**설치 완료 단계**:
1. ✅ GitHub 저장소 clone (`/mnt/c/Users/ksj27/PROJECTS/qgis_mcp`)
2. ✅ QGIS 플러그인 설치 완료 (`/mnt/c/Users/ksj27/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp_plugin`)
3. ✅ Claude Desktop 설정 완료 (`claude_desktop_config.json`)

**QGIS 플러그인 설치 방법**:
```bash
# 1. QGIS 프로필 폴더 확인
# QGIS 메뉴 (한글): 설정 → 사용자 프로필 → 활성 프로필 폴더 열기

# 2. 플러그인 복사 (이미 완료됨)
# Windows 경로: C:\Users\ksj27\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\qgis_mcp_plugin
# 설치 위치: /mnt/c/Users/ksj27/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp_plugin

# 3. QGIS에서 플러그인 활성화
# QGIS 메뉴: 플러그인 → 플러그인 설치 및 관리
# "설치됐습니다" 탭에서 "QGIS MCP" 검색 후 체크박스 선택
```

**Claude Desktop 설정 완료**:
```json
// /mnt/c/Users/ksj27/AppData/Roaming/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "qgis": {
      "command": "C:\\Users\\ksj27\\AppData\\Local\\Programs\\Python\\Python313\\Scripts\\uv.exe",
      "args": [
        "--directory",
        "C:\\Users\\ksj27\\PROJECTS\\qgis_mcp\\src\\qgis_mcp",
        "run",
        "qgis_mcp_server.py"
      ]
    }
  }
}
```

**⚠️ 중요**:
- `--directory` 경로는 `src/qgis_mcp` 서브디렉토리를 가리켜야 합니다
- 스크립트 이름은 `qgis_mcp_server.py` (하이픈이 아닌 언더스코어)
- Windows 경로 형식 사용: `C:\\Users\\...` (WSL 경로 아님)
- `command`는 **uv.exe의 전체 경로** (Claude Desktop은 PATH를 읽지 못함!)

**✅ 설치 완료 및 연결 성공!**

2025년 11월 18일 기준:
- QGIS MCP 서버: ✅ 정상 작동
- Claude Desktop 연결: ✅ 성공 (`pong: true`)
- 사용 가능 기능: 프로젝트 관리, 레이어 작업, 공간 분석, 지도 렌더링, Python 코드 실행

**📋 사용 방법**:

1. **QGIS 플러그인 시작**
   - QGIS 실행 (버전: 3.40.11-Brailslava)
   - 메뉴: `플러그인` → `QGIS MCP` → `QGIS MCP`
   - "Start Server" 버튼 클릭 (포트 9876에서 대기)

2. **Claude Desktop에서 사용**
   - Claude Desktop 실행
   - QGIS 작업 요청 (예: "QGIS에서 새 프로젝트 만들고 shapefile 로드해줘")
   - MCP 도구가 자동으로 QGIS를 제어

3. **연결 확인**
   - "QGIS에 연결되었는지 확인해줘 (ping)"
   - 성공 시: `pong: true` 응답

**사용 예시**:
```
사용자: QGIS에서 새 프로젝트 만들고 /mnt/c/.../jubulli_categorized.shp 파일 로드해줘

Claude: [QGIS MCP 도구 사용]
        1. create_new_project - 새 프로젝트 생성
        2. add_vector_layer - shapefile 레이어 추가
        3. zoom_to_layer - 레이어로 화면 이동
```

#### 2. **qgis-plugin-manager** (CLI 도구)
- **버전**: 1.7.2
- **설치**: ✅ `pip install qgis-plugin-manager`
- **기능**: QGIS 플러그인 다운로드 및 관리

**사용 예시**:
```bash
# QGIS 플러그인 검색
qgis-plugin-manager search "processing"

# 플러그인 다운로드
qgis-plugin-manager download "plugin-name"
```

#### 3. **qgis-stubs** (타입 힌팅)
- **버전**: 0.2.0.post1
- **설치**: ✅ `pip install qgis-stubs`
- **기능**: PyQGIS Python 스텁 파일 (.pyi) 제공
- **용도**: IDE에서 PyQGIS 코드 자동완성 및 타입 체킹

#### 4. **uv 패키지 매니저**
- **위치**: `/home/ksj27/.local/bin/uv`
- **버전**: 최신
- **용도**: QGIS MCP 서버 실행에 필요

### ⏳ 설치 필요 (선택 사항)

#### 5. **GDAL/OGR** (지리공간 데이터 처리)
- **최신 버전**: 3.12.0 (2025년 11월)
- **현재 상태**: ❌ 미설치 (시스템 라이브러리 필요)

**설치 방법 (Ubuntu/WSL)**:
```bash
# 시스템 패키지 설치 (sudo 권한 필요)
sudo apt-get update
sudo apt-get install -y gdal-bin python3-gdal libgdal-dev

# 가상환경에 Python 바인딩 설치
source venv/bin/activate
pip install GDAL==3.12.0
```

**GDAL CLI 도구**:
- `ogr2ogr`: 벡터 데이터 변환
- `ogrinfo`: 벡터 정보 확인
- `gdal_translate`: 래스터 변환
- `gdalinfo`: 래스터 정보 확인

**사용 예시**:
```bash
# Shapefile을 GeoJSON으로 변환
ogr2ogr -f GeoJSON output.geojson input.shp

# Shapefile 정보 확인
ogrinfo -al input.shp

# 좌표계 변환 (EPSG:5186 → EPSG:4326)
ogr2ogr -t_srs EPSG:4326 -s_srs EPSG:5186 output.shp input.shp
```

### 💡 사용 권장사항

**개발 시 활용**:
1. **QGIS MCP 서버**: Claude AI로 QGIS 작업 자동화
2. **qgis-stubs**: IDE에서 PyQGIS 코드 작성 시 자동완성
3. **GDAL/OGR**: 명령줄에서 빠른 데이터 변환 (설치 시)

**작업 흐름 예시**:
```
1. Claude AI로 데이터 분석 계획 수립
   ↓
2. QGIS MCP로 자동으로 레이어 로드 및 처리
   ↓
3. PyQGIS 스크립트로 세부 작업 수행
   ↓
4. GDAL로 최종 데이터 변환 (필요시)
```

## 관련 프로젝트

- **korea-cadastral-tools**: DBF 파싱, 지오메트리 추출, 면적 변환을 위한 공유 Python 라이브러리 (`../korea-cadastral-tools`에 위치)
- **korean-apartment-viewer**: 아파트 데이터용 웹맵 뷰어 (별도 저장소)

## 추가 리소스

- **QGIS 공식 문서**: https://docs.qgis.org/
- **PyQGIS Cookbook**: https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/
- **한국 좌표계 정보**: https://epsg.io/5186
