# src/rules/csv_to_ruleset.py
import csv
import json
from pathlib import Path
from service.entity_normalizer import load_entity_index

CSV_PATH = Path("data/rules/food_drug_interaction.csv")
JSON_PATH = Path("data/rules/ruleset.json")


def split_values(value: str) -> list[str]:
    """
    CSV 셀 값을 | 기준으로 분리
    - 빈 값 / ALL → []
    """
    if not value:
        return []

    value = value.strip()
    if not value or value == "ALL":
        return []

    return [v.strip() for v in value.split("|") if v.strip()]


def map_to_entity_ids(values, entity_map, rule_id, field):
    """CSV 값 → entity_id 매핑"""
    result = []
    for v in values:
        if v in entity_map:
            result.append(entity_map[v])
        else:
            print(f"[WARN] rule={rule_id} unmapped {field}: '{v}'")
    return result


def convert():
    rules = []

    # 1. entity_index 로드
    entity_index = load_entity_index()

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            rule_id = row["rule_id"]

            # 2. CSV 값 분리
            drug_names = split_values(row.get("drug_name"))
            food_keywords = split_values(row.get("food_keyword_match"))
            situations = split_values(row.get("condition"))

            # 3. entity_id 매핑
            drug_ids = map_to_entity_ids(
                drug_names,
                entity_index.get("drugs", {}),
                rule_id,
                "drug"
            )
            food_ids = map_to_entity_ids(
                food_keywords,
                entity_index.get("foods", {}),
                rule_id,
                "food"
            )
            situation_ids = map_to_entity_ids(
                situations,
                entity_index.get("situations", {}),
                rule_id,
                "situation"
            )

            # 4. conditions (항상 키는 존재)
            conditions = {
                "drugs": drug_ids,        # [] → 약 조건 없음
                "foods": food_ids,        # [] → 음식 조건 없음
                "situations": situation_ids
            }

            if not drug_ids and not food_ids and not situation_ids:
                print(f"[WARN] rule={rule_id} has empty conditions")

            # 5. rule 생성
            rules.append({
                "rule_id": rule_id,
                "persona": row["persona"],
                "conditions": conditions,
                "risk_type": row["risk_type"],
                "risk_level_hint": row["risk_level"],
                "message_id": row["message_id"],
                "description": row["description"]
            })

    # 6. JSON 저장
    JSON_PATH.write_text(
        json.dumps({"rules": rules}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    convert()
