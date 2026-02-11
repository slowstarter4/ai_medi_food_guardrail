from src.rag.retriever import retrieve_evidence
from src.rag.explainer import generate_explanation

def run_explanation(result):
    """
    RAG 파이프라인 실행:
    1. Evidence Key 추출
    2. Evidence DB 검색
    3. LLM 설명 생성
    """
    # Input handling: main.py passes risk_result directly, but robust check
    risk_result = result.get("risk_result", result)
    
    # Evidence Key 추출
    evidence_keys = risk_result.get("evidence_keys", [])
    
    evidences = []
    if risk_result.get("evidence_info"):
        evidences = list(risk_result["evidence_info"]) # copy list
    elif evidence_keys:
         evidences = retrieve_evidence(evidence_keys)

    # [Fallback] Evidence가 없으면(규칙 미매칭), 약물명으로 검색 시도 (External API)
    if not evidences:
        entities = risk_result.get("entities_involved", {})
        drugs = entities.get("drugs", [])
        drug_names = [d["raw"] for d in drugs]
        if drug_names:
            evidences = retrieve_evidence(drug_names)
            # Fetch된 Evidence를 결과 객체에 반영 (Debug/Audit용)
            if isinstance(risk_result, dict):
                risk_result["evidence_info"] = evidences
                
    # LLM 설명 생성시 input text도 필요함
    explanation_input = {
        "input_text": risk_result.get("input_text", ""), # result instead of risk_result if needed
        "risk_level": risk_result.get("risk_level", "UNKNOWN")
    }

    return generate_explanation(explanation_input, evidences)
