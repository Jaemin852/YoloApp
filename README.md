# YOLO Docker 웹앱

FastAPI + Ultralytics YOLOv8 + Docker Compose를 이용해  
이미지 업로드 → 객체 탐지 → 결과 이미지·라벨 표시까지 한 번에 실행되는  
“풀스택” 웹 애플리케이션입니다.

---

## 🔥 주요 기능

- **이미지 업로드 & YOLOv8 객체 탐지**
- **실시간 웹UI**: 업로드 버튼 클릭 한 번으로 결과 확인
- **Docker Compose**: 멀티스테이지 빌드 & GPU 지원
- **StaticFiles 서빙**: 프론트엔드(CSS/JS), 결과 이미지
- **Healthcheck & Restart Policy**: 안정적 서비스 운영

---

## 🚀 기술 스택

- **Backend**: Python 3.10, FastAPI, Ultralytics YOLOv8, Uvicorn
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Containerization**: Docker, Docker Compose, NVIDIA Container Toolkit

---

## ⚙️ 설치 및 실행

1. **사전 조건**
   - Docker & Docker Compose
   - (GPU 사용 시) NVIDIA 드라이버 + NVIDIA Container Toolkit

2. **모델 가중치 다운로드**
   ```bash
   mkdir weights
   cd weights
   curl -L -o yolov8n.pt https://ultralytics.com/assets/yolov8n.pt
   cd ..
   ```

3. **환경 변수 설정**
   프로젝트 루트에 `.env` 파일을 생성하고,
   ```env
   MODEL_NAME=yolov8n.pt
   ```

4. **빌드 & 기동**
   ```bash
   docker compose up -d --build
   ```

5. **웹 UI 접속**
   브라우저에서 → `http://localhost:5000/`

6. **이미지 업로드 & 탐지**
   - “파일 선택” 후 “업로드 & 탐지” 버튼 클릭
   - 하단에 감지된 객체 라벨과 결과 이미지 표시

---

## 🛠️ 활용된 Docker 주요 기능

- **Multi-stage Build**: 빌드·런타임 스테이지 분리
- **GPU 지원**: `device_requests` 로 NVIDIA GPU 할당
- **Volumes**: `weights/`, `outputs/` 영속화
- **Environment & .env**: 모델명 설정 분리
- **Healthcheck**: `/health` 엔드포인트 헬스체크
- **Restart Policy**: `restart: always` 로 장애 자동 복구

---


