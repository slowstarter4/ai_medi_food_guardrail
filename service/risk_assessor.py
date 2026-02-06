from typing import Dict, List, Any

RISK_PRIORITY = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW":1
}

def assess_risk(
        entities: Dict[str, List[str]],
        matched_rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    룰 기반 최종 위험도 판단
    이 함수가 프로젝트의 유일한 판단 지점이다
    """
    if not matched_rules:
        return {
            "risk_level": "LOW",
            "risk_code": None,
            "decision_basis": {
                "rule_based": True,
                "matched_rules": []
            },
            "entities_involved": entities,
            "evidence_keys": []    
        }
    
    highest_rule = max(
        matched_rules,
        key=lambda r: RISK_PRIORITY.get(r.get("risk_level_hint", "LOW"), 1)
    )
    return {
        "risk_level": highest_rule["risk_level_hint"],
        "risk_code": highest_rule.get("risk_code"),
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in matched_rules]
        },
        "entities_involved": entities,
        "evidence_keys": list({
            key
            for r in matched_rules
            for key in r.get("evidence_keys", [])
        })
    }