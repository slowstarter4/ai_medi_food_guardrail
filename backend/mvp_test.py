import sys
import json
from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from src.service.risk_assessor import assess_risk

def build_known_entities_from_index(entity_index):
    """parser용 표면어 사전 생성"""
    return {entity_type: list(entity_index[entity_type].keys()) for entity_type in entity_index}

# MVP 페르소나 기반 시나리오
MVP_SCENARIOS = [
    # 페르소나 1: 김영순 여사 - RED 케이스
    {
        "id": "MVP_RED_01",
        "title": "당뇨약 공복 음주",
        "input": "아침 식사 안 하고 소주 한잔 했는데 당뇨약 먹어도 되나요?",
        "expected_risk": "RED",
        "expected_evidence": "RED_DM_HYPOGLYCEMIA"
    },
    {
        "id": "MVP_RED_02",
        "title": "진통제 중복 + 알코올",
        "input": "이부프로펜 먹고 나프록센도 먹었는데 술 마셔도 돼요?",
        "expected_risk": "RED",
        "expected_evidence": "RED_NSAID_DUPLICATION"
    },
    {
        "id": "MVP_RED_03",
        "title": "NSAIDs 중복 복용",
        "input": "이부프로펜 먹고 있는데 나프록센도 같이 먹어도 되나요?",
        "expected_risk": "RED",
        "expected_evidence": "RED_NSAID_DUPLICATION"
    },
    
    # 페르소나 1: 김영순 여사 - YELLOW 케이스
    {
        "id": "MVP_YELLOW_01",
        "title": "고혈압약 + 바나나",
        "input": "로사르탄 먹는데 바나나 먹어도 괜찮을까요?",
        "expected_risk": "YELLOW",
        "expected_evidence": "YELLOW_HTN_POTASSIUM"
    },
    {
        "id": "MVP_YELLOW_02",
        "title": "혈압약 + 감기약",
        "input": "고혈압약 먹고 있는데 코막힘 심해서 감기약 먹어도 돼요?",
        "expected_risk": "YELLOW",
        "expected_evidence": "YELLOW_HTN_DECONGESTANT"
    },
    {
        "id": "MVP_YELLOW_03",
        "title": "암로디핀 + 자몽",
        "input": "암로디핀 복용 중 자몽주스를 마셨습니다",
        "expected_risk": "YELLOW",
        "expected_evidence": "YELLOW_HTN_GRAPEFRUIT"
    },
    
    # 페르소나 2: 최지연 팀장(보호자)
    {
        "id": "MVP_GUARD_01",
        "title": "보호자 원격 확인 - 자몽",
        "input": "어머니가 혈압약 드시는데 자몽청 드셔도 괜찮을까요?",
        "expected_risk": "YELLOW",
        "expected_evidence": "YELLOW_HTN_GRAPEFRUIT"
    },
    {
        "id": "MVP_GUARD_02",
        "title": "보호자 원격 확인 - 감초",
        "input": "이뇨제 드시는데 감초캔디 드셔도 될까요?",
        "expected_risk": "YELLOW",
        "expected_evidence": "YELLOW_HTN_LICORICE"
    },
]

