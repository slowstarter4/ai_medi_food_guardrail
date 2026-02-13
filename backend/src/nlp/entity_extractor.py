import re

# 간단한 조사/어미 패턴 (MVP용)
POSTFIX_PATTERN = re.compile(r"(을|를|이|가|은|는|과|와|및)$")

def clean_token(token: str) -> str:
    return POSTFIX_PATTERN.sub("", token)

def extract_entities(text: str):
    """
    OCR 텍스트에서 엔티티 후보 추출 (조사 제거 포함)
    """
    raw_tokens = re.findall(r"[가-힣A-Za-z0-9]+", text)

    cleaned = []
    for tok in raw_tokens:
        cleaned.append(clean_token(tok))

    # 중복 제거
    return list(set(cleaned))
