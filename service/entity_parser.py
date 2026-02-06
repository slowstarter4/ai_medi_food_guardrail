from typing import Dict, List
import re
from service.entity_normalizer import normalize_entities

def _normalize(text: str) -> str:
    """
    v1: 단순 소문자화 + 공백 정리
    """
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text

def parse_entities(
    raw_text: str,
    known_entities: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    raw_text에서 food / drug / supplement 엔티티 추출

    known_entities 예시:
    {
      "foods": ["자몽", "우유", "알코올"],
      "drugs": ["와파린", "암로디핀"],
      "supplements": ["칼슘보충제"]
    }
    """

    normalized_text = _normalize(raw_text)

    entities = {
        "foods": [],
        "drugs": [],
        "supplements": []        
    }

    for entity_type, candidates in known_entities.items():
        for name in candidates:
            name_norm = _normalize(name)
            if name_norm in normalized_text:
                entities[entity_type].append(name)

    return normalize_entities(entities)