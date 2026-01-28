import json
from nlp.extractor import extract_entities

def load_rules():
    with open('rules/sample_rules.json', 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def match_risk(drug, intake, rules):
    for rule in rules:
        if rule['drug'] == drug and rule['intake'] == intake:
            return rule
    return None

def run(text_input):
    entities = extract_entities(text_input)
    rules = load_rules()

    drug = entities['drug'][0]
    intake = entities['intake'][0]

    matched = match_risk(drug, intake, rules)

    if matched:
        return {
            "input": entities,
            "result": {
                "risk_level": matched["risk_level"],
                "risk_summary": matched["description"]
            },
            "reason": [
                {
                    "type": "drug-food",
                    "description": matched["description"],
                    "evidence": matched["evidence"]
                }
            ],
            "source": ["e약은요"],
            "disclaimer": "의료적 판단이 아닙니다"
        }
    else:
        return {
            "input": entities,
            "result": {
                "risk_level": "none",
                "risk_summary": "알려진 위험 사례가 없습니다."
            },
            "reason": [],
            "source": [],
            "disclaimer": "의료적 판단이 아닙니다"
        }

if __name__ == "__main__":
    text = input("입력: ")
    output = run(text)
    print(json.dumps(output, ensure_ascii=False, indent=2))