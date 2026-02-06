from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.risk_assessor import assess_risk

def build_known_entities(rules):
    """
    ruleset.json에 등장하는 모든 엔티티를 수집
    entity_parser용 사전 생성
    """
    known_entities = {
        "foods" : set(),
        "drugs" : set(),
        "supplements": set()
    }

    for rule in rules:
        conditions = rule.get("conditions", {})
        for key in known_entities.keys():
            for value in conditions.get(key, []):
                known_entities[key].add(value)

    # set -> list 변환
    return {k : list(v) for k, v in known_entities.items()}

def main():
    # 1. 입력
    raw_text = """
    어제 술 마시고 알프라졸람 먹었어
    """
    # 2. 룰 로딩
    ruleset = load_ruleset()
    rules = ruleset["rules"]

    # 3. entity 사전 구성
    known_entities = build_known_entities(rules)

    # 4. 엔티티 파싱
    entities = parse_entities(raw_text, known_entities)
    
    # 5. 룰 매칭
    matched_rules = evaluate_rules(entities, rules)

    # 6. 위험도 판단 (유일한 판단 지점)
    result = assess_risk(entities, matched_rules)

    # 7. 출력
    print("\n=== ENTITIES ===")
    print(entities)

    print("\n=== MATCHED RULES ===")
    for r in matched_rules:
        print(f"- {r['rule_id']} ({r['risk_level_hint']})")

    print("\n=== FINAL RISK RESULT ===")
    print(result)

if __name__ == "__main__":
    main()