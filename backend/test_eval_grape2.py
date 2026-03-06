import sys
import os
import json
sys.path.append(os.getcwd())

from src.rules.evaluator import evaluate_rules
import json

with open("data/rules/ruleset.json", "r", encoding="utf-8") as f:
    rules = json.load(f)["rules"]

normalized_entities = {
    "drugs": [{"raw": "로사르탄", "entity_id": "DRUG_LOSARTAN", "match_type": "exact"}],
    "foods": [{"raw": "자몽", "entity_id": "FOOD_GRAPEFRUIT", "match_type": "exact"}],
    "situations": [{"raw": "고령", "canonical": "고령", "entity_id": "CONDITION_elderly"}, {"raw": "고혈압", "canonical": "고혈압", "entity_id": "CONDITION_hypertension"}]
}

res = evaluate_rules(normalized_entities, rules)
print(json.dumps(res, indent=2, ensure_ascii=False))
