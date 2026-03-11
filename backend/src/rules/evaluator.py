import re
from typing import Dict, List

# 약물 ID -> 계열 매핑
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
    "DRUG_HYPERTENSION_GENERIC": "ACE/ARB|CCB|이뇨제",
    "DRUG_DIABETES_GENERIC": "비구아나이드|설폰요소제|SGLT2",
    "DRUG_DIURETIC_GENERIC": "이뇨제",
    "DRUG_PAINKILLER_GENERIC": "NSAIDs"
}

def evaluate_rules(entities: Dict, rules: List[Dict]) -> List[Dict]:
    """
    ruleset v2.0 매칭 엔진
    """
    drugs = entities.get("drugs", [])
    foods = entities.get("foods", [])
    situations = entities.get("situations", [])
    
    user_persona_ids = {
        s.get("entity_id", "").replace("CONDITION_", "") 
        for s in situations if s.get("entity_id", "").startswith("CONDITION_")
    }
    user_persona_raws = {
        s.get("raw", "") for s in situations if s.get("entity_id", "").startswith("CONDITION_")
    }

    matched = []

    for rule in rules:
        # 1. 페르소나 체크
        rule_persona = rule.get("persona", "").strip()
        if rule_persona and rule_persona != "API_DEFAULT":
            persona_parts = set(rule_persona.split("_"))
            is_persona_match = False
            for p in persona_parts:
                if not p: continue
                if p in user_persona_raws: is_persona_match = True
                if p.lower() in [id.lower() for id in user_persona_ids]: is_persona_match = True
            
            if not is_persona_match:
                continue

        # 2. 약물 매칭
        rule_cat = rule.get("drug_category", "ALL")
        rule_drug_name = rule.get("drug_name", "ALL")
        
        primary_drugs = []
        if rule_cat == "ALL" and rule_drug_name == "ALL":
            if drugs:
                primary_drugs = drugs
            else:
                primary_drugs = [{"raw": "약물", "entity_id": "DRUG_GENERIC"}]
        else:
            for d in drugs:
                d_id = d.get("entity_id", "UNKNOWN")
                d_raw = d.get("raw", "")
                actual_cat_str = ID_TO_CATEGORY.get(d_id, "UNKNOWN")
                actual_cats = actual_cat_str.split("|")
                # 룰 계열이 CCB|ARB 처럼 복수일 수도 있음
                rule_cats = rule_cat.split("|")
                
                cat_match = (rule_cat == "ALL") or any(rc.strip() in actual_cats for rc in rule_cats)
                name_match = (rule_drug_name == "ALL") or bool(re.search(rule_drug_name, d_raw + "|" + d_id, re.I))
                
                if cat_match and name_match:
                    primary_drugs.append(d)
        
        if not primary_drugs:
            continue

        # 3. 타겟 매칭 (food_keyword_match)
        rule_target = rule.get("food_keyword_match", "ALL")
        target_match = False
        
        if rule_target == "ALL":
            target_match = True
        else:
            external_targets = []
            for f in foods:
                external_targets.extend([f.get("raw", ""), f.get("entity_id", "")])
            for s in situations:
                external_targets.extend([s.get("raw", ""), s.get("canonical", ""), s.get("entity_id", "")])
            
            for target_text in external_targets:
                if target_text and re.search(rule_target, target_text, re.I):
                    target_match = True
                    break

            if not target_match:
                for d in drugs:
                    d_text = d.get("raw", "") + "|" + d.get("entity_id", "")
                    if re.search(rule_target, d_text, re.I):
                        is_same_instance = any(pd is d for pd in primary_drugs)
                        if is_same_instance:
                            if len(primary_drugs) >= 2 or (rule_persona and rule_persona != "API_DEFAULT"):
                                target_match = True
                                break
                        else:
                            target_match = True
                            break
        
        if not target_match:
            continue

        # 4. 상황 매칭
        rule_cond = rule.get("condition", "ALL")
        if rule_cond != "ALL":
            cond_match = False
            for s in situations:
                s_text = s.get("raw", "") + "|" + s.get("canonical", "") + "|" + s.get("entity_id", "")
                if re.search(rule_cond, s_text, re.I):
                    cond_match = True
                    break
            
            # 특수한 경우: 상호 호환 상황어 매핑
            if not cond_match:
                for s in situations:
                    s_id = s.get("entity_id", "")
                    # 병용/동시/함께
                    if any(x in rule_cond for x in ["병용", "동시", "함께"]) and s_id in ["SITUATION_CONCURRENT", "SITUATION_DRUG_DUPLICATION"]:
                        cond_match = True
                    # 탈수/땀/사우나
                    elif any(x in rule_cond for x in ["탈수", "땀", "사우나"]) and s_id == "SITUATION_DEHYDRATION":
                        cond_match = True
                    # 공복/식사/미섭취/거름
                    elif any(x in rule_cond for x in ["공복", "식사", "미섭취", "거름"]) and s_id == "SITUATION_FASTING":
                        cond_match = True
                    
                    if cond_match: break
            
            if not cond_match:
                continue

        for pd in primary_drugs:
            m_rule = rule.copy()
            m_rule.update({
                "matched_drug": pd.get("raw"),
                "matched_target": rule_target if rule_target != "ALL" else rule_cond
            })
            matched.append(m_rule)

    return matched
