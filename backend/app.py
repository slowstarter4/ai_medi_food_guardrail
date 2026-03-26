import os
import json
import shutil
import tempfile
import logging
import traceback
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from src.rules.loader import load_ruleset
from src.rules.evaluator import evaluate_rules
from service.entity_parser import parse_entities
from service.entity_normalizer import normalize_entities, load_entity_index
from service.llm_entity_parser import parse_entities_with_llm
from src.external_api.drug_info_client import fetch_drug_info_from_api
from src.service.risk_assessor import assess_risk
from src.ocr.processor import extract_text_from_image
from src.utils.logger import save_analysis_log
from src.service.report_service import generate_weekly_report
from src.constants import (
    CLASS_VERIFICATION_KEYWORDS,
    SITUATION_KEYWORD_MAP,
    DISEASE_KEYWORD_MAP,
)

# LLM 설명 생성 (RAG 파이프라인)
try:
    from src.pipeline.explanation_pipeline import run_explanation
    HAS_EXPLANATION = True
except Exception:
    HAS_EXPLANATION = False

logger = logging.getLogger(__name__)

# 질환 라벨 → ID 매핑
LABEL_TO_ID = {
    "고령": "elderly", "고혈압": "hypertension", "당뇨": "diabetes",
    "고지혈증": "hyperlipidemia", "관절염": "arthritis", "천식": "asthma"
}

# AI 경로를 유발하는 트리거 키워드
_AI_TRIGGER_KEYWORDS = [
    "감기", "약", "처방", "성분", "같이", "함께", "먹어",
    "운동", "사우나", "찜질방", "공복", "거름", "안먹", "밥못",
    "매일", "계속", "장기", "한달", "커피", "카페인", "에너지음료",
    "짜게", "젓갈", "국물", "소금", "주스", "자몽"
]


def _detect_situations_from_text(input_text: str, normalized: dict) -> None:
    """입력 텍스트에서 상황어 및 질환명을 자동 감지하여 normalized에 주입"""
    input_norm = input_text.replace(" ", "")

    for keywords, situ_entry in SITUATION_KEYWORD_MAP:
        if any(kw in input_norm for kw in keywords):
            normalized.setdefault("situations", []).append(situ_entry.copy())

    for keyword, situ_entry in DISEASE_KEYWORD_MAP:
        if keyword in input_norm:
            normalized.setdefault("situations", []).append(situ_entry.copy())


def _inject_user_inputs(
    normalized: dict,
    entity_index: dict,
    known_entities: dict,
    user_meds: list,
    user_conditions: list,
    user_situations: list,
) -> None:
    """사용자 수동 입력(약물, 질환, 상황칩)을 normalized에 주입"""
    # 1. 사용자 약물 주입
    if user_meds:
        for med in user_meds:
            med_norm = normalize_entities(parse_entities(med, known_entities), source="manual")
            if med_norm.get("drugs"):
                existing_raws = [d["raw"] for d in normalized.get("drugs", [])]
                existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
                for d in med_norm["drugs"]:
                    if d["entity_id"] not in existing_ids and d["raw"] not in existing_raws:
                        normalized.setdefault("drugs", []).append(d)

    # 2. 사용자 질환(칩) 주입
    if user_conditions:
        for cond in user_conditions:
            cid = LABEL_TO_ID.get(cond, cond)
            normalized.setdefault("situations", []).append(
                {"raw": cond, "canonical": cond, "entity_id": f"CONDITION_{cid}"})

    # 3. 사용자 상황(칩) 주입
    if user_situations:
        for situ in user_situations:
            s_clean = situ.strip()
            sid = entity_index.get("situations", {}).get(s_clean, "UNKNOWN")
            if sid == "UNKNOWN":
                sid = entity_index.get("foods", {}).get(s_clean, "UNKNOWN")

            logger.debug(f"Processing user_situation: '{s_clean}' -> ID: {sid}")
            if sid == "UNKNOWN":
                sid = situ if situ.startswith("SITUATION_") else "UNKNOWN"

            existing_sids = [s["entity_id"] for s in normalized.get("situations", [])]
            if sid not in existing_sids:
                normalized.setdefault("situations", []).append(
                    {"raw": situ, "canonical": situ, "entity_id": sid})

            if sid.startswith("FOOD_") or sid.startswith("NUTRITION_"):
                existing_fids = [f["entity_id"] for f in normalized.get("foods", [])]
                if sid not in existing_fids:
                    normalized.setdefault("foods", []).append(
                        {"raw": situ, "entity_id": sid, "match_type": "manual"})


