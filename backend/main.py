import sys
import json
from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from src.service.risk_assessor import assess_risk
from src.pipeline.explanation_pipeline import run_explanation
from src.ocr.processor import extract_text_from_image

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

def build_known_entities_from_index(entity_index):
    """parser용 표면어 사전 생성"""
    return {entity_type: list(entity_index[entity_type].keys()) for entity_type in entity_index}

def analyze_text(raw_text):
    """
    MVP 서비스 파이프라인: Text -> Parsing -> Risk Assessment -> Explanation
    """
    # 1. 데이터 로딩 (실제 서비스에서는 캐싱 필요)
    ruleset = load_ruleset()
    rules = ruleset["rules"]
    entity_index = load_entity_index()
    known_entities = build_known_entities_from_index(entity_index)

    # 2. 엔티티 파싱 및 정규화
    parsed_entities = parse_entities(raw_text, known_entities)
    normalized_entities = normalize_entities(parsed_entities)

    # 3. 상황 추론 (복합 상황 자동 인식)
    # 3.1 병용 섭취 (Multiple Drugs or Drug+Food)
    has_multiple_drugs = len(normalized_entities.get("drugs", [])) >= 2
    has_drug_and_food = normalized_entities.get("drugs") and normalized_entities.get("foods")
    
    if has_multiple_drugs or has_drug_and_food:
        normalized_entities.setdefault("situations", []).append({
            "raw": "병용",
            "canonical": "병용 섭취",
            "entity_id": "SITUATION_CONCURRENT"
        })

    # 3.2 공복 음주 (Fasting + Alcohol)
    food_ids = [f['entity_id'] for f in normalized_entities.get('foods', [])]
    situation_ids = [s['entity_id'] for s in normalized_entities.get('situations', [])]
    
    if 'FOOD_ALCOHOL' in food_ids and 'SITUATION_FASTING' in situation_ids:
        normalized_entities['situations'].append({
            "raw": "공복 음주",
            "canonical": "공복 상태에서 음주",
            "entity_id": "SITUATION_FASTING_ALCOHOL"
        })

    # 4. 룰 평가
    matched_rules = evaluate_rules(normalized_entities, rules)

    # 5. 위험도 판단
    risk_result = assess_risk(normalized_entities, matched_rules)
    
    # [추가] LLM 프롬프트 구성을 위해 input_text 추가
    risk_result["input_text"] = raw_text

    # 6. 설명 생성 (RAG/LLM)
    explanation = run_explanation(risk_result)

    return {
        "input_text": raw_text,
        "risk_result": risk_result,
        "explanation": explanation,
        "debug_info": {
            "entities": normalized_entities,
            "matched_rules": matched_rules
        }
    }

def analyze_image(image_path: str):
    """
    [향후 확장용] 이미지 파일에서 정보를 추출하여 분석 파이프라인을 실행합니다.
    
    1. OCR 엔진 호출 (이미지 -> 텍스트 변환)
    2. 추출된 텍스트를 analyze_text()에 전달
    """
    # 1. OCR을 통한 텍스트 추출
    extracted_text = extract_text_from_image(image_path)
    
    # 2. 분석 파이프라인 실행
    if not extracted_text:
        return {
            "error": "OCR 인식 결과가 없거나 이미지를 처리할 수 없습니다.",
            "status": "FAIL"
        }
        
    return analyze_text(extracted_text)

def main():
    # Windows 한글 출력 깨짐 방지
    sys.stdout.reconfigure(encoding='utf-8')

    print("============================================================")
    print(" 세이프잇 (SafeEat) - AI Food-Medication Guardrail MVP")
    print("============================================================")

    for scenario in MVP_SCENARIOS:
        print(f"\n\n[SCENARIO] {scenario['id']} - {scenario['title']}")
        print(f"Input: {scenario['input']}")
        print("-" * 60)

        # 서비스 분석 호촐
        result = analyze_text(scenario["input"])

        # 결과 출력
        print(f"Risk Level: {result['risk_result']['risk_level']}")
        print("\n[EXPLANATION]")
        print(result['explanation'])
        
        print("\n[DEBUG: DETAILED RESULT]")
        # 덤프 시 한글 깨짐 방지
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)

if __name__ == "__main__":
    main()
