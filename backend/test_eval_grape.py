import sys
import os
import json
sys.path.append(os.getcwd())

from src.pipeline.evaluator import Evaluator

evaluator = Evaluator()

normalized_entities = {
    "drugs": [{"raw": "로사르탄", "entity_id": "DRUG_LOSARTAN", "match_type": "exact"}],
    "foods": [{"raw": "자몽", "entity_id": "FOOD_GRAPEFRUIT", "match_type": "exact"}],
    "situations": []
}
user_conditions = ["고령", "고혈압"]

res = evaluator.evaluate(normalized_entities, user_conditions)
print(json.dumps(res, indent=2, ensure_ascii=False))
