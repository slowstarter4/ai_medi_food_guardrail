"""
safeeat_additional_testcases_50.csv의 상위 5개(LIMIT) 케이스를 테스트합니다.
실행방법: backend/ 디렉토리에서 python tests/test_subset_5.py
"""
import os
import sys
import csv
import io
from contextlib import redirect_stdout

# backend 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import analyze_text

# 경로 설정
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(ROOT, "safeeat_additional_testcases_50.csv")
LOG_PATH = os.path.join(ROOT, "test_subset_result.txt")

LIMIT = 50  # 이 숫자를 바꾸면 실행 개수 조절 가능


def run_tests():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("case_id", "").strip()]

    subset = rows[:LIMIT]

    lines = []
    lines.append("=" * 60)
    lines.append(f"  SafeEat 검증 테스트 ({LIMIT}개 케이스)")
    lines.append("=" * 60)

    results = []
    for row in subset:
        case_id       = row["case_id"].strip()
        input_text    = row["input"].strip()
        expected_rule = row["expected_rule"].strip()
        expected_risk = row["expected_risk"].strip()

        lines.append(f"\n[{case_id}] 입력: {input_text}")

        try:
            # DEBUG print 출력 억제
            buf = io.StringIO()
            with redirect_stdout(buf):
                analysis = analyze_text(input_text)

            risk_result = analysis.get("risk_result", {})
            actual_risk = risk_result.get("risk_level", "UNKNOWN")

            rep_rule = risk_result.get("representative_rule")
            actual_rule = rep_rule.get("rule_id", "NONE") if rep_rule else "NONE"

        except Exception as e:
            actual_risk = "ERROR"
            actual_rule = f"오류: {e}"

        risk_ok = (actual_risk == expected_risk)
        status = "PASS" if risk_ok else "FAIL"

        lines.append(f"  예상 규칙: {expected_rule}  |  실제 규칙: {actual_rule}")
        lines.append(f"  예상 위험도: {expected_risk}  |  실제 위험도: {actual_risk}  ->  {status}")
        results.append({"case_id": case_id, "status": status})

    lines.append("")
    lines.append("=" * 60)
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines.append(f"  최종 결과: {passed} / {LIMIT} PASS")
    lines.append("=" * 60)

    output = "\n".join(lines)
    print(output)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write(output)
    print(f"[로그 저장] {LOG_PATH}")


if __name__ == "__main__":
    run_tests()
