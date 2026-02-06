FOOD_SUFFIXES = [
    "주스", "즙", "차", "분말", "환", "정", "캡슐", "보충제"
]

FOOD_ANCHOR_MAP = {
    "그레이프프루트": "자몽",
    "녹황색채소": "비타민K",
}

def normalize_food(food:str) -> str:
    f = food.strip()

    # suffix 제거
    for suffix in FOOD_SUFFIXES:
        if f.endswith(suffix):
            f = f[:-len(suffix)]

    # 앵커 매핑
    return FOOD_ANCHOR_MAP.get(f, f)

def normalize_entities(entities: dict) -> dict:
    return {
        "foods": [normalize_food(f) for f in entities.get("foods", [])],
        "drugs": entities.get("drugs", []),
        "supplements": entities.get("supplements", [])
    }
