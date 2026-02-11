# Medication & Food Safety Guardrail System

## 프로젝트 개요

본 프로젝트는 **처방전 및 식품·건강기능식품 성분표를 분석하여**  
약물–음식(또는 건강기능식품) 간 **잠재적인 상호작용 위험을 사전에 탐지**하고,  
사용자에게 **예방 중심의 경고를 제공하는 AI 기반 가드레일 시스템**을 구축하는 것을 목표로 한다.

병원 외 일상 환경에서 발생하는 복약·식단 충돌 사고는  
정보의 부재가 아니라, **정보가 분산되어 있고 해석이 어렵기 때문에** 발생한다.

본 시스템은 처방전, 약 봉투, 식품 성분표에 존재하는 정보를  
**연결·구조화하여 섭취 직전에 위험 여부를 간단히 확인**할 수 있도록 돕는다.

> ⚠️ 본 시스템은 의료 진단, 처방, 치료 결정을 제공하지 않는다.

---

## 문제 정의

사용자는 병원에서 처방받은 약물과  
일상적으로 섭취하는 음식, 음료, 건강기능식품 간의 **충돌 위험을 직접 판단하기 어렵다**.

- 필요한 정보는 이미 존재함
  - 처방전
  - 약 봉투
  - 식품 및 건강기능식품 성분표
- 그러나 정보가
  - 전문 용어 위주로 제공되고
  - 서로 분산되어 있으며
  - 직관적인 비교가 어렵다

이로 인해 대부분의 사고는 **섭취 이후에야 인지**된다.

본 프로젝트는 **사고 발생 이후 대응이 아닌, 사전 예방 중심의 가드레일 시스템**을 제안한다.

---

## 주요 기능 (MVP)

- **AI 기반 정밀 분석 (Hybrid RAG)**
  - **Rule-based Guardrail**: 사전에 정의된 안전 규칙(`ruleset.json`)을 통한 즉각적인 위험 탐지.
  - **External API Fallback**: 내부 규칙에 없는 약물은 **식약처 'e약은요' API**를 통해 실시간 데이터 조회.
  - **LLM Explanation**: OpenAI `gpt-4o-mini`를 사용하여 의학적 근거 기반의 쉽고 강력한 경고 메시지 생성.
- **다국어 및 상황 대응**: 한국어 기반의 친절하고 전문적인 설명 제공.
- **Persona 기반 테스트**: 고혈압, 당뇨 환자 등 실제 사용자 페르소나를 반영한 8가지 MVP 시나리오 검증 완료.

---

## 설치 및 설정

본 프로젝트를 실행하기 위해서는 다음의 API 키가 필요합니다.

1.  **OpenAI API Key**: LLM 설명 생성용
2.  **공공데이터포털 API Key**: 식약처 'e약은요' 의약품 정보 조회용

### 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음과 같이 설정합니다.

```env
OPENAI_API_KEY=your_openai_api_key_here
DATA_GO_KR_API_KEY=your_public_data_api_key_here
```

### 라이브러리 설치
```bash
pip install -r requirements.txt
```

---

## 시스템 아키텍처

시스템은 **Hybrid RAG(Retrieval-Augmented Generation)** 구조를 따릅니다.

1.  **Entity Parsing**: 사용자의 질문에서 약물, 식품, 상황 엔티티를 추출.
2.  **Risk Assessment**: 추출된 엔티티를 바탕으로 내부 룰셋 매칭.
3.  **Knowledge Retrieval**: 
    - 내부 DB(`evidence_db.json`) 검색.
    - 검색 실패 시 **식약처 API**를 통해 외부 지식 획득.
4.  **Explanation Generation**: 수집된 근거(Evidence)와 위험 등급을 LLM에 전달하여 사용자 맞춤형 설명 생성.

---

## 기술 스택

- **Language**: Python 3.11+
- **LLM**: OpenAI GPT-4o-mini
- **External API**: 식약처 의약품개요정보(e약은요) 서비스
- **Data Conversion**: Rule-based matching, JSON/XML parsing

---

## 실행 방법

### MVP 시나리오 테스트
정의된 8가지 시나리오에 대한 통합 테스트를 수행합니다. (LLM 설명 포함)
```bash
python mvp_test.py
```

### API 연동 테스트
새로운 약물(예: 타이레놀)에 대한 외부 API 연동 기능을 테스트합니다.
```bash
python test_api_rag.py
```

---

## Disclaimer

본 시스템은 의료적 진단이나 처방을 제공하지 않으며, 참고용 정보 제공 및 사고 예방 목적의 가드레일 시스템이다. 의학적 판단이 필요한 경우 반드시 전문가와 상담해야 한다.

