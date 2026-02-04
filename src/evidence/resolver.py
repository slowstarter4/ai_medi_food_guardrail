from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = BASE_DIR / "docs" / "evidence"

def load_evidence(evidence_key: str) -> str:
    path = EVIDENCE_DIR / f"{evidence_key}.md"
    if not path.exists():
        raise FileNotFoundError(f"Evidence not found: {evidence_key}")
    return path.read_text(encoding="utf-8")
