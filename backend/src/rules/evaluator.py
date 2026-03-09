import re
from typing import Dict, List

# 약물 ID -> 계열 매핑 (룰 엔진 v2 필수 데이터)
ID_TO_CATEGORY = {
    "DRUG_LOSARTAN": "ACE/ARB",
    "DRUG_ENALAPRIL": "ACE/ARB",
    "DRUG_ACE_ARB": "ACE/ARB",
    "DRUG_AMLODIPINE": "CCB",
    "DRUG_CCB": "CCB",
    "DRUG_HYDROCHLOROTHIAZIDE": "이뇨제",
    "DRUG_DIURETIC_LOOP": "이뇨제",
    "DRUG_SPIRONOLACTONE": "이뇨제",
    "DRUG_SULFONYLUREA": "설폰요소제",
    "DRUG_METFORMIN": "비구아나이드",
    "DRUG_DAPAGLIFLOZIN": "SGLT2",
    "DRUG_EMPAGLIFLOZIN": "SGLT2",
    "DRUG_SGLT2": "SGLT2",
    "DRUG_IBUPROFEN": "NSAIDs",
    "DRUG_NAPROXEN": "NSAIDs",
    "DRUG_NSAID": "NSAIDs",
    # Generic mappings for categorical terms
    "DRUG_HYPERTENSION_GENERIC": "ACE/ARB|CCB|이뇨제",
    "DRUG_DIABETES_GENERIC": "비구아나이드|설폰요소제|SGLT2",
    "DRUG_DIURETIC_GENERIC": "이뇨제",
    "DRUG_PAINKILLER_GENERIC": "NSAIDs"
}

def evaluate_rules(entities: Dict, rules: List[Dict]) -> List[Dict]:
    """
    ruleset v2.0 매칭 엔진
    - drug_category: ALL 또는 특정 계열 매칭
    - drug_name: ALL 또는 Regex 매칭
    - food_keyword_match: Regex 기반 복합 대상 매칭 (식품, 상황, 타 약물)
    - persona: 사용자 기저 질환 매칭
    """
    
    drugs = entities.get("drugs", [])
    foods = entities.get("foods", [])
    situations = entities.get("situations", [])
    
    # 모든 엔터티의 텍스트 및 ID 집합 (Target Matching용)
    all_targets = []
    for d in drugs:
        all_targets.append(d.get("raw", ""))
        all_targets.append(d.get("entity_id", ""))
    for f in foods:
        all_targets.append(f.get("raw", ""))
        all_targets.append(f.get("entity_id", ""))
    for s in situations:
        all_targets.append(s.get("raw", ""))
        all_targets.append(s.get("canonical", ""))
        all_targets.append(s.get("entity_id", ""))
    
    # 사용자 페르소나 (CONDITION_... ID 보유 여부)
    user_persona_ids = {
        s["entity_id"].replace("CONDITION_", "") 
        for s in situations if s["entity_id"].startswith("CONDITION_")
    }
    # 텍스트상 매칭된 질환 이름도 포함
    user_persona_raws = {
        s["raw"] for s in situations if s["entity_id"].startswith("CONDITION_")
    }

    matched = []

    for rule in rules:
        # 1. 페르소나 체크
        rule_persona = rule.get("persona", "")
        if rule_persona:
            persona_parts = set(rule_persona.split("_"))
            # 고령_고혈압 -> {고령, 고혈압}
            # user_persona_ids는 {hypertension, diabetes...} 이므로 한글명칭/ID 둘다 체크 필요
            is_persona_match = False
            for p in persona_parts:
                if p in user_persona_raws: is_persona_match = True
                # ID가 룰에 적혀있을 경우 대비 (예: hypertension)
                if p.lower() in [id.lower() for id in user_persona_ids]: is_persona_match = True
            
            # if not is_persona_match:
            #     print(f"DEBUG: Rule {rule['rule_id']} persona mismatch. Rule needs: {rule_persona}, User has: {user_persona_raws}/{user_persona_ids}")
            #     continue
            if not is_persona_match:
                continue

        # 2. 약물 매칭 (Category & Name)
        rule_cat = rule.get("drug_category", "ALL")
        rule_drug_name = rule.get("drug_name", "ALL")
        
        # 해당 룰의 주체가 되는 약물 찾기
        primary_drugs = []
        if rule_cat == "ALL" and rule_drug_name == "ALL":
            # 약물 상관 없이 발동하는 룰 (예: DM_004 공복)
            # 하지만 최소한 '약'이 감지된 맥락이어야 함
            if drugs:
                primary_drugs = drugs
            else:
                # 약이 없어도 상황만으로 발동하는 룰이면 허용 (예: 당뇨 환자가 공복일 때)
                # 이 경우 더미 약물 객체 생성
                primary_drugs = [{"raw": "약물", "entity_id": "DRUG_GENERIC"}]
        else:
            for d in drugs:
                d_id = d.get("entity_id", "UNKNOWN")
                d_raw = d.get("raw", "")
                d_cat = ID_TO_CATEGORY.get(d_id, "UNKNOWN")
                
                # Category 매칭 (Regex 허용 - 예: CCB|ARB 가 ACE/ARB 에 매칭되도독 설정 가능. 하지만 CCB|ARB는 ARB만 쓰였을때 직관적이지 않으므로 contains로 처리하거나 정규식 사용)
                cat_match = (rule_cat == "ALL") or bool(re.search(rule_cat, d_cat, re.I))
                
                # Name 매칭 (Regex)
                name_match = (rule_drug_name == "ALL") or bool(re.search(rule_drug_name, d_raw + "|" + d_id, re.I))
                
                if cat_match and name_match:
                    primary_drugs.append(d)
        
        if not primary_drugs:
            # print(f"DEBUG: Rule {rule['rule_id']} drug mismatch. Rule cat: {rule_cat}, name: {rule_drug_name}")
            continue

        # 3. 타겟 매칭 (food_keyword_match)
        rule_target = rule.get("food_keyword_match", "ALL")
        target_match = False
        
        if rule_target == "ALL":
            target_match = True
        else:
            # any target matches the regex
            for target_text in all_targets:
                if target_text and re.search(rule_target, target_text, re.I):
                    # 주체 약물과 타켓이 동일한 경우는 제외 (자기 자신과의 매칭 방지)
                    # 단, persona가 비어있지 않은 룰은 페르소나-약물 간의 관계이므로 자기 자신(약물) 매칭을 허용함
                    if not rule_persona:
                        # 주체 약물들의 raw/id와 겹치는지 체크
                        primary_texts = []
                        for pd in primary_drugs:
                            primary_texts.append(pd.get("raw", ""))
                            primary_texts.append(pd.get("entity_id", ""))
                        if target_text in primary_texts:
                            continue

                    target_match = True
                    break
        
        if not target_match:
            continue

        # 모든 조건 충족
        matched.append({
            "rule_id": rule.get("rule_id"),
            "risk_level_hint": rule.get("risk_level_hint"),
            "risk_type": rule.get("risk_type"),
            "description": rule.get("description"),
            "evidence_key": rule.get("evidence_key"),
            "level": rule.get("level", 2)
        })

    return matched
