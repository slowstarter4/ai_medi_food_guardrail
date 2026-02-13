import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from .schema import Evidence

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def generate_explanation(
    risk_result: Dict,
    evidences: List[Evidence]
) -> str:
    """
    OpenAI API를 사용하여 위험 분석 결과에 대한 사용자 친화적인 설명을 생성합니다.
    """
    if not client:
        return "OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."

    # 프롬프트 구성
    input_text = risk_result.get("input_text", "") # main.py에서 전달 필요, 없으면 빈 문자열
    risk_level = risk_result.get("risk_level", "UNKNOWN")
    
    evidence_text = "\n".join(
        f"- {e['title']}: {e['summary']} (출처: {e['source']})"
        for e in evidences
    )

    system_prompt = """
    당신은 '세이프잇(SafeEat)' 서비스의 다정하고 전문적인 의료 상담 보조 AI입니다.
    
    [매우 중요 - 절대 원칙]
    사용자의 질문 분석 결과인 **[시스템 분석 결과 - 위험 등급]**을 **절대적인 진실**로 받아들여야 합니다.
    위험 등급이 **'RED'**라면, 무조건 **"매우 위험합니다"**, **"절대 금지"**라고 명확히 경고해야 합니다.
    
    [답변 가이드]
    1. **전문성 및 구체성**: 단순히 "위험하다"고 하지 말고, 제공된 [의학적 근거]를 바탕으로 "왜" 위험한지 생리학적/의학적 이유(예: 혈당 조절 방해, 출혈 위험 증가, 약물 농도 급상승 등)를 상세히 설명하세요.
    2. **다정한 말투**: 고령자(김영순 여사님)가 이해하기 쉽도록 쉽고 정중하며 다정한 말투를 유지하세요.
    3. **출처 명시**: 제공된 근거 데이터의 'source' 정보를 활용하여 답변 끝에 반드시 출처를 표기하세요.
    
    [답변 형식 (Strict Format)]
    반드시 아래의 구조를 지켜서 답변하세요:
    
    ■ **[결론]**: (위험 등급에 맞춘 강력하고 명확한 한 문장 요약)
    ■ **[이유]**: (의학적 근거를 바탕으로 왜 위험한지 상세 설명 - 가장 중요한 부분)
    ■ **[대처]**: (사용자가 즉시 취해야 할 행동 지침)
    ■ **[출처]**: (근거 데이터의 출처 명시 - 예: 식약처 e약은요, 세이프잇 내부 가이드라인 등)
    """

    user_prompt = f"""
    [사용자 질문]
    "{input_text}"

    [시스템 분석 결과]
    - 위험 등급: {risk_level}

    [의학적 근거 데이터]
    {evidence_text}

    위 정보를 바탕으로 '세이프잇' 답변 형식에 맞춰 상세히 작성해주세요. 
    특히 [이유] 섹션에서 의학적 원리를 사용자가 알기 쉽게 설명하는 데 집중해주세요.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"설명 생성 중 오류가 발생했습니다: {str(e)}"
