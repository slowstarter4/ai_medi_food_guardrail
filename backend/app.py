import os
import shutil
import tempfile
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# main.py에서 분석 로직 가져오기
from main import analyze_text, analyze_image
from src.ocr.processor import extract_text_from_image

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
        return result
    except Exception as e:
        import traceback
        print(f"[ERROR] API analyze/text failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/image")
async def api_analyze_image(
    file: UploadFile = File(...), 
    medications: Optional[str] = None,
    conditions: Optional[str] = None
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
            # 1. OCR을 통한 텍스트 추출
            extracted_text = extract_text_from_image(tmp_path)
            print(f"[OCR_API] 추출된 텍스트: {extracted_text[:100]}...")
            if not extracted_text:
                print("[OCR_API] 추출된 텍스트가 없습니다.")
                return {"drugs": [], "status": "FAIL"}

            # 2. 텍스트에서 약물 엔티티 추출
            # entity_index를 사용하여 알려진 약물들만 필터링
            from service.entity_normalizer import load_entity_index
            from service.entity_parser import parse_entities
            
            entity_index = load_entity_index()
            known_entities = { "drugs": list(entity_index["drugs"].keys()) }
            
            parsed = parse_entities(extracted_text, known_entities)
            print(f"[OCR_API] 파싱된 결과: {parsed}")
            
            # 중복 제거 및 리턴 (원형 이름 유지)
            unique_drugs = list(set(parsed.get("drugs", [])))
            
            return {
                "drugs": unique_drugs,
                "status": "SUCCESS",
                "raw_text": extracted_text[:200] # 디버그용
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        import traceback
        print(f"[ERROR] API ocr/prescription failed: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Render는 PORT 환경 변수를 제공하므로 이를 우선 사용합니다.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
