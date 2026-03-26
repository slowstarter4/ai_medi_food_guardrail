"""
프로젝트 전역 상수 정의

약물 계열 매핑, API 검증 키워드, 상황어 자동 감지 데이터를 한 곳에서 관리합니다.
"""
from typing import Dict, List, Tuple

# ============================================================
# 약물 ID → 계열 매핑
# (evaluator.py 규칙 매칭 및 entity_normalizer.py 엔티티 정규화 공용)
# ============================================================
ID_TO_CATEGORY: Dict[str, str] = {
    "DRUG_LOSARTAN": "ACE/ARB",
    "DRUG_ENALAPRIL": "ACE/ARB",
    "DRUG_ACE_ARB": "ACE/ARB",
    "DRUG_AMLODIPINE": "CCB",
    "DRUG_CCB": "CCB",
    "DRUG_HYDROCHLOROTHIAZIDE": "이뇨제",
    "DRUG_DIURETIC_LOOP": "이뇨제",
    "DRUG_SPIRONOLACTONE": "이뇨제",
    "DRUG_SULFONYLUREA": "설폰요소제",
    "DRUG_METFORMIN": "비구아나이드",
    "DRUG_DAPAGLIFLOZIN": "SGLT2",
    "DRUG_EMPAGLIFLOZIN": "SGLT2",
    "DRUG_SGLT2": "SGLT2",
    "DRUG_IBUPROFEN": "NSAIDs",
    "DRUG_NAPROXEN": "NSAIDs",
    "DRUG_NSAID": "NSAIDs",
    # 제네릭 약물 ID → 계열 매핑 (Context Gate 통과를 위해 필수)
    "DRUG_HYPERTENSION_GENERIC": "ACE/ARB|CCB|이뇨제",
    "DRUG_DIABETES_GENERIC": "비구아나이드|설폰요소제|SGLT2",
    "DRUG_DIURETIC_GENERIC": "이뇨제",
    "DRUG_PAINKILLER_GENERIC": "NSAIDs",
}

# ============================================================
# LLM 추론 계열명 → 약물 표준 ID 매핑
# (llm_entity_parser.py 폴백 매핑 사용)
# ============================================================
CLASS_TO_DRUG_ID: Dict[str, str] = {
    # 고혈압약
    "HTN_ARB": "DRUG_ACE_ARB",
    "HTN_ACE": "DRUG_ACE_ARB",
    "HTN_CCB": "DRUG_CCB",
    "HTN_DIURETIC": "DRUG_DIURETIC_GENERIC",
    "HTN_MED": "DRUG_HYPERTENSION_GENERIC",       # 구버전 하위 호환
    # 당뇨약
    "DM_METFORMIN": "DRUG_METFORMIN",
    "DM_SULFONYLUREA": "DRUG_SULFONYLUREA",
    "DM_SGLT2": "DRUG_SGLT2",
    "DM_DPP4": "DRUG_SITAGLIPTIN",
    "DIABETES_MED": "DRUG_DIABETES_GENERIC",      # 구버전 하위 호환
    # 기타
    "NSAID": "DRUG_NSAID",
    "PAINKILLER": "DRUG_PAINKILLER_GENERAL",
    "STATIN": "DRUG_STATIN",
    "ANTIHISTAMINE": "DRUG_ANTIHISTAMINE",
    "ANTIBIOTIC": "DRUG_ANTIBIOTIC",
    "DECONGESTANT": "DRUG_DECONGESTANT",
    "ANTICOAGULANT": "DRUG_ANTICOAGULANT",
    "DIGESTIVE": "DRUG_DIGESTIVE_GENERAL",
}

# ============================================================
# API 교차 검증용 약물 계열 → 약효 키워드 매핑
# (app.py LLM 추론 결과를 공공 API로 검증할 때 사용)
# ============================================================
CLASS_VERIFICATION_KEYWORDS: Dict[str, List[str]] = {
    "DECONGESTANT": ["코막힘", "비충혈", "비염", "감기", "교감신경"],
    "NSAID": ["해열", "진통", "소염", "염증", "비스테로이드"],
    "PAINKILLER": ["해열", "진통", "통증"],
    "HTN_MED": ["혈압", "고혈압", "채널차단"],
    "DIABETES_MED": ["당뇨", "혈당", "메트포르민"],
    "STATIN": ["고지혈증", "콜레스테롤", "이상지질혈증"],
    "ANTIHISTAMINE": ["알레르기", "비염", "가려움", "두드러기", "항히스타민"],
    "DIGESTIVE": ["소화", "위장", "위염", "속쓰림", "제산"],
}

# ============================================================
# 텍스트 키워드 기반 상황어 자동 감지
# (app.py 입력 텍스트 분석 시 사용)
# 각 항목: (감지 키워드 리스트, 주입할 situation 딕셔너리)
# ============================================================
SITUATION_KEYWORD_MAP: List[Tuple[List[str], Dict]] = [
    (
        ["공복", "밥안먹", "식사안", "밥못", "식사거름", "아침안", "금식", "빈속", "굶", "식사못", "밥못드"],
        {"raw": "공복", "canonical": "공복 복용", "entity_id": "SITUATION_FASTING"},
    ),
    (
        ["사우나", "찜질방", "땀많이", "더웠", "땀흘린", "탈수", "수분부족", "땀나", "목말", "갈증"],
        {"raw": "탈수", "canonical": "탈수/수분부족", "entity_id": "SITUATION_DEHYDRATION"},
    ),
    (
        ["중복", "두개", "두가지", "또먹", "추가로먹", "한번에", "같이먹어", "함께먹어"],
        {"raw": "중복복용", "canonical": "중복 복용", "entity_id": "SITUATION_DUPLICATION"},
    ),
    (
        ["운동", "격한", "헬스", "달리기"],
        {"raw": "운동", "canonical": "격한 운동", "entity_id": "SITUATION_EXERCISE"},
    ),
    (
        ["매일", "계속", "장기", "한달", "연속"],
        {"raw": "장기복용", "canonical": "장기 연속 복용", "entity_id": "SITUATION_LONG_TERM_USE"},
    ),
    (
        ["불규칙", "제때", "들쑥날쑥"],
        {"raw": "불규칙식사", "canonical": "불규칙한 식사", "entity_id": "SITUATION_MEAL_IRREGULAR"},
    ),
]

# ============================================================
# 텍스트 키워드 기반 질환 컨텍스트 자동 주입
# (app.py 입력 텍스트에 질환명이 포함된 경우 사용)
# 각 항목: (감지 키워드, 주입할 situation 딕셔너리)
# ============================================================
DISEASE_KEYWORD_MAP: List[Tuple[str, Dict]] = [
    ("고혈압", {"raw": "고혈압", "canonical": "고혈압", "entity_id": "CONDITION_hypertension"}),
    ("당뇨", {"raw": "당뇨", "canonical": "당뇨", "entity_id": "CONDITION_diabetes"}),
]
