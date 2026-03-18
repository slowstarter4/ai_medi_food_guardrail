import re
from typing import List, Dict, Optional
from service.entity_normalizer import load_entity_index

# ============================================================
# 처방전 OCR 텍스트에서 약물별 용법/용량 추출
# 한국 표준 처방전 표 형식 지원:
#   약품코드(9자리) 약품명+용량(내복) 1회투여량 1일투여횟수 총투약일수
# ============================================================

# 제형명 목록 (약물명 정규화용)
DRUG_FORM_SUFFIXES = ("서방정", "필름정", "정", "캡슐", "시럽", "액", "주사", "크림", "연고", "패치", "겔", "산", "과립", "좌제")

# 제형명 단독 블랙리스트 (노이즈 필터)
FORM_ONLY_BLACKLIST = {
    "정", "캡슐", "시럽", "액", "주사", "크림", "연고", "패치", "겔", "산",
    "과립", "좌제", "수정", "입정", "서방정", "분말", "필름정", "내복", "외용",
    # 제형 조합 표현 (노이즈 필터)
    "필름코팅정", "원형필름코팅정", "필름코팅", "장용코팅정", "장용정",
    "이중정", "복합정", "서방캡슐",
}

# 약물 토큰에 허용되지 않는 특수문자 패턴 (노이즈 필터)
NOISE_CHAR_PATTERN = re.compile(r"[:：\[\]\(\)·\.]{1,}|···|\.\.\.|_{2,}|[\[기타]")

# 투여 경로 제거 패턴: (내복), (외용), (주사) 등
ROUTE_PATTERN = re.compile(r"\(내복\)|\(외용\)|\(주사\)|\(국소\)|\(흡입\)")

# 용량 패턴: 5mg, 500mg, 50/1000mg, 0.5mg, 10mcg
DOSE_IN_NAME_PATTERN = re.compile(r"[\d/]+\.?\d*\s*(mg|mcg|g|ml|IU|iu|μg|%)", re.IGNORECASE)

# 약품 코드 패턴 (6~9자리 숫자)
DRUG_CODE_PATTERN = re.compile(r"^\d{6,9}$")

# 복용 시점 키워드
TIMING_KEYWORDS = ["식후", "식전", "취침전", "취침 전", "공복", "아침", "저녁", "점심"]
TIMING_PATTERN = re.compile("|".join(TIMING_KEYWORDS))

# 1일 n회 패턴
FREQUENCY_PATTERN = re.compile(r"1일\s*\d+\s*회")


def _preprocess_tokens(tokens: list) -> list:
    """
    OCR 토큰 전처리: '14-저녁', '1-저녁' 같은 숫자-문자 혼합 토큰을 분리
    예: ['14-저녁'] → ['14', '저녁']
    """
    result = []
    for t in tokens:
        m = re.match(r'^(\d+\.?\d*)[-~_]([가-힣]+)$', t)
        if m:
            result.append(m.group(1))  # 숫자 부분
            result.append(m.group(2))  # 문자 부분
        else:
            result.append(t)
    return result


def _clean_drug_token(raw: str) -> str:
    """약품명 토큰에서 투여경로, 내장 용량, OCR 노이즈 제거 → 순수 약품명 반환"""
    t = raw.strip()
    t = ROUTE_PATTERN.sub("", t)
    # OCR 노이즈 제거: ···, [기타, _ 등
    t = re.sub(r"···|\.\.\.|\[.*|_+", "", t).strip()
    t = DOSE_IN_NAME_PATTERN.sub("", t).strip()
    return t


def _normalize_for_lookup(name: str) -> str:
    """인덱스 조회용 정규화: 소문자, 공백 제거, 제형 접미사 제거"""
    n = name.lower().replace(" ", "")
    for suffix in DRUG_FORM_SUFFIXES:  # 긴 것부터 정의되어 있음
        if n.endswith(suffix) and len(n) > len(suffix):
            n = n[:-len(suffix)]
            break
    return n


