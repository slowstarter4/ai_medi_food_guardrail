import os
import logging
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
    input_text = risk_result.get("input_text", "")
    risk_level = risk_result.get("risk_level", "UNKNOWN")
    user_conditions = risk_result.get("user_conditions", [])
    
    # 실질적으로 검출된 약물과 식품 추출
    entities = risk_result.get("entities_involved", {})
    detected_drugs = [d['raw'] for d in entities.get("drugs", [])]
    detected_foods = [f['raw'] for f in entities.get("foods", [])]
    
    drug_names_str = ", ".join(detected_drugs) if detected_drugs else "없음"
    food_names_str = ", ".join(detected_foods) if detected_foods else "없음"
    conditions_str = ", ".join(user_conditions) if user_conditions else "없음"
    
    evidence_text = "\n".join(
        f"- [강도: {e.get('evidence_strength', 'N/A')}] {e.get('evidence_source_label', '출처 미상')}: "
        f"{e.get('evidence_summary_user', '정보 없음')}"
        for e in evidences
    )

    system_prompt = f"""
    당신은 '세이프잇(SafeEat)' 서비스의 다정하고 전문적인 의료 상담 보조 AI입니다.
    사용자의 건강 상태는 다음과 같습니다: [{conditions_str}]
    
    [매우 중요 - 절대 원칙]
    사용자의 상황분석 결과인 **[시스템 분석 결과 - 위험 등급]**을 **절대적인 진실**로 받아들여야 합니다.
    위험 등급이 **'RED'**라면, 무조건 **" 매우 위험합니다"**, **"절대 금지"**라고 명확히 경고해야 합니다.
    
    [답변 가이드]
    0. **복약 현황 인지 표시**: 답변 시작 부분에서 사용자의 복약 정보([{drug_names_str}])를 인지하고 있음을 명확히 밝히세요.
    1. **근거 기반 설명**: 제공된 [의학적 근거]의 '강도(Strength)'와 '출처(Source)'를 활용하여 신뢰도를 높이세요. (예: "FDA 가이드라인에 따른 높은 강도의 권고 사항에 따르면~")
    2. **원인-위험-행동 흐름**: [이유] 섹션에서 왜 위험한지(기전), 어떤 일이 벌어질 수 있는지(위험), 어떻게 해야 하는지(행동)를 상세히 설명하세요.
    3. **정중하고 다정한 말투**: 사용자가 이해하기 쉽도록 쉽고 친절한 말투를 유지하세요.
    4. **출처 명시**: 제공된 근거의 'evidence_source_label'을 활용하여 답변 끝에 출처를 표기하세요.
    
    [답변 형식 (Strict Format)]
    반드시 아래의 구조(기호, 대괄호 포함)를 토대 하나 틀리지 말고 정확히 지켜서 답변하세요:
    
    ■ **[결론]**: (위험 등급에 맞춘 강력하고 명확한 한 문장 요약)
    ■ **[이유]**: (검출된 약물, 식품, 그리고 사용자의 상태를 연결하여 왜 위험한지 의학적 원리를 상세 설명)
    ■ **[대안]**: (위험한 식품 대신 안전하게 섭취할 수 있는 구체적인 대체 식품 추천 - 예: 자몽 대신 오렌지나 사과 등)
    ■ **[대처]**: (사용자가 즉시 취해야 할 행동 지침)
    ■ **[출처]**: (근거 데이터의 출처 명시 - 예: 식약처 e약은요, 세이프잇 내부 가이드라인 등)
    """

    user_prompt = f"""
    [입력 데이터]
    - 사용자 건강 상태: {conditions_str}
    - 사용자가 현재 복용 중인 '내 약': {drug_names_str}
    - 스캔한 식품 속 성분: {food_names_str}

    [시스템 분석 결과]
    - 위험 등급: {risk_level}

    [의학적 근거 데이터]
    {evidence_text}

    위 정보를 바탕으로 '**{drug_names_str}**'을 복용 중인 사용자가 '**{food_names_str}**'이 포함된 식품을 섭취하려 할 때의 상호작용 위험성을 분석해주세요.
    사용자의 상태('{conditions_str}')를 고려하여 '세이프잇' 답변 형식에 맞춰 상세히 작성해주세요.
    
    [중요] **사용자가 복용 중인 약물이 있다면 ({drug_names_str})**, 설령 위험도가 낮더라도 반드시 해당 약물을 복용 중임을 인지하고 답변하세요. 절대 "복용 중인 약물이 없으므로"와 같은 실수를 하지 마세요.
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
