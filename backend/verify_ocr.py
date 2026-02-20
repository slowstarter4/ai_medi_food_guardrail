import os
import sys
from src.ocr.processor import extract_text_from_image
from main import analyze_text
import json

def test_ocr_integration():
    # 실제 이미지 경로가 없으므로 파일 존재 여부만 체크하고 시뮬레이션하거나 
    # 사용자에게 테스트용 이미지를 요청할 수 있음.
    # 여기서는 로직 연결성만 테스트하기 위해 존재하지 않는 파일로 에러 핸들링 확인
    
    test_image = "non_existent_image.jpg"
    print(f"---Testing with non-existent file: {test_image}---")
    try:
        text = extract_text_from_image(test_image)
        print(f"Extracted Text: {text}")
    except FileNotFoundError as e:
        print(f"Caught expected error: {e}")

    print("\n---Testing OCR API Call Logic (Requires Valid Config)---")
    # .env가 이미 세팅되었으므로, 실제 파일이 있다면 작동함.
    # 사용자의 clover_ocr_test.py 경로를 참고하여 테스트 시도 가능
    
    potential_image = "c:/Users/kwing/Downloads/Github/ai_medi_food_guardrail/test_image.jpg" # 예시
    if os.path.exists(potential_image):
        text = extract_text_from_image(potential_image)
        print(f"Extracted Text: {text}")
        if text:
            result = analyze_text(text)
            print("Analysis Result:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Skipping actual API call test as {potential_image} not found.")

if __name__ == "__main__":
    # 프로젝트 루트가 아닌 backend 디렉토리에서 실행될 것을 가정
    sys.path.append(os.getcwd())
    test_ocr_integration()
