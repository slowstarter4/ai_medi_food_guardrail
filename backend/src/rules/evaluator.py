import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

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
    # 제네릭 약물 ID → 계열 매핑 (Context Gate 통과를 위해 필수)
    "DRUG_HYPERTENSION_GENERIC": "ACE/ARB|CCB|이뇨제",
    "DRUG_DIABETES_GENERIC": "비구아나이드|설폰요소제|SGLT2",
    "DRUG_DIURETIC_GENERIC": "이뇨제",
    "DRUG_PAINKILLER_GENERIC": "NSAIDs",
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

    DM_CATEGORIES = ["설폰요소제", "비구아나이드", "SGLT2"]
    HTN_CATEGORIES = ["ACE/ARB", "CCB", "이뇨제"]
    NSAID_CATEGORIES = ["NSAIDs"]

    def check_context(category_list, target_categories):
        for d in drugs:
            d_cat = ID_TO_CATEGORY.get(d.get("entity_id", ""), "")
            if any(c.strip() in target_categories for c in d_cat.split("|") if c.strip()):
                return True
        return False

    has_diabetes_context = any(s.get("entity_id") == "CONDITION_diabetes" for s in situations) or \
                           check_context(drugs, DM_CATEGORIES)
    has_htn_context = any(s.get("entity_id") == "CONDITION_hypertension" for s in situations) or \
                      check_context(drugs, HTN_CATEGORIES)
    has_nsaid_context = any(ID_TO_CATEGORY.get(d.get("entity_id")) in NSAID_CATEGORIES for d in drugs) or \
                        check_context(drugs, NSAID_CATEGORIES)

    # [핵심 수정] 약물 계열 감지 시 페르소나(질환 컨텍스트) 자동 추론
    # CSV 테스트나 간단 질의 시 질환 정보(칩)가 없어도 규칙이 매칭되도록 함
    if has_htn_context and "hypertension" not in user_persona_ids:
        user_persona_ids.add("hypertension")
        user_persona_raws.add("고혈압")
    if has_diabetes_context and "diabetes" not in user_persona_ids:
        user_persona_ids.add("diabetes")
        user_persona_raws.add("당뇨")

    for rule in rules:
        rule_id = rule.get("rule_id", "")

        # Context Gate 적용
        if rule_id.startswith("DM_") and not has_diabetes_context:
            continue
        if rule_id.startswith("HTN_") and not has_htn_context:
            continue
        if rule_id.startswith("NSAID_") and not has_nsaid_context:
            continue

        # 1. 페르소나 체크
        rule_persona = rule.get("persona", "").strip()
        logger.debug(f"Rule {rule.get('rule_id')} persona: {rule_persona}, user raws: {user_persona_raws}, ids: {user_persona_ids}")
        if rule_persona and rule_persona not in ["API_DEFAULT", "ALL"]:
            persona_parts = set(rule_persona.split("_"))
            is_persona_match = False
            for p in persona_parts:
                if not p: continue
                if p in user_persona_raws: is_persona_match = True
                if p.lower() in [id.lower() for id in user_persona_ids]: is_persona_match = True
            
            if not is_persona_match:
                continue
        
        logger.debug(f"Rule {rule.get('rule_id')} persona matched")

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
            logger.debug(f"Rule {rule.get('rule_id')} drug match failed")
            continue

        logger.debug(f"Rule {rule.get('rule_id')} drug matched: {[d['raw'] for d in primary_drugs]}")

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
            # Add other drugs to targets for cross-drug matching
            for d in drugs:
                external_targets.extend([d.get("raw", ""), d.get("entity_id", ""), ID_TO_CATEGORY.get(d.get("entity_id", ""), "")])
            
            for target_text in external_targets:
                if target_text and re.search(rule_target, target_text, re.I):
                    target_match = True
                    # Check if this target is not just the same primary drug itself (unless allowed)
                    if any(pd.get("entity_id") == target_text for pd in primary_drugs):
                        situ_ids = [s.get("entity_id") for s in situations]
                        is_duplication = any(sid in ["SITUATION_DUPLICATION", "SITUATION_DRUG_DUPLICATION"] for sid in situ_ids)
                        if is_duplication and rule.get("rule_id") == "NSAID_003":
                            target_match = True # Keep it
                        elif rule_cat == "ALL":
                            target_match = True # ALL rules allowed
                        else:
                            target_match = False # Reset if it's just itself and no duplication
                            continue
                    
                    if target_match:
                        break

            if not target_match:
                logger.debug(f"Rule {rule.get('rule_id')} target match failed (rule_target: {rule_target})")
                for d in drugs:
                    d_text = d.get("raw", "") + "|" + d.get("entity_id", "")
                    if re.search(rule_target, d_text, re.I):
                        is_same_instance = any(pd is d for pd in primary_drugs)
                        situ_ids = [s.get("entity_id") for s in situations]
                        has_duplication_situ = any(sid in ["SITUATION_DUPLICATION", "SITUATION_DRUG_DUPLICATION"] for sid in situ_ids)
                        
                        if is_same_instance and rule_cat != "ALL" and not (has_duplication_situ and rule.get("rule_id") == "NSAID_003"):
                            # ALL 카테고리 룰이 아니고, 중복 상황도 아니면 동일 인스턴스 제외
                            continue
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
                s_id = s.get("entity_id", "")
                s_text = s.get("raw", "") + "|" + s.get("canonical", "") + "|" + s_id
                
                # 1) ID 또는 정규식 일치
                if re.search(rule_cond, s_text, re.I):
                    cond_match = True
                    break
                
                # 2) 특수한 경우: 상호 호환 상황어 매핑 (SITUATION_CONCURRENT 등)
                if rule_cond in ["SITUATION_CONCURRENT", "병용", "동시", "함께"] and s_id in ["SITUATION_CONCURRENT", "SITUATION_DRUG_DUPLICATION", "SITUATION_DUPLICATION"]:
                    cond_match = True
                    break
                if rule_cond in ["SITUATION_DEHYDRATION", "탈수", "땀", "사우나"] and s_id == "SITUATION_DEHYDRATION":
                    cond_match = True
                    break
                if rule_cond in ["SITUATION_FASTING", "공복", "식사", "미섭취", "거름"] and s_id == "SITUATION_FASTING":
                    cond_match = True
                    break
        
            if not cond_match:
                logger.debug(f"Rule {rule.get('rule_id')} condition match failed (rule_cond: {rule_cond})")
                continue

        for pd in primary_drugs:
            m_rule = rule.copy()
            m_rule.update({
                "matched_drug": pd.get("raw"),
                "matched_target": rule_target if rule_target != "ALL" else rule_cond
            })
            matched.append(m_rule)

    return matched
