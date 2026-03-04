import sys
import os

# 백엔드 경로 추가
sys.path.append(os.getcwd())

from app import _run_pipeline

def test_scenario(name, text, meds=None, conditions=None, situations=None):
    print(f"\n>>> Testing Scenario: {name}")
    print(f"Input: Text='{text}', Meds={meds}, Conditions={conditions}, Situations={situations}")
    
    res = _run_pipeline(text, user_meds=meds, user_conditions=conditions, user_situations=situations)
    risk = res['risk_result']
    
    print(f"Result: {risk['risk_level']} (Rule: {risk['representative_rule']})")
    print(f"Explanation: {res['explanation'][:100]}...")
    
    return risk

# 1. HTN_001: 로사르탄 + 바나나
test_scenario(
    "HTN_001 (Losartan + Banana)",
    "바나나 먹어도 되나요?",
    meds=["로사르탄"],
    conditions=["고혈압"]
)

# 2. DM_001: 설폰요소제 + 술
test_scenario(
    "DM_001 (Sulfonylurea + Alcohol)",
    "소주 한 잔 했어요",
    meds=["글리메피리드"],
    conditions=["당뇨"],
    situations=["공복"]
)

# 3. NSAID_001: 이부프로펜 + 술
test_scenario(
    "NSAID_001 (Ibuprofen + Alcohol)",
    "술 마셨는데 애드빌 먹어도 되나요?",
    meds=["애드빌"],
    conditions=["관절염"]
)

# 4. DM_004: 당뇨 + 공복 (ALL/ALL 매칭)
test_scenario(
    "DM_004 (Diabetes + Fasting behavior)",
    "밥 안먹고 약 먹었어요",
    meds=["자누메트"],
    conditions=["당뇨"]
)

# 5. HTN_005: 혈압약 + NSAID (HTN_MED context)
test_scenario(
    "HTN_005 (HTN Med + NSAID)",
    "혈압약 먹는데 이부프로펜 먹어도 되나요?",
    conditions=["고혈압"]
)
