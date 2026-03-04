import sys
import os
import json

# 백엔드 경로 추가
sys.path.append(os.path.join(os.getcwd(), "backend"))

from service.llm_entity_parser import parse_entities_with_llm

def test_inference():
    print("=== [LLM 추론 및 계열 분류 테스트] ===")
    
    test_cases = [
        # (입력 텍스트, 기대하는 Entity ID)
        ("슈다페드정 처방받았어요", "DRUG_DECONGESTANT"), 
        ("판피린 티 먹어도 될까?", "DRUG_DECONGESTANT"), # 판피린에는 페닐에프린(충혈제거제) 포함
        ("덱시부프로펜 400mg", "DRUG_NSAID"),
        ("타이레놀이랑 술 마심", "DRUG_ACETAMINOPHEN"),
        ("공복에 사우나 갔어", "SITUATION_DEHYDRATION")
    ]
    
    success_count = 0
    for text, expected_id in test_cases:
        print(f"\n입력: {text}")
        result = parse_entities_with_llm(text)
        
        found_ids = []
        for cat, items in result.items():
            for item in items:
                found_ids.append(item["entity_id"])
        
        status = "✅ PASS" if expected_id in found_ids else "❌ FAIL"
        if status == "✅ PASS":
            success_count += 1
            
        print(f"추출된 IDs: {found_ids}")
        print(f"결과: {status}")

    print("\n" + "="*30)
    print(f"최종 결과: {success_count}/{len(test_cases)} 통과")

if __name__ == "__main__":
    test_inference()
