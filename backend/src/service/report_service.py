import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

LOG_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "logs"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_weekly_logs() -> List[Dict[str, Any]]:
    """
    최근 7일간의 로그를 수집합니다.
    """
    logs = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        log_dir = LOG_BASE_DIR / date_str
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.json"):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs.append(json.load(f))
                except Exception as e:
                    print(f"[REPORTER] 파일 읽기 실패: {log_file}, {e}")
        
        current_date += timedelta(days=1)
    
    return logs

def calculate_stats(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    로그 데이터를 바탕으로 통계를 수집합니다.
    """
    total_count = len(logs)
    risk_counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}
    top_ingredients = {}
    
    for log in logs:
        risk = log.get("result", {}).get("risk_level", "GREEN")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        # 성분 집계 (위험 성분 중심)
        entities = log.get("result", {}).get("full_result", {}).get("risk_result", {}).get("entities_involved", {})
        for food in entities.get("foods", []):
            name = food.get("raw")
            top_ingredients[name] = top_ingredients.get(name, 0) + 1
            
    # 정렬하여 Top 3 추출
    sorted_ingredients = sorted(top_ingredients.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # 안전 지수 계산 (임의 산식)
    # 초기 100점, RED -10, YELLOW -5
    safety_score = max(0, 100 - (risk_counts["RED"] * 10) - (risk_counts["YELLOW"] * 5))
    
    return {
        "total_count": total_count,
        "risk_distribution": risk_counts,
        "top_ingredients": [name for name, count in sorted_ingredients],
        "safety_score": safety_score
    }

def generate_persona_messages(stats: Dict[str, Any], logs: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    LLM을 사용하여 페르소나별 요약 메시지를 생성합니다.
    """
    if not logs:
        return {
            "senior": "이번 주에는 분석하신 내역이 없네요. 건강 관리를 위해 식사 전 꼭 확인해보세요!",
            "guardian": "어머니께서 이번 주에는 아직 서비스를 이용하지 않으셨습니다."
        }

    # 로그 요약 (LLM 전달용)
    summary_for_llm = f"""
    - 총 스캔 횟수: {stats['total_count']}회
    - 위험 등급: RED {stats['risk_distribution']['RED']}건, YELLOW {stats['risk_distribution']['YELLOW']}건
    - 주요 주의 성분: {', '.join(stats['top_ingredients'])}
    """

    messages = {}
    
    # 1. 김영순 여사용 (Senior)
    prompt_senior = f"""
    당신은 '세이프잇' 서비스의 친절한 AI 건강 도우미입니다. 
    70대 김영순 여사님께 이번 주 식단 및 복약 안전에 대한 격려 메시지를 작성해주세요.
    말투는 다정하고 친근하며, 구스름한 할머니 말투나 지나치게 격식 있는 표현보다는 
    따뜻한 자녀나 손주가 말하는 것 같은 느낌으로 작성해주세요.
    
    데이터: {summary_for_llm}
    조건:
    - 3문장 이내로 작성.
    - 위험(RED/YELLOW)이 있었다면 조심하자고 다독이고, 그린 위주였다면 칭찬해주세요.
    """
    
    # 2. 최지연 팀장용 (Guardian)
    prompt_guardian = f"""
    당신은 '세이프잇'의 분석 엔진입니다. 
    보호자인 최지연 팀장에게 어머니의 건강 가드레일 준수 현황을 요약 보고해주세요.
    말투는 전문적이고 분석적이어야 합니다.
    
    데이터: {summary_for_llm}
    안전 점수: {stats['safety_score']}
    조건:
    - 3문장 이내로 작성.
    - 주요 위험 요소와 모니터링 포인트를 짚어주세요.
    """

    try:
        # Senior Message
        res_s = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_senior}]
        )
        messages["senior"] = res_s.choices[0].message.content.strip()

        # Guardian Message
        res_g = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt_guardian}]
        )
        messages["guardian"] = res_g.choices[0].message.content.strip()
    except Exception as e:
        print(f"[REPORTER] LLM 호출 실패: {e}")
        messages["senior"] = "이번 주에도 건강하게 식사하시느라 수고 많으셨어요!"
        messages["guardian"] = "어머니의 이번 주 안전 지수는 안정적입니다."

    return messages

def generate_weekly_report():
    """
    주간 리포트 전체 프로세스를 실행합니다.
    """
    logs = get_weekly_logs()
    stats = calculate_stats(logs)
    persona_messages = generate_persona_messages(stats, logs)
    
    return {
        "period": f"{(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
        "stats": stats,
        "messages": persona_messages,
        "log_count": len(logs)
    }
