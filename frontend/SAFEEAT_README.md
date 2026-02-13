# SafeEat (세이프잇) - AI 기반 식품·복약 안전 서비스

## 브랜드 개요

SafeEat은 'Safe(안전한)'와 'Eat(먹다)'의 합성어로, AI 기반 개인 맞춤형 식품·복약 안전 서비스입니다.

**슬로건**: "당신의 식탁 위, AI가 지키는 안전"

## 주요 기능

### 1. 메인 페이지 (/)
- 오늘의 복약 현황 위젯
- 다음 복용 시간 알림
- 최근 식품 스캔 결과 요약
- 새로운 식품 스캔 버튼

### 2. 프로필 관리 (/profile)
- 복약 정보 입력 (약물명, 용법, 용량)
- 처방전 이미지 업로드 (준비 중)
- 질환 프리셋 선택 (고혈압, 당뇨병 등)
- 복약 스케줄 설정 (준비 중)

### 3. 식품 스캔 (/scan)
- **실시간 카메라 스캔**: OCR 기술로 성분표 인식
- **Bounding Box 시각화**: 인식된 성분을 실시간으로 박스 표시
- **텍스트 미리보기**: 박스 옆에 인식된 텍스트 표시
- 바코드 스캔 (준비 중)
- 수동 검색 및 성분 수정

### 4. 위험도 결과 (/result)
- **Safety Card**: 위험도별 색상 구분 (Green/Orange/Red)
- 위험 성분 태그 표시
- 의학적 근거 및 출처 명시
- **대체 식품 추천**: 위험 성분이 없는 안전한 대체품 제안
- 공유 및 상세 정보 링크

### 5. 설정 (/settings)
- 알림 설정
- 개인정보 처리방침
- 데이터 보안 정책
- FAQ
- 앱 정보

## 디자인 시스템

### 컬러 시스템 (신호등 시스템)
- **Main (Teal)**: #009688 - 브랜드 신뢰감, 정상 상태
- **Success (Green)**: #4CAF50 - 안전, 섭취 가능
- **Warning (Orange)**: #FFB74D - 주의, 제한적 섭취 권장
- **Danger (Red)**: #E53935 - 위험, 섭취 중단 권고
- **Background**: #F5F5F5 - 콘텐츠 분리
- **Text**: #263238 - 고도의 가독성

### 타이포그래피
- Primary Font: Noto Sans KR
- Headline: 20-24pt, Bold
- Body: 14-16pt, Regular
- Caption: 12pt, Medium

## 기술 스택

- **React** with TypeScript
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Motion** (Framer Motion) for animations
- **Lucide React** for icons
- **localStorage** for data persistence

## 주요 컴포넌트

### SafetyCard
위험도별 색상과 아이콘으로 결과를 표시하는 카드 컴포넌트

### IngredientChip
인식된 성분을 위험도별로 색상 구분하여 표시하는 칩 컴포넌트

### MedicationTag
등록된 약물 정보를 표시하는 태그 컴포넌트

### BottomNav
하단 네비게이션 바 (홈, 프로필, 스캔, 설정)

### WelcomeScreen
첫 방문 시 표시되는 온보딩 화면

## 데이터 구조

### Medication
```typescript
{
  id: string;
  name: string;
  dosage: string;
}
```

### ScanResult
```typescript
{
  id: string;
  foodName: string;
  riskLevel: "safe" | "warning" | "danger";
  message: string;
  timestamp: Date;
  ingredients?: string[];
}
```

## 특별 기능

### 1. 실시간 OCR 시각화
카메라 스캔 시 성분표의 텍스트를 실시간으로 인식하고 Bounding Box로 표시합니다. 각 박스 옆에는 인식된 텍스트가 미리보기로 표시되어 기술적 신뢰성을 높입니다.

### 2. 대체 식품 추천
위험한 식품을 스캔했을 때, 단순히 경고만 하는 것이 아니라 위험 성분이 없는 안전한 대체 식품을 이미지와 함께 추천합니다.

### 3. 근거 기반 분석
모든 위험도 판단에는 의학적 근거와 출처(식약처, 대한당뇨병학회 등)를 명시하여 신뢰성을 제공합니다.

## 사용 방법

1. 첫 방문 시 온보딩 화면에서 "시작하기"
2. 프로필 페이지에서 복용 중인 약물 등록
3. 메인 페이지에서 "새로운 식품 스캔하기" 클릭
4. 카메라로 성분표 촬영 또는 수동 입력
5. 위험도 분석 결과 확인
6. 필요시 대체 식품 추천 확인

## 로컬 스토리지 키

- `hasVisited`: 첫 방문 여부
- `medications`: 등록된 약물 목록
- `conditions`: 선택된 질환 프리셋
- `recentScans`: 최근 스캔 결과 (최대 10개)

## 향후 개발 예정

- 처방전 OCR 자동 인식
- 바코드 스캔 API 연동
- 복약 알림 푸시 기능
- 가족 공유 기능
- 다국어 지원
- 백엔드 연동 (Supabase)
