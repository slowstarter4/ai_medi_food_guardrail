import json
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
ENTITY_INDEX_PATH = BASE_DIR / "data" / "normalization" / "entity_index.json"

# 모듈 레벨 캐시 (파일 반복 로딩 방지)
_INDEX_CACHE: Dict = None

FOOD_SUFFIXES = ["주스", "즙", "차", "분말", "환", "정", "캡슐", "보충제"]

# =========================
# 1. Surface Normalization
# =========================
def normalize_food_surface(text: str) -> str:
    t = text.strip()
    for s in FOOD_SUFFIXES:
        if t.endswith(s):
            t = t[:-len(s)]
    return t

def normalize_surface(entity_type: str, text: str) -> str:
    if entity_type == "foods":
        return normalize_food_surface(text)
    return text.strip()

# =========================
# 2. Entity Index 로딩
# =========================
def load_entity_index() -> Dict[str, Dict[str, str]]:
    """
    {
      "drugs": { "로사르탄": "DRUG_LOSARTAN" },
      "foods": { "자몽": "FOOD_GRAPEFRUIT" },
      "situations": { "공복 복용": "SITU_FASTING" }
    }
    캐시된 인덱스를 반환 (최초 1회만 파일 읽기)
    """
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        with open(ENTITY_INDEX_PATH, encoding="utf-8") as f:
            _INDEX_CACHE = json.load(f)
    return _INDEX_CACHE

# =========================
# 3. Entity Normalization
# =========================
def normalize_entities(
    parsed_entities: Dict[str, List[str]]
) -> Dict[str, List[Dict]]:

    index = load_entity_index()

    normalized = {
        "foods": [],
        "drugs": [],
        "situations": []
    }

    for entity_type, values in parsed_entities.items():
        lookup = index.get(entity_type, {})

        for raw in values:
            surface = normalize_surface(entity_type, raw)

            if surface not in lookup:
                continue

            entity_id = lookup[surface]

            normalized[entity_type].append({
                "raw": raw,
                "entity_id": entity_id
            })

    return normalized
