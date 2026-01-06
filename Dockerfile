# 1. 가벼운 파이썬 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 파일들 복사
COPY omnihub-web/ .

# 4. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. Cloud Run은 PORT 환경 변수를 사용하므로 이에 맞춰 실행
ENV PORT 8080
EXPOSE 8080

# 6. Streamlit 실행 명령
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]