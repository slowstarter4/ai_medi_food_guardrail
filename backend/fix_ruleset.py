import json

with open("data/rules/ruleset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Define explicit mappings of rule_id to the new evidence_id
mappings = {
    "HTN_001": "EV_HTN_001",
    "HTN_002": "EV_HTN_002",
    "HTN_003": "EV_HTN_004",   # CCB + 자몽
    "HTN_004": "EXTRA_HTN_DECONGESTANT",
    "HTN_005": "EXTRA_HTN_NSAID",
    "HTN_006": "EV_HTN_005",   # 이뇨제 + 감초
    "HTN_007": "EXTRA_HTN_DEHYDRATION",

    "DM_001": "EV_DM_004",     # 당뇨약 + 공복음주 -> 공복 음주
    "DM_002": "EXTRA_DM_HYPERGLYCEMIA",
    "DM_003": "EV_DM_001",     # 메트포르민 + 과음
    "DM_004": "EXTRA_DM_MEAL_SKIP",
    "DM_005": "EXTRA_DM_DEHYDRATION",
    "DM_006": "EV_DM_003",     # 설폰요소제 + 공복음주

    "NSAID_001": "EV_NSAID_001",  # NSAID + 음주
    "NSAID_002": "EXTRA_NSAID_GI",
    "NSAID_003": "EXTRA_NSAID_DUPLICATION",
    "NSAID_004": "EV_NSAID_003",  # NSAID + 탈수
    "NSAID_005": "EV_NSAID_002"   # NSAID + 출혈 (와파린)
}

for rule in data["rules"]:
    if rule["rule_id"] in mappings:
        rule["evidence_key"] = mappings[rule["rule_id"]]

with open("data/rules/ruleset.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Ruleset dynamically updated!")
