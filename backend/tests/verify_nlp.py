import sys
import os
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.append(str(Path(__file__).resolve().parents[1]))

from service.llm_entity_parser import parse_entities_with_llm
from service.prescription_parser import parse_prescription
import json

def test_entity_normalization():
    print("\n[TEST] Entity Normalization (Fuzzy/Semantic)")
    test_cases = [
        "아침에 자몽주수 마심",
        "암로디핀 5미리 복용중",
        "혈압약이랑 자몽쥬스 같이 먹어도 돼?"
    ]
    
    for text in test_cases:
        print(f"\nInput: {text}")
        result = parse_entities_with_llm(text)
        print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")

def test_prescription_fallback():
    print("\n[TEST] Prescription Parser Fallback (LLM)")
    # 일부러 규칙 기반(표 형식)으로 읽기 힘든 흐트러진 텍스트 제공
    raw_ocr = """
    처방전 정보입니다.
    자누메트정 50/1000mg 1정씩 아침저녁 14일분
    로사르탄 5mg 1일 1회 식후 30분
    """
    
    print(f"\nInput OCR Text:\n{raw_ocr}")
    result = parse_prescription(raw_ocr)
    print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    test_entity_normalization()
    test_prescription_fallback()
