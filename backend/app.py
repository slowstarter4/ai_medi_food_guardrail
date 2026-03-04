import os
import json
import shutil
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from src.service.risk_assessor import assess_risk
from src.ocr.processor import extract_text_from_image
from src.utils.logger import save_analysis_log
from src.service.report_service import generate_weekly_report

# LLM 설명 생성 (RAG 파이프라인)
try:
    from src.pipeline.explanation_pipeline import run_explanation
    HAS_EXPLANATION = True
except Exception:
    HAS_EXPLANATION = False

# 질환 라벨 → ID 매핑
LABEL_TO_ID = {
    "고령": "elderly", "고혈압": "hypertension", "당뇨": "diabetes",
    "고지혈증": "hyperlipidemia", "관절염": "arthritis", "천식": "asthma"
}


def _run_pipeline(input_text: str, user_meds: list = None, user_conditions: list = None):
    """핵심 분석 파이프라인: 파싱 → 정규화 → 규칙 매칭 → 위험도 판정 → LLM 설명"""
    ruleset = load_ruleset()
    rules = ruleset["rules"]
    entity_index = load_entity_index()
    known_entities = {etype: list(entity_index[etype].keys()) for etype in entity_index}

    # 1. 입력 텍스트 파싱 & 정규화
    parsed = parse_entities(input_text, known_entities)
    normalized = normalize_entities(parsed)

    # 2. 사용자 약물 주입
    if user_meds:
        for med in user_meds:
            med_norm = normalize_entities(parse_entities(med, known_entities))
            if med_norm.get("drugs"):
                existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
                for d in med_norm["drugs"]:
                    if d["entity_id"] not in existing_ids:
                        normalized.setdefault("drugs", []).append(d)

    # 3. 상황어 자동 감지
    input_norm = input_text.replace(" ", "")
    if any(kw in input_norm for kw in ["공복", "밥안먹고", "식사안하고", "밥못먹고"]):
        normalized.setdefault("situations", []).append(
            {"raw": "공복", "canonical": "공복 복용", "entity_id": "SITUATION_FASTING"})
    if any(kw in input_norm for kw in ["사우나", "땀많이", "더웠어"]):
        normalized.setdefault("situations", []).append(
            {"raw": "탈수", "canonical": "탈수/수분부족", "entity_id": "SITUATION_DEHYDRATION"})

    # 4. 사용자 질환 주입
    if user_conditions:
        for cond in user_conditions:
            cid = LABEL_TO_ID.get(cond, cond)
            normalized.setdefault("situations", []).append(
                {"raw": cond, "canonical": cond, "entity_id": f"CONDITION_{cid}"})

    # 5. 병용 상황어 자동 주입
    has_multi = len(normalized.get("drugs", [])) >= 2
    has_drug_food = normalized.get("drugs") and normalized.get("foods")
    if has_multi or has_drug_food or normalized.get("drugs") or normalized.get("foods"):
        normalized.setdefault("situations", []).append(
            {"raw": "병용", "canonical": "병용 섭취", "entity_id": "SITUATION_CONCURRENT"})
    if has_multi:
        normalized.setdefault("situations", []).append(
            {"raw": "약물 병용", "canonical": "여러 약물", "entity_id": "SITUATION_DRUG_DUPLICATION"})

    # 공복 음주 복합 상황
    food_ids = [f["entity_id"] for f in normalized.get("foods", [])]
    situ_ids = [s["entity_id"] for s in normalized.get("situations", [])]
    if "FOOD_ALCOHOL" in food_ids and "SITUATION_FASTING" in situ_ids:
        normalized["situations"].append(
            {"raw": "공복 음주", "canonical": "공복 음주", "entity_id": "SITUATION_FASTING_ALCOHOL"})

    # 6. 규칙 매칭 & 위험도 평가
    matched_rules = evaluate_rules(normalized, rules)
    risk_result = assess_risk(normalized, matched_rules)

    # user_conditions을 결과에 포함 (프론트엔드에서 사용)
    risk_result["user_conditions"] = user_conditions or []
    risk_result["input_text"] = input_text

    # 7. LLM 설명 생성 (RAG)
    explanation = ""
    if HAS_EXPLANATION and risk_result.get("risk_level") != "GREEN":
        try:
            explanation = run_explanation({"risk_result": risk_result})
        except Exception as e:
            logging.warning(f"LLM 설명 생성 실패: {e}")
            explanation = ""

    return {
        "input_text": input_text,
        "risk_result": risk_result,
        "explanation": explanation,
        "debug_info": {"entities": normalized}
    }


