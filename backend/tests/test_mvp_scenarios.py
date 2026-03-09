"""
SafeEat MVP 시나리오 E2E 테스트 스크립트
- LLM 설명 생성(OpenAI API)을 건너뛰고
  파싱 → 규칙 매칭 → 위험도 판정 핵심 파이프라인만 검증합니다
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from src.service.risk_assessor import assess_risk

PASS = "[PASS]"
FAIL = "[FAIL]"

LABEL_TO_ID = {
    "고령": "elderly", "고혈압": "hypertension", "당뇨": "diabetes",
    "고지혈증": "hyperlipidemia", "관절염": "arthritis", "천식": "asthma"
}


def _run_core(input_text, user_meds=None, user_conditions=None):
    """LLM 없이 규칙 매칭 + 위험도만 반환"""
    ruleset = load_ruleset()
    rules = ruleset["rules"]
    entity_index = load_entity_index()
    known_entities = {etype: list(entity_index[etype].keys()) for etype in entity_index}

    parsed = parse_entities(input_text, known_entities)
    normalized = normalize_entities(parsed)

    if user_meds:
        for med in user_meds:
            med_norm = normalize_entities(parse_entities(med, known_entities))
            if med_norm.get("drugs"):
                existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
                for d in med_norm["drugs"]:
                    if d["entity_id"] not in existing_ids:
                        normalized.setdefault("drugs", []).append(d)
            else:
                normalized.setdefault("drugs", []).append({"raw": med, "entity_id": "DRUG_UNKNOWN"})
    # 사용자 인풋에서 직접 상황어 매칭 (공복, 식전 등)
    input_norm = input_text.replace(" ", "")
    if "공복" in input_norm or "밥안먹고" in input_norm or "식사안하고" in input_norm or "밥못먹고" in input_norm or "식사를거르" in input_norm or "밥거르" in input_norm:
        normalized.setdefault("situations", []).append({
            "raw": "공복", "canonical": "공복 복용", "entity_id": "SITUATION_FASTING"
        })
    if "사우나" in input_norm or "땀많이" in input_norm or "더웠어" in input_norm:
        normalized.setdefault("situations", []).append({
            "raw": "탈수", "canonical": "탈수/수분부족", "entity_id": "SITUATION_DEHYDRATION"
        })

    # 사용자 질환 주입
    if user_conditions:
        for cond in user_conditions:
            cid = LABEL_TO_ID.get(cond, cond)
            normalized.setdefault("situations", []).append({
                "raw": cond, "canonical": cond, "entity_id": f"CONDITION_{cid}"
            })

    has_multi = len(normalized.get("drugs", [])) >= 2
    has_drug_food = normalized.get("drugs") and normalized.get("foods")
    if has_multi or has_drug_food or len(normalized.get("drugs", [])) > 0 or len(normalized.get("foods", [])) > 0:
        # 단일 약물/식품이라도 질환이나 특정 상황(탈수 등)과 매칭을 위해 병용 상황어 임의 주입
        normalized.setdefault("situations", []).append({"raw": "병용", "canonical": "병용 섭취", "entity_id": "SITUATION_CONCURRENT"})
    if has_multi:
        normalized.setdefault("situations", []).append({"raw": "약물 병용", "canonical": "여러 약물", "entity_id": "SITUATION_DRUG_DUPLICATION"})

    food_ids = [f["entity_id"] for f in normalized.get("foods", [])]
    situ_ids = [s["entity_id"] for s in normalized.get("situations", [])]
    if "FOOD_ALCOHOL" in food_ids and "SITUATION_FASTING" in situ_ids:
        normalized["situations"].append({"raw": "공복 음주", "canonical": "공복 음주", "entity_id": "SITUATION_FASTING_ALCOHOL"})

    # print(f"\n[DEBUG] Input: {input_text}")
    # print(f"  Drugs: {[d['entity_id'] for d in normalized.get('drugs', [])]}")
    # print(f"  Foods: {food_ids}")
    # print(f"  Situations: {situ_ids}")

    matched_rules = evaluate_rules(normalized, rules)
    risk_result = assess_risk(normalized, matched_rules)
    return risk_result["risk_level"], [r["rule_id"] for r in matched_rules]


TEST_CASES = [
    # 1. NSAID + Alcohol (RED)
    {"id": "T01", "group": "1-NSAID_ALC", "desc": "이부프로펜 + 술", "input": "이부프로펜 먹고 술 마셔도 되나요", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
    {"id": "T02", "group": "1-NSAID_ALC", "desc": "나프록센 + 맥주", "input": "나프록센 먹었는데 맥주 마셔도 되나요", "meds": ["나프록센"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
    {"id": "T03", "group": "1-NSAID_ALC", "desc": "진통제 + 소주", "input": "진통제 먹고 소주 마셔도 되나요", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
    {"id": "T04", "group": "1-NSAID_ALC", "desc": "이부프로펜 + 술(의문)", "input": "이부프로펜 복용 중 술 마시면 안되나요", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
    {"id": "T05", "group": "1-NSAID_ALC", "desc": "나프록센 + 와인", "input": "나프록센 먹고 와인 마셔도 되나요", "meds": ["나프록센"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},

    # 2. ACE/ARB + 고칼륨 식품 (YELLOW)
    {"id": "T06", "group": "2-HTN_K_FOOD", "desc": "로사르탄 + 바나나", "input": "로사르탄 먹는데 바나나 먹어도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T07", "group": "2-HTN_K_FOOD", "desc": "엔알라프릴 + 토마토", "input": "엔알라프릴 복용 중 토마토 먹어도 되나요", "meds": ["엔알라프릴"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T08", "group": "2-HTN_K_FOOD", "desc": "로사르탄 + 감자", "input": "혈압약 로사르탄 먹는데 감자 괜찮나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T09", "group": "2-HTN_K_FOOD", "desc": "엔알라프릴 + 오렌지", "input": "엔알라프릴 먹고 오렌지 먹어도 되나요", "meds": ["엔알라프릴"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T10", "group": "2-HTN_K_FOOD", "desc": "로사르탄 + 코코넛워터", "input": "로사르탄 복용 중 코코넛워터 마셔도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},

    # 3. ACE/ARB + 칼륨 보충제 (RED)
    {"id": "T11", "group": "3-HTN_K_SUPP", "desc": "엔알라프릴 + 칼륨 보충제", "input": "엔알라프릴 먹는데 칼륨 보충제 먹어도 되나요", "meds": ["엔알라프릴"], "conditions": ["고혈압"], "expected_risk": "RED", "expected_rule": "HTN_002"},
    {"id": "T12", "group": "3-HTN_K_SUPP", "desc": "혈압약 + 칼륨 소금", "input": "혈압약 먹는데 칼륨 소금 써도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "RED", "expected_rule": "HTN_002"},
    {"id": "T13", "group": "3-HTN_K_SUPP", "desc": "엔알라프릴 + KCl", "input": "엔알라프릴 복용 중 KCl 보충제 먹어도 되나요", "meds": ["엔알라프릴"], "conditions": ["고혈압"], "expected_risk": "RED", "expected_rule": "HTN_002"},

    # 4. CCB + 자몽 (YELLOW)
    {"id": "T14", "group": "4-HTN_GRAPEFRUIT", "desc": "암로디핀 + 자몽", "input": "암로디핀 먹는데 자몽 먹어도 되나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T15", "group": "4-HTN_GRAPEFRUIT", "desc": "암로디핀 + 자몽주스", "input": "혈압약 암로디핀 복용 중 자몽주스 괜찮나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T16", "group": "4-HTN_GRAPEFRUIT", "desc": "암로디핀 + 자몽청", "input": "암로디핀 먹는데 자몽청 마셔도 되나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T17", "group": "4-HTN_GRAPEFRUIT", "desc": "암로디핀 + 자몽 캔디", "input": "암로디핀 복용 중 자몽 캔디 먹어도 되나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T18", "group": "4-HTN_GRAPEFRUIT", "desc": "혈압약 + 자몽주스", "input": "혈압약 먹고 자몽주스 마셔도 되나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},

    # 5. 고혈압 + 충혈제거제 (YELLOW)
    {"id": "T19", "group": "5-HTN_DECONG", "desc": "고혈압 + 슈도에페드린", "input": "고혈압인데 슈도에페드린 먹어도 되나요", "meds": [], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_004"},
    {"id": "T20", "group": "5-HTN_DECONG", "desc": "혈압약 + 페닐에프린", "input": "혈압약 먹는데 페닐에프린 들어간 감기약 먹어도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_004"},
    {"id": "T21", "group": "5-HTN_DECONG", "desc": "슈도에페드린 + 고혈압", "input": "코막힘약 슈도에페드린 먹어도 되나요 고혈압입니다", "meds": [], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_004"},
    {"id": "T22", "group": "5-HTN_DECONG", "desc": "혈압약 + 충혈제거제", "input": "혈압약 복용 중 충혈제거제 써도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_004"},

    # 6. 고혈압 + NSAID (YELLOW)
    {"id": "T23", "group": "6-HTN_NSAID", "desc": "혈압약 + 이부프로펜", "input": "혈압약 먹는데 이부프로펜 같이 먹어도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_005"},
    {"id": "T24", "group": "6-HTN_NSAID", "desc": "고혈압 + 나프록센", "input": "고혈압인데 나프록센 먹어도 되나요", "meds": [], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_005"},
    {"id": "T25", "group": "6-HTN_NSAID", "desc": "혈압약 + NSAID", "input": "혈압약 복용 중 NSAID 진통제 먹어도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_005"},
    {"id": "T26", "group": "6-HTN_NSAID", "desc": "혈압약 + 이부프로펜(중복)", "input": "혈압약 먹는데 진통제 이부프로펜 괜찮나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_005"},

    # 7. 이뇨제 + 감초 (YELLOW)
    {"id": "T27", "group": "7-DIURETIC_LICORICE", "desc": "이뇨제 + 감초차", "input": "이뇨제 먹는데 감초차 마셔도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_006"},
    {"id": "T28", "group": "7-DIURETIC_LICORICE", "desc": "이뇨제 + 감초캔디", "input": "혈압약 이뇨제 복용 중 감초캔디 먹어도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_006"},
    {"id": "T29", "group": "7-DIURETIC_LICORICE", "desc": "히드로크로로티아지드 + 감초", "input": "히드로클로로티아지드 먹는데 감초 괜찮나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_006"},
    {"id": "T30", "group": "7-DIURETIC_LICORICE", "desc": "이뇨제 + 한약 감초", "input": "이뇨제 먹는데 한약 감초 들어있어도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_006"},

    # 8. 이뇨제 + 탈수 (YELLOW)
    {"id": "T31", "group": "8-DIURETIC_DEHYD", "desc": "이뇨제 + 사우나", "input": "이뇨제 먹는데 사우나 가도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_007"},
    {"id": "T32", "group": "8-DIURETIC_DEHYD", "desc": "이뇨제 + 탈수 위험", "input": "이뇨제 복용 중 탈수되면 위험한가요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_007"},
    {"id": "T33", "group": "8-DIURETIC_DEHYD", "desc": "이뇨제 + 수분부족", "input": "혈압약 이뇨제 먹는데 물 많이 안 마셔도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_007"},
    {"id": "T34", "group": "8-DIURETIC_DEHYD", "desc": "이뇨제 + 땀/운동", "input": "이뇨제 먹는데 운동하고 땀 많이 흘려도 되나요", "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_007"},

    # 9. 당뇨 + 식사 거름 (YELLOW)
    {"id": "T35", "group": "9-DM_FASTING", "desc": "당뇨약 + 식사 안함", "input": "당뇨약 먹었는데 식사 안 했어요 괜찮나요", "meds": ["메트포르민"], "conditions": ["당뇨"], "expected_risk": "YELLOW", "expected_rule": "DM_ALL_MEAL_SKIP_YELLOW"},
    {"id": "T36", "group": "9-DM_FASTING", "desc": "당뇨약 + 밥 안먹음", "input": "당뇨약 먹고 밥 안 먹으면 위험한가요", "meds": ["메트포르민"], "conditions": ["당뇨"], "expected_risk": "YELLOW", "expected_rule": "DM_ALL_MEAL_SKIP_YELLOW"},
    {"id": "T37", "group": "9-DM_FASTING", "desc": "당뇨약 + 공복 상태", "input": "당뇨약 복용 후 공복 상태인데 괜찮나요", "meds": ["메트포르민"], "conditions": ["당뇨"], "expected_risk": "YELLOW", "expected_rule": "DM_ALL_MEAL_SKIP_YELLOW"},
    {"id": "T38", "group": "9-DM_FASTING", "desc": "공복 + 당뇨약", "input": "식사 안 하고 당뇨약 먹었어요", "meds": ["메트포르민"], "conditions": ["당뇨"], "expected_risk": "YELLOW", "expected_rule": "DM_ALL_MEAL_SKIP_YELLOW"},

    # 10. 정상 케이스 (GREEN)
    {"id": "T39", "group": "10-SAFE", "desc": "타이레놀 + 물", "input": "타이레놀 먹고 물 마셔도 되나요", "meds": ["타이레놀"], "conditions": [], "expected_risk": "GREEN", "expected_rule": "NONE"},
    {"id": "T40", "group": "10-SAFE", "desc": "혈압약 + 밥", "input": "혈압약 먹고 밥 먹어도 되나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "GREEN", "expected_rule": "NONE"},
    {"id": "T41", "group": "10-SAFE", "desc": "약 + 우유", "input": "약 먹고 우유 마셔도 되나요", "meds": ["타이레놀"], "conditions": [], "expected_risk": "GREEN", "expected_rule": "NONE"},
    {"id": "T42", "group": "10-SAFE", "desc": "감기약 + 물", "input": "감기약 먹고 물 마셔도 되나요", "meds": ["감기약"], "conditions": [], "expected_risk": "GREEN", "expected_rule": "NONE"},
    {"id": "T43", "group": "10-SAFE", "desc": "약 + 취명", "input": "약 먹고 잠자도 되나요", "meds": ["타이레놀"], "conditions": [], "expected_risk": "GREEN", "expected_rule": "NONE"},

    # 11. OCR 오류 / 오타 (Fuzzy Matching check)
    {"id": "T44", "group": "11-OCR_ERROR", "desc": "이부프로팬(오타) + 술", "input": "이부프로팬 먹고 술 마셔도 되나요", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
    {"id": "T45", "group": "11-OCR_ERROR", "desc": "암로디핀정(접미사) + 자몽", "input": "암로디핀정 먹는데 자몽주스 괜찮나요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T46", "group": "11-OCR_ERROR", "desc": "로사르탄정(접미사) + 바나나", "input": "로사르탄정 먹는데 바나나 괜찮나요", "meds": ["로사르탄"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T47", "group": "11-OCR_ERROR", "desc": "엔알라프릴정(접미사) + 토마토", "input": "엔알라프릴정 먹는데 토마토 먹어도 되나요", "meds": ["엔알라프릴"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_001"},
    {"id": "T48", "group": "11-OCR_ERROR", "desc": "이부프로펜정(접미사) + 맥주", "input": "이부프로펜정 먹고 맥주 마셔도 되나요", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},

    # 12. 동의어 / 자연어 변형
    {"id": "T49", "group": "12-SYNONYM", "desc": "혈압약(포괄) + 자몽", "input": "혈압약 먹는데 자몽 괜찮을까요", "meds": ["암로디핀"], "conditions": ["고혈압"], "expected_risk": "YELLOW", "expected_rule": "HTN_003"},
    {"id": "T50", "group": "12-SYNONYM", "desc": "진통제(포괄) + 술", "input": "진통제 복용 중 술 마셔도 되는지 궁금합니다", "meds": ["이부프로펜"], "conditions": ["관절염"], "expected_risk": "RED", "expected_rule": "NSAID_ALL_ALCOHOL"},
]


def run_tests():
    results = []
    print("=" * 70)
    print("  SafeEat MVP E2E 테스트 (규칙 매칭 + 위험도 판정 only, 속도 빠름)")
    print("=" * 70)

    current_group = None
    for tc in TEST_CASES:
        if tc["group"] != current_group:
            current_group = tc["group"]
            print(f"\n[{current_group}]")

        try:
            actual_risk, matched_ids = _run_core(tc["input"], tc["meds"], tc["conditions"])
            risk_ok = actual_risk == tc["expected_risk"]
            
            if tc["expected_rule"] == "NONE":
                rule_ok = len(matched_ids) == 0
            else:
                rule_ok = tc["expected_rule"] in matched_ids
            
            status = PASS if (risk_ok and rule_ok) else FAIL

            # print(f"  {status} {tc['id']}: {tc['desc']}")
            # if status == FAIL:
            #     print(f"         기대  위험도: {tc['expected_risk']}  규칙: {tc['expected_rule']}")
            #     print(f"         실제  위험도: {actual_risk}  매칭된 규칙: {matched_ids}")

            results.append({"id": tc["id"], "status": status,
                             "actual_risk": actual_risk, "matched_rules": matched_ids,
                             "input": tc["input"], "expected_risk": tc["expected_risk"], "expected_rule": tc["expected_rule"]})
        except Exception as e:
            # print(f"  [-] ERROR {tc['id']}: {str(e)}")
            results.append({"id": tc["id"], "status": "ERROR", "error": str(e)})

    total = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    
    # Save to JSON for robust debugging
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"  총 {total}개 중 {passed}개 통과")
    print("  상세 결과는 test_results.json을 확인하세요.")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_tests()
