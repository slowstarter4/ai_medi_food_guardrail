# src/pipeline/demo_runner.py
from app import analyze_text

DEMO_SCENARIOS = [
    {
        "id": "DEMO_1_GRAPEFRUIT",
        "title": "자몽 + 혈압약",
        "input": "암로디핀 복용 중 자몽주스를 마셨습니다"
    },
    {
        "id": "DEMO_2_NSAID_DUP",
        "title": "진통제 중복 복용",
        "input": "이부프로펜 먹고 있는데 나프록센도 같이 먹어도 되나요?"
    },
    {
        "id": "DEMO_3_COLD_MED",
        "title": "고혈압 + 감기약",
        "input": "고혈압약 먹고 있는데 감기약 같이 먹어도 괜찮을까요?"
    }
]


def run_demo():
    for s in DEMO_SCENARIOS:
        print("\n" + "=" * 60)
        print(f"[SCENARIO] {s['id']} — {s['title']}")
        print("=" * 60)
        print(f"[INPUT]\n{s['input']}\n")

        result = analyze_text(s["input"])
        print(f"[RESULT] 위험도: {result.get('risk_result', {}).get('risk_level', 'N/A')}")
        if result.get("explanation"):
            print(f"[EXPLANATION]\n{result['explanation'][:200]}...")


if __name__ == "__main__":
    run_demo()
