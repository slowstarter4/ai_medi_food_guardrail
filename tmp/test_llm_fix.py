import sys
import os
import json

# 프로젝트 루트를 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.service.llm_entity_parser import parse_entities_with_llm

def test_llm_correction():
    test_cases = [
        "아무로디핀 먹고 있는데 자몽주스 마셔도 돼?", # 아무로디핀 -> 암로디핀 (HTN_MED)
        "이부프로팬 한 알 먹었어", # 이부프로팬 -> 이부프로펜 (NSAID)
        "슈다패드정 처방받았는데 커피 괜찮나?", # 슈다패드 -> 슈다페드 (DECONGESTANT)
        "혈압약 아모디팬 복용 중", # 아모디팬 -> 아모디핀 (HTN_MED)
        "알러지 때문에 지르텍ㄹ 먹었어" # 지르텍ㄹ -> 지르텍 (ANTIHISTAMINE)
    ]

    print("=== LLM Entity Extraction & Correction Test ===")
    for text in test_cases:
        print(f"\n[Input]: {text}")
        result = parse_entities_with_llm(text)
        
        for drug in result.get("drugs", []):
            raw = drug.get("raw")
            corrected = drug.get("corrected_name")
            eid = drug.get("entity_id")
            icr = drug.get("inferred_class")
            conf = drug.get("confidence")
            reason = drug.get("reasoning")
            
            print(f"  - Raw: {raw}")
            print(f"  - Corrected: {corrected}")
            print(f"  - Entity ID: {eid}")
            print(f"  - Inferred Class: {icr}")
            print(f"  - Confidence: {conf}")
            print(f"  - Reasoning: {reason}")

if __name__ == "__main__":
    test_llm_correction()