def analyze_text(text: str, medications: list = None, conditions: list = None):
    """텍스트 기반 분석"""
    return _run_pipeline(text, medications, conditions)


def analyze_image(image_path: str, medications: list = None, conditions: list = None):
    """이미지 기반 분석 (OCR → 텍스트 → 파이프라인)"""
    extracted_text = extract_text_from_image(image_path)
    if not extracted_text:
        return {
            "input_text": "",
            "risk_result": {"risk_level": "GREEN", "risk_code": "GREEN",
                            "representative_rule": None, "entities_involved": {},
                            "evidence_keys": [], "evidence_info": [],
                            "user_conditions": conditions or []},
            "explanation": "이미지에서 텍스트를 인식하지 못했습니다. 다시 촬영해주세요.",
            "debug_info": {"entities": {}}
        }
    return _run_pipeline(extracted_text, medications, conditions)


app = FastAPI(title="SafeEat API")

# CORS 설정
# Render 배포 환경 및 로컬 개발 환경 대응
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://safeeat-frontend.onrender.com", # 실제 배포 URL이 확정되면 여기에 추가
]

# 환경 변수에서 추가 오리진을 받을 수 있도록 설정
env_origins = os.environ.get("ALLOWED_ORIGINS")
if env_origins:
    ALLOWED_ORIGINS.extend(env_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if (os.environ.get("RENDER") == "true" or os.environ.get("NODE_ENV") == "production") else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextAnalysisRequest(BaseModel):
    text: str
    medications: Optional[List[str]] = []
    conditions: Optional[List[str]] = []

class ImageAnalysisRequest(BaseModel):
    pass

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/analyze/text")
async def api_analyze_text(request: TextAnalysisRequest):
    try:
        result = analyze_text(request.text, request.medications, request.conditions)
        
        # 로그 저장
        save_analysis_log(
            request_data={
                "type": "text",
                "text": request.text,
                "medications": request.medications,
                "conditions": request.conditions
            },
            result_data=result
        )
        
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] API analyze/text failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/image")
async def api_analyze_image(
    file: UploadFile = File(...), 
    medications: Optional[str] = Form(None),
    conditions: Optional[str] = Form(None)
):
    # medications, conditions는 JSON string으로 전달받음
    user_meds = []
    if medications:
        try:
            import json
            user_meds = json.loads(medications)
        except:
            pass
            
    user_conditions = []
    if conditions:
        try:
            import json
            user_conditions = json.loads(conditions)
        except:
            pass

    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            result = analyze_image(tmp_path, user_meds, user_conditions)
            
            # 로그 저장
            save_analysis_log(
                request_data={
                    "type": "image",
                    "filename": file.filename,
                    "medications": user_meds,
                    "conditions": user_conditions
                },
                result_data=result
            )
            
            return result
        finally:
            # 작업 완료 후 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        import traceback
        print(f"[ERROR] API analyze/image failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr/prescription")
async def api_ocr_prescription(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            print(f"[OCR_API] 이미지 분석 시작: {tmp_path}")
            # 1. OCR 텍스트 추출
            extracted_text = extract_text_from_image(tmp_path)
            print(f"[OCR_API] 추출된 텍스트: {extracted_text[:150]}...")
            if not extracted_text:
                print("[OCR_API] 추출된 텍스트가 없습니다.")
                return {"prescriptions": [], "drugs": [], "unknown_drugs": [], "status": "FAIL"}

            # 2. 처방전 파서: 약물별 용법/용량 1:1 매핑
            from service.prescription_parser import parse_prescription
            prescriptions = parse_prescription(extracted_text)
            print(f"[OCR_API] 파싱 결과: {prescriptions}")

            # 3. known/unknown 분리
            known_drugs = [p["drug_name"] for p in prescriptions if not p["is_unknown"]]
            unknown_drugs = [p["raw_name"] for p in prescriptions if p["is_unknown"]]

            return {
                "prescriptions": prescriptions,   # 용법/용량 전체 포함
                "drugs": known_drugs,              # 인덱스 매칭된 약물명 (하위 호환)
                "unknown_drugs": unknown_drugs,    # 미등록 약물 후보
                "status": "SUCCESS",
                "raw_text": extracted_text[:200]  # 디버그용
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        import traceback
        print(f"[ERROR] API ocr/prescription failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/weekly")
async def api_weekly_report():
    try:
        report = generate_weekly_report()
        return report
    except Exception as e:
        import traceback
        print(f"[ERROR] API report/weekly failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render는 PORT 환경 변수를 제공하므로 이를 우선 사용합니다.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
