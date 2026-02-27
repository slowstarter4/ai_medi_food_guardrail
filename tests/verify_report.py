import sys
from pathlib import Path
import json

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from src.service.report_service import generate_weekly_report

def test_report():
    print("Testing weekly report generation...")
    try:
        report = generate_weekly_report()
        print("\n--- REPORT SUMMARY ---")
        print(f"Period: {report['period']}")
        print(f"Log Count: {report['log_count']}")
        print(f"Safety Score: {report['stats']['safety_score']}")
        print(f"Risk Distribution: {report['stats']['risk_distribution']}")
        print(f"Top Ingredients: {report['stats']['top_ingredients']}")
        print("\n--- SENIOR MESSAGE ---")
        print(report['messages']['senior'])
        print("\n--- GUARDIAN MESSAGE ---")
        print(report['messages']['guardian'])
        
        if report['log_count'] >= 0:
            print("\nSUCCESS: Report generated successfully.")
        else:
            print("\nFAILED: Report count is negative (unexpected).")
            
    except Exception as e:
        print(f"\nFAILED: Error during report generation: {e}")

if __name__ == "__main__":
    test_report()
