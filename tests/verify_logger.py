import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from main import analyze_text
from src.utils.logger import save_analysis_log

def test_logging():
    print("Testing logging system...")
    
    # Simulate analysis
    input_text = "로사르탄 먹는데 바나나 먹어도 되나요?"
    user_meds = ["로사르탄"]
    user_conditions = ["고혈압"]
    
    result = analyze_text(input_text, user_meds, user_conditions)
    
    # Save log
    log_path = save_analysis_log(
        request_data={
            "type": "text",
            "text": input_text,
            "medications": user_meds,
            "conditions": user_conditions
        },
        result_data=result
    )
    
    if log_path and os.path.exists(log_path):
        print(f"SUCCESS: Log saved at {log_path}")
        # Check content
        import json
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Log risk level: {data['result']['risk_level']}")
            print(f"Personalized context: {data['request']['conditions']}")
    else:
        print("FAILED: Log not saved")

if __name__ == "__main__":
    test_logging()
