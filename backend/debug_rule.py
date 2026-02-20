import json
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from main import analyze_text

def test_debug_case():
    print("Testing Losartan + Grapefruit Juice...")
    # Simulation: User med is Losartan, Input is Grapefruit Juice
    result = analyze_text("자몽주스", user_meds=["로사르탄"])
    
    print(f"\n[RESULT] Risk Level: {result['risk_result']['risk_level']}")
    print(f"[ENTITIES] {json.dumps(result['debug_info']['entities'], ensure_ascii=False)}")
    print(f"[MATCHED RULES] {json.dumps(result['debug_info']['matched_rules'], ensure_ascii=False)}")
    print("\n[EXPLANATION]")
    print(result.get("explanation", "NO EXPLANATION FIELD"))

if __name__ == "__main__":
    test_debug_case()
