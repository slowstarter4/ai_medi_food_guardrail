"""
SafeEat MVP 시나리오 E2E 테스트 스크립트
- LLM 설명 생성(OpenAI API)을 건너뛰고
  파싱 → 규칙 매칭 → 위험도 판정 핵심 파이프라인만 검증합니다
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from src.service.risk_assessor import assess_risk

PASS = "✅ PASS"
FAIL = "❌ FAIL"

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

    if user_conditions:
        for cond in user_conditions:
            cid = LABEL_TO_ID.get(cond, cond)
            normalized.setdefault("situations", []).append({
                "raw": cond, "canonical": cond, "entity_id": f"CONDITION_{cid}"
            })

    has_multi = len(normalized.get("drugs", [])) >= 2
    has_drug_food = normalized.get("drugs") and normalized.get("foods")
    if has_multi or has_drug_food:
        normalized.setdefault("situations", []).append({"raw": "병용", "canonical": "병용 섭취", "entity_id": "SITUATION_CONCURRENT"})
    if has_multi:
        normalized.setdefault("situations", []).append({"raw": "약물 병용", "canonical": "여러 약물", "entity_id": "SITUATION_DRUG_DUPLICATION"})

    food_ids = [f["entity_id"] for f in normalized.get("foods", [])]
    situ_ids = [s["entity_id"] for s in normalized.get("situations", [])]
    if "FOOD_ALCOHOL" in food_ids and "SITUATION_FASTING" in situ_ids:
        normalized["situations"].append({"raw": "공복 음주", "canonical": "공복 음주", "entity_id": "SITUATION_FASTING_ALCOHOL"})

    matched_rules = evaluate_rules(normalized, rules)
    risk_result = assess_risk(normalized, matched_rules)
    return risk_result["risk_level"], [r["rule_id"] for r in matched_rules]


TEST_CASES = [
    # [A] HTN
    {"id": "HTN_003", "group": "A-HTN", "desc": "암로디핀 + 자몽주스",
     "input": "암로디핀 복용 중에 자몽주스를 마셨어요",
     "meds": ["암로디핀"], "conditions": ["고혈압"],
     "expected_risk": "YELLOW", "expected_rule": "HTN_003"},

    {"id": "HTN_004", "group": "A-HTN", "desc": "혈압약 + 감기약(충혈제거제)",
     "input": "고혈압 약 먹고 있는데 코막힘 심해서 감기약 먹어도 되나요?",
     "meds": ["로사르탄", "감기약"], "conditions": ["고혈압"],
     "expected_risk": "YELLOW", "expected_rule": "HTN_004"},

    {"id": "HTN_005", "group": "A-HTN", "desc": "혈압약 + 이부프로펜 병용",
     "input": "고혈압약이랑 이부프로펜을 같이 먹고 있어요",
     "meds": ["로사르탄", "이부프로펜"], "conditions": ["고혈압"],
     "expected_risk": "YELLOW", "expected_rule": "HTN_005"},

    {"id": "HTN_006", "group": "A-HTN", "desc": "이뇨제 + 감초",
     "input": "이뇨제 먹는데 감초사탕 먹어도 돼요?",
     "meds": ["히드로크로로티아지드"], "conditions": ["고혈압"],
     "expected_risk": "YELLOW", "expected_rule": "HTN_006"},

    {"id": "HTN_007", "group": "A-HTN", "desc": "탈수 상황 AND 조건",
     "input": "사우나 다녀왔는데 혈압약 먹어도 돼요?",
     "meds": ["암로디핀"], "conditions": ["고혈압"],
     "expected_risk": "YELLOW", "expected_rule": "HTN_007"},

    # [B] DM
    {"id": "DM_001", "group": "B-DM", "desc": "당뇨약 + 공복 음주",
     "input": "아침 식사 안 하고 소주 한잔 했는데 당뇨약 먹어도 되나요?",
     "meds": ["메트포르민"], "conditions": ["당뇨"],
     "expected_risk": "RED", "expected_rule": "DM_001"},

    {"id": "DM_003", "group": "B-DM", "desc": "메트포르민 + 과도한 음주",
     "input": "메트포르민 복용 중인데 어제 술을 많이 마셨어요",
     "meds": ["메트포르민"], "conditions": ["당뇨"],
     "expected_risk": "RED", "expected_rule": "DM_003"},

    {"id": "DM_006", "group": "B-DM", "desc": "설폰요소제 + 공복 음주",
     "input": "밥 거르고 소주 마셨는데 글리메피리드 먹어도 되나요?",
     "meds": ["글리메피리드"], "conditions": ["당뇨"],
     "expected_risk": "RED", "expected_rule": "DM_006"},

    {"id": "DM_004", "group": "B-DM", "desc": "공복 복용 단독",
     "input": "아침 밥 못 먹고 당뇨약을 복용했어요",
     "meds": ["메트포르민"], "conditions": ["당뇨"],
     "expected_risk": "YELLOW", "expected_rule": "DM_004"},

    # [C] NSAID
    {"id": "NSAID_001", "group": "C-NSAID", "desc": "이부프로펜 + 알코올 (단일 약물)",
     "input": "이부프로펜 먹고 소주 마셔도 괜찮아요?",
     "meds": ["이부프로펜"], "conditions": [],
     "expected_risk": "RED", "expected_rule": "NSAID_001"},

    {"id": "NSAID_002", "group": "C-NSAID", "desc": "진통제 공복 복용",
     "input": "밥 안 먹고 이부프로펜 먹었어요",
     "meds": ["이부프로펜"], "conditions": [],
     "expected_risk": "YELLOW", "expected_rule": "NSAID_002"},

    {"id": "NSAID_003", "group": "C-NSAID", "desc": "이부프로펜 + 나프록센 중복",
     "input": "이부프로펜 먹고 있는데 나프록센도 같이 먹어도 되나요?",
     "meds": ["이부프로펜", "나프록센"], "conditions": [],
     "expected_risk": "RED", "expected_rule": "NSAID_003"},

    {"id": "NSAID_005", "group": "C-NSAID", "desc": "이부프로펜 + 와파린 병용",
     "input": "와파린 먹는데 이부프로펜을 같이 먹어도 될까요?",
     "meds": ["이부프로펜", "와파린"], "conditions": [],
     "expected_risk": "RED", "expected_rule": "NSAID_005"},
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
            rule_ok = tc["expected_rule"] in matched_ids
            status = PASS if (risk_ok and rule_ok) else FAIL

            print(f"  {status} {tc['id']}: {tc['desc']}")
            if status == FAIL:
                print(f"         기대  위험도: {tc['expected_risk']}  규칙: {tc['expected_rule']}")
                print(f"         실제  위험도: {actual_risk}  매칭된 규칙: {matched_ids}")

            results.append({"id": tc["id"], "status": status,
                             "actual_risk": actual_risk, "matched_rules": matched_ids})
        except Exception as e:
            print(f"  ❌ ERROR {tc['id']}: {str(e)}")
            results.append({"id": tc["id"], "status": "❌ ERROR", "error": str(e)})

    total = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    print("\n" + "=" * 70)
    print(f"  결과: {passed} / {total} 통과 {'🎉' if passed == total else '⚠️ 일부 실패'}")
    print("=" * 70)
    return results


if __name__ == "__main__":
    run_tests()
