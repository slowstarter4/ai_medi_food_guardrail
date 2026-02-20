import csv
import json
import sys
import os
import unicodedata
from pathlib import Path

# 프로젝트 루트(backend)를 패스에 추가하여 service 등 모듈 임포트 가능하게 함
sys.path.append(str(Path(__file__).resolve().parents[2]))

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

    # 유니코드 정규화 (Han Gul NFC)
    value = unicodedata.normalize('NFC', value.strip())
    
    if not value or value == "ALL":
        return []

    return [v.strip() for v in value.split("|") if v.strip()]


def map_to_entity_ids(values, entity_map, rule_id, field):
    """CSV 값 → entity_id 매핑 (대소문자 무시 + 유니코드 정규화)"""
    result = []
    # entity_map의 키를 정규화+소문자로 하는 맵 생성
    lower_map = {unicodedata.normalize('NFC', k).lower(): v for k, v in entity_map.items()}
    
    for v in values:
        v_norm = unicodedata.normalize('NFC', v).lower()
        if v_norm in lower_map:
            result.append(lower_map[v_norm])
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

            # 4. Level 결정 로직 (데이터 분석팀 요청 반영)
            # Level 1: 특정 성분/약명이 명시됨 (drug_name != ALL)
            # Level 2: 약물명은 모르나 계열은 암 (drug_name == ALL and drug_category != ALL)
            # Level 3: 약물명/계열 모두 모름 (drug_category == ALL)
            
            csv_drug_name = row.get("drug_name", "ALL")
            csv_drug_cat = row.get("drug_category", "ALL")
            
            if csv_drug_name and csv_drug_name != "ALL":
                level = 1
            elif csv_drug_cat and csv_drug_cat != "ALL":
                level = 2
            else:
                level = 3

            # 5. conditions (항상 키는 존재)
            conditions = {
                "drugs": drug_ids,        # [] → 약 조건 없음
                "foods": food_ids,        # [] → 음식 조건 없음
                "situations": situation_ids
            }

            if not drug_ids and not food_ids and not situation_ids:
                print(f"[WARN] rule={rule_id} has empty conditions")

            # 6. rule 생성
            rules.append({
                "rule_id": rule_id,
                "level": level,
                "persona": row["persona"],
                "conditions": conditions,
                "risk_type": row["risk_type"],
                "risk_level_hint": row["risk_level"],
                "message_id": row["message_id"],
                "evidence_key": row["message_id"],
                "description": row["description"]
            })

    # 6. JSON 저장
    JSON_PATH.write_text(
        json.dumps({"rules": rules}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


if __name__ == "__main__":
    convert()
