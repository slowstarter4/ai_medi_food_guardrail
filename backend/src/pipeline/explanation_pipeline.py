from typing import TypedDict, List, Dict, Annotated
from langgraph.graph import StateGraph, END
from src.rag.retriever import retrieve_evidence
from src.rag.explainer import generate_explanation

# 상태 정의
class PipelineState(TypedDict):
    risk_result: Dict
    evidences: List[Dict]
    explanation: str

def retrieve_node(state: PipelineState) -> PipelineState:
    """근거 데이터를 수집하는 노드"""
    risk_result = state["risk_result"]
    evidence_keys = risk_result.get("evidence_keys", [])
    
    evidences = []
    if risk_result.get("evidence_info"):
        evidences = list(risk_result["evidence_info"])
    elif evidence_keys:
        evidences = retrieve_evidence(evidence_keys)

    # [Fallback] Evidence가 없으면 약물명으로 검색 시도
    if not evidences:
        entities = risk_result.get("entities_involved", {})
        drugs = entities.get("drugs", [])
        drug_names = [d["raw"] for d in drugs]
        if drug_names:
            evidences = retrieve_evidence(drug_names)
    
    # 결과 업데이트를 위해 원본 객체에도 반영 (하위 호환성)
    risk_result["evidence_info"] = evidences
    
    return {"evidences": evidences}

def explain_node(state: PipelineState) -> PipelineState:
    """설명을 생성하는 노드"""
    risk_result = state["risk_result"]
    evidences = state["evidences"]
    
    explanation_input = {
        "input_text": risk_result.get("input_text", ""),
        "risk_level": risk_result.get("risk_level", "UNKNOWN")
    }
    
    explanation = generate_explanation(explanation_input, evidences)
    return {"explanation": explanation}

# 그래프 구축
workflow = StateGraph(PipelineState)

# 노드 추가
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("explain", explain_node)

# 엣지 연결
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "explain")
workflow.add_edge("explain", END)

# 컴파일
app = workflow.compile()

def run_explanation(result):
    """
    LangGraph 기반 RAG 파이프라인 실행
    """
    # 초기 상태 설정
    risk_result = result.get("risk_result", result)
    initial_state = {
        "risk_result": risk_result,
        "evidences": [],
        "explanation": ""
    }
    
    # 그래프 실행
    final_state = app.invoke(initial_state)
    
    return final_state["explanation"]
