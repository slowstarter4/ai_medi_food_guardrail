from typing import Dict, List

def evaluate_rules(entities, rules):

    food_ids = {v["entity_id"] for v in entities.get("foods", [])}
    drug_ids = {v["entity_id"] for v in entities.get("drugs", [])}
    situation_ids = {v["entity_id"] for v in entities.get("situations", [])}

    matched = []

    for rule in rules:
        cond = rule["conditions"]

        rule_foods = set(cond.get("foods", []))
        rule_drugs = set(cond.get("drugs", []))
        rule_situations = set(cond.get("situations", []))

        # 1️⃣ 핵심 도메인 매칭 (foods / drugs 중 하나는 반드시)
        domain_matched = False

        if rule_foods and (rule_foods & food_ids):
            domain_matched = True

        if rule_drugs and (rule_drugs & drug_ids):
            domain_matched = True

        if not domain_matched:
            continue  # ❌ 핵심 엔티티 매칭 없으면 탈락

        # 2️⃣ 상황 조건은 보조
        if rule_situations and not (rule_situations & situation_ids):
            continue

        matched.append(rule)

    return matched
