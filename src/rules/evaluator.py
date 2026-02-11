from typing import Dict, List

def evaluate_rules(entities: Dict, rules: List[Dict]) -> List[Dict]:
    """
    entities: 파싱+정규화된 엔티티 딕셔너리
    rules: ruleset.json에서 불러온 룰 리스트
    return: matched_rules 리스트 (rule_id, risk_level_hint, description, evidence_key 포함)
    """

    food_ids = {v["entity_id"] for v in entities.get("foods", [])}
    drug_ids = {v["entity_id"] for v in entities.get("drugs", [])}
    situation_ids = {v["entity_id"] for v in entities.get("situations", [])}

    matched = []

    for rule in rules:
        cond = rule.get("conditions", {})

        rule_foods = set(cond.get("foods", []))
        rule_drugs = set(cond.get("drugs", []))
        rule_situations = set(cond.get("situations", []))

        # 1. 핵심 도메인 매칭 수정: AND 조건 적용
        # 룰이 특정 Foods를 정의했다면, 그 중 하나라도 포함되어야 함
        if rule_foods and not (rule_foods & food_ids):
            continue
            
        # 룰이 특정 Drugs를 정의했다면, 그 중 하나라도 포함되어야 함
        if rule_drugs and not (rule_drugs & drug_ids):
            continue

        # 룰이 Drugs도 Foods도 정의하지 않은 경우 (SITUATION ONLY?) -> 일단 허용하거나 pass
        # 하지만 보통 최소한 하나는 있음. 둘 다 비어있으면 매칭된 것으로 간주(Precondition이 없는 셈)
        
        # 2. 상황 조건 체크

        # 2️⃣ 상황 조건은 보조
        if rule_situations and not (rule_situations & situation_ids):
            continue

        # matched_rule에 필요한 key만 안전하게 포함
        matched.append({
            "rule_id": rule.get("rule_id"),
            "risk_level_hint": rule.get("risk_level_hint"),
            "description": rule.get("description"),
            "evidence_key": rule.get("evidence_key")  # 존재하지 않으면 None
        })

    return matched
