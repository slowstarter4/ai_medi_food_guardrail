import sys
import os
import json
sys.path.append(os.getcwd())

from src.rag.explainer import generate_explanation

test_risk_result = {
    "input_text": "로사르탄이랑 바나나 먹었어요",
    "risk_level": "RED",
    "user_conditions": ["고혈압", "고령"],
    "entities_involved": {
        "drugs": [{"raw": "로사르탄", "entity_id": "DRUG_LOSARTAN"}],
        "foods": [{"raw": "바나나", "entity_id": "FOOD_BANANA"}]
    }
}

test_evidences = [
    {
        "evidence_id": "EVD_HTN_POTASSIUM_FOOD",
        "evidence_source_label": "FDA drug label (losartan)",
        "evidence_strength": "HIGH",
        "evidence_summary_user": "혈압약(ACE/ARB) 복용 시 칼륨 배출이 억제됩니다. 바나나나 토마토 등 고칼륨 식품을 많이 드시면 위험한 부정맥이 올 수 있으니 섭취량을 조절하세요."
    }
]

print(">>> Generating Explanation")
res = generate_explanation(test_risk_result, test_evidences)
print(res)
