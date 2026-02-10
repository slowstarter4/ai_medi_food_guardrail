from typing import Dict, List
import re

def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text

def parse_entities(
    raw_text: str,
    known_entities: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    raw_text에서 표면 엔티티만 추출
    (의미 정규화는 절대 여기서 하지 않음)
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

    return entities
