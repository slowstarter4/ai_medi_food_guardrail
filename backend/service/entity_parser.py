from typing import Dict, List
import re
import difflib
import unicodedata

def _normalize(text: str) -> str:
    text = text.lower()
    # 1. 괄호 및 그 안의 내용 처리 (예: 제품명(성분명) -> 제품명 성분명)
    # 괄호를 공백으로 치환하여 두 단어 모두 검색 가능하게 함
    text = re.sub(r"[\(\)\[\]\{\}]", " ", text)
    # 2. 특수문자 제거 (정규화용)
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", "", text)
    # 3. 약물 접미사 제거 (정, 캡슐, 서방정, 시럽, 액 등)
    # 문자열 중간이나 끝에 있는 접미사를 공백과 함께 처리
    text = re.sub(r"(서방정|서방캡슐|정|캡슐|시럽|액|정제)(\s|$)", " ", text)
    # 4. 모든 공백 제거 (암 로 디 핀 → 암로디핀 대응용 최종 비교용)
    # 주의: 여기서 공백을 완전히 제거하면 단어 경계가 사라짐. 
    # parse_entities에서 name_norm in normalized_text로 비교하므로 공백 제거 버전도 유용함.
    return re.sub(r"\s+", "", text)

def parse_entities(
    raw_text: str,
    known_entities: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    raw_text에서 표면 엔티티 추출 (Fuzzy matching 지원)
    - 중복 추가 방지: already_matched set으로 추적
    - 완전일치 우선, 이후 Fuzzy matching
    """

    normalized_text = _normalize(raw_text)
    # 공백 기반 토큰화 (Fuzzy matching용 - normalize 적용)
    tokens = [_normalize(t) for t in raw_text.split()]

    entities = {
        "foods": [],
        "drugs": [],
        "supplements": [],
        "situations": []
    }

    for entity_type, candidates in known_entities.items():
        if entity_type not in entities:
            continue

        # 이미 추가된 이름 추적 (중복 방지)
        already_matched = set()

        for name in candidates:
            name_norm = _normalize(name)
            if name in already_matched:
                continue

            # 1. 완전 일치 (공백 제거 정규화 기준)
            if name_norm in normalized_text:
                entities[entity_type].append(name)
                already_matched.add(name)
                continue

            # 2. 유사도 기반 매칭 (OCR 오류 대응)
            # 단어 길이가 너무 짧으면(3자 미만) 하지 않음 (오탐 방지)
            if len(name_norm) >= 3:
                name_jamo = unicodedata.normalize('NFKD', name_norm)
                for token in tokens:
                    token_jamo = unicodedata.normalize('NFKD', token)
                    similarity = difflib.SequenceMatcher(None, name_jamo, token_jamo).ratio()
                    if similarity >= 0.9: # 0.8은 너무 낮아 오분류 발생 가능 (이부프로펜-이부루펜 등)
                        entities[entity_type].append(name)
                        already_matched.add(name)
                        break

    return entities