def _inject_compound_situations(normalized: dict) -> None:
    """병용 섭취 등 복합 상황어를 자동으로 주입"""
    has_multi = len(normalized.get("drugs", [])) >= 2
    has_drug_food = normalized.get("drugs") and normalized.get("foods")

    if has_multi or has_drug_food or normalized.get("drugs") or normalized.get("foods"):
        normalized.setdefault("situations", []).append(
            {"raw": "병용", "canonical": "병용 섭취", "entity_id": "SITUATION_CONCURRENT"})
    if has_multi:
        normalized.setdefault("situations", []).append(
            {"raw": "약물 병용", "canonical": "여러 약물", "entity_id": "SITUATION_DRUG_DUPLICATION"})

    food_ids = [f["entity_id"] for f in normalized.get("foods", [])]
    situ_ids = [s["entity_id"] for s in normalized.get("situations", [])]
    if "SITUATION_FASTING" in situ_ids and "FOOD_ALCOHOL" in food_ids:
        if "SITUATION_FASTING_ALCOHOL" not in situ_ids:
            normalized.setdefault("situations", []).append(
                {"raw": "공복 음주", "canonical": "공복 음주", "entity_id": "SITUATION_FASTING_ALCOHOL"})


def _run_pipeline(input_text: str, user_meds: list = None, user_conditions: list = None, user_situations: list = None):
    """핵심 분석 파이프라인: 고속 로컬 매칭 → (필요시) LLM 추론 → API 교차 검증 → 규칙 매칭"""
    ruleset = load_ruleset()
    rules = ruleset["rules"]
    entity_index = load_entity_index()
    known_entities = {etype: list(entity_index[etype].keys()) for etype in entity_index}

    # 1. [Fast Path] 로컬 색인 매칭
    parsed = parse_entities(input_text, known_entities)
    normalized = normalize_entities(parsed, source="ocr")
    for d in normalized.get("drugs", []):
        d["verification_status"] = "VERIFIED"

    # 2. [AI Path] 하이브리드 판단
    text_no_space = input_text.replace(" ", "")
    needs_ai = (
        not normalized.get("drugs")
        or any(kw in text_no_space for kw in _AI_TRIGGER_KEYWORDS)
    )

    if needs_ai:
        ai_normalized = parse_entities_with_llm(input_text)

        # 3. [Cross-Check] 공공 API를 통한 AI 추론 검증
        for ai_item in ai_normalized.get("drugs", []):
            existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
            if ai_item["entity_id"] == "UNKNOWN" or ai_item["entity_id"] in existing_ids:
                continue

            search_name = ai_item.get("corrected_name") or ai_item["raw"]
            inferred_class = ai_item.get("inferred_class", "UNKNOWN")

            api_data = fetch_drug_info_from_api(search_name)
            if not api_data and search_name != ai_item["raw"]:
                api_data = fetch_drug_info_from_api(ai_item["raw"])

            is_verified = False
            if api_data and "summary" in api_data:
                keywords = CLASS_VERIFICATION_KEYWORDS.get(inferred_class, [])
                summary = api_data["summary"]
                if any(kw in summary for kw in keywords):
                    is_verified = True
                elif ai_item.get("confidence", 0) >= 0.95:
                    is_verified = True

            ai_item["verification_status"] = "VERIFIED" if is_verified else "INFERRED"
            normalized.setdefault("drugs", []).append(ai_item)

        # 식품 및 상황 병합
        for etype in ["foods", "situations"]:
            existing_ids = [item["entity_id"] for item in normalized.get(etype, [])]
            existing_raws_clean = [item["raw"].replace(" ", "") for item in normalized.get(etype, [])]

            for ai_item in ai_normalized.get(etype, []):
                ai_raw_clean = ai_item["raw"].replace(" ", "")
                is_overlap = any(ai_raw_clean in er or er in ai_raw_clean for er in existing_raws_clean)

                if ai_item["entity_id"] != "UNKNOWN" and ai_item["entity_id"] not in existing_ids and not is_overlap:
                    normalized.setdefault(etype, []).append(ai_item)

    # 4. 텍스트 기반 상황어 자동 감지 + 사용자 입력 주입
    _detect_situations_from_text(input_text, normalized)
    _inject_user_inputs(normalized, entity_index, known_entities, user_meds, user_conditions, user_situations)
    _inject_compound_situations(normalized)

    # 5. 규칙 매칭 & 위험도 평가
    logger.debug("Starting evaluate_rules...")
    logger.debug(f"Drugs to check: {[d['entity_id'] for d in normalized.get('drugs', [])]}")
    logger.debug(f"Foods to check: {[f['entity_id'] for f in normalized.get('foods', [])]}")
    logger.debug(f"Situations to check: {[s['entity_id'] for s in normalized.get('situations', [])]}")

    matched_rules = evaluate_rules(normalized, rules)
    logger.debug(f"matched_rules count: {len(matched_rules)}")
    for r in matched_rules:
        logger.debug(f"Matched Rule ID: {r['rule_id']} (Level: {r.get('level')}, Risk: {r.get('risk_level_hint')})")

    risk_result = assess_risk(normalized, matched_rules)
    logger.debug(f"Final Risk Result: {risk_result.get('risk_level')}")

    # 6. DUR 상호작용 체크 (보조 정보)
    drug_names = [d["raw"] for d in normalized.get("drugs", [])]
    dur_alerts = []
    if len(drug_names) >= 2:
        from src.external_api.dur_client import get_drug_interaction
        dur_alerts = get_drug_interaction(drug_names)

    risk_result["supplementary_info"] = {
        "dur_alerts": dur_alerts,
        "api_verified_drugs": [d["raw"] for d in normalized.get("drugs", []) if d.get("verification_status") == "VERIFIED"]
    }
    risk_result["user_conditions"] = user_conditions or []
    risk_result["input_text"] = input_text

    # 7. LLM 설명 생성 (RAG)
    explanation = ""
    if HAS_EXPLANATION and (risk_result.get("risk_level") != "GREEN" or dur_alerts):
        try:
            explanation = run_explanation({"risk_result": risk_result})
        except Exception as e:
            logger.warning(f"LLM 설명 생성 실패: {e}")

    all_candidates = [
        cand
        for d in normalized.get("drugs", [])
        if d.get("match_type") == "candidate"
        for cand in d.get("candidates", [])
    ]

    return {
        "input_text": input_text,
        "risk_result": risk_result,
        "explanation": explanation,
        "candidates": all_candidates,
        "debug_info": {"entities": normalized}
    }


