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
    당신은 'AI Food-Medication Guardrail' 서비스의 의료 상담 보조 AI입니다.
    
    [매우 중요 - 절대 원칙]
    사용자의 질문 분석 결과인 **[시스템 분석 결과 - 위험 등급]**을 **절대적인 진실**로 받아들여야 합니다.
    만약 위험 등급이 **'RED'**라면, 당신의 의학적 판단이나 상황의 불확실성과 관계없이 무조건 **"매우 위험합니다"**, **"절대 금지"**라고 말해야 합니다.
    "판단하기 어렵다", "상황에 따라 다르다"는 말은 시스템 오류로 간주됩니다. 절대 사용하지 마세요.

    [답변 가이드]
    1. **RED (위험)**:
       - **결론**: "**[경고] 매우 위험합니다! 절대 같이 드시지 마세요.**" (이 문구로 시작)
       - **이유**: 제공된 [의학적 근거]를 인용하여 심각한 부작용(출혈, 저혈당 쇼크 등)을 경고.
       - **대처**: "즉시 섭취를 중단하고 병원을 방문하세요." 또는 "절대 병용하지 마세요."

    2. **YELLOW (주의)**:
       - **결론**: "**주의가 필요합니다.**"
       - **이유**: 상호작용 가능성 설명.
       - **대처**: "시간 간격을 두거나 의사와 상의하세요."

    3. **답변 형식 (Strict Format)**:
       - **결론**: (한 문장 강력 요약)
       - **이유**: (근거 기반 설명)
       - **대처**: (행동 지침)
    """

    user_prompt = f"""
    [사용자 질문]
    "{input_text}"

    [시스템 분석 결과]
    - 위험 등급: {risk_level} (<<< 이 등급이 절대적 기준입니다. RED면 무조건 위험하다고 말하세요.)

    [의학적 근거]
    {evidence_text}

    위 정보를 바탕으로 가이드라인에 맞춰 답변을 작성해주세요.
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
