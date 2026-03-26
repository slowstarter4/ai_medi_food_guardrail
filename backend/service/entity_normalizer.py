import json
import logging
import threading
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
ENTITY_INDEX_PATH = BASE_DIR / "data" / "normalization" / "entity_index.json"

# 모듈 레벨 캐시 (파일 반복 로딩 방지)
_INDEX_CACHE: Dict = None
_INDEX_CACHE_LOCK = threading.Lock()

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
        with _INDEX_CACHE_LOCK:
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
from src.rules.evaluator import ID_TO_CATEGORY

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
                item = {"raw": raw, "entity_id": entity_id, "match_type": "exact"}
                if entity_type == "drugs":
                    item["drug_category"] = ID_TO_CATEGORY.get(entity_id, "UNKNOWN")
                normalized[entity_type].append(item)
                continue

            # 2. Fuzzy Match
            # 수동 입력(이부프로팬)은 90.9점 정도, OCR(타이레놀ㄹ)은 94.7점 정도 나옴
            if source == "manual":
                base_threshold = 90 # 자모 분리 후 보수적 기준을 90으로 조정 (원래 95는 1자만 틀려도 탈락)
            else:
                base_threshold = 88 # OCR 노이즈 

            current_threshold = base_threshold
            
            if entity_type == "drugs":
                current_threshold = 80 # 오타 인식률 제고 (이브프로팬 등 대응)
            elif entity_type == "foods":
                current_threshold = 80 # 영양소 등

            results = process.extract(surface_jamo, jamo_choices, scorer=fuzz.WRatio, limit=2)
            
            if results:
                best_match_jamo, score, best_idx = results[0]
                original_best_match = jamo_to_original[best_match_jamo]
                matched_id = lookup[original_best_match]
                
                # 고위험 식품군/영양소 임계값 예외 처리
                if entity_type == "foods":
                    if matched_id in HIGH_RISK_FOOD_IDS:
                        current_threshold = 75 # 더 공격적으로 탐지 (FN 방지)
                    elif "NUTRITION_" in matched_id:
                        current_threshold = 80
                
                if score >= current_threshold:
                    is_ambiguous = False
                    if entity_type == "drugs" and len(results) > 1:
                        top2_score = results[1][1]
                        if (score - top2_score) < 5:
                            is_ambiguous = True
                            logger.debug(f"Ambiguous drug match [{surface}]: '{original_best_match}'({score}) vs '{jamo_to_original[results[1][0]]}'({top2_score})")

                    if not is_ambiguous:
                        logger.debug(f"Fuzzy match found [{entity_type}/{source}]: '{surface}' -> '{original_best_match}' (Score: {score:.1f}, ID: {matched_id})")
                        
                        item = {
                            "raw": raw,
                            "entity_id": matched_id,
                            "match_type": "fuzzy",
                            "score": round(score, 1)
                        }
                        if entity_type == "drugs":
                            item["drug_category"] = ID_TO_CATEGORY.get(matched_id, "UNKNOWN")
                        normalized[entity_type].append(item)
                elif entity_type == "drugs" and score >= 75:
                    # [NEW] 후보군 제안 로직 (80~88점 사이 또는 보수적 하한선 75점)
                    # 확정은 아니지만 사용자에게 물어볼 가치가 있는 목록
                    candidates = []
                    for m_jamo, m_score, m_idx in results:
                        if m_score >= 75:
                            m_original = jamo_to_original[m_jamo]
                            candidates.append({
                                "name": m_original,
                                "entity_id": lookup[m_original],
                                "score": round(m_score, 1)
                            })
                    
                    if candidates:
                        logger.debug(f"Candidate drug found [{surface}]: {candidates}")
                        normalized[entity_type].append({
                            "raw": raw,
                            "entity_id": "UNKNOWN",
                            "match_type": "candidate",
                            "candidates": candidates
                        })

    return normalized
