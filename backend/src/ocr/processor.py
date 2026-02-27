import os
import json
import uuid
import time
import tempfile
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

load_dotenv()

# Clova OCR 제한: 최대 2MB, 1920px 권장
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
MAX_IMAGE_DIMENSION = 1920


def _preprocess_image(image_path: str) -> tuple[str, bool]:
    """
    Clova OCR 전송 전 이미지 전처리.
    파일 크기 > 2MB 또는 해상도 > 1920px 이면
    임시파일로 리사이즈/압쳙 후 경로 반환.
    Returns: (actual_path, is_temp) — is_temp=True이면 사용 후 삭제 필요
    """
    if not _PIL_AVAILABLE:
        return image_path, False

    file_size = os.path.getsize(image_path)
    need_resize = file_size > MAX_IMAGE_SIZE_BYTES

    if not need_resize:
        try:
            with Image.open(image_path) as img:
                w, h = img.size
                if max(w, h) > MAX_IMAGE_DIMENSION:
                    need_resize = True
        except Exception:
            return image_path, False

    if not need_resize:
        return image_path, False

    # 리사이즈 + 압쳙
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)

            tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            tmp_path = tmp.name
            tmp.close()

            quality = 85
            img.save(tmp_path, "JPEG", quality=quality, optimize=True)

            # 여전히 크면 quality 낮춰서 재압쳙
            while os.path.getsize(tmp_path) > MAX_IMAGE_SIZE_BYTES and quality > 40:
                quality -= 10
                img.save(tmp_path, "JPEG", quality=quality, optimize=True)

            print(f"[OCR] 이미지 리사이즈: {file_size // 1024}KB → {os.path.getsize(tmp_path) // 1024}KB (quality={quality})")
            return tmp_path, True
    except Exception as e:
        print(f"[OCR] 이미지 전처리 실패, 원본 사용: {e}")
        return image_path, False


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

    # 전송 전 이미지 전처리 (리사이즈/압쳙)
    actual_path, is_temp = _preprocess_image(image_path)

    # 확장자에 따른 포맷 결정
    ext = os.path.splitext(actual_path)[1].lower().replace(".", "")
    if ext == "jpg": ext = "jpeg"
    if ext not in ["jpeg", "png"]: ext = "jpeg"

    request_json = {
        "images": [{"format": ext, "name": "scan_image"}],
        "requestId": str(uuid.uuid4()),
        "version": "V2",
        "timestamp": int(time.time() * 1000),
    }

    payload = {"message": json.dumps(request_json)}
    headers = {"X-OCR-SECRET": secret_key}

    try:
        with open(actual_path, "rb") as f:
            files = {"file": f}
            response = requests.post(api_url, headers=headers, data=payload, files=files, timeout=30)

        response.raise_for_status()
        res_data = response.json()

        fields = res_data.get("images", [{}])[0].get("fields", [])
        extracted_text = " ".join([f.get("inferText", "") for f in fields])

        return extracted_text.strip()

    except Exception as e:
        print(f"[OCR] 오류 발생: {str(e)}")
        return ""
    finally:
        # 임시 파일 정리
        if is_temp and os.path.exists(actual_path):
            os.remove(actual_path)

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
