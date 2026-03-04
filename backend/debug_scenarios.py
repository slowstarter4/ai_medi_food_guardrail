import json
import sys
import os

# backend 경로 추가
sys.path.append(os.getcwd())

from app import _run_pipeline

def debug_scenario(name, text, meds=None, conditions=None, situations=None):
    print(f"\n=== DEBUG: {name} ===")
    res = _run_pipeline(text, meds, conditions, situations)
    
    print(f"Risk: {res['risk_result']['risk_level']}")
    print(f"Matched Rules: {[r['rule_id'] for r in res['risk_result'].get('matched_rules', [])]}")
    
    situ_ids = [s['entity_id'] for s in res.get('debug_info', {}).get('entities', {}).get('situations', [])]
    print(f"Situations IDs: {situ_ids}")
    
    drug_ids = [d['entity_id'] for d in res.get('debug_info', {}).get('entities', {}).get('drugs', [])]
    print(f"Drug IDs: {drug_ids}")
    
    if res['risk_result']['risk_level'] == 'GREEN':
        print("FAIL: Expected higher risk but got GREEN")
    else:
        print("PASS: Risk detected")

# 1. 사우나 + 고혈압
debug_scenario("Scenario 1", "사우나 가려고 해요", ["로사르탄"], ["고혈압"])

# 11. 글리메피리드 + 공복 (칩 기반)
debug_scenario("Scenario 11", "제 약이에요", ["글리메피리드"], ["당뇨"], ["공복"])
