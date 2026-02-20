from typing import Dict, List
import re

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", "", text) # 모든 공백 제거 (암 로 디 핀 -> 암로디핀 대응)
    return text

import difflib

def parse_entities(
    raw_text: str,
    known_entities: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    raw_text에서 표면 엔티티 추출 (Fuzzy matching 지원)
    """

    normalized_text = _normalize(raw_text)
    # 텍스트를 공백 기반 토큰으로 분리 (Fuzzy matching용 - 원본 텍스트 사용)
    tokens = raw_text.lower().split()

    entities = {
        "foods": [],
        "drugs": [],
        "supplements": [],
        "situations": []
    }

    for entity_type, candidates in known_entities.items():
        for name in candidates:
            name_norm = _normalize(name)
            
            # 1. 완전 일치
            if name_norm in normalized_text:
                entities[entity_type].append(name)
                continue
            
            # 2. 유사도 기반 매칭 (OCR 오류 대응)
            # 단어 길이가 너무 짧으면(3자 미만) 하지 않음 (오탐 방지)
            if len(name_norm) >= 3:
                for token in tokens:
                    similarity = difflib.SequenceMatcher(None, name_norm, token).ratio()
                    if similarity >= 0.8: # 임계값 0.8
                        entities[entity_type].append(name)
                        break

    return entities
