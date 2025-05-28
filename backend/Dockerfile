 FROM python:3.10-slim AS builder
 WORKDIR /app

 COPY requirements.txt .
 RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

 FROM python:3.10-slim AS runtime
 WORKDIR /app

 RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 \
  && rm -rf /var/lib/apt/lists/*

 # Python 패키지 & 바이너리 복사
 COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
 COPY --from=builder /usr/local/bin /usr/local/bin

 # 애플리케이션 및 정적 파일
 COPY app.py static/ ./

 EXPOSE 5000
 CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
