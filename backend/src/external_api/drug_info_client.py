import os
import json
import logging
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

BASE_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

def fetch_drug_info_from_api(drug_name: str) -> Optional[Dict]:
    """
    e약은요 의약품 정보 조회 및 RAG용 데이터 추출
    """
    service_key = os.getenv("DATA_GO_KR_API_KEY")
    if not service_key:
        logger.warning("DATA_GO_KR_API_KEY not found in environment variables.")
        return None

    # URL Decode key if necessary (requests might handle it, but public keys often need unquoting)
    # For now, use as is. Public data portal keys often need decoding if they contain %
    from urllib.parse import unquote
    service_key_decoded = unquote(service_key)

    params = {
        "serviceKey": service_key_decoded,
        "itemName": drug_name,
        "numOfRows": 5,
        "pageNo": 1,
        "type": "json",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        
        # JSON Parsing (공공데이터 포털은 가끔 JSON 형식이 깨질 수 있음)
        try:
            data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response for {drug_name}")
            return None

        return extract_drug_fields(data, drug_name)

    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed for {drug_name}: {e}")
        if hasattr(e, 'response') and e.response:
            logger.debug(f"Response Body: {e.response.text}")
        return None

def extract_drug_fields(json_data: Dict, drug_name: str) -> Optional[Dict]:
    """
    API JSON 응답에서 가장 관련성 높은 첫 번째 항목의 정보를 추출
    RAG에 사용할 Evidence 형태로 변환
    """
    items_container = json_data.get("body", {}).get("items", {})
    
    items_raw = []
    if not items_container:
        return None

    # items_container가 dict이면 'item' 키를 가져오고, 리스트이면 그대로 사용 (XML->JSON 변환 특성)
    if isinstance(items_container, list):
         items_raw = items_container
    elif isinstance(items_container, dict):
        # 만약 바로 item 리스트나 딕셔너리가 아니라면 구조 확인 필요하지만, 
        # 공공데이터포털 JSON은 보통 body -> items -> [List] or body -> items (List) 구조임
        # 위 코드(eyak_api.py) 로직 참조
        items_raw = items_container # eyak_api.py 로직을 따름. 
        # 하지만 보통 items가 list인 경우가 많음. 
        # eyak_api.py: items_container.get("item", []) -> 이 부분이 핵심
        # items 자체가 리스트일수도 있음.
        pass

    # eyak_api.py 로직 재현 (안전하게)
    final_items = []
    if isinstance(items_container, list):
        final_items = items_container
    elif isinstance(items_container, dict):
        # items 내부에 item key가 있는지 확인
        if "item" in items_container:
            temp = items_container["item"]
            if isinstance(temp, list):
                final_items = temp
            else:
                 final_items = [temp]
        else:
            # items 자체가 dict 하나일 수도 (항목이 1개일 때)
            # 하지만 보통 item 키 안에 둠.
            # 예외적으로 items가 바로 데이터일수도 있으나 드묾.
            pass

    if not final_items:
        return None

    # 첫 번째 항목만 사용 (가장 정확도 높음)
    item = final_items[0]
    
    # HTML 태그 제거 필요할 수 있음 (일단 그대로 사용)
    return {
        "source": "MFDS_API",
        "title": f"{item.get('itemName', drug_name)} 정보",
        "summary": _format_summary(item),
        "url": item.get("itemImage", "") # 이미지가 있으면 URL로 사용
    }

def _format_summary(item: Dict) -> str:
    """효능, 주의사항, 상호작용을 하나의 요약 텍스트로 병합"""
    parts = []
    if item.get("efcyQesitm"):
        parts.append(f"[효능효과]\n{_clean_text(item['efcyQesitm'])}")
    if item.get("atpnQesitm"):
        parts.append(f"[주의사항]\n{_clean_text(item['atpnQesitm'])}")
    if item.get("intrcQesitm"):
        parts.append(f"[상호작용]\n{_clean_text(item['intrcQesitm'])}")
    
    return "\n\n".join(parts)

def _clean_text(text: str) -> str:
    """HTML 태그 제거 및 정제"""
    if not text: return ""
    # 간단한 태그 제거 (정규식 사용 권장하지만 여기선 간단히)
    import re
    clean = re.sub(r'<.*?>', '', text) 
    clean = clean.replace("&nbsp;", " ").replace("\n\n", "\n").strip()
    return clean
