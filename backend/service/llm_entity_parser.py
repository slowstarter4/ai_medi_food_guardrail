import os
import json
import logging
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

BASE_DIR = Path(__file__).resolve().parents[1]
ENTITY_INDEX_PATH = BASE_DIR / "data" / "normalization" / "entity_index.json"

# 인덱스 캐시 (파일 중복 로딩 방지)
_INDEX_CACHE: Dict = None


def _load_entity_index() -> Dict:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        with open(ENTITY_INDEX_PATH, "r", encoding="utf-8") as f:
            _INDEX_CACHE = json.load(f)
    return _INDEX_CACHE


def _extract_entities_via_llm(raw_text: str) -> Dict:
    """
    [Step 1] LLM으로 텍스트에서 엔티티와 약물 계열(Class)을 함께 추출합니다.
    """
    system_prompt = """
    당신은 의료·식품 상호작용 검사를 위한 엔티티 추출 전문가입니다.
    사용자가 제공하는 텍스트에서 다음 카테고리에 해당하는 항목을 분석하고 추출하세요.
    
    [추출 카테고리]
    1. drugs: 약물명(성분명/상품명)
       - 각 약물별로 'name'(원본명)과 'inferred_class'(추론된 계열)를 JSON 객체로 추출하세요.
       - 'inferred_class'는 다음 중 하나로 분류하세요: [DECONGESTANT, NSAID, ANTIHISTAMINE, ANTIBIOTIC, HTN_MED, DIABETES_MED, STATIN, PAINKILLER, DIGESTIVE, UNKNOWN]
    2. foods: 식품, 음료, 영양 성분
       - 예: 자몽, 바나나, 술, 알코올(음주), 카페인(커피/에너지음료), 고염식(국물/젓갈/김치), 단 음식(케이크/당류) 등
    3. situations: 복용 상황/사용자 행태/신체 상태
       - 예: 공복(식사거름), 식전/식후, 사우나(찜질방), 격한 운동, 탈수, 장기 복용(매일 복용), 불규칙한 식사 등
    
    [주의사항]
    - 일상적인 말투(예: "운동하고 왔어", "사우나 갈 거야", "아침 걸렀어")에서 핵심 상황 키워드를 정확히 추출하세요.
    - 결과는 JSON 형식으로만 응답하세요. 예시:
      {
        "drugs": [{"name": "슈다페드", "inferred_class": "DECONGESTANT"}],
        "foods": ["커피", "고염식"],
        "situations": ["격한 운동", "공복"]
      }
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text}
            ],
            response_format={"type": "json_object"},
            temperature=0,
            timeout=30
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "drugs": data.get("drugs", []),
            "foods": data.get("foods", []),
            "situations": data.get("situations", [])
        }
    except Exception as e:
        logging.error(f"LLM entity extraction failed: {str(e)}")
        return {"drugs": [], "foods": [], "situations": []}


def _normalize_to_ids(extracted: Dict) -> Dict[str, List[Dict]]:
    """
    [Step 2] 추출된 항목을 entity_index.json 기반 표준 ID로 매핑합니다.
    색인에 없어도 LLM이 추론한 계열 정보(inferred_class)를 활용합니다.
    """
    index = _load_entity_index()
    normalized = {"foods": [], "drugs": [], "situations": []}

    # 1. 약물 정규화 (이름 매핑 우선, 실패 시 계열 매핑)
    lookup_drugs = index.get("drugs", {})
    for drug_info in extracted.get("drugs", []):
        name = drug_info.get("name", "")
        inferred_class = drug_info.get("inferred_class", "UNKNOWN")
        name_clean = name.strip().lower().replace(" ", "")

        matched_id = None
        # 이름 기반 완전/부분 매칭
        for key, eid in lookup_drugs.items():
            key_norm = key.lower().replace(" ", "")
            if key_norm == name_clean or key_norm in name_clean or name_clean in key_norm:
                matched_id = eid
                break
        
        # 이름 매칭 실패 시 계열 기반 매칭
        if not matched_id and inferred_class != "UNKNOWN":
            class_to_id_map = {
                "DECONGESTANT": "DRUG_DECONGESTANT",
                "NSAID": "DRUG_NSAID",
                "ANTIHISTAMINE": "DRUG_ANTIHISTAMINE",
                "ANTIBIOTIC": "DRUG_ANTIBIOTIC",
                "PAINKILLER": "DRUG_PAINKILLER_GENERAL",
                "DIGESTIVE": "DRUG_DIGESTIVE_GENERAL",
                "HTN_MED": "DRUG_AMLODIPINE",  # 기본 대표 ID
                "DIABETES_MED": "DRUG_METFORMIN",
                "STATIN": "DRUG_STATIN"
            }
            matched_id = class_to_id_map.get(inferred_class)

        normalized["drugs"].append({
            "raw": name,
            "entity_id": matched_id if matched_id else "UNKNOWN",
            "inferred_class": inferred_class
        })

    # 2. 식품 및 상황 정규화
    for etype in ["foods", "situations"]:
        lookup = index.get(etype, {})
        for raw in extracted.get(etype, []):
            raw_clean = raw.strip().lower().replace(" ", "")
            matched_id = None
            for key, eid in lookup.items():
                key_norm = key.lower().replace(" ", "")
                if key_norm == raw_clean or key_norm in raw_clean or raw_clean in key_norm:
                    matched_id = eid
                    break
            
            normalized[etype].append({
                "raw": raw,
                "entity_id": matched_id if matched_id else "UNKNOWN"
            })

    return normalized


def parse_entities_with_llm(raw_text: str) -> Dict[str, List[Dict]]:
    """
    LLM 추론을 활용하여 엔티티를 추출하고 표준 ID로 정규화합니다.
    """
    if not client:
        return {"foods": [], "drugs": [], "situations": []}

    extracted = _extract_entities_via_llm(raw_text)
    return _normalize_to_ids(extracted)
