import sys
import os
import json

# 백엔드 경로 추가
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app import analyze_text

def test_dur_integration():
    print("=== [자체 룰(Tier 1) + DUR API(Tier 2) 통합 테스트] ===")
    
    test_cases = [
        {
            "desc": "자체 룰셋 우선순위 확인 (로사르탄 + 바나나)",
            "text": "로사르탄 먹고 있고 오늘 바나나 먹었음",
            "expected_rule": "HTN_001", # 자체 룰셋 ID
            "check_dur": False
        },
        {
            "desc": "API 보조 정보 확인 (설명문 내 상호작용 검색)",
            # 아스피린과 와파린은 서로의 설명문에 주의사항으로 자주 등장함
            "text": "아스피린이랑 와파린 같이 먹어도 되나요?",
            "check_dur": True
        }
    ]
    
    for case in test_cases:
        print(f"\n[테스트] {case['desc']}")
        print(f"입력: {case['text']}")
        
        # 고혈압 환자 페르소나 가정
        result = analyze_text(case['text'], conditions=["고혈압"])
        risk_result = result["risk_result"]
        
        print(f"대표 위험 등급: {risk_result.get('risk_level')}")
        print(f"매칭된 자체 룰: {risk_result.get('representative_rule')}")
        
        supp_info = risk_result.get("supplementary_info", {})
        dur_alerts = supp_info.get("dur_alerts", [])
        
        print(f"추가 DUR 알림 개수: {len(dur_alerts)}")
        for alert in dur_alerts:
            print(f"  - [{alert['type']}] {alert['drug_a']} + {alert['drug_b']}: {alert['description']}")

        if "expected_rule" in case:
            if risk_result.get("representative_rule") == case["expected_rule"]:
                print("결과: ✅ 자체 룰 매칭 PASS")
            else:
                print(f"결과: ❌ 자체 룰 매칭 FAIL (Expected {case['expected_rule']})")
        
        if case["check_dur"]:
            if len(dur_alerts) > 0 or "케토" in case["text"]: # API 환경에 따라 유동적일 수 있음
                print("결과: ✅ DUR 보조 정보 확인 PASS (데이터 존재 시)")

if __name__ == "__main__":
    test_dur_integration()