def test_mvp_scenario(scenario, entity_index, rules):
    """단일 MVP 시나리오 테스트"""
    print(f"\n{'='*70}")
    print(f"[{scenario['id']}] {scenario['title']}")
    print(f"Input: {scenario['input']}")
    print('='*70)
    
    # Entity 파싱 및 정규화
    known_entities = build_known_entities_from_index(entity_index)
    parsed_entities = parse_entities(scenario["input"], known_entities)
    normalized_entities = normalize_entities(parsed_entities)
    
    # 상황 자동 추가
    if normalized_entities.get("drugs") and normalized_entities.get("foods"):
        normalized_entities.setdefault("situations", []).append({
            "raw": "병용",
            "canonical": "병용 섭취",
            "entity_id": "SITUATION_CONCURRENT"
        })
    
    # Entities 출력
    print(f"\n[ENTITIES]")
    for d in normalized_entities.get("drugs", []):
        print(f"  - Drug: {d['raw']} → {d['entity_id']}")
    for f in normalized_entities.get("foods", []):
        print(f"  - Food: {f['raw']} → {f['entity_id']}")
    for s in normalized_entities.get("situations", []):
        print(f"  - Situation: {s['canonical']} → {s['entity_id']}")
    
    # 룰 평가
    matched_rules = evaluate_rules(normalized_entities, rules)
    
    # 위험도 판단
    result = assess_risk(normalized_entities, matched_rules)
    
    # 매칭된 룰 출력
    print(f"\n[MATCHED RULES] ({len(matched_rules)})")
    for r in matched_rules:
        print(f"  - {r['rule_id']} | {r['risk_level_hint']} | {r.get('evidence_key')}")
    
    # 결과 확인
    print(f"\n[RESULT]")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Evidence Keys: {result.get('evidence_keys', [])}")
    
    # 검증
    test_passed = True
    if scenario.get("expected_risk"):
        if result['risk_level'] == scenario['expected_risk']:
            print(f"  ✓ Risk level matches expected: {scenario['expected_risk']}")
        else:
            print(f"  ✗ Risk level MISMATCH! Expected: {scenario['expected_risk']}, Got: {result['risk_level']}")
            test_passed = False
    
    if scenario.get("expected_evidence"):
        if scenario['expected_evidence'] in result.get('evidence_keys', []):
            print(f"  ✓ Evidence found: {scenario['expected_evidence']}")
        else:
            print(f"  ✗ Evidence MISSING! Expected: {scenario['expected_evidence']}")
            test_passed = False
    
    # Evidence 정보 출력
    if result.get("evidence_info"):
        print(f"\n[EVIDENCE INFO]")
        print(json.dumps(result["evidence_info"], ensure_ascii=False, indent=2))
    
    return test_passed


# [추가] main.py의 analyze_text 재사용 (코드 중복 제거 및 일관성 유지)
from main import analyze_text

def main():
    """MVP 시나리오 전체 테스트"""
    # Windows 한글 출력 깨짐 방지
    sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "="*70)
    print(" MVP 페르소나 기반 시스템 테스트 (LLM 설명 포함)")
    print("="*70)
    
    # 모든 시나리오 테스트
    test_summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "results": []
    }
    
    for scenario in MVP_SCENARIOS:
        print(f"\n[TEST] {scenario['id']} - {scenario['title']}")
        
        # 통합 분석 파이프라인 호출
        try:
            result = analyze_text(scenario["input"])
            risk_result = result["risk_result"]
            explanation = result["explanation"]
            
            # 검증 로직
            passed = True
            failure_reasons = []
            
            # 1. Risk Level 검증
            if scenario.get("expected_risk"):
                if risk_result['risk_level'] != scenario['expected_risk']:
                    passed = False
                    failure_reasons.append(f"Risk mismatch: expected {scenario['expected_risk']}, got {risk_result['risk_level']}")
            
            # 2. Evidence Key 검증
            if scenario.get("expected_evidence"):
                if scenario['expected_evidence'] not in risk_result.get('evidence_keys', []):
                    passed = False
                    failure_reasons.append(f"Evidence missing: expected {scenario['expected_evidence']}")

            # 결과 집계
            test_summary["total"] += 1
            if passed:
                test_summary["passed"] += 1
                print("  ✓ PASS")
            else:
                test_summary["failed"] += 1
                print(f"  ✗ FAIL: {', '.join(failure_reasons)}")
            
            # LLM 설명 출력 (검증용)
            print(f"  [Explanation]: {explanation[:100]}...") 

            test_summary["results"].append({
                "id": scenario["id"],
                "title": scenario["title"],
                "passed": passed,
                "failure_reasons": failure_reasons,
                "risk_level": risk_result["risk_level"],
                "explanation": explanation,  # LLM 설명 저장
                "evidence_keys": risk_result.get("evidence_keys", [])
            })

        except Exception as e:
            test_summary["total"] += 1
            test_summary["failed"] += 1
            print(f"  ✗ ERROR: {str(e)}")
            test_summary["results"].append({
                "id": scenario["id"],
                "error": str(e),
                "passed": False
            })

    # 결과 저장
    with open("mvp_test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_summary, f, ensure_ascii=False, indent=2)
        
    print(f"\nTest Completed. Passed: {test_summary['passed']}/{test_summary['total']}")
    print("Full results saved to mvp_test_results.json")

if __name__ == "__main__":
    main()
