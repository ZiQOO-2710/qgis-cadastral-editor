# 자동 에이전트 선택 로직

## 키워드 기반 자동 선택

### Context7 Agent 활성화
```yaml
triggers:
  keywords:
    - "사용법"
    - "API"
    - "문서"
    - "예제"
    - "라이브러리"
    - "QGIS"
    - "PyQGIS"
    - "Leaflet"
    - "패키지"

  patterns:
    - "어떻게 사용"
    - "방법 알려"
    - "문서 찾아"
    - "예제 보여"
```

### Sequential Thinking Agent 활성화
```yaml
triggers:
  keywords:
    - "왜"
    - "원인"
    - "분석"
    - "구조"
    - "설계"
    - "인코딩"
    - "좌표계"
    - "변환"
    - "디버그"

  patterns:
    - "왜 안 되"
    - "문제가 뭐"
    - "원인 파악"
    - "분석해"
```

### OpenAI Codex Agent 활성화
```yaml
triggers:
  keywords:
    - "Codex"
    - "GPT"
    - "검증"
    - "리뷰"
    - "대안"
    - "최적화"
    - "품질"
    - "버그"

  patterns:
    - "코드 검증"
    - "Codex로"
    - "GPT로"
    - "대안 제시"
```

### Claude Code Agent 활성화
```yaml
triggers:
  keywords:
    - "만들어"
    - "수정"
    - "추가"
    - "삭제"
    - "코드"
    - "파일"
    - "실행"
    - "테스트"

  patterns:
    - "코드 작성"
    - "파일 생성"
    - "스크립트 실행"
```

---

## 복잡도 기반 자동 선택

### 단순 작업 (단일 에이전트)
```yaml
conditions:
  - 단일 파일 수정
  - 간단한 질문
  - 명확한 요청

agent: Claude Code (기본)
```

### 중간 복잡도 (2개 에이전트)
```yaml
conditions:
  - 여러 파일 관련
  - 분석 + 구현
  - 문서 참조 필요

agents:
  - Context7 또는 Sequential (분석)
  - Claude Code (구현)
```

### 높은 복잡도 (3개 이상 에이전트)
```yaml
conditions:
  - 시스템 전체 수정
  - 검증 요청 포함
  - 다단계 작업

agents:
  - Context7 (문서)
  - Sequential (분석)
  - Claude Code (구현)
  - Codex (검증)
```

---

## 우선순위 규칙

### 1. 명시적 요청 우선
사용자가 특정 에이전트를 언급하면 해당 에이전트 사용:
- "Codex로 검증해줘" → Codex 사용
- "Context7에서 찾아줘" → Context7 사용

### 2. 작업 유형별 기본 에이전트
```yaml
GeoJSON_작업:
  primary: Claude Code
  support: Sequential (인코딩 분석)

웹_개발:
  primary: Claude Code
  support: Context7 (Leaflet 문서)

문제_해결:
  primary: Sequential
  support: Context7

코드_검증:
  primary: Codex
  support: Claude Code
```

### 3. 병렬 vs 순차 결정
```yaml
병렬_실행:
  - 독립적인 분석 작업
  - 동시에 가능한 검색
  - 서로 의존성 없음

순차_실행:
  - 이전 결과가 필요한 경우
  - 분석 → 구현 → 검증 흐름
  - 파일 생성 후 검증
```

---

## 자동 선택 알고리즘

```python
def select_agents(user_request):
    agents = []

    # 1. 키워드 매칭
    if matches_context7_keywords(user_request):
        agents.append("Context7")

    if matches_sequential_keywords(user_request):
        agents.append("Sequential")

    if matches_codex_keywords(user_request):
        agents.append("Codex")

    # 2. 기본 에이전트 (항상 포함)
    agents.append("Claude Code")

    # 3. 복잡도에 따른 실행 방식 결정
    if len(agents) == 1:
        return {"mode": "single", "agents": agents}
    elif len(agents) == 2:
        return {"mode": "sequential", "agents": agents}
    else:
        return {"mode": "hybrid", "agents": agents}
```

---

## 피드백 루프

### 실패 시 자동 재시도
```yaml
retry_logic:
  max_attempts: 3

  on_failure:
    - 다른 에이전트로 전환
    - 추가 컨텍스트 수집
    - 사용자에게 확인 요청
```

### 결과 검증
```yaml
validation:
  - 파일 존재 확인
  - 한글 인코딩 검증
  - 기능 동작 테스트
```
