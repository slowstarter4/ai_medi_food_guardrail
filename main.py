from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from service.risk_assessor import assess_risk

def build_known_entities_from_index(entity_index):
    """
    parser용 표면어 사전 생성
    """
    return {
        entity_type: list(entity_index[entity_type].keys())
        for entity_type in entity_index
    }

def main(input_payload=None):
    if input_payload is None:
        raw_text = "암로디핀 복용 중 자몽주스를 마셨습니다"
    else:
        raw_text = input_payload["raw_text"]

    # 2. 룰 로딩
    ruleset = load_ruleset()
    rules = ruleset["rules"]

    # 3. entity index 로딩 (정규화 기준)
    entity_index = load_entity_index()

    # 4. parser용 표면어 사전
    known_entities = build_known_entities_from_index(entity_index)

    # 5. 엔티티 파싱 (표면어)
    parsed_entities = parse_entities(raw_text, known_entities)

    # 6. 엔티티 정규화 (entity_id)
    normalized_entities = normalize_entities(parsed_entities)

    if normalized_entities.get("drugs") and normalized_entities.get("foods"):
        normalized_entities.setdefault("situations", []).append({
            "raw": "병용",
            "canonical": "병용 섭취",
            "entity_id": "SITUATION_CONCURRENT"
        })

    # 7. 룰 매칭
    matched_rules = evaluate_rules(normalized_entities, rules)

    # 8. 위험도 판단
    result = assess_risk(normalized_entities, matched_rules)

    # 출력

    print("\n[ENTITIES]")
    for d in normalized_entities.get("drugs", []):
        print(f"- Drug: {d['raw']} → {d['entity_id']}")
    for f in normalized_entities.get("foods", []):
        print(f"- Food: {f['raw']} → {f['entity_id']}")
    for s in normalized_entities.get("situations", []):
        print(f"- Situation: {s['canonical']} → {s['entity_id']}")

    print("\n[MATCHED RULES]")
    for r in matched_rules:
        print(f"- {r['rule_id']} | {r['risk_level_hint']}")
        print(f"  ↳ {r['description']}")

    print("\n[FINAL DECISION]")
    print(f"Risk Level : {result['risk_level']}")

if __name__ == "__main__":
    main()
