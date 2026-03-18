# [API 명세서] SafeEat: AI 분석 엔진 API

본 문서는 SafeEat 백엔드 서버에서 제공하는 주요 API 종단점에 대해 설명합니다.

- **Base URL**: `http://localhost:8000` (개발 서버 기준)
- **Content-Type**: `application/json` (이미지 업로드 제외)

---

## 1. 텍스트 기반 위험 분석
입력된 문장과 사용자의 상태(질환, 약물 이력, 상황)를 종합하여 위험도를 분석합니다.

- **Endpoint**: `POST /api/analyze/text`
- **Request Body**:
```json
{
  "text": "오늘 아침에 고혈압약 먹었는데, 자몽주스 한 잔 마셔도 될까?",
  "medications": ["아스피린"],           // (선택) 기존 복용 중인 약물
  "conditions": ["고혈압", "고령"],      // (선택) 기저 질환 페르소나
  "situations": ["공복"]                 // (선택) 현재 상황 칩 설정값
}
```
- **Response**:
  - `risk_result`: 분석된 위험도 및 대표 규칙 정보
  - `explanation`: AI가 생성한 근거 기반 설명
  - `candidates`: 약물 이름 보정 후보 리스트

---

## 2. 이미지 기반 위험 분석
약 봉투나 식품 정보를 포함한 이미지를 업로드하여 분석을 수행합니다.

- **Endpoint**: `POST /api/analyze/image`
- **Request Type**: `multipart/form-data`
- **Parameters**:
  - `file`: 이미지 파일 (필수)
  - `medications`: JSON string (예: `["타이레놀"]`)
  - `conditions`: JSON string (예: `["당뇨"]`)
  - `manual_situations`: JSON string (예: `["음주"]`)

---

## 3. 처방전 OCR 전용 분석
이미지에서 약물 정보를 추출하고 각각의 용법/용량을 구조화하여 반환합니다.

- **Endpoint**: `POST /api/ocr/prescription`
- **Request Type**: `multipart/form-data`
- **Response**:
```json
{
  "prescriptions": [
    {
      "drug_name": "아모디핀",
      "dosage": "5mg",
      "frequency": "1일 1회",
      "is_unknown": false
    }
  ],
  "drugs": ["아모디핀"],
  "unknown_drugs": [],
  "status": "SUCCESS"
}
```

---

## 4. 주간 복약 리포트 요약
저장된 분석 로그를 기반으로 한 주간의 위험 노출 현황 및 주의 사항을 생성합니다.

- **Endpoint**: `GET /api/report/weekly`
- **Response**:
  - `summary`: 전체 리포트 텍스트
  - `risk_counts`: 위험 단계별 발생 횟수 통계

---

## 5. 주요 데이터 모델

### RiskResult (위험 분석 결과)
- `risk_level`: `RED` | `YELLOW` | `GREEN`
- `representative_rule`: 매칭된 가장 치명적인 규칙 정보
- `entities_involved`: 분석에 포함된 약물, 식품, 상황 엔티티 리스트

### Error Codes
- `422 Unprocessable Entity`: 필수 파라미터 누락 혹은 데이터 형식 오류
- `500 Internal Server Error`: OCR 엔진 오류 혹은 LLM API 타임아웃
