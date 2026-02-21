FROM node:20-slim

WORKDIR /app

# 종속성 파일 복사 및 설치
COPY package*.json ./
RUN npm install

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 5173

# 앱 실행 (데모용이므로 dev 서버 사용)
CMD ["npm", "run", "dev", "--", "--host"]
