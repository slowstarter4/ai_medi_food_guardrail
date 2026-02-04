import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RULESET_PATH = BASE_DIR / "src" / "rules" / "ruleset.json"

RISK_PRIORITY = {
    "RED": 3,
    "YELLOW": 2,
    "GREEN": 1,
    "UNKWNON" : 0
}

def load_rules():
    with open(RULESET_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)
    
RULES = load_rules()

def assess_risk(foods: list[str], drugs: list[str]) -> dict:
    matched_rules = []

    for rule in RULES:
        food_hit = any(f in foods for f in rule["condition"].get("foods", []))
        drug_hit = any(d in drugs for d in rule["condition"].get("drugs", []))

        if food_hit and drug_hit:
            matched_rules.append(rule)

    if not matched_rules:
        return {
            "risk_level": "GREEN",
            "risk_code": "NO_KNOWN_RISK",
            "decision_basis": {
                "rule_based": True,
                "matched_rules": []
            },
            "evidence_keys": [],
            "debug": {}
        }

    top_rule = max(
        matched_rules,
        key=lambda r: RISK_PRIORITY.get(r["risk_level"], 0)
    )

    return {
        "risk_level": top_rule["risk_level"],
        "risk_code": top_rule["risk_code"],
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in matched_rules]
        },
        "evidence_keys": list({
            r["evidence_key"]
            for r in matched_rules
            if "evidence_key" in r
        }),
        "debug": {
            "matched_rules": matched_rules
        }
    }