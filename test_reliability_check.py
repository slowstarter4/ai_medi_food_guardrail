import sys
import os
import json

# 백엔드 경로 추가
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app import analyze_text

def test_reliability():
    print("=== [신뢰성 강화: AI 추론 + API 교차 검증 테스트] ===")
    
    test_cases = [
        {
            "desc": "색인 등록 약물 (로컬 보증)",
            "text": "로사르탄정 처방",
            "expected_id": "DRUG_LOSARTAN",
            "expected_status": "VERIFIED"
        },
        {
            "desc": "색인 미등록 + API 일치 (공공데이터 보증)",
            "text": "슈다페드정",
            "expected_id": "DRUG_DECONGESTANT",
            "expected_status": "VERIFIED"
        },
        {
            "desc": "색인 미등록 + API 불일치/실패 (AI 추론만)",
            "text": "이상한가상의약품123", # API 검색 실패 예상
            "expected_status": "INFERRED"
        }
    ]
    
    for case in test_cases:
        print(f"\n[테스트] {case['desc']}")
        print(f"입력: {case['text']}")
        
        result = analyze_text(case['text'])
        entities = result["debug_info"]["entities"]
        
        drugs = entities.get("drugs", [])
        if not drugs:
            print("결과: ❌ 약물이 탐지되지 않음")
            continue
            
        found_drug = drugs[0]
        status = found_drug.get("verification_status")
        
        is_success = (status == case["expected_status"])
        if "expected_id" in case:
            is_success = is_success and (found_drug["entity_id"] == case["expected_id"])
            
        status_msg = "✅ PASS" if is_success else "❌ FAIL"
        print(f"탐지명: {found_drug['raw']}, ID: {found_drug['entity_id']}, Status: {status}")
        print(f"결과: {status_msg}")

if __name__ == "__main__":
    test_reliability()
