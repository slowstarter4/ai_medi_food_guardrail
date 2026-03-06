import os
import sys
import json

sys.path.append(os.getcwd())

from app import analyze_text

# Set encoding for Windows terminal
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def test_single():
    text = "이부프로펜 먹고 술 마셔도 되나요"
    conditions = ["관절염", "고령"]
    user_meds = []
    
    print(f"Testing: {text}")
    print(f"Conditions: {conditions}")
    
    result = analyze_text(text, medications=user_meds, conditions=conditions)
    
    print("\n--- Full Result ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    risk_result = result.get("risk_result", {})
    risk_level = risk_result.get("risk_level")
    matched_rules = risk_result.get("decision_basis", {}).get("matched_rules", [])
    
    print(f"\nRisk Level: {risk_level}")
    print(f"Matched Rules: {[r.get('rule_id') for r in matched_rules]}")
    
    if matched_rules:
        repres = risk_result.get("representative_rule")
        print(f"Representative Rule: {repres}")

if __name__ == "__main__":
    test_single()
