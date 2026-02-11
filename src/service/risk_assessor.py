import json
from pathlib import Path

PRIORITY = {
    "RED": 3,
    "YELLOW": 2,
    "LOW": 1
}

EVIDENCE_DB_PATH = Path("src/evidence/evidence_db.json")
with open(EVIDENCE_DB_PATH, "r", encoding="utf-8") as f:
    EVIDENCE_DB = json.load(f)

def assess_risk(normalized_entities, matched_rules):
    if not matched_rules:
        final_risk = "LOW"
        top_rule = None
    else:
        # 룰 매칭 우선순위 규칙 적용:
        # 1. Level (1 > 2 > 3) - 오름차순
        # 2. Risk Level (RED > YELLOW > LOW) - 내림차순 (PRIORITY 점수 이용)
        # 3. Rule ID (알파벳 오름차순) - 안정성 확보
        
        sorted_rules = sorted(
            matched_rules,
            key=lambda r: (
                r.get("level", 3), 
                -PRIORITY.get(r.get("risk_level_hint"), 0), 
                r.get("rule_id", "")
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
