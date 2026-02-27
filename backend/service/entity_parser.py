from typing import Dict, List
import re
import difflib

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", "", text)  # 모든 공백 제거 (암 로 디 핀 → 암로디핀 대응)
    # 접미사 제거 (정, 캡슐, 서방정 등) - 매칭률 향상을 위해
    text = re.sub(r"(정|캡슐|서방정|시럽|액)$", "", text)
    return text

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
                for token in tokens:
                    similarity = difflib.SequenceMatcher(None, name_norm, token).ratio()
                    if similarity >= 0.8:
                        entities[entity_type].append(name)
                        already_matched.add(name)
                        break

    return entities
