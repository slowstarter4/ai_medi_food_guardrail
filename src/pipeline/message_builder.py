def build_user_message(risk_result: dict) -> dict:
    level = risk_result.get("risk_level", "UNKNOWN")

    if level == "RED":
        return {
            "summary": "복용 중인 약물과 식품 간 위험이 있을 수 있습니다 ",
            "tone": "warning"
        }
    
    if level == "YELLOW":
        return {
            "summary": "약물과 식품 간 주의가 필요합니다",
            "tone": "info"
        }
    if level == "GREEN":
        return {
            "summary":"알려진 특별한 위험은 없습니다.",
            "tone": "neutral"
        }
    return {
        "summary": "위험 여부를 판단하기에 정보가 충분하지 않습니다.",
        "tone": "neutral"
    }