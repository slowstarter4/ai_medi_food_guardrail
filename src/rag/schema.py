from typing import TypedDict, List

class Evidence(TypedDict):
    evidence_key: str
    source: str          # MFDS | 논문 | 전문가DB | 임시
    title: str
    summary: str
    url: str | None