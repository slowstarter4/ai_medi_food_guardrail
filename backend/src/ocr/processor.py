import os
from typing import Dict, List, Optional

def extract_text_from_image(image_path: str) -> str:
    """
    이미지 파일(처방전, 약봉투, 식품 성분표 등)에서 텍스트를 추출합니다.
    
    Args:
        image_path (str): 분석할 이미지 파일의 경로
        
    Returns:
        str: 인식된 텍스트 전체
        
    Note:
        향후 Google Vision API, Tesseract 또는 CLOVA OCR 연동이 필요한 부분입니다.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    # TODO: 실제 OCR 엔진 연동
    print(f"[OCR] 이미지 처리 시작: {image_path}...")
    
    # 현재는 가상의 결과를 반환하도록 설계
    return "인식된 텍스트 예시 (아직 구현되지 않음)"

def process_medication_document(image_path: str) -> Dict[str, str]:
    """
    이미지를 분석하여 문서 종류와 텍스트를 담은 객체를 반환합니다.
    """
    raw_text = extract_text_from_image(image_path)
    
    return {
        "raw_text": raw_text,
        "document_type": "UNKNOWN", # 이미지 분석을 통해 'PRESCRIPTION', 'FOOD_LABEL' 등으로 분류 예정
        "processed_at": "2026-02-11" # 타임스탬프
    }
