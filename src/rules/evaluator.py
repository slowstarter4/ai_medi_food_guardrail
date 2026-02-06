from typing import Dict, List, Any

def _match_condition(
        entity_values: List[str],
        rule_values: List[str]
) -> bool:
    """
    rule_values가 비어 있으면 조건 없음 → True
    rule_values ⊆ entity_values 인지 검사
    """
    if not rule_values:
        return True

    entity_set = set(entity_values)
    rule_set = set(rule_values)

    return rule_set.issubset(entity_set)

def evaluate_rules(
    entities: Dict[str, List[str]],
    rules: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    entities와 rules를 비교하여 매칭된 룰만 반환
    판단 로직은 포함하지 않는다
    """
    matched_rules = []

    for rule in rules:
        conditions = rule.get("conditions", {})

        if not (
            _match_condition(entities.get("foods", []), conditions.get("foods", [])) and
            _match_condition(entities.get("drugs", []), conditions.get("drugs", [])) and
            _match_condition(entities.get("supplements", []), conditions.get("supplements", []))
        ):
            continue

        matched_rules.append({
            "rule_id": rule["rule_id"],
            "category": rule.get("category"),
            "risk_level_hint": rule.get("risk_level_hint"),
            "risk_code": rule.get("risk_code"),
            "description": rule.get("description"),
            "evidence_keys": rule.get("evidence_keys", [])
        })

    return matched_rules