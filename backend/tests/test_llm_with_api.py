import sys
import os
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (tests/ 폴더에서 실행 시 필요)
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app import analyze_text
import json

def test_llm_api_integration():
    # Windows 한글 출력 깨짐 방지
    sys.stdout.reconfigure(encoding='utf-8')

    input_text = "타이레놀 먹고 술 마셔도 돼?"
    print(f"Testing E2E with Input: {input_text}")
    print("-" * 60)

    # 1. Analyze Text (Should trigger API call for '타이레놀')
    result = analyze_text(input_text)

    # 2. Check Evidence
    evidence_keys = result['risk_result'].get('evidence_keys', [])
    evidence_info = result['risk_result'].get('evidence_info', [])
    
    print(f"Risk Level: {result['risk_result']['risk_level']}")
    print(f"Evidence Keys: {evidence_keys}")
    
    api_hit = False
    for evi in evidence_info:
        if evi.get('source') == "MFDS_API":
            api_hit = True
            print(f"\n[API HIT] Found external evidence for: {evi.get('title')}")
            print(f"Summary: {evi.get('summary')[:100]}...")

    if not api_hit:
        print("\n[FAIL] Did not use External API data.")
    
    # 3. Check Explanation
    print(f"\n[LLM Explanation]\n{result['explanation']}")

if __name__ == "__main__":
    test_llm_api_integration()
