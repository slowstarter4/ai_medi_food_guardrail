
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.getcwd())

from src.rules.evaluator import evaluate_rules
from src.rules.loader import load_ruleset
from service.entity_normalizer import normalize_entities, load_entity_index
from service.entity_parser import parse_entities

def quick_test():
    rules = load_ruleset()
    entity_index = load_entity_index()
    text = "술"
    meds = ["메트포르민"]
    
    # 1. Parse food
    parsed = parse_entities(text, entity_index)
    normalized = normalize_entities(parsed)
    
    # 2. Parse and add med
    med_p = parse_entities(meds[0], entity_index)
    med_n = normalize_entities(med_p)
    if "drugs" not in normalized: normalized["drugs"] = []
    normalized["drugs"].extend(med_n["drugs"])
    
    # 3. Add situation (same as main.py logic)
    if not "situations" in normalized: normalized["situations"] = []
    normalized["situations"].append({
        "raw": "병용",
        "canonical": "병용 섭취",
        "entity_id": "SITUATION_CONCURRENT"
    })
    
    # 4. Add persona (당뇨)
    normalized["situations"].append({
        "raw": "당뇨",
        "canonical": "당뇨",
        "entity_id": "CONDITION_diabetes"
    })
    
    matched = evaluate_rules(normalized, rules)
    print(f"Matched Rule IDs: {[r['rule_id'] for r in matched]}")
    for r in matched:
        if r['rule_id'] == 'DM_003':
            print(f"DM_003 Risk Level Hint: {r.get('risk_level_hint')}")

if __name__ == "__main__":
    quick_test()
