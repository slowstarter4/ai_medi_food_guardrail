
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.getcwd())

from main import analyze_text

def test_dm_003():
    text = "술"
    meds = ["메트포르민"]
    conditions = ["당뇨"]
    
    print(f"Testing analyze_text with meds={meds}, text='{text}', conditions={conditions}")
    result = analyze_text(text, meds, conditions)
    
    import json
    print(f"Result API Response keys: {list(result.keys())}")
    if 'risk_result' in result:
        rr = result['risk_result']
        print(f"Risk Level: {rr.get('risk_level')}")
        print(f"Representative Rule: {rr.get('representative_rule')}")
        print(f"Matched Rules: {rr.get('decision_basis', {}).get('matched_rules')}")
    else:
        print("Error: risk_result not found in result")

    print(f"Explanation Preview: {result.get('explanation', '')[:100]}...")

if __name__ == "__main__":
    test_dm_003()
