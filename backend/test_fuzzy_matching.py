import sys
import os
import json

# 백엔드 경로 추가
sys.path.append(os.getcwd())

from service.entity_normalizer import normalize_entities

# 테스트 케이스 1: OCR 입력 (노이즈 심함, Threshold 92)
test_input_ocr = {
    "drugs": ["글레미피리드", "타이레놀ㄹ"], 
    "foods": ["바나나나", "자몽쥬쓰"], # 자몽은 위험성분이라 92 필요
    "situations": ["공복복용"]
}

# 테스트 케이스 2: 수동 입력 (오타, Threshold 95)
test_input_manual = {
    "drugs": ["이부프로팬", "타이레놀서방정"], 
    "foods": ["탄수화물함유"], # 일반 영양소 85
    "situations": ["격한운동"]
}

print("\n>>> Testing [OCR] Source")
res_ocr = normalize_entities(test_input_ocr, source="ocr")
print(json.dumps(res_ocr, indent=2, ensure_ascii=False))

print("\n>>> Testing [MANUAL] Source")
res_manual = normalize_entities(test_input_manual, source="manual")
print(json.dumps(res_manual, indent=2, ensure_ascii=False))

# 테스트 케이스 3: 약물 모호성 (Ambiguity Check)
# "유글리콘" vs "유글로콘" (둘 다 Sulfonylurea이지만 만약 다르면?)
# 현재 index에는 둘 다 같은 ID라 상관없지만, 점수 차이가 적으면 경고 떠야함
test_ambiguity = {
    "drugs": ["유글로콜"] # 유글로콘, 유글로콜 등이 인덱스에 있음
}
print("\n>>> Testing Ambiguity Check")
res_ambig = normalize_entities(test_ambiguity, source="manual")
print(json.dumps(res_ambig, indent=2, ensure_ascii=False))
