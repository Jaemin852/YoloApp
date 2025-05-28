# 1) Builder 스테이지
FROM python:3.10-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 2) Runtime 스테이지
FROM python:3.10-slim
WORKDIR /app

# OpenCV, PIL 등의 네이티브 라이브러리
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin              /usr/local/bin

# 앱 코드 및 정적 파일 복사
COPY app.py        ./app.py
COPY requirements.txt ./
COPY static/       ./static/

EXPOSE 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
