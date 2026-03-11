import sys
import os

# 프로젝트 루트 경로 추가 (현재 디렉토리가 루트임을 가정)
sys.path.append(os.getcwd())

from backend.src.rules.evaluator import evaluate_rules

# 테스트 케이스 1: 이부프로펜 + 알코올
entities1 = {
    "drugs": [{"raw": "이부프로펜", "entity_id": "DRUG_IBUPROFEN"}],
    "foods": [{"raw": "소주", "entity_id": "FOOD_ALCOHOL"}],
    "situations": [{"raw": "관절염", "entity_id": "CONDITION_arthritis"}]
}

# 테스트 케이스 2: 이부프로펜 + 나프록센 (중복 복용)
entities2 = {
    "drugs": [
        {"raw": "이부프로펜", "entity_id": "DRUG_IBUPROFEN"},
        {"raw": "나프록센", "entity_id": "DRUG_NAPROXEN"}
    ],
    "foods": [],
    "situations": [{"raw": "관절염", "entity_id": "CONDITION_arthritis"}]
}

# 가짜 룰셋 (실제와 유사하게 구성)
test_rules = [
    {
        "rule_id": "NSAID_ALL_ALCOHOL",
        "persona": "관절염",
        "drug_category": "NSAIDs",
        "food_keyword_match": "술|알코올|소주",
        "risk_level_hint": "RED"
    },
    {
        "rule_id": "NSAID_003",
        "persona": "관절염",
        "drug_category": "NSAIDs",
        "food_keyword_match": "이부프로펜|나프록센",
        "risk_level_hint": "RED"
    }
]

print("--- Test Case 1: Ibuprofen + Alcohol ---")
matched1 = evaluate_rules(entities1, test_rules)
for m in matched1:
    print(f"Matched: {m['rule_id']}")

print("\n--- Test Case 2: Ibuprofen + Naproxen ---")
matched2 = evaluate_rules(entities2, test_rules)
for m in matched2:
    print(f"Matched: {m['rule_id']}")

# 검증
assert "NSAID_ALL_ALCOHOL" in [m['rule_id'] for m in matched1]
assert "NSAID_003" not in [m['rule_id'] for m in matched1]
assert "NSAID_003" in [m['rule_id'] for m in matched2]

print("\n[SUCCESS] Fix verified!")
