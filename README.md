# YOLO Docker 웹앱 (DB 통합 버전)

FastAPI + Ultralytics YOLOv8 + Docker Compose + PostgreSQL을 이용해  
이미지 업로드 → 객체 탐지 → 결과 이미지·라벨 표시 → 탐지 이력 저장 및 조회까지  
한 번에 실행되는 “풀스택” 웹 애플리케이션입니다.

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

### 1. 사전 조건
- Docker & Docker Compose  
- (GPU 사용 시) NVIDIA 드라이버 + NVIDIA Container Toolkit  

### 2. 모델 가중치 다운로드
```bash
mkdir weights
cd weights
curl -L -o yolov8n.pt https://ultralytics.com/assets/yolov8n.pt
curl -L -o yolov8s.pt https://ultralytics.com/assets/yolov8s.pt
# 필요 시 yolov8m.pt, yolov8l.pt, yolov8x.pt 등을 추가
cd ..
```

### 3. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고, 아래 내용을 작성합니다:
```env
MODEL_NAME=yolov8n.pt

DB_USER=admin
DB_PASS=secretpassword
DB_NAME=yolodb
DB_HOST=db
DB_PORT=5432
```

### 4. Docker Compose 빌드 & 기동
```bash
docker compose down
docker compose up -d --build
```

- `docker-compose.yml`에 정의된 `yolo-backend`(FastAPI)와 `db`(PostgreSQL) 컨테이너가 동시에 기동됩니다.

### 5. 웹 UI 접속
브라우저에서 → `http://localhost:5000/`

### 6. 이미지 업로드 & 탐지
1. 모델 드롭다운에서 원하는 YOLOv8 모델 파일(`yolov8n.pt`, `yolov8s.pt` 등) 선택  
2. “파일 선택” 버튼으로 이미지 업로드  
3. “업로드 & 탐지” 버튼 클릭  
4. 하단에 감지된 라벨 목록과, `/outputs`에 저장된 결과 이미지를 확인

### 7. 탐지 이력 조회
- “이력 보기” 버튼 클릭 시 `/history` 엔드포인트에서 최근 최대 50개 이력을 가져와 테이블로 출력  
- 이 테이블에는 ID, 한국 표준시 기준의 탐지 시간, 모델명, 파일명, 라벨 목록이 표시됩니다.

---

## 🛠️ Docker 활용 기능

1. **Multi-stage Build**  
   - Builder 스테이지에서 Python 의존성(`requirements.txt`) 설치  
   - Runtime 스테이지에는 빌드 결과만 복사해 경량화된 이미지를 생성

2. **GPU 지원**  
   - `deploy.resources.reservations.devices`에 `driver: nvidia`, `capabilities: [gpu]` 설정  
   - 컨테이너 내부에서 YOLO 추론 시 GPU를 사용해 속도 향상

3. **Volumes (데이터 영속화)**  
   - `weights` 폴더: 호스트에 저장된 모델 가중치를 `/app/weights`로 마운트  
   - `outputs` 볼륨: `/app/outputs`에 결과 이미지 저장, 컨테이너 재시작 후에도 데이터 유지  
   - `db-data` 볼륨: PostgreSQL 데이터 디렉터리(`/var/lib/postgresql/data`)로 마운트해 DB 데이터 영속화

4. **Environment & `.env`**  
   - `.env` 파일에 모델 이름 및 DB 접속 정보 정의  
   - `docker-compose.yml`의 `env_file`에서 불러와 컨테이너 실행 시 설정

5. **Healthcheck & depends_on**  
   - `db` 서비스: `pg_isready -U ${DB_USER}` 헬스체크  
   - `yolo-backend` 서비스: `/health` 헬스체크  
   - `yolo-backend`는 `depends_on: db.condition=service_healthy`로 DB 준비 후 기동

6. **Restart Policy**  
   - `restart: always` 적용해 애플리케이션이나 DB가 예기치 않게 종료돼도 자동 재시작

7. **Network (네트워크 격리)**  
   - `yolo-net` 브리지 네트워크를 생성해, 애플리케이션과 DB가 같은 네트워크에서만 통신

---


