from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index

def build_known_entities_from_index(entity_index):
    return {entity_type: list(entity_index[entity_type].keys()) for entity_type in entity_index}

# Test scenarios
scenarios = [
    {"id": "DEMO_2", "input": "이부프로펜 먹고 있는데 나프록센도 같이 먹어도 되나요?"},
    {"id": "DEMO_3", "input": "고혈압약 먹고 있는데 감기약 같이 먹어도 괜찮을까요?"}
]

ruleset = load_ruleset()
rules = ruleset["rules"]
entity_index = load_entity_index()
known_entities = build_known_entities_from_index(entity_index)

for scenario in scenarios:
    print(f"\n{'='*60}")
    print(f"[{scenario['id']}] {scenario['input']}")
    print('='*60)
    
    # Parse and normalize
    parsed = parse_entities(scenario["input"], known_entities)
    normalized = normalize_entities(parsed)
    
    # Add situation if needed
    if normalized.get("drugs") and normalized.get("foods"):
        normalized.setdefault("situations", []).append({
            "raw": "병용",
            "canonical": "병용 섭취",
            "entity_id": "SITUATION_CONCURRENT"
        })
    
    print(f"\nParsed entities:")
    print(f"  Drugs: {[d['entity_id'] for d in normalized.get('drugs', [])]}")
    print(f"  Foods: {[f['entity_id'] for f in normalized.get('foods', [])]}")
    print(f"  Situations: {[s['entity_id'] for s in normalized.get('situations', [])]}")
    
    # Evaluate rules
    matched_rules = evaluate_rules(normalized, rules)
    
    print(f"\nMatched rules: {len(matched_rules)}")
    for r in matched_rules:
        print(f"  - {r['rule_id']}: evidence_key = {r.get('evidence_key')}")
