import json
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from main import analyze_text

def test_debug_case():
    print("Testing Enalapril + Potassium...")
    # Simulation: User med is Enalapril, Input is Potassium (칼륨)
    result = analyze_text("칼륨", user_meds=["엔알라프릴"])
    
    print(f"\n[RESULT] Risk Level: {result['risk_result']['risk_level']}")
    print(f"[ENTITIES] {json.dumps(result['debug_info']['entities'], ensure_ascii=False)}")
    print(f"[MATCHED RULES] {json.dumps(result['debug_info']['matched_rules'], ensure_ascii=False)}")
    print("\n[EXPLANATION]")
    print(result.get("explanation", "NO EXPLANATION"))

if __name__ == "__main__":
    test_debug_case()
