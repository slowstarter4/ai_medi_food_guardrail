# Risk Assessment Engine (Rule-based Core)

## 개요

본 프로젝트는 **약물·음식 입력에 대한 위험도를 판단하는 룰 기반 엔진**을 중심으로 구성되어 있으며,  
LLM/RAG는 **설명 보조 역할로만 확장 가능**하도록 설계되었다.

핵심 원칙은 다음과 같다.

- **Rule Engine은 판단하지 않는다**
- **의사결정은 단일 진입점에서만 수행한다**
- **AI(LLM)는 필수 구성요소가 아니다**

---

## 디렉토리 구조

```text
app/
├─ data/
│  └─ rules/
│     └─ ruleset.json        # 룰 정의 (정적 데이터)
│
├─ service/
│  ├─ risk_assessor.py       # 최종 위험도 판단 (assess_risk)
│  └─ entity_parser.py       # 입력 텍스트 → entities
│
├─ src/
│  └─ rules/
│     ├─ loader.py           # ruleset.json 로딩
│     └─ evaluator.py        # 룰 매칭 로직
│
├─ docs/
│  └─ rule_spec.md           # 룰 설명 및 근거 문서
│
└─ main.py                   # 엔트리 포인트
```

## 책임 분리 설계 (Separation of Responsibilities)

Risk Engine은 **판단 로직, 규칙 정의, 입출력 인터페이스를 명확히 분리**하는 것을 핵심 설계 원칙으로 한다.  
이를 통해 규칙 변경, 엔진 교체, LLM/RAG 확장을 최소한의 영향 범위로 수행할 수 있다.

---

### 1. Risk Engine (`risk_engine.py`)

**책임**

- 외부 입력을 받아 위험 판단 프로세스를 오케스트레이션
- Rule Set을 로드하고 규칙 평가를 수행
- 최종 Risk 판단 결과를 표준 스키마로 반환

**하지 않는 것**

- 규칙 자체를 하드코딩하지 않음
- 의료/식품 지식 판단을 직접 생성하지 않음
- LLM 기반 판단을 직접 수행하지 않음

```text
입력 → 규칙 평가 → risk_level 산출 → 결과 구조화
```

### 2. Rule Definition (`ruleset.json`)

**책임**

- 위험 판단 기준을 선언적으로 정의
- 규칙 추가/수정 시 코드 변경 없이 대응 가능
- rule_id, 조건, 위험 레벨 매핑 관리

**설계 의도**

- 기획자/도메인 지식 보유자가 코드 수정 없이 규칙 관리
- 규칙 버전 관리 및 변경 이력 추적 용이

### 3. Input Layer (상위 Service / API)

**책임**

- OCR, 텍스트 입력, 사용자 입력 등 원천 데이터 처리
- 표준화된 엔진 입력 포맷으로 변환
  **엔진과의 경게**
- Risk Engine은 입력이 이미 정제되었다는 가정 하에 동작
- 입력 품질 문제는 상위 계층 책임

### 4. Output Consumer (RAG / LLM / UI)

**책임**

- Risk Engine의 판단 결과를 해석 및 설명
- LLM 기반 근거 생성, 사용자 친화적 메시지 변환
- UI 표시 및 사용자 액션 연결

### 5. 설계 효과 요약

| 항목      | 효과                         |
| --------- | ---------------------------- |
| 규칙 변경 | JSON 수정만으로 가능         |
| 엔진 교체 | 인터페이스 유지 시 영향 최소 |
| LLM 연동  | 안전망(Rule Engine) 유지     |
| 테스트    | 규칙/엔진 단위 테스트 가능   |

### 6. 향후 확장 포인트

- Rule Engine 결과 + RAG 기반 근거 문서 연결
- Rule 기반 판단 실패 시 LLM 보조 판단
- 규칙 충돌 감지 및 우선순위 시스템 도입
