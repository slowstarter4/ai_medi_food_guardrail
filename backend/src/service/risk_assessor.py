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
    """
    1. 모든 매칭된 룰을 검사함 (Matched Rules)
    2. 대표 룰(primary_rule)은 Level -> Risk Level -> Rule ID 순으로 1개 선정
    3. 나머지는 보조 룰(secondary_rules)로 리스트업
    """
    if not matched_rules:
        return {
            "risk_level": "GREEN",
            "risk_code": "GREEN",
            "primary_rule": None,
            "secondary_rules": [],
            "decision_basis": {"rule_based": True, "matched_rules": []},
            "entities_involved": normalized_entities,
            "evidence_keys": [],
            "evidence_info": []
        }

    # 1. 룰 매칭 결과 정렬 (대표 룰 선정을 위함)
    # 정밀도(Level: 1 > 2 > 3) -> 위험등급(RED > YELLOW > GREEN) -> rule_id(오름차순)
    sorted_rules = sorted(
        matched_rules,
        key=lambda r: (
            r.get("level", 3),                          # 1차: Level (1 > 2 > 3)
            -PRIORITY.get(r.get("risk_level_hint"), 0), # 2차: Risk Level (RED > YELLOW)
            r.get("rule_id", "")                        # 3차: Rule ID (안정성)
        )
    )

    primary_rule_data = sorted_rules[0]
    final_risk = primary_rule_data["risk_level_hint"]
    
    # 2. 대표 룰을 제외한 나머지는 보조 룰로 분류 (GREEN 제외)
    secondary_rules = []
    if len(sorted_rules) > 1:
        for r in sorted_rules[1:]:
            if r.get("risk_level_hint") != "GREEN":
                secondary_rules.append({
                    "rule_id": r["rule_id"],
                    "risk_level": r["risk_level_hint"],
                    "description": r.get("description", ""),
                    "risk_type": r.get("risk_type", "알림"),
                })

    # 전체 매칭된 룰의 근거 키 수집
    evidence_keys = list({
        r.get("evidence_key")
        for r in sorted_rules
        if r.get("evidence_key") in EVIDENCE_DB
    })

    evidence_info = [EVIDENCE_DB[k] for k in evidence_keys if k in EVIDENCE_DB]

    return {
        "risk_level": final_risk,
        "risk_code": final_risk,
        "primary_rule": primary_rule_data["rule_id"],
        "matched_entities": primary_rule_data.get("matched_entities"),
        "secondary_rules": secondary_rules,
        "decision_basis": {
            "rule_based": True,
            "matched_rules": [r["rule_id"] for r in sorted_rules]
        },
        "entities_involved": normalized_entities,
        "evidence_keys": evidence_keys,
        "evidence_info": evidence_info
    }
