# 자동화 스크립트 테스트 가이드

## 빠른 테스트 (5분)

### 1. 스크립트 실행
```bash
cd /mnt/c/Users/ksj27/PROJECTS/qgis-cadastral-editor
source venv/bin/activate
python scripts/cadastral_auto.py --config projects/jubulli/config.yaml
```

**예상 결과**:
```
✅ 자동화 완료!
  GREEN: 11필지, 4,177㎡
  BLUE: 6필지, 1,426㎡
```

### 2. 출력 파일 확인
```bash
ls -lh output/jubulli_categorized.*
cat output/jubulli_areas.csv
```

**확인 사항**:
- ✅ `.shp`, `.dbf`, `.shx`, `.prj` 파일 존재
- ✅ CSV에 17개 필지 정보
- ✅ 면적이 0이 아닌 실제 값

### 3. 웹맵 열기
```bash
# WSL에서 실행
explorer.exe output/webmap/index.html
```

**확인 사항**:
- ✅ 지도에 17개 필지 표시
- ✅ 클릭 시 정보 팝업
- ✅ 범례 (녹색/파란색)
- ✅ 필지 개수 표시

## 상세 테스트 (10분)

### 1. DBF 인코딩 테스트
```bash
python << 'EOF'
from korea_cadastral import read_dbf

records = read_dbf('output/jubulli_categorized.dbf', encoding='cp949')
print(f"총 레코드: {len(records)}개")

# 한글 지번 확인
for idx, record in list(records.items())[:3]:
    jibun = record.get('JIBUN', '')
    category = record.get('CATEGORY', '')
    print(f"  {jibun} - {category}")
EOF
```

**예상 결과**:
```
총 레코드: 17개
  924-4도 - GREEN
  924대 - GREEN
  926-4대 - GREEN
```

### 2. 지오메트리 검증
```bash
python << 'EOF'
from korea_cadastral import parse_shapefile_geometry

geometries = parse_shapefile_geometry('output/jubulli_categorized.shp')
print(f"지오메트리 개수: {len(geometries)}개")

# 면적 샘플
for idx, area in list(geometries.items())[:3]:
    print(f"  필지 {idx}: {area:.2f}㎡")
EOF
```

**예상 결과**:
```
지오메트리 개수: 17개
  필지 0: 132.83㎡
  필지 1: 253.13㎡
  필지 2: 486.25㎡
```

### 3. GeoJSON 검증
```bash
python << 'EOF'
import json

with open('output/webmap/parcels.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

features = data['features']
print(f"GeoJSON 필지: {len(features)}개")

# 좌표계 확인 (EPSG:4326)
first_coords = features[0]['geometry']['coordinates'][0][0]
print(f"첫 좌표: {first_coords}")
print(f"  경도: {first_coords[0]:.6f}")
print(f"  위도: {first_coords[1]:.6f}")
EOF
```

**예상 결과**:
```
GeoJSON 필지: 17개
첫 좌표: [127.243124, 37.249276]
  경도: 127.243124
  위도: 37.249276
```

### 4. CATEGORY 필드 검증
```bash
python << 'EOF'
from korea_cadastral import read_dbf

records = read_dbf('output/jubulli_categorized.dbf', encoding='cp949')

categories = {}
for idx, record in records.items():
    cat = record.get('CATEGORY', '')
    categories[cat] = categories.get(cat, 0) + 1

print("카테고리별 필지 개수:")
for cat in ['GREEN', 'BLUE', 'RED']:
    count = categories.get(cat, 0)
    print(f"  {cat}: {count}개")
EOF
```

**예상 결과**:
```
카테고리별 필지 개수:
  GREEN: 11개
  BLUE: 6개
  RED: 0개
```

## QGIS 테스트 (선택사항)

### QGIS에서 shapefile 로드 및 스타일 적용

1. **QGIS 실행** (버전 3.40+)

2. **Python 콘솔 열기**: `Ctrl+Alt+P`

3. **테스트 스크립트 실행**:
   ```python
   exec(open(r'C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/test_in_qgis.py', encoding='utf-8').read())
   ```

4. **스타일 적용 스크립트 실행**:
   ```python
   exec(open(r'C:/Users/ksj27/PROJECTS/qgis-cadastral-editor/output/jubulli_qgis_script.py', encoding='utf-8').read())
   ```

**확인 사항**:
- ✅ 레이어가 프로젝트에 추가됨
- ✅ 17개 필지 표시
- ✅ 카테고리별 색상 적용:
  - GREEN: 연한 녹색 (#90EE90)
  - BLUE: 하늘색 (#87CEEB)
  - RED: 연한 빨강 (#FFB6C1)
- ✅ 범례에 카테고리 표시

## 문제 해결

### 한글이 깨져 보임
```bash
# DBF 인코딩 확인
python -c "from korea_cadastral import read_dbf; r = read_dbf('output/jubulli_categorized.dbf', encoding='cp949'); print(list(r.values())[0])"
```

### 면적이 0으로 나옴
```bash
# parse_shapefile_geometry() 확인
python -c "from korea_cadastral import parse_shapefile_geometry; g = parse_shapefile_geometry('output/jubulli_categorized.shp'); print(list(g.values())[:3])"
```

### 웹맵이 비어있음
```bash
# GeoJSON 크기 확인
ls -lh output/webmap/parcels.geojson

# 필지 개수 확인
python -c "import json; d = json.load(open('output/webmap/parcels.geojson')); print(f'필지: {len(d[\"features\"])}개')"
```

## 성공 기준

✅ **모든 테스트 통과 시**:
- 17개 필지 추출 (GREEN: 11, BLUE: 6, RED: 0)
- 총 면적: 5,603㎡ (1,695.10평)
- Shapefile 4개 파일 생성 (.shp, .dbf, .shx, .prj)
- CSV에 정확한 면적 데이터
- GeoJSON 17개 필지 포함
- 웹맵에서 필지 클릭 가능
- QGIS에서 카테고리별 색상 표시

## 다음 단계

테스트 완료 후:
1. `projects/` 디렉토리에 새 프로젝트 폴더 생성
2. `config.yaml` 복사 및 수정
3. `input/` 디렉토리에 필지 목록 파일 추가
4. 자동화 스크립트 실행
