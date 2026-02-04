from typing import List, Dict

RULES = [
    {
        "id" : "R001",
        "foods" : ["자몽"],
        "drugs" : ["고혈압약"],
        "risk_level" : "HIGH",
        "risk_code" : "FOOD_DRUG_INTERACTION",
        "evidence_key": "GRAPEFRUIT_BP_DRUG",
    },
    {
        "id": "R002",
        "foods": ["우유"],
        "drugs": ["항생제"],
        "risk_level": "MEDIUM",
        "risk_code": "FOOD_DRUG_INTERACTION",
        "evidence_key": "MILK_ANTIBIOTIC_ABSORPTION",
    },
]

def assess_risk(foods: List[str], drugs: List[str]) -> Dict:
    matched_rules = []

    for rule in RULES:
        if (
            any(food in foods for food in rule["foods"])
            and any(drug in drugs for drug in rule["drugs"])
        ):
            matched_rules.append(rule)
    if not matched_rules:
        return {
            "risk_level": "LOW",
            "risk_code": "INSUFFICIENT_INFO",
            "evidence_keys": [],
            "debug": {
                "matched_rules": []
            }
        }
    
    priority = {"HIGH" : 3, "MEDIUM": 2, "LOW": 1}
    top_rule = sorted(
        matched_rules,
        key=lambda r: priority[r["risk_level"]],
        reverse=True
    )[0]

    return {
        "risk_level": top_rule["risk_level"],
        "risk_code": top_rule["risk_code"],
        "evidence_keys": [top_rule["evidence_key"]],
        "confidence": "RULE_BASED",
        "debug": {
            "matched_rules": [r["id"] for r in matched_rules]
        }
    }