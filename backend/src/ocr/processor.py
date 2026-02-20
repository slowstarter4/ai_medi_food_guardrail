import os
import json
import uuid
import time
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_image(image_path: str) -> str:
    """
    이미지 파일(처방전, 약봉투, 식품 성분표 등)에서 텍스트를 추출합니다.
    (Naver CLOVA OCR API 연동)
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

    api_url = os.getenv("CLOVA_OCR_API_URL")
    secret_key = os.getenv("CLOVA_OCR_SECRET")

    if not api_url or not secret_key:
        print("[OCR] 경고: CLOVA_OCR API 설정이 없습니다. .env 파일을 확인하세요.")
        return "OCR 설정 오류"

    print(f"[OCR] 이미지 처리 시작(CLOVA): {image_path}...")
    
    # 확장자에 따른 포맷 결정 (jpeg, png, etc)
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "jpg": ext = "jpeg"
    if ext not in ["jpeg", "png"]: ext = "jpeg" # 기본값

    request_json = {
        "images": [{"format": ext, "name": "scan_image"}], 
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(time.time() * 1000),
    }

    payload = {"message": json.dumps(request_json)}
    headers = {"X-OCR-SECRET": secret_key}

    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(api_url, headers=headers, data=payload, files=files, timeout=30)
        
        response.raise_for_status()
        res_data = response.json()
        
        # 필드별 텍스트 병합
        fields = res_data.get("images", [{}])[0].get("fields", [])
        extracted_text = " ".join([f.get("inferText", "") for f in fields])
        
        return extracted_text.strip()
        
    except Exception as e:
        print(f"[OCR] 오류 발생: {str(e)}")
        return ""

def process_medication_document(image_path: str) -> Dict[str, str]:
    """
    이미지를 분석하여 문서 종류와 텍스트를 담은 객체를 반환합니다.
    """
    raw_text = extract_text_from_image(image_path)
    
    return {
        "raw_text": raw_text,
        "document_type": "UNKNOWN",
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
