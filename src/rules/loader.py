#룰 로딩 전용
import json
from pathlib import Path

def load_rules():
    path = Path(__file__).parent / "ruleset.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)