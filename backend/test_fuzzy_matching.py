import sys
import os

# 백엔드 경로 추가
sys.path.append(os.getcwd())

from service.entity_normalizer import normalize_entities

# 테스트 케이스
test_input = {
    "drugs": ["글레미피리드", "타이레놀ㄹ"], # 오타
    "foods": ["바나나나", "자몽주스"], # 오타/접미사
    "situations": ["공복복용", "술마셨어요", "격한운동"] # 오타/유사표현
}

print(">>> Testing Fuzzy Matching Engine")
res = normalize_entities(test_input)

import json
print(json.dumps(res, indent=2, ensure_ascii=False))
