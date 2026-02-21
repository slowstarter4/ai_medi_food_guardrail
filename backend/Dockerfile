FROM python:3.11-slim

WORKDIR /app

# 시스템 라이브러리 설치 (필요한 경우)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 종속성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 앱 실행
CMD ["python", "app.py"]
