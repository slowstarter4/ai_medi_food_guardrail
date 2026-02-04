# src/service/risk_assessor.py
from src.rules.loader import load_rules
from src.rules.evaluator import evaluate_rules

PRIORITY = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

def assess_risk(entities):
    rules = load_rules()
    matched = evaluate_rules(entities, rules)

    if not matched:
        final_risk = "LOW"
    else:
        final_risk = max(
            matched,
            key=lambda r: PRIORITY.get(r["risk_level"], 0)
        )["risk_level"]

    return {
        "risk_level": final_risk,
        "risk_code": final_risk,
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in matched]
        },
        "evidence_keys": [r.get("evidence_key") for r in matched]
    }
