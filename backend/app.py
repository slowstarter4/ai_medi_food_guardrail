import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# main.py에서 분석 로직 가져오기
from main import analyze_text, analyze_image

app = FastAPI(title="SafeEat API")

# CORS 설정: Vite 개발 서버 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 구체적인 오리진 지정 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextAnalysisRequest(BaseModel):
    text: str

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/analyze/text")
async def api_analyze_text(request: TextAnalysisRequest):
    try:
        result = analyze_text(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/image")
async def api_analyze_image(file: UploadFile = File(...)):
    # 임시 파일로 저장하여 분석 로직에 전달
    try:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        try:
            result = analyze_image(tmp_path)
            return result
        finally:
            # 작업 완료 후 임시 파일 삭제
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
