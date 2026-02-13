import json
from pathlib import Path


def load_ruleset() -> dict:
    """
    ruleset.json 로딩
    """
    base_dir = Path(__file__).resolve().parents[2]
    ruleset_path = base_dir / "data" / "rules" / "ruleset.json"

    with open(ruleset_path, "r", encoding="utf-8") as f:
        return json.load(f)