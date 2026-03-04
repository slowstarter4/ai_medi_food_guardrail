import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

# e약은요 (DrbEasyDrugInfoService) 기반 보조 상호작용 체크
# 사용자가 제공한 두 API 링크 모두 'e약은요' 정보를 기반으로 하고 있습니다.
BASE_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

def get_drug_interaction(drug_names: List[str]) -> List[Dict]:
    """
    약물 리스트를 받아 'e약은요' API의 상호작용(intrcQesitm) 필드에서 
    다른 약물의 이름이 포함되어 있는지 보조적으로 검색합니다.
    """
    service_key = os.getenv("DATA_GO_KR_API_KEY")
    if not service_key or not drug_names or len(drug_names) < 2:
        return []

    service_key_decoded = unquote(service_key)
    interactions = []

    for i in range(len(drug_names)):
        target_drug = drug_names[i]
        others = [name for idx, name in enumerate(drug_names) if idx != i]
        
        params = {
            "serviceKey": service_key_decoded,
            "itemName": target_drug,
            "type": "json",
            "numOfRows": 1
        }

        try:
            response = requests.get(BASE_URL, params=params, timeout=5)
            if response.status_code != 200: continue
            
            data = response.json()
            items_container = data.get("body", {}).get("items", [])
            item = {}
            if isinstance(items_container, list) and items_container:
                item = items_container[0]
            elif isinstance(items_container, dict):
                item = items_container.get("item", items_container)

            if not item: continue
            
            # 'intrcQesitm' (상호작용) 필드 추출 및 정제
            interaction_text = item.get("intrcQesitm", "")
            if not interaction_text: continue
            
            import re
            clean_text = re.sub(r'<.*?>', '', interaction_text).replace("&nbsp;", " ")
            
            for other_drug in others:
                # 다른 약물명이 상호작용 텍스트에 포함되어 있는지 확인
                if other_drug in clean_text:
                    interactions.append({
                        "drug_a": target_drug,
                        "drug_b": other_drug,
                        "type": "일반 상호작용 (API 보조)",
                        "description": f"'{target_drug}'의 공식 주의사항에 '{other_drug}' 관련 내용이 포함되어 있습니다: {clean_text[:100]}...",
                        "source": "식약처 e약은요"
                    })
        except Exception as e:
            print(f"[API 보조 체크 실패] {target_drug}: {str(e)}")
                
    return interactions
                
    return interactions
