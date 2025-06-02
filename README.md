# YOLO 객체 탐지 애플리케이션

## 소개 [Description]:
FastAPI + Ultralytics YOLOv8 + Docker Compose + PostgreSQL을 이용해  
이미지 업로드 → 객체 탐지 → 결과 이미지·라벨 표시 → 탐지 이력 저장 및 조회까지  
한 번에 실행되는 “풀스택” 웹 애플리케이션입니다.

---

## 실행 환경 [Environment]:
- **Docker Engine** 20.10.12 이상  
- **Docker Compose** v2.3.3 이상  
  - Docker 설치가 되어 있지 않으면 Docker 설치 필요  

- **(GPU 가속 이용 시)**  
  NVIDIA 드라이버 + NVIDIA Container Toolkit  
  → NVIDIA Container Toolkit (nvidia-docker2) 설치  
  ```bash
  sudo apt-get update
  sudo apt-get install -y nvidia-docker2
  sudo systemctl restart docker
  ```

---

## 주요 파일 [Files]:
- **docker-compose.yml**  
  ▶ 전체 서비스를 정의하는 compose 설정 파일  
  ▶ `yolo-backend`(FastAPI 앱)과 `db`(PostgreSQL) 컨테이너를 함께 기동하도록 구성

- **backend/app.py**  
  ▶ FastAPI 기반의 핵심 애플리케이션 코드

---

## 설치 및 실행 [Usage]:
1. **사전 조건**  
   - Docker & Docker Compose  
   - (GPU 사용 시) NVIDIA 드라이버 + NVIDIA Container Toolkit  

2. **모델 가중치 다운로드**  
   ```bash
   mkdir weights
   cd weights
   curl -L -o yolov8n.pt https://ultralytics.com/assets/yolov8n.pt
   curl -L -o yolov8s.pt https://ultralytics.com/assets/yolov8s.pt
   # 필요 시 yolov8m.pt, yolov8l.pt, yolov8x.pt 등을 추가
   cd ..
   ```

3. **환경 변수 설정**  
   프로젝트 루트에 `.env` 파일을 생성하고, 아래 내용을 작성합니다:  
   ```env
   MODEL_NAME=yolov8n.pt

   DB_USER=admin
   DB_PASS=secretpassword
   DB_NAME=yolodb
   DB_HOST=db
   DB_PORT=5432
   ```

4. **Docker Compose 빌드 & 기동**  
   ```bash
   docker compose down
   docker compose up -d --build
   ```
   - `docker-compose.yml`에 정의된 `yolo-backend`(FastAPI)와 `db`(PostgreSQL) 컨테이너가 동시에 기동됩니다.

5. **웹 UI 접속**  
   브라우저에서 → `http://localhost:5000/`

6. **이미지 업로드 & 탐지**  
   1. 모델 드롭다운에서 원하는 YOLOv8 모델 파일(`yolov8n.pt`, `yolov8s.pt` 등) 선택  
   2. “파일 선택” 버튼으로 이미지 업로드  
   3. “업로드 & 탐지” 버튼 클릭  
   4. 감지된 라벨 목록과, 결과 이미지를 확인

7. **탐지 이력 조회**  
   - “이력 보기” 버튼 클릭 시 `/history` 엔드포인트에서 최근 최대 50개 이력을 가져와 테이블로 출력  
   - 이 테이블에는 ID, 시간, 모델명, 파일명, 라벨 목록이 표시됩니다.
   - 이력을 삭제하려면 아래 명령어를 이용하세요.
   ```bash
   docker compose down -v
   ```