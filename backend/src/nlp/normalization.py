import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def load_dict(name):
    path = BASE_DIR / "data" / "normalization" / name
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    
FOOD_DICT = load_dict("food_normalization.json")
DRUG_DICT = load_dict("drug_normalization.json")

def normalize_entity(token: str) -> dict:
    cleaned = token.replace(" ", "").strip()

    if cleaned in FOOD_DICT:
        return {
            "original": token,
            "normalized": FOOD_DICT[cleaned],
            "type": "food"
        }

    if cleaned in DRUG_DICT:
        return {
            "original": token,
            "normalized": DRUG_DICT[cleaned],
            "type": "drug"
        }

    return {
        "original": token,
        "normalized": "unknown",
        "type": "unknown"
    }