def _lookup_entity_id(drug_name_norm: str, entity_index: Dict) -> Optional[str]:
    """정규화된 약물명으로 entity_id 조회 (완전일치 우선, 접두어 폴백)"""
    drugs = entity_index.get("drugs", {})
    # 1. 완전일치
    for key, eid in drugs.items():
        if key.lower().replace(" ", "") == drug_name_norm:
            return eid
    # 2. 인덱스 키가 drug_name_norm의 접두어인 경우 (예: "자누메트" ⊂ "자누메트정")
    for key, eid in drugs.items():
        key_norm = key.lower().replace(" ", "")
        if len(key_norm) >= 3 and drug_name_norm.startswith(key_norm):
            return eid
    return None


def _is_drug_token(token: str, entity_index: Dict = None) -> bool:
    """토큰이 약품명인지 판별.
    1순위: entity_index 직접 매칭 (브랜드명/성분명, 제형 없이도 OK)
    2순위: 제형 접미사(정/캡슐 등) 포함 한글 2자 이상
    3순위: 한글 3자 이상 단독 토큰 (봉투/라벨에 브랜드명만 적힌 경우)
    """
    if re.search(r"[:：]\s*$", token):
        return False
    cleaned = ROUTE_PATTERN.sub("", token)
    cleaned = re.sub(r"···|\.\.\.|\[.*|_+", "", cleaned)
    cleaned = DOSE_IN_NAME_PATTERN.sub("", cleaned).strip()
    if len(cleaned) < 2:
        return False
    if cleaned in FORM_ONLY_BLACKLIST:
        return False

    # 1. entity_index 키와 완전 일치 (카나브, 피마사르탄 등 등록된 브랜드명)
    if entity_index:
        cleaned_norm = cleaned.lower().replace(" ", "")
        for key in entity_index.get("drugs", {}):
            if key.lower().replace(" ", "") == cleaned_norm:
                return True

    # 2. 한글 + 제형 접미사 패턴 (기존 처방전 형식)
    suffix_pattern = "|".join(re.escape(s) for s in DRUG_FORM_SUFFIXES)
    if re.search(r"[가-힣]{2,}(" + suffix_pattern + r")", cleaned):
        return True

    # 3. 한글 3자 이상 단독 브랜드명 (제형 없이 라벨에만 표기된 경우)
    if re.fullmatch(r"[가-힣]{3,}", cleaned):
        return True

    return False


def _parse_table_format(tokens: List[str], entity_index: Dict) -> List[Dict]:
    """
    한국 표준 처방전 표 형식 파싱:
      [약품코드?] [약품명+용량+(내복)] [1회투여량] [1일투여횟수] [총투약일수] [용법?]

    Clova OCR은 표 셀을 왼→오 순서로 반환하므로
    약품명 뒤에 오는 숫자 3개를 순서대로 매핑합니다.
    """
    results = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        # 약품 코드(숫자만) 스킵
        if DRUG_CODE_PATTERN.match(token):
            i += 1
            continue

        # 약품명 토큰 감지
        if _is_drug_token(token, entity_index):
            raw_name = token
            cleaned = _clean_drug_token(raw_name)

            # 약품명 안에 내장된 용량 추출: "자누메트정50/1000mg" → "50/1000mg"
            dose_in_name = DOSE_IN_NAME_PATTERN.search(raw_name)
            embedded_dose = dose_in_name.group(0).strip() if dose_in_name else None

            # 뒤따르는 토큰에서 숫자 3개 + timing 수집
            # (1회투여량 / 1일투여횟수 / 총투약일수 / 복용시점)
            nums = []
            timing = None
            j = i + 1
            while j < len(tokens):
                t = tokens[j]
                # 다음 약품명이 나오면 중단
                if _is_drug_token(t, entity_index) or DRUG_CODE_PATTERN.match(t):
                    break
                # 숫자(정수 또는 소수) 수집 — 최대 3개
                if re.match(r"^\d+\.?\d*$", t) and len(nums) < 3:
                    nums.append(t)
                # 복용 시점: 매치된 키워드만 저장
                elif TIMING_PATTERN.search(t):
                    timing = TIMING_PATTERN.search(t).group(0)
                # 숫자 3개 + timing 모두 수집했으면 종료
                if len(nums) >= 3 and timing is not None:
                    j += 1
                    break
                j += 1

            amount_per_dose = nums[0] if len(nums) > 0 else None
            daily_frequency = nums[1] if len(nums) > 1 else None
            total_days = nums[2] if len(nums) > 2 else None

            # 1일 n회 텍스트로 변환
            frequency_str = f"1일 {daily_frequency}회" if daily_frequency else None

            # entity_id 조회
            drug_norm = _normalize_for_lookup(cleaned)
            entity_id = _lookup_entity_id(drug_norm, entity_index)

            results.append({
                "raw_name": raw_name,
                "drug_name": cleaned,
                "entity_id": entity_id,
                "dose": embedded_dose,
                "frequency": frequency_str,
                "amount_per_dose": f"{amount_per_dose}정" if amount_per_dose else None,
                "total_days": f"{total_days}일" if total_days else None,
                "timing": timing,
                "is_unknown": entity_id is None
            })

            i = j  # 소비한 토큰 이후부터 계속
            continue

        i += 1

    return results


