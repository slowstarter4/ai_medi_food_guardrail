def extract_entities(text: str):
    """
    입력 예: "와파린 복용 중인데 시금치 먹어도 되나요?"
    """
    return {
        "drug":["와파린"],
        "intake":["시금치"],
    }