"""
Import 진단 스크립트 - 어느 단계에서 멈추는지 확인용
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

print("Step 1: 기본 라이브러리 OK")

from src.rules.loader import load_ruleset
print("Step 2: load_ruleset OK")

from src.rules.evaluator import evaluate_rules
print("Step 3: evaluate_rules OK")

from service.entity_parser import parse_entities
print("Step 4: entity_parser OK")

from service.entity_normalizer import normalize_entities, load_entity_index
print("Step 5: entity_normalizer OK")

from src.service.risk_assessor import assess_risk
print("Step 6: risk_assessor OK")

print("\n모든 import 성공! 기본 테스트 실행...")

entity_index = load_entity_index()
known_entities = {etype: list(entity_index[etype].keys()) for etype in entity_index}
parsed = parse_entities("이부프로펜 먹는데 술을 마셨어요", known_entities)
normalized = normalize_entities(parsed)

# 주입: 관절염 상태
normalized.setdefault("situations", []).append({
    "raw": "관절염", "canonical": "관절염", "entity_id": "CONDITION_arthritis"
})
# 주입: 동시 매칭 상황어 
normalized.setdefault("situations", []).append({"raw": "동시", "canonical": "동시복용", "entity_id": "SITUATION_CONCURRENT"})

print(f"파싱 결과: drugs={[d['entity_id'] for d in normalized.get('drugs',[])]} foods={[f['entity_id'] for f in normalized.get('foods',[])]}")

ruleset = load_ruleset()
matched = evaluate_rules(normalized, ruleset["rules"])
result = assess_risk(normalized, matched)

print(f"매칭 결과:")
print(f"  - 최종 위험도: {result['risk_level']}")
print(f"  - 대표 규칙(Representative): {result['representative_rule']}")
for ev in result['evidence_info']:
    print("\n--- 근거 데이터 ---")
    print(f"  - 근거 ID: {ev.get('evidence_id')}")
    print(f"  - 출처 라벨: {ev.get('evidence_source_label')}")
    print(f"  - 근거 강도: {ev.get('evidence_strength')}")
    print(f"  - 사용자 요약: {ev.get('evidence_summary_user')}")
    print(f"  - 태그: {ev.get('evidence_tags')}")
print("\nDone!")
