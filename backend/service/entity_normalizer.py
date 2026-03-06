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
# =========================
# 3. Entity Normalization
# =========================
from rapidfuzz import process, fuzz

# 상호작용 위험 성분 (보수적 처리 필요)
HIGH_RISK_FOOD_IDS = ["FOOD_GRAPEFRUIT", "FOOD_ALCOHOL", "FOOD_CAFFEINE", "FOOD_LICORICE"]

import unicodedata

def to_jamo(text):
    return unicodedata.normalize('NFKD', text)

def normalize_entities(
    parsed_entities: Dict[str, List[str]],
    source: str = "ocr" # "ocr" or "manual"
) -> Dict[str, List[Dict]]:

    index = load_entity_index()

    normalized = {
        "foods": [],
        "drugs": [],
        "situations": []
    }

    for entity_type, values in parsed_entities.items():
        lookup = index.get(entity_type, {})
        choices = list(lookup.keys())
        if not choices:
            continue

        # 자모 분리된 choices 사전 (매칭 시 높은 정확도를 위함)
        jamo_to_original = {to_jamo(choice.replace(" ", "").lower()): choice for choice in choices}
        jamo_choices = list(jamo_to_original.keys())

        for raw in values:
            surface = normalize_surface(entity_type, raw).replace(" ", "").lower()
            surface_jamo = to_jamo(surface)
            
            # 1. Exact Match
            entity_id = None
            if surface_jamo in jamo_to_original:
                original_choice = jamo_to_original[surface_jamo]
                entity_id = lookup[original_choice]
            
            if entity_id:
                normalized[entity_type].append({"raw": raw, "entity_id": entity_id, "match_type": "exact"})
                continue

            # 2. Fuzzy Match
            # 수동 입력(이부프로팬)은 90.9점 정도, OCR(타이레놀ㄹ)은 94.7점 정도 나옴
            if source == "manual":
                base_threshold = 90 # 자모 분리 후 보수적 기준을 90으로 조정 (원래 95는 1자만 틀려도 탈락)
            else:
                base_threshold = 88 # OCR 노이즈 

            current_threshold = base_threshold
            
            if entity_type == "drugs":
                current_threshold = max(90, base_threshold)
            elif entity_type == "foods":
                current_threshold = 80 # 영양소 등

            results = process.extract(surface_jamo, jamo_choices, scorer=fuzz.WRatio, limit=2)
            
            if results:
                best_match_jamo, score, best_idx = results[0]
                original_best_match = jamo_to_original[best_match_jamo]
                matched_id = lookup[original_best_match]
                
                if entity_type == "foods":
                    if matched_id in HIGH_RISK_FOOD_IDS:
                        current_threshold = 90
                    elif "NUTRITION_" in matched_id:
                        current_threshold = 80
                
                if score >= current_threshold:
                    is_ambiguous = False
                    if entity_type == "drugs" and len(results) > 1:
                        top2_score = results[1][1]
                        if (score - top2_score) < 5:
                            is_ambiguous = True
                            print(f"DEBUG: Ambiguous drug match [{surface}]: '{original_best_match}'({score}) vs '{jamo_to_original[results[1][0]]}'({top2_score})")

                    if not is_ambiguous:
                        print(f"DEBUG: Fuzzy match found [{entity_type}/{source}]: '{surface}' -> '{original_best_match}' (Score: {score:.1f}, ID: {matched_id})")
                        
                        normalized[entity_type].append({
                            "raw": raw,
                            "entity_id": matched_id,
                            "match_type": "fuzzy",
                            "score": round(score, 1)
                        })

    return normalized
