# 구현 계획 - 5주차: 로그(기록) 및 지능형 리포트

사용자가 수행한 복약·식품 안전성 검사 결과를 기록하고, 이를 분석하여 인사이트를 제공하는 **세이프잇(SafeEat)** 기록 시스템을 설계합니다.

## 1. 로그 데이터 스키마 (Log Schema)
각 분석 결과를 다음과 같은 구조로 저장하여 추후 통계 및 요약에 활용합니다.

```json
{
  "log_id": "uuid",
  "user_id": "user_01",
  "timestamp": "2026-02-11T16:15:00Z",
  "input": {
    "type": "text | image",
    "content": "타이레놀 먹고 술 마셔도 돼?"
  },
  "analysis_result": {
    "risk_level": "RED",
    "detected_drugs": ["아세트아미노펜"],
    "detected_foods": ["알코올"],
    "risk_id": "RED_ALCOHOL_ACETAMINOPHEN"
  },
  "explanation": "간 손상 위험이 높으니 절대 금지입니다...",
  "status": "CHECKED"
}
```

## 2. 데이터 저장 방식 (Storage Strategy)
- **초기(MVP)**: `data/logs/{user_id}/{YYYY-MM-DD}.json` 파일 시스템 기반 저장.
  - 장점: 별도의 DB 설정 없이 빠르게 구현 가능하며, 인간이 읽기 쉬움.
- **고도화**: SQLite를 도입하여 복잡한 쿼리(예: 특정 기간 위험 노출 횟수 합산) 처리 속도 개선.

## 3. 주간 리포트 생성 로직 (Weekly Summary Pipeline)
1. **데이터 수집**: 특정 기간(예: 7일) 동안의 로그 파일을 모두 로드.
2. **지표 계산**:
   - 총 검사 횟수
   - 위험 단계별 발생 빈도 (RED / CAUTION / NONE)
   - 가장 자주 확인한 약물/식품 TOP 3
3. **LLM 맞춤형 요약**: 수집된 통계 데이터를 LLM에게 전달하여 '사람의 목소리'로 요약.

## 4. 페르소나별 리포트 구성 (Customized Reports)

### **A. 김영순 여사님 (사용자용)**
- **톤앤매너**: 따뜻하고 친절한 동네 약사님 말투.
- **핵심 정보**: "칭찬과 주의" 중심. 
  - *"이번 주에는 5번이나 미리 확인해보셨네요! 정말 잘하고 계세요. 다만 화요일처럼 술과 약을 같이 드시면 간이 아플 수 있으니 그것만 꼭 조심해요."*

### **B. 최지연 팀장님 (보호자용)**
- **톤앤매너**: 명확하고 전문적인 리포트 데이터 형식.
- **핵심 정보**: "위험 이벤트 로그 및 통계" 중심. 
  - *"지난 7일간 총 1건의 고위험(RED) 경고가 발생했습니다. 해당 이벤트는 '당뇨약 복용 중 공복 음주' 시도였습니다."*

## 5. 단계별 구현 순서
1. **Log Logger 구현**: `analyze_text()` 호출 시 결과를 자동으로 JSON 저장하는 유틸리티 작성.
2. **Report Generator 구현**: 저장된 JSON 파일들을 읽어 LLM 요약을 만드는 파이프라인 구축.
3. **API 엔드포인트 마련**: 프론트엔드에서 리포트를 요청하면 결과값을 반환하는 인터페이스 설계.

---

# 구현 계획 - 네이버 CLOVA OCR 통합

이 계획은 식품 및 약품 라벨에서 자동으로 텍스트를 추출하기 위해 네이버 클라우드 CLOVA OCR을 세이프잇(SafeEat) 애플리케이션에 통합하는 상세 과정을 담고 있습니다.

## 사용자 검토 필요 사항

> [!IMPORTANT]
> `clover_ocr_test.py`에 포함된 CLOVA OCR API 설정 정보(URL, Secret Key)를 보안을 위해 `.env` 파일로 이동하여 관리할 예정입니다.
> `medi_list.csv` 파일이 확인되면 해당 파일의 약물 키워드를 메인 `entity_index.json`에 통합하여 분석 정확도를 높일 계획입니다.

## 제안된 변경 사항

### 백엔드 (Backend)
#### [수정] [.env](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/.env)
- `CLOVA_OCR_API_URL`과 `CLOVA_OCR_SECRET` 항목 추가.

#### [수정] [processor.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/src/ocr/processor.py)
- 기존 가상(Mock) 추출 로직을 실제 CLOVA OCR API 호출 로직으로 교체.
- API 호출 실패 및 이미지 형식 오류에 대한 예외 처리 구현.

#### [수정] [entity_index.json](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/data/normalization/entity_index.json)
- OCR로 추출된 텍스트가 정확히 파싱될 수 있도록 관련 약물 키워드 보강 및 통합.

### 프론트엔드 (Frontend)
#### [수정] [ScanPage.tsx](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ScanPage.tsx)
- 백엔드에서 글자 좌표(Bounding Box) 데이터를 제공할 경우, 이를 화면에 실제 위치에 맞게 표시할 수 있도록 구조 준비.

## 검증 계획

### 자동화 테스트
- 샘플 이미지를 사용하여 `extract_text_from_image` 함수가 텍스트를 정확히 반환하는지 확인하는 테스트 스크립트 실행.

### 수동 검증
1. 프론트엔드에서 "카메라 스캔" 기능을 실행합니다.
2. 약봉투나 식품 성분표 사진을 업로드하거나 촬영합니다.
3. 성분이 올바르게 인식되고 위험도 분석 결과가 정상적으로 출력되는지 확인합니다.
