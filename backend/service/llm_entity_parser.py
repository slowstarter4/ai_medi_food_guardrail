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
    [Step 1] LLM으로 텍스트에서 엔티티를 추출하고, 오타 교정 및 계열(Class) 추론을 수행합니다.
    """
    system_prompt = """
    당신은 의료·식품 상호작용 검사를 위한 엔티티 추출 전문가입니다.
    사용자가 제공하는 텍스트(OCR 결과 포함)에서 약물, 식품, 상황 정보를 추출하세요.
    
    [drugs 스키마]
    - raw: 텍스트에서 발견된 원본 문자열
    - corrected_name: 교정된 표준 성분명 (오타·상품명 → 일반명. 예: '바이코자정' → '로사르탄', '타이레놀' → '아세트아미노펜')
    - inferred_class: 아래 분류 중 **가장 구체적인** 것으로 분류하세요.
        고혈압약 계열: HTN_ARB (로사르탄/발사르탄/텔미사르탄 등 ARB), HTN_ACE (에날라프릴/리시노프릴 등 ACE억제제), HTN_CCB (암로디핀/니페디핀 등 칼슘채널차단제), HTN_DIURETIC (이뇨제)
        당뇨약 계열: DM_METFORMIN, DM_SULFONYLUREA, DM_SGLT2, DM_DPP4
        진통/소염: NSAID (이부프로펜/나프록센/디클로페낙), PAINKILLER (아세트아미노펜/코데인)
        기타: STATIN, ANTIHISTAMINE, ANTIBIOTIC, DECONGESTANT, ANTICOAGULANT, DIGESTIVE, UNKNOWN
    - confidence: 확신도 (0.0~1.0)
    - reasoning: 판단 근거 (한 줄)
    
    [주의사항]
    - 상품명·오타를 성분 일반명으로 반드시 교정하세요. (corrected_name 필드)
    - foods, situations는 문자열 리스트로 반환하세요.
    - 반드시 JSON만 반환하세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"입력 텍스트: {raw_text}"}
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
    LLM의 교정된 이름(corrected_name)과 계열 정보(inferred_class)를 순차적으로 활용합니다.
    """
    index = _load_entity_index()
    normalized = {"foods": [], "drugs": [], "situations": []}

    # 1. 약물 정규화
    lookup_drugs = index.get("drugs", {})
    for drug_info in extracted.get("drugs", []):
        raw_name = drug_info.get("raw", "")
        # 교정된 이름이 있으면 우선 사용
        corrected_name = drug_info.get("corrected_name", raw_name)
        inferred_class = drug_info.get("inferred_class", "UNKNOWN")
        
        # 1-1. 교정된 이름 기반 매핑 시도
        matched_id = None
        search_name = corrected_name.strip().lower().replace(" ", "")
        
        for key, eid in lookup_drugs.items():
            key_norm = key.lower().replace(" ", "")
            if key_norm == search_name or key_norm in search_name or search_name in key_norm:
                matched_id = eid
                break
        
        # 1-2. 매칭 실패 시 계열 기반 폴백
        if not matched_id and inferred_class != "UNKNOWN":
            class_to_id_map = {
                # 고혈압약 세분화 (기존 HTN_MED→DRUG_AMLODIPINE 버그 제거)
                "HTN_ARB": "DRUG_ACE_ARB",       # 로사르탄, 발사르탄 등 ARB
                "HTN_ACE": "DRUG_ACE_ARB",        # 에날라프릴 등 ACE억제제
                "HTN_CCB": "DRUG_CCB",            # 암로디핀 등 칼슘채널차단제
                "HTN_DIURETIC": "DRUG_DIURETIC_GENERIC",
                # 구버전 HTN_MED도 generic ID로 폴백 (하위 호환)
                "HTN_MED": "DRUG_HYPERTENSION_GENERIC",
                # 당뇨약 세분화
                "DM_METFORMIN": "DRUG_METFORMIN",
                "DM_SULFONYLUREA": "DRUG_SULFONYLUREA",
                "DM_SGLT2": "DRUG_SGLT2",
                "DM_DPP4": "DRUG_SITAGLIPTIN",
                "DIABETES_MED": "DRUG_DIABETES_GENERIC",
                # 기타
                "NSAID": "DRUG_NSAID",
                "PAINKILLER": "DRUG_PAINKILLER_GENERAL",
                "STATIN": "DRUG_STATIN",
                "ANTIHISTAMINE": "DRUG_ANTIHISTAMINE",
                "ANTIBIOTIC": "DRUG_ANTIBIOTIC",
                "DECONGESTANT": "DRUG_DECONGESTANT",
                "ANTICOAGULANT": "DRUG_ANTICOAGULANT",
                "DIGESTIVE": "DRUG_DIGESTIVE_GENERAL",
            }
            matched_id = class_to_id_map.get(inferred_class)

        normalized["drugs"].append({
            "raw": raw_name,
            "corrected_name": corrected_name,
            "entity_id": matched_id if matched_id else "UNKNOWN",
            "inferred_class": inferred_class,
            "confidence": drug_info.get("confidence", 0.0),
            "reasoning": drug_info.get("reasoning", "")
        })

    # 2. 식품 및 상황 정규화 (LLM이 string 혹은 dict 형태로 반환할 수 있으므로 방어 처리)
    for etype in ["foods", "situations"]:
        lookup = index.get(etype, {})
        for raw in extracted.get(etype, []):
            # LLM이 {"name": "자몽"} 형태의 dict를 반환할 수 있으므로 string으로 변환
            if isinstance(raw, dict):
                raw_str = raw.get("name", raw.get("raw", raw.get("value", str(raw))))
            else:
                raw_str = str(raw)
            
            raw_clean = raw_str.strip().lower().replace(" ", "")
            matched_id = None
            for key, eid in lookup.items():
                key_norm = key.lower().replace(" ", "")
                if key_norm == raw_clean or key_norm in raw_clean or raw_clean in key_norm:
                    matched_id = eid
                    break
            
            normalized[etype].append({
                "raw": raw_str,
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
