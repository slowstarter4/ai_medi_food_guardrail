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


def _extract_entities_via_llm(raw_text: str) -> Dict[str, List[str]]:
    """
    [Step 1] LLM으로 텍스트에서 엔티티명(표면어)만 추출합니다.
    인덱스 전체를 프롬프트에 넣지 않아 토큰 비용이 적고 빠릅니다.
    """
    system_prompt = """
    당신은 의료·식품 상호작용 검사를 위한 엔티티 추출 전문가입니다.
    사용자가 제공하는 텍스트에서 다음 세 가지 카테고리에 해당하는 항목만 추출하세요.
    
    - drugs: 약물명, 의약품명 (예: 암로디핀, 이부프로펜, 로사르탄, 혈압약, 당뇨약 등)
    - foods: 식품, 음료, 영양 성분 (예: 자몽, 바나나, 알코올, 소주 등)
    - situations: 복용 상황/행위 (예: 공복, 식전, 병용 복용, 아침 식사 안 하고 등)
    
    [주의사항]
    - 위 세 카테고리에 해당하지 않는 단어는 포함하지 마세요.
    - 가능한 한 원문에 나온 그대로 추출하세요.
    - 결과는 JSON 형식으로만 응답하세요. 예시:
      {"drugs": ["암로디핀", "이부프로펜"], "foods": ["자몽주스"], "situations": ["공복"]}
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
            timeout=30  # 30초 타임아웃
        )
        data = json.loads(response.choices[0].message.content)
        # 기본 구조 보장
        return {
            "drugs": data.get("drugs", []),
            "foods": data.get("foods", []),
            "situations": data.get("situations", [])
        }
    except Exception as e:
        logging.error(f"LLM entity extraction failed: {str(e)}")
        return {"drugs": [], "foods": [], "situations": []}


def _normalize_to_ids(extracted: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
    """
    [Step 2] 추출된 표면어를 entity_index.json 기반으로 표준 ID에 매핑합니다.
    기존 entity_normalizer.py 로직을 재사용합니다.
    """
    import re
    index = _load_entity_index()

    normalized = {"foods": [], "drugs": [], "situations": []}

    for entity_type in ["drugs", "foods", "situations"]:
        lookup = index.get(entity_type, {})
        for raw in extracted.get(entity_type, []):
            raw_clean = raw.strip().lower().replace(" ", "")

            matched_id = None
            matched_key = None

            # 1. 완전 일치 (공백 제거 기준)
            for key, eid in lookup.items():
                if key.lower().replace(" ", "") == raw_clean:
                    matched_id = eid
                    matched_key = key
                    break

            # 2. 부분 포함 (raw가 key를 포함하거나 key가 raw를 포함)
            if not matched_id:
                for key, eid in lookup.items():
                    key_norm = key.lower().replace(" ", "")
                    if key_norm in raw_clean or raw_clean in key_norm:
                        matched_id = eid
                        matched_key = key
                        break

            if matched_id:
                normalized[entity_type].append({
                    "raw": raw,
                    "entity_id": matched_id
                })
            else:
                # 미등록 엔티티는 UNKNOWN으로 기록 (LLM 설명 생성 시 참고)
                normalized[entity_type].append({
                    "raw": raw,
                    "entity_id": "UNKNOWN"
                })

    return normalized


def parse_entities_with_llm(raw_text: str) -> Dict[str, List[Dict]]:
    """
    LLM으로 표면어를 추출(Step 1)한 뒤, 표준 ID에 매핑(Step 2)합니다.
    LLM에 전체 인덱스를 넘기지 않아 속도와 비용 모두 최적화됩니다.
    """
    if not client:
        logging.warning("OpenAI API key not set. Falling back to empty entities.")
        return {"foods": [], "drugs": [], "situations": []}

    # Step 1: LLM으로 표면어 추출
    extracted = _extract_entities_via_llm(raw_text)
    logging.info(f"[LLM Parser] Extracted: {extracted}")

    # Step 2: 표준 ID 매핑
    normalized = _normalize_to_ids(extracted)
    logging.info(f"[LLM Parser] Normalized: {normalized}")

    return normalized
