import json
import requests

BASE_URL = "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"

def fetch_drug_info_from_api(drug_name: str, service_key: str):
    """
    e약은요 의약품 정보 조회
    """ 
    params = {
        "serviceKey": service_key,
        "itemName": drug_name,
        "numOfRows":5,
        "pageNo":1,
        "type": "json",
    }

    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    return response.json()

def extract_drug_fields(json_data):
    """
    API JSON 응답에서 필요한 필드만 추출
    """
    items_container = json_data.get("body", {}).get("items", {})
    
    # items_container가 dict이면 'item' 키를 가져오고, 리스트이면 그대로 사용
    if isinstance(items_container, dict):
        items_raw = items_container.get("item", [])
        if isinstance(items_raw, dict):
            items_raw = [items_raw]
    elif isinstance(items_container, list):
        items_raw = items_container
    else:
        items_raw = []

    extracted = []
    for item in items_raw:
        extracted.append({
            "itemName": item.get("itemName", ""),
            "efcyQesitm": item.get("efcyQesitm", ""),       # 효능
            "atpnQesitm": item.get("atpnQesitm", ""),       # 주의사항
            "intrcQesitm": item.get("intrcQesitm", ""),     # 상호작용
            "itemImage": item.get("itemImage", "")          # 이미지
        })
    return extracted

if __name__ == "__main__":
    EYAK_SERVICE_KEY = "56f8c68f23eb75176255204bdd10da3894a2b56dd2f255b7efd61c4d6f0fa530"
    drug_name = "아네모정"

    result = fetch_drug_info_from_api(drug_name, EYAK_SERVICE_KEY)
    extracted = extract_drug_fields(result)

    print(json.dumps(extracted, ensure_ascii=False, indent=2))
