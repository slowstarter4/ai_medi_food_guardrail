import os
import json
import time
from datetime import datetime
from pathlib import Path

# 로그 저장 디렉토리 설정
LOG_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "logs"

def save_analysis_log(request_data: dict, result_data: dict, session_id: str = None):
    """
    분석 요청과 결과를 JSON 파일로 저장합니다.
    """
    try:
        # 디렉토리 생성
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = LOG_BASE_DIR / today_str
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일명 생성 (타임스탬프 + 세션ID)
        timestamp = int(time.time() * 1000)
        file_id = session_id if session_id else f"anon_{timestamp}"
        filename = f"log_{timestamp}_{file_id}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "request": request_data,
            "result": {
                "risk_level": result_data.get("risk_result", {}).get("risk_level"),
                "representative_rule": result_data.get("risk_result", {}).get("representative_rule"),
                "explanation_summary": result_data.get("explanation", "")[:200] + "...",
                "full_result": result_data
            }
        }
        
        with open(log_dir / filename, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
            
        print(f"[LOGGER] 로그 저장 완료: {log_dir / filename}")
        return str(log_dir / filename)
        
    except Exception as e:
        print(f"[LOGGER] 로그 저장 실패: {str(e)}")
        return None
