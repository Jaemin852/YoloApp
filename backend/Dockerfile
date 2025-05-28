# ── 1) 빌드 스테이지 ──
FROM python:3.10-slim AS builder
WORKDIR /app

# 파이썬 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── 2) 런타임 스테이지 ──
FROM python:3.10-slim AS runtime
WORKDIR /app

# OpenCV 등 네이티브 라이브러리 설치
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 \
 && rm -rf /var/lib/apt/lists/*

# 빌드 스테이지에서 설치된 파이썬 패키지와 실행 파일 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 및 정적 파일만 복사
COPY app.py ./ 
COPY static/ ./static/

# weights는 볼륨으로 마운트할 것이므로 COPY하지 않습니다!

EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
