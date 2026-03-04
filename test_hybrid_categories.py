import sys
import os
import json

# 백엔드 경로 추가
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app import analyze_text

def test_hybrid_logic():
    print("=== [하이브리드 파싱 로직 테스트] ===")
    
    test_cases = [
        {
            "desc": "색인에 있는 약물 (로컬 매칭)",
            "text": "로사르탄 복용 중",
            "expected_id": "DRUG_LOSARTAN"
        },
        {
            "desc": "색인에 없는 상품명 (AI 추론)",
            "text": "슈다페드정 먹어도 돼?",
            "expected_id": "DRUG_DECONGESTANT"
        },
        {
            "desc": "복합 상황 (로컬 + AI)",
            "text": "로사르탄이랑 슈다페드 같이 먹음",
            "expected_ids": ["DRUG_LOSARTAN", "DRUG_DECONGESTANT"]
        }
    ]
    
    for case in test_cases:
        print(f"\n[테스트] {case['desc']}")
        print(f"입력: {case['text']}")
        
        result = analyze_text(case['text'])
        entities = result["debug_info"]["entities"]
        
        found_ids = [d["entity_id"] for d in entities.get("drugs", [])]
        
        if "expected_ids" in case:
            success = all(eid in found_ids for eid in case["expected_ids"])
            expected = case["expected_ids"]
        else:
            success = case["expected_id"] in found_ids
            expected = [case["expected_id"]]
            
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"추출된 IDs: {found_ids}")
        print(f"결과: {status}")

if __name__ == "__main__":
    test_hybrid_logic()
