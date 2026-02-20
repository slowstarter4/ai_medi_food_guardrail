# 구현 계획 - 세이프잇(SafeEat) 프로젝트

이 문서는 세이프잇 프로젝트의 주요 기능 구현 및 개선 계획을 담고 있습니다.

---

# 1. 네이버 CLOVA OCR 통합 및 고도화

이미지에서 성분 정보를 자동으로 추출하기 위해 CLOVA OCR을 통합합니다.

## 사용자 검토 필요 사항
> [!IMPORTANT]
> - `clover_ocr_test.py`에 포함된 API 키를 `.env`로 이동하여 보안을 강화합니다.
> - `medi_list.csv` 파일이 확인되면 해당 데이터를 `entity_index.json`에 통합할 예정입니다.

## 제안된 변경 사항

### 백엔드 (Backend)
#### [수정] [.env](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/.env)
- `CLOVA_OCR_API_URL` 및 `CLOVA_OCR_SECRET` 추가.

#### [수정] [processor.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/src/ocr/processor.py)
- 실제 API 호출 로직으로 교체하고, **파일 확장자에 따른 이미지 포맷(jpeg, png 등) 자동 지정** 기능을 추가합니다.
- 예외 처리(API 실패, 네트워크 오류 등)를 보강합니다.

#### [수정] [entity_index.json](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/data/normalization/entity_index.json)
- OCR 인식률 향상을 위해 주요 의약품 키워드(탁센, 애드빌 등)를 추가합니다.

### 프론트엔드 (Frontend)
#### [수정] [ScanPage.tsx](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ScanPage.tsx)
- **에러 핸들링**: 백엔드에서 분석 오류가 발생할 경우 사용자에게 알림(alert)을 표시합니다.
- **결과 안내**: 성분이 인식되지 않았을 때의 안내 메시지를 추가합니다.

---

# 2. 질병 컨텍스트 통합 (Disease Context Integration)

사용자의 질병 정보를 분석에 활용하여 더욱 정확하고 개인화된 식품-약물 상호작용 분석을 제공합니다.

## 제안된 변경 사항

- [x] Link ScanPage to user medications
- [NEW] Add '고령' (Senior) to disease presets in `ProfilePage.tsx`
- [NEW] Pass `conditions` from `ScanPage.tsx` to backend analysis endpoints
- [NEW] Update backend to incorporate `conditions` into the analysis pipeline

### Frontend

#### [MODIFY] [ProfilePage.tsx](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ProfilePage.tsx)
- Add `{ id: "elderly", label: "고령" }` to `commonConditions`.

#### [MODIFY] [ScanPage.tsx](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ScanPage.tsx)
- Retrieve `conditions` from `localStorage`.
- Include `conditions` in the body/form data of analysis requests.

### Backend

#### [MODIFY] [app.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/app.py)
- Update `TextAnalysisRequest` to include `conditions`.
- Update `api_analyze_image` to accept `conditions`.

#### [MODIFY] [main.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/main.py)
- Update `analyze_text` and `analyze_image` to accept `conditions`.
- Pass `conditions` to the risk assessment and explanation stages.

---

# 3. 중간 결과물(Middle Report)을 위한 E2E 고도화

현재 OCR과 기본 룰 매칭은 잘 작동하지만, 실제 서비스의 핵심 가치인 '사용자 약물 기반 맞춤형 분석'을 완료하기 위해 다음 기능을 구현합니다.

## 제안된 변경 사항

### 백엔드 (Backend)
#### [수정] [app.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/app.py)
- 분석 API(`/api/analyze/image`, `/api/analyze/text`)가 사용자의 현재 복용 약물 목록(`medications`)을 인자로 받을 수 있도록 수정합니다.

#### [수정] [main.py](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/backend/main.py)
- 전달받은 약물 목록을 분석 엔진에 주입하여, 스캔한 식품과 사용자의 약물 간 상호작용을 정확히 판별하도록 로직을 개선합니다.

### 프론트엔드 (Frontend)
#### [수정] [ScanPage.tsx](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ScanPage.tsx)
- 분석 요청 시 `localStorage`에 저장된 사용자의 복용 약물 정보를 함께 서버로 전송합니다.

#### [신규] [Prescription OCR](file:///c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/frontend/src/app/pages/ProfilePage.tsx)
- '처방전 업로드' 기능을 활성화하여, 사진 촬영만으로 복용 약물을 자동으로 등록할 수 있는 E2E 시나리오를 완성합니다.

## 검증 계획

### E2E 테스트 시나리오
1. **약물 등록**: 사용자가 처방전 사진을 찍어 '로사르탄'을 등록합니다.
2. **식품 스캔**: 사용자가 '자몽 주스'를 스캔합니다.
3. **결정**: 시스템이 사용자의 '로사르탄' 정보를 바탕으로 자몽 주스에 대해 'YELLOW' 경고를 띄우는지 확인합니다.
