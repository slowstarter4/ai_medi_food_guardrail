from typing import TypedDict, List, Optional

class Evidence(TypedDict, total=False):
    evidence_key: str
    evidence_id: str
    source: str                    # External API fallback key
    evidence_source_label: str     # evidence_db.json primary key
    evidence_strength: str         # HIGH | MODERATE | LOW
    title: str
    summary: str                   # External API fallback key
    evidence_summary_user: str     # evidence_db.json primary key
    evidence_tags: List[str]
    url: Optional[str]
