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

        # 1. 핵심 도메인 매칭: AND 조건 적용
        # 룰이 특정 Foods를 정의했다면, 그 중 하나라도 포함되어야 함
        if rule_foods and not (rule_foods & food_ids):
            continue
            
        # 룰이 특정 Drugs를 정의했다면 매칭 확인
        if rule_drugs:
            matched_drug_count = len(rule_drugs & drug_ids)
            if matched_drug_count == 0:
                continue
            
            # [특수 케이스] 약물 중복/병용 룰 (SITUATION_DRUG_DUPLICATION 요구 시)
            # 최소 2종 이상의 약물이 해당 리스트 내에서 매칭되어야 함
            if "SITUATION_DRUG_DUPLICATION" in rule_situations and matched_drug_count < 2:
                continue

        # 룰이 Drugs도 Foods도 정의하지 않은 경우 (SITUATION ONLY?) -> 일단 허용하거나 pass
        # 하지만 보통 최소한 하나는 있음. 둘 다 비어있으면 매칭된 것으로 간주(Precondition이 없는 셈)
        
        # 2. 상황 조건 및 페르소나 체크
        # 2.1 페르소나 체크 (Persona 필드가 있으면 사용자 상태와 대조)
        rule_persona = rule.get("persona")
        if rule_persona:
            # entities["situations"]에서 CONDITION_... 들의 raw 값 추출
            user_specs = {
                v["raw"] for v in entities.get("situations", []) 
                if v.get("entity_id", "").startswith("CONDITION_")
            }
            persona_parts = set(rule_persona.split("_"))
            # 페르소나 구성 요소 중 하나라도 사용자 상태와 일치하면 매칭 (더 유연한 매칭)
            if not (persona_parts & user_specs):
                continue

        # 2.2 개별 상황 조건 체크: ALL 매칭 (issubset)
        # 룰에서 정의한 모든 상황이 사용자 상황에 포함되어야 함
        if rule_situations and not rule_situations.issubset(situation_ids):
            continue

        # matched_rule에 필요한 key만 안전하게 포함
        matched.append({
            "rule_id": rule.get("rule_id"),
            "level": rule.get("level", 3),  # 기본값 Level 3 (가장 낮음)
            "risk_level_hint": rule.get("risk_level_hint"),
            "description": rule.get("description"),
            "evidence_key": rule.get("evidence_key")
        })

    return matched
