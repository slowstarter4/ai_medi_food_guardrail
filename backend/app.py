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
from service.llm_entity_parser import parse_entities_with_llm
from src.external_api.drug_info_client import fetch_drug_info_from_api
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


def _run_pipeline(input_text: str, user_meds: list = None, user_conditions: list = None, user_situations: list = None):
    """핵심 분석 파이프라인: 고속 로컬 매칭 → (필요시) LLM 추론 → API 교차 검증 → 규칙 매칭"""
    ruleset = load_ruleset()
    rules = ruleset["rules"]
    entity_index = load_entity_index()
    known_entities = {etype: list(entity_index[etype].keys()) for etype in entity_index}

    # 1. [Fast Path] 로컬 색인 매칭
    parsed = parse_entities(input_text, known_entities)
    normalized = normalize_entities(parsed, source="ocr") # 기본 분석 요청은 OCR/텍스트 입력을 의미
    # 로컬 매칭은 이미 검증된 것으로 간주
    for d in normalized.get("drugs", []):
        d["verification_status"] = "VERIFIED"

    # 2. [AI Path] 하이브리드 판단
    needs_ai = False
    if not normalized.get("drugs"):
        needs_ai = True
    else:
        # 상황적 맥락이나 식품/약물 상호작용 의심 키워드 확장
        trigger_keywords = [
            "감기", "약", "처방", "성분", "같이", "함께", "먹어", 
            "운동", "사우나", "찜질방", "공복", "거름", "안먹", "밥못",
            "매일", "계속", "장기", "한달", "커피", "카페인", "에너지음료",
            "짜게", "젓갈", "국물", "소금", "주스", "자몽"
        ]
        text_no_space = input_text.replace(" ", "")
        if any(kw in text_no_space for kw in trigger_keywords):
            needs_ai = True

    if needs_ai:
        ai_normalized = parse_entities_with_llm(input_text)
        
        # 3. [Cross-Check] 공공 API를 통한 AI 추론 검증
        for ai_item in ai_normalized.get("drugs", []):
            existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
            if ai_item["entity_id"] != "UNKNOWN" and ai_item["entity_id"] not in existing_ids:
                
                # API 교차 확인 로직 (교정된 이름 우선)
                search_name = ai_item.get("corrected_name") or ai_item["raw"]
                inferred_class = ai_item.get("inferred_class", "UNKNOWN")
                
                api_data = fetch_drug_info_from_api(search_name)
                # 교정된 이름으로 실패 시 원본으로 재시도
                if not api_data and search_name != ai_item["raw"]:
                    api_data = fetch_drug_info_from_api(ai_item["raw"])

                is_verified = False
                if api_data and "summary" in api_data:
                    # 계열별 키워드 매칭 고도화
                    check_map = {
                        "DECONGESTANT": ["코막힘", "비충혈", "비염", "감기", "교감신경"],
                        "NSAID": ["해열", "진통", "소염", "염증", "비스테로이드"],
                        "PAINKILLER": ["해열", "진통", "통증"],
                        "HTN_MED": ["혈압", "고혈압", "채널차단"],
                        "DIABETES_MED": ["당뇨", "혈당", "메트포르민"],
                        "STATIN": ["고지혈증", "콜레스테롤", "이상지질혈증"],
                        "ANTIHISTAMINE": ["알레르기", "비염", "가려움", "두드러기", "항히스타민"],
                        "DIGESTIVE": ["소화", "위장", "위염", "속쓰림", "제산"]
                    }
                    keywords = check_map.get(inferred_class, [])
                    summary = api_data["summary"]
                    if any(kw in summary for kw in keywords):
                        is_verified = True
                    # LLM 확신도가 매우 높고 API에서 데이터가 검색된 경우 (이름 일치율 높음) 검증 성공 간주
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
                # 이미 exact match로 찾은 엔티티와 raw text가 겹치면 LLM의 할루시네이션 방지를 위해 스킵
                is_overlap = any(ai_raw_clean in er or er in ai_raw_clean for er in existing_raws_clean)
                
                if ai_item["entity_id"] != "UNKNOWN" and ai_item["entity_id"] not in existing_ids and not is_overlap:
                    normalized.setdefault(etype, []).append(ai_item)

    # 2. 사용자 약물 주입
    if user_meds:
        for med in user_meds:
            med_norm = normalize_entities(parse_entities(med, known_entities), source="manual")
            if med_norm.get("drugs"):
                existing_raws = [d["raw"] for d in normalized.get("drugs", [])]
                existing_ids = [d["entity_id"] for d in normalized.get("drugs", [])]
                for d in med_norm["drugs"]:
                    # 동일한 raw 이름이거나 동일한 ID면 추가하지 않음 (중복 방지)
                    if d["entity_id"] not in existing_ids and d["raw"] not in existing_raws:
                        normalized.setdefault("drugs", []).append(d)

    # 3. 상황어 자동 감지 고도화
    input_norm = input_text.replace(" ", "")
    if any(kw in input_norm for kw in ["공복", "밥안먹", "식사안", "밥못", "식사거름", "아침안", "금식", "빈속", "굶", "식사못", "밥못드"]):
        normalized.setdefault("situations", []).append(
            {"raw": "공복", "canonical": "공복 복용", "entity_id": "SITUATION_FASTING"})
    if any(kw in input_norm for kw in ["사우나", "찜질방", "땀많이", "더웠", "땀흘린", "탈수", "수분부족", "땀나", "목말", "갈증"]):
        normalized.setdefault("situations", []).append(
            {"raw": "탈수", "canonical": "탈수/수분부족", "entity_id": "SITUATION_DEHYDRATION"})
    if any(kw in input_norm for kw in ["중복", "두개", "두가지", "또먹", "추가로먹", "한번에", "같이먹어", "함께먹어"]):
        normalized.setdefault("situations", []).append(
            {"raw": "중복복용", "canonical": "중복 복용", "entity_id": "SITUATION_DUPLICATION"})
    if any(kw in input_norm for kw in ["운동", "격한", "헬스", "달리기"]):
        normalized.setdefault("situations", []).append(
            {"raw": "운동", "canonical": "격한 운동", "entity_id": "SITUATION_EXERCISE"})
    if any(kw in input_norm for kw in ["매일", "계속", "장기", "한달", "연속"]):
        normalized.setdefault("situations", []).append(
            {"raw": "장기복용", "canonical": "장기 연속 복용", "entity_id": "SITUATION_LONG_TERM_USE"})
    if any(kw in input_norm for kw in ["불규칙", "제때", "들쑥날쑥"]):
        normalized.setdefault("situations", []).append(
            {"raw": "불규칙식사", "canonical": "불규칙한 식사", "entity_id": "SITUATION_MEAL_IRREGULAR"})

    # 질환명(고혈압, 당뇨)이 텍스트에 포함되어 있으면 페르소나 컨텍스트 강제 주입
    if "고혈압" in input_norm:
        normalized.setdefault("situations", []).append(
            {"raw": "고혈압", "canonical": "고혈압", "entity_id": "CONDITION_hypertension"})
    if "당뇨" in input_norm:
        normalized.setdefault("situations", []).append(
            {"raw": "당뇨", "canonical": "당뇨", "entity_id": "CONDITION_diabetes"})

    # 4. 사용자 질환 및 상황(칩) 주입
    if user_conditions:
        for cond in user_conditions:
            cid = LABEL_TO_ID.get(cond, cond)
            normalized.setdefault("situations", []).append(
                {"raw": cond, "canonical": cond, "entity_id": f"CONDITION_{cid}"})

    if user_situations:
        for situ in user_situations:
            # entity_index의 situations 및 foods에서 ID 조회
            s_clean = situ.strip()
            sid = "UNKNOWN"
            # 1. 상황어 사전에서 먼저 조회
            sid = entity_index.get("situations", {}).get(s_clean, "UNKNOWN")
            # 2. 식품 사전에서도 조회 (예: '음주' -> FOOD_ALCOHOL)
            if sid == "UNKNOWN":
                sid = entity_index.get("foods", {}).get(s_clean, "UNKNOWN")
            
            print(f"DEBUG: Processing user_situation: '{s_clean}' -> ID: {sid}")
            if sid == "UNKNOWN":
                # 직접 ID로 왔을 가능성 대비 (예: SITUATION_FASTING)
                sid = situ if situ.startswith("SITUATION_") else "UNKNOWN"
            
            # 기존에 없는 경우에만 추가
            existing_sids = [s["entity_id"] for s in normalized.get("situations", [])]
            if sid not in existing_sids:
                normalized.setdefault("situations", []).append(
                    {"raw": situ, "canonical": situ, "entity_id": sid})
            
            # 만약 식품 관련 ID라면 foods 리스트에도 추가 (상호작용 연동을 위함)
            if sid.startswith("FOOD_") or sid.startswith("NUTRITION_"):
                existing_fids = [f["entity_id"] for f in normalized.get("foods", [])]
                if sid not in existing_fids:
                    normalized.setdefault("foods", []).append(
                        {"raw": situ, "entity_id": sid, "match_type": "manual"})

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
    has_fasting = "SITUATION_FASTING" in situ_ids
    has_alcohol = "FOOD_ALCOHOL" in food_ids # 사용자가 칩으로 입력할 때 음주는 FOOD_ALCOHOL로 맵핑됨
    
    if has_fasting and has_alcohol:
        if "SITUATION_FASTING_ALCOHOL" not in situ_ids:
            normalized.setdefault("situations", []).append(
                {"raw": "공복 음주", "canonical": "공복 음주", "entity_id": "SITUATION_FASTING_ALCOHOL"}
            )

    # 6. 규칙 매칭 & 위험도 평가 (Tier 1: 자체 룰셋)
    print(f"DEBUG: Starting evaluate_rules...")
    print(f"DEBUG: Drugs to check: {[d['entity_id'] for d in normalized.get('drugs', [])]}")
    print(f"DEBUG: Foods to check: {[f['entity_id'] for f in normalized.get('foods', [])]}")
    print(f"DEBUG: Situations to check: {[s['entity_id'] for s in normalized.get('situations', [])]}")
    
    matched_rules = evaluate_rules(normalized, rules)
    print(f"DEBUG: matched_rules count: {len(matched_rules)}")
    for r in matched_rules:
        print(f"DEBUG: Matched Rule ID: {r['rule_id']} (Level: {r.get('level')}, Risk: {r.get('risk_level_hint')})")

    risk_result = assess_risk(normalized, matched_rules)
    print(f"DEBUG: Final Risk Result: {risk_result.get('risk_level')}")

    # 7. DUR 상호작용 체크 (Tier 2: 보조 정보)
    drug_names = [d["raw"] for d in normalized.get("drugs", [])]
    dur_alerts = []
    if len(drug_names) >= 2:
        from src.external_api.dur_client import get_drug_interaction
        dur_alerts = get_drug_interaction(drug_names)
    
    risk_result["supplementary_info"] = {
        "dur_alerts": dur_alerts,
        "api_verified_drugs": [d["raw"] for d in normalized.get("drugs", []) if d.get("verification_status") == "VERIFIED"]
    }

    # user_conditions을 결과에 포함 (프론트엔드에서 사용)
    risk_result["user_conditions"] = user_conditions or []
    risk_result["input_text"] = input_text

    # 8. LLM 설명 생성 (RAG)
    explanation = ""
    if HAS_EXPLANATION and (risk_result.get("risk_level") != "GREEN" or dur_alerts):
        try:
            explanation = run_explanation({"risk_result": risk_result})
        except Exception as e:
            logging.warning(f"LLM 설명 생성 실패: {e}")
            explanation = ""

    # 9. 응답 구성 (후보군 포함)
    all_candidates = []
    for d in normalized.get("drugs", []):
        if d.get("match_type") == "candidate":
            all_candidates.extend(d.get("candidates", []))

    return {
        "input_text": input_text,
        "risk_result": risk_result,
        "explanation": explanation,
        "candidates": all_candidates, # 프론트엔드에서 보정 다이얼로그 노출용
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
        
        # 로그 저장
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
        import traceback
        print(f"[ERROR] API analyze/text failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/image")
async def api_analyze_image(
    file: UploadFile = File(...), 
    medications: Optional[str] = Form(None),
    conditions: Optional[str] = Form(None),
    manual_situations: Optional[str] = Form(None)
):
    # medications, conditions, situations는 JSON string으로 전달받음
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

    user_situations = []
    if manual_situations:
        try:
            import json
            user_situations = json.loads(manual_situations)
        except:
            pass

    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            result = analyze_image(tmp_path, user_meds, user_conditions, user_situations)
            
            # 로그 저장
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
    # 로컬 개발 환경에서는 hot-reload를 활성화합니다.
    is_dev = os.environ.get("RENDER") != "true"
    if is_dev:
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=port)
