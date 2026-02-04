# demo_runner.py
# from src.nlp.entity_extractor import extract_entities
from src.rules.rule_engine import assess_risk
from src.pipeline.message_builder import build_user_message

# 시연용 고정 입력
foods = ["자몽", "녹황색채소"]
drugs = ["와파린", "암로디핀"]

if __name__ == "__main__":
    print("DEBUG foods:", foods)
    print("DEBUG drugs:", drugs)

    result = assess_risk(foods, drugs)

    print("\n[RISK RESULT]")
    print(result)

    user_message = build_user_message(result)

    print("\n[USER MESSAGE]")
    print(user_message)