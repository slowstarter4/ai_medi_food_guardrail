import json
from pathlib import Path

PRIORITY = {
    "RED": 3,
    "YELLOW": 2,
    "GREEN": 1
}

EVIDENCE_DB_PATH = Path(__file__).parent.parent / "evidence" / "evidence_db.json"
with open(EVIDENCE_DB_PATH, "r", encoding="utf-8") as f:
    EVIDENCE_DB = json.load(f)

def assess_risk(normalized_entities, matched_rules):
    if not matched_rules:
        final_risk = "GREEN"
        top_rule = None
    else:
        STRENGTH_SCORE = {
            "HIGH": 4,
            "MODERATE": 3,
            "LOW": 2,
            "EXPERT_PENDING": 1
        }
        
        # Helper to get the evidence strength of a rule from EVIDENCE_DB
        def get_strength_score(rule):
            key = rule.get("evidence_key")
            if key and key in EVIDENCE_DB:
                strength = EVIDENCE_DB[key].get("evidence_strength", "LOW")
                return STRENGTH_SCORE.get(strength.upper(), 0)
            return 0
            
        sorted_rules = sorted(
            matched_rules,
            key=lambda r: (
                r.get("level", 3),                          # 1순위: 정밀도 (1 > 2 > 3)
                -PRIORITY.get(r.get("risk_level_hint"), 0), # 2순위: 위험도 (RED > YELLOW)
                r.get("rule_id", "")                        # 3순위: ID (안정화)
            )
        )
        
        top_rule = sorted_rules[0]
        final_risk = top_rule["risk_level_hint"]

    evidence_keys = list({
        r.get("evidence_key")
        for r in matched_rules
        if r.get("evidence_key") in EVIDENCE_DB
    })

    evidence_info = [EVIDENCE_DB[k] for k in evidence_keys if k in EVIDENCE_DB]

    return {
        "risk_level": final_risk,
        "risk_code": final_risk,
        "representative_rule": top_rule["rule_id"] if top_rule else None,
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in matched_rules]
        },
        "entities_involved": normalized_entities,
        "evidence_keys": evidence_keys,
        "evidence_info": evidence_info
    }