def analyze_text(text: str, medications: list = None, conditions: list = None, situations: list = None):
    """텍스트 기반 분석"""
    return _run_pipeline(text, medications, conditions, situations)


def analyze_image(image_path: str, medications: list = None, conditions: list = None, situations: list = None):
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
    return _run_pipeline(extracted_text, medications, conditions, situations)


app = FastAPI(title="SafeEat API")

# CORS 설정
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://safeeat-frontend.onrender.com",
]

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
    situations: Optional[List[str]] = []


class ImageAnalysisRequest(BaseModel):
    pass


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/analyze/text")
async def api_analyze_text(request: TextAnalysisRequest):
    try:
        result = analyze_text(request.text, request.medications, request.conditions, request.situations)
        save_analysis_log(
            request_data={
                "type": "text",
                "text": request.text,
                "medications": request.medications,
                "conditions": request.conditions,
                "situations": request.situations
            },
            result_data=result
        )
        return result
    except Exception as e:
        logger.error(f"API analyze/text failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/image")
async def api_analyze_image(
    file: UploadFile = File(...),
    medications: Optional[str] = Form(None),
    conditions: Optional[str] = Form(None),
    manual_situations: Optional[str] = Form(None)
):
    user_meds = []
    if medications:
        try:
            user_meds = json.loads(medications)
        except Exception as e:
            logger.warning(f"medications JSON 파싱 실패: {e}")

    user_conditions = []
    if conditions:
        try:
            user_conditions = json.loads(conditions)
        except Exception as e:
            logger.warning(f"conditions JSON 파싱 실패: {e}")

    user_situations = []
    if manual_situations:
        try:
            user_situations = json.loads(manual_situations)
        except Exception as e:
            logger.warning(f"manual_situations JSON 파싱 실패: {e}")

    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            result = analyze_image(tmp_path, user_meds, user_conditions, user_situations)
            save_analysis_log(
                request_data={
                    "type": "image",
                    "filename": file.filename,
                    "medications": user_meds,
                    "conditions": user_conditions,
                    "situations": user_situations
                },
                result_data=result
            )
            return result
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        logger.error(f"API analyze/image failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr/prescription")
async def api_ocr_prescription(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        try:
            logger.info(f"[OCR_API] 이미지 분석 시작: {tmp_path}")
            extracted_text = extract_text_from_image(tmp_path)
            logger.info(f"[OCR_API] 추출된 텍스트: {extracted_text[:150]}...")
            if not extracted_text:
                logger.warning("[OCR_API] 추출된 텍스트가 없습니다.")
                return {"prescriptions": [], "drugs": [], "unknown_drugs": [], "status": "FAIL"}

            from service.prescription_parser import parse_prescription
            prescriptions = parse_prescription(extracted_text)
            logger.info(f"[OCR_API] 파싱 결과: {prescriptions}")

            known_drugs = [p["drug_name"] for p in prescriptions if not p["is_unknown"]]
            unknown_drugs = [p["raw_name"] for p in prescriptions if p["is_unknown"]]

            return {
                "prescriptions": prescriptions,
                "drugs": known_drugs,
                "unknown_drugs": unknown_drugs,
                "status": "SUCCESS",
                "raw_text": extracted_text[:200]
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        logger.error(f"API ocr/prescription failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/weekly")
async def api_weekly_report():
    try:
        report = generate_weekly_report()
        return report
    except Exception as e:
        logger.error(f"API report/weekly failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    is_dev = os.environ.get("RENDER") != "true"
    if is_dev:
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=port)
