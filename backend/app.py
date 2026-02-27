import os
import shutil
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# main.py에서 분석 로직 가져오기
from main import analyze_text, analyze_image
from src.ocr.processor import extract_text_from_image
from src.utils.logger import save_analysis_log
from src.service.report_service import generate_weekly_report

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
