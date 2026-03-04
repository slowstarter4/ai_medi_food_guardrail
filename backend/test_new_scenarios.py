import requests
import json

def test_scenario(input_text, user_meds=None, user_conditions=None, user_situations=None):
    """실제 API 파이프라인과 유사한 동작 수행"""
    # app.py의 _run_pipeline을 직접 호출하여 테스트
    from app import _run_pipeline
    try:
        result = _run_pipeline(input_text, user_meds, user_conditions, user_situations)
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    # 시나리오 1: 고혈압 + 사우나 (탈수 위험)
    res1 = test_scenario("사우나 가려고 해요", ["로사르탄"], ["고혈압"])
    if "error" not in res1:
        print(f"\n[Scenario 1] 사우나 + 고혈압")
        print(f"Risk: {res1['risk_result']['risk_level']}")
        print(f"Situations: {[s['entity_id'] for s in res1.get('debug_info', {}).get('entities', {}).get('situations', [])]}")
        print(f"Matched Rules: {[r['rule_id'] for r in res1['risk_result'].get('matched_rules', [])]}")

    # 시나리오 2: 당뇨 + 격한 운동 + 공복 (저혈당 위험)
    res2 = test_scenario("격한 운동 하고 왔는데 아직 밥은 안 먹었어요", ["메트포르민"], ["당뇨"])
    if "error" not in res2:
        print(f"\n[Scenario 2] 격한 운동 + 공복 + 당뇨")
        print(f"Risk: {res2['risk_result']['risk_level']}")
        print(f"Entities: {res2.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res2['explanation'][:200]}...")

    # 시나리오 3: 고혈압 + 젓갈 (고염 식단)
    res3 = test_scenario("오늘 저녁에 젓갈이랑 국물이랑 짜게 먹었어요", ["로사르탄"], ["고혈압"])
    if "error" not in res3:
        print(f"\n[Scenario 3] 고염 식단 + 고혈압")
        print(f"Risk: {res3['risk_result']['risk_level']}")
        print(f"Entities: {res3.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res3['explanation'][:200]}...")

    # 시나리오 4: 관절염 + 매일 복용 (장기 복용 독성)
    res4 = test_scenario("이 약을 한 달째 매일 복용 중이에요", ["이부프로펜"], ["관절염"])
    if "error" not in res4:
        print(f"\n[Scenario 4] 장기 복용 + 소염진통제")
        print(f"Risk: {res4['risk_result']['risk_level']}")
        print(f"Entities: {res4.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res4['explanation'][:200]}...")

    # 시나리오 5: 설폰요소제 + 공복 + 음주 (심각한 저혈당 위험)
    res5 = test_scenario("설폰요소제 먹고 있는데 공복에 술 마셔도 되나요?", [], ["당뇨"])
    if "error" not in res5:
        print(f"\n[Scenario 5] 설폰요소제 + 공복 + 음주")
        print(f"Risk: {res5['risk_result']['risk_level']}")
        print(f"Entities: {res5.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res5['explanation'][:200]}...")

    # 시나리오 6: ACE/ARB 계열 + 바나나
    res6 = test_scenario("ACE/ARB 계열 혈압약 복용 중인데 바나나 먹어도 될까요?", [], ["고혈압"])
    if "error" not in res6:
        print(f"\n[Scenario 6] ACE/ARB + 바나나")
        print(f"Risk: {res6['risk_result']['risk_level']}")
        print(f"Entities: {res6.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res6['explanation'][:200]}...")

    # 시나리오 7: CCB + 자몽
    res7 = test_scenario("CCB 약 먹는데 자몽 주스 괜찮나요?", [], ["고혈압"])
    if "error" not in res7:
        print(f"\n[Scenario 7] CCB + 자몽")
        print(f"Risk: {res7['risk_result']['risk_level']}")
        print(f"Entities: {res7.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res7['explanation'][:200]}...")

    # 시나리오 8: SGLT2 + 사우나
    res8 = test_scenario("SGLT2 억제제 처방받았는데 오늘 사우나 가도 되나요?", [], ["당뇨"])
    if "error" not in res8:
        print(f"\n[Scenario 8] SGLT2 + 사우나")
        print(f"Risk: {res8['risk_result']['risk_level']}")
        print(f"Entities: {res8.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res8['explanation'][:200]}...")

    # 시나리오 9: NSAIDs + 술
    res9 = test_scenario("NSAIDs 진통제 먹고 술 마시면 안 되나요?", [], ["관절염"])
    if "error" not in res9:
        print(f"\n[Scenario 9] NSAIDs + 술")
        print(f"Risk: {res9['risk_result']['risk_level']}")
        print(f"Entities: {res9.get('debug_info', {}).get('entities', {})}")
        print(f"Explanation: {res9['explanation'][:200]}...")

    # 시나리오 10: 제품명(성분명) 혼합형
    res10 = test_scenario("글루피드정(글리메피리드) 처방받았어요", [], ["당뇨"])
    if "error" not in res10:
        print(f"\n[Scenario 10] 제품명(성분명) 혼합")
        print(f"Risk: {res10['risk_result']['risk_level']}")
        print(f"Entities: {res10.get('debug_info', {}).get('entities', {})}")

    # 시나리오 11: 글리메피리드 + 상황 칩(공복) 주입
    res11 = test_scenario("제 약이에요", ["글리메피리드"], ["당뇨"], ["SITUATION_FASTING"])
    if "error" not in res11:
        print(f"\n[Scenario 11] 글리메피리드 + 공복 칩 주입")
        print(f"Risk: {res11['risk_result']['risk_level']}")
        print(f"Situations: {[s['entity_id'] for s in res11.get('debug_info', {}).get('entities', {}).get('situations', [])]}")
        print(f"Matched Rules: {[r['rule_id'] for r in res11['risk_result'].get('matched_rules', [])]}")
    else:
        print(f"\n[Scenario 11 ERROR] {res11['error']}")
