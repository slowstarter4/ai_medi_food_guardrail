import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import unquote

load_dotenv()

BASE_URL = "http://apis.data.go.kr/1471000/DurgPrntnInfoService05/getContraindicationList"

def debug_dur():
    service_key = os.getenv("DATA_GO_KR_API_KEY")
    if not service_key:
        print("API KEY MISSING")
        return

    # '메트포르민' 검색 시 병용금기 성분들이 나오는지 확인
    # 실제 식료품/약물보다는 약물/약물 상호작용이 주 목표
    drugs_to_test = ["메트포르민", "아스피린", "케토롤락"]
    
    for name in drugs_to_test:
        print(f"\n--- Testing DUR API for: {name} ---")
        params = {
            "serviceKey": unquote(service_key),
            "itemName": name,
            "type": "json",
            "numOfRows": 5
        }
        
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(response.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_dur()
