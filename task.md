# 세이프잇 (SafeEat) 주차별 작업 현황

### [1~4주차] 기초 및 고도화 (완료)
- [x] 1주차: 문제 정의 및 범위 확정
- [x] 2주차: 텍스트 기반 위험 판단 MVP
- [x] 3주차: OCR(Naver CLOVA) 통합
- [x] 4주차: 지능형 설명 생성(LLM/RAG)

### [5주차] 로그 & 리포트 (진행 중)
- [x] 분석 로그 저장 로직 구현 (`data/logs/`) <!-- id: 108 -->
- [x] 의약품 엔티티 사전 (`entity_index.json`) 고도화 <!-- id: 109 -->
- [x] ResultPage 사용자 맞춤 컨텍스트 UI 적용 <!-- id: 110 -->
- [x] 주간 요약 리포트(Summary Report) 생성 로직 <!-- id: 111 -->
- [x] 통계 지표 정의 및 데이터 정리 <!-- id: 112 -->

### [6주차] MVP 시나리오 정확도 및 신뢰성 완성 (완료 🔥)

> 범위 확장 대신 **정해진 3가지 페르소나의 핵심 시나리오 작동** 및 **위험 근거 명확화(Evidence Fields)**에 집중

**[A] HTN (고혈압 페르소나) — `고령_고혈압` (5/5 완료)**
- [x] HTN_003: 암로디핀 + 자몽 → YELLOW 매칭
- [x] HTN_004: 혈압약 + 감기약(충혈제거제) 병용 → YELLOW 매칭
- [x] HTN_005: 혈압약 + NSAIDs 병용 → YELLOW 매칭
- [x] HTN_006: 이뇨제 + 감초 → YELLOW 매칭 
- [x] HTN_007: 탈수 상황 AND 조건 테스트 → YELLOW 매칭

**[B] DM (당뇨 페르소나) — `고령_당뇨` (4/4 완료)**
- [x] DM_001: 당뇨약 + 공복 음주 → RED 매칭 
- [x] DM_003: 메트포르민 + 과도한 음주 → RED 매칭
- [x] DM_004: 공복 복용 단독 → YELLOW 매칭
- [x] DM_006: 설폰요소제 + 공복 음주 → RED 매칭

**[C] NSAID (진통제 페르소나) — `고령_관절염` (4/4 완료)**
- [x] NSAID_001: NSAID + 알코올 단독 (NSAID_004와 통합) → RED 매칭
- [x] NSAID_002: NSAID + 공복 복용 단독 → YELLOW 매칭
- [x] NSAID_003: 이부프로펜 + 나프록센 중복복용 → RED 매칭 
- [x] NSAID_005: NSAIDs + 와파린 병용 → RED 매칭 

**[+] 위험 근거 구조화 및 평가 로직 고도화 (완료)**
- [x] `evidence_db.json` 필드 세분화: `evidence_source_label`, `evidence_strength`, `evidence_summary_user` 도입
- [x] `risk_assessor.py` 최우선순위 로직 보강: 다중 매칭 시 `risk_level` 적용 후 `evidence_strength` (HIGH>MODERATE>LOW) 순으로 대표 규칙 선정
- [x] 위 개편안을 바탕으로 13개 E2E 테스트 100% 통과 유지 검증

**[공통] 테스트 & 안정화**
- [x] 위 시나리오 전체 E2E 테스트 정리 및 자동화 (1차 완료, 로컬 스크립트 기반)
- [x] 엣지케이스: 약물·식품 미감지 시 GREEN 안전 응답 확인
- [x] `ProfilePage.tsx` 약물/질환 입력 UX 안정화 <!-- id: 128 -->


### [7주차] 마무리 (진행 중 🔧)

**[A] 안정화 및 예외 처리**
- [x] `main.py` 의존성 완전 제거 → `app.py`에 분석 파이프라인 인라인 통합
- [x] LLM 근거 필드명 불일치 수정 (`explainer.py`: `summary`/`source` → `evidence_summary_user`/`evidence_source_label`)
- [x] Evidence 스키마 확장 (`schema.py`: 내부 DB + 외부 API 필드 호환)
- [x] OCR 실패 시 GREEN 안전 응답 Fallback 처리 (`analyze_image`)
- [x] E2E 테스트 18개 확장 (HTN_001~002, DM_002/005, NSAID_004, 엣지케이스 추가) 전체 통과
- [x] 약물 사전 양방향 동기화: `entity_index.json` 상용약 10종 추가, `medi_info.csv` 110+ 키워드 통합
- [x] `엔알라프릴` 표기 통일
- [x] `ProfilePage.tsx` 질환 선택 UI → 2열 그리드 칩 리팩토링
- [x] MVP 시나리오 50개 확장 및 100% 검증 (`test_mvp_scenarios.py`)
- [x] 규칙 엔진 고도화: 페르소나 자가 상호작용 및 범용 카테고리 매핑 지원
- [x] `ruleset.json` / `entity_index.json` 키워드 및 Entity ID 동기화 (50/50 통과)

**[B] 데모 준비 (진행 중)**
- [x] 최종 테스트 결과 리포트 (`test_results.json`) 생성 및 검증
- [ ] 데모 영상 촬영 및 편집
- [ ] 발표 자료 준비
