# ── 1) Builder 스테이지 ──
FROM python:3.10-slim AS builder
WORKDIR /app

# 시스템 패키지 업데이트 및 python 빌드 도구 설치
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── 2) Runtime 스테이지 ──
FROM python:3.10-slim
WORKDIR /app

# 운영에 필요한 네이티브 라이브러리 설치 (OpenCV, GL 등)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx \
      libglib2.0-0 \
      libsm6 \
      libxrender1 \
      libxext6 \
      libpq5 \
 && rm -rf /var/lib/apt/lists/*

# ① Builder 스테이지에서 설치한 파이썬 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin              /usr/local/bin

# ② 애플리케이션 코드 및 정적 파일 복사
COPY app.py           ./app.py
COPY requirements.txt ./requirements.txt
COPY static/          ./static/

# ③ 앱 실행
EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
