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
    else:
        # 가장 높은 우선순위 룰 선택
        final_risk = max(
            matched_rules,
            key=lambda r: PRIORITY.get(r.get("risk_level_hint"), 0)
        )["risk_level_hint"]

    evidence_keys = list({
        r.get("evidence_key")
        for r in matched_rules
        if r.get("evidence_key") in EVIDENCE_DB
    })

    evidence_info = [EVIDENCE_DB[k] for k in evidence_keys if k in EVIDENCE_DB]

    return {
        "risk_level": final_risk,
        "risk_code": final_risk,
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in matched_rules]
        },
        "entities_involved": normalized_entities,
        "evidence_keys": evidence_keys,
        "evidence_info": evidence_info
    }