def _parse_inline_format(ocr_text: str, entity_index: Dict) -> List[Dict]:
    """
    인라인 형식 파싱 (폴백):
      "암로디핀정 5mg 1일 1회 1정 식후"
    표 형식에서 약물을 못 찾았을 때 사용.
    """
    results = []
    tokens = ocr_text.split()
    already = set()

    for token in tokens:
        if not _is_drug_token(token, entity_index):
            continue
        cleaned = _clean_drug_token(token)
        if cleaned in already or cleaned in FORM_ONLY_BLACKLIST:
            continue

        drug_norm = _normalize_for_lookup(cleaned)
        entity_id = _lookup_entity_id(drug_norm, entity_index)
        already.add(cleaned)

        idx = ocr_text.find(token)
        context = ocr_text[idx:idx + 30]
        dose_m = DOSE_IN_NAME_PATTERN.search(token)
        freq_m = FREQUENCY_PATTERN.search(context)
        time_m = TIMING_PATTERN.search(context)

        results.append({
            "raw_name": token,
            "drug_name": cleaned,
            "entity_id": entity_id,
            "dose": dose_m.group(0).strip() if dose_m else None,
            "frequency": freq_m.group(0).strip() if freq_m else None,
            "amount_per_dose": None,
            "total_days": None,
            "timing": time_m.group(0).strip() if time_m else None,
            "is_unknown": entity_id is None
        })

    return results


def parse_prescription(ocr_text: str) -> List[Dict]:
    """
    처방전 OCR 텍스트에서 약물별 용법/용량을 추출합니다.

    지원 형식:
    1. 한국 표준 처방전 표 형식 (약품코드 약품명+용량(내복) 1회량 1일횟수 일수)
    2. 인라인 형식 (약품명 용량 1일 n회 시점) — 폴백

    반환 형식:
    [
      {
        "raw_name":        "자누메트정50/1000mg(내복)",
        "drug_name":       "자누메트정",
        "entity_id":       "DRUG_METFORMIN",
        "dose":            "50/1000mg",
        "frequency":       "1일 2회",
        "amount_per_dose": "1정",
        "total_days":      "14일",
        "timing":          "식후",
        "is_unknown":      false
      }
    ]
    """
    entity_index = load_entity_index()
    tokens = _preprocess_tokens(ocr_text.split())

    # 표 형식 시도
    results = _parse_table_format(tokens, entity_index)

    # 표 형식으로 아무것도 못 찾으면 인라인 폴백
    if not results:
        results = _parse_inline_format(ocr_text, entity_index)

    return results
