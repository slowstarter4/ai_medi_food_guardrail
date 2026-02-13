import json
from pathlib import Path
from typing import List, Dict
from src.external_api.drug_info_client import fetch_drug_info_from_api

EVIDENCE_DB_PATH = Path("src/evidence/evidence_db.json")

def retrieve_evidence(keys: List[str]) -> List[Dict]:
    """
    1. Internal DB Search (Evidence Key)
    2. External API Search (Drug Name) - Fallback
    """
    evidences = []
    
    # 1. Load Internal DB
    db = {}
    if EVIDENCE_DB_PATH.exists():
        with open(EVIDENCE_DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)

    for key in keys:
        # 1. Internal DB Hit
        if key in db:
            evidences.append(db[key])
        # 2. External API Hit (Treat key as Drug Name if not in DB)
        #    Evidence Key는 보통 대문자+언더바 조합이므로, 
        #    약물명(한글)이 들어오면 API 검색을 시도하도록 조건 추가 가능.
        #    여기서는 단순히 DB에 없으면 약물명으로 간주하고 검색.
        else:
            # 키가 한글을 포함하거나, 특정 패턴이 아니면 약물명으로 간주
            # (간단히 DB에 없으면 API 호출 시도)
            external_data = fetch_drug_info_from_api(key)
            if external_data:
                evidences.append(external_data)
    
    return evidences
