import os
import io
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError
from PIL import Image
from ultralytics import YOLO

# ───── DB 설정 ────────────────────────────────────────────────────
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "secretpassword")
DB_NAME = os.getenv("DB_NAME", "yolodb")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

# history 테이블: id, timestamp, model, filename, labels(JSON 문자열)
history = Table(
    "history",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("timestamp", DateTime, nullable=False),
    Column("model", String(50), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("labels", Text, nullable=False),
)

# 테이블 생성 (컨테이너 시작 시 한 번만 실행)
def create_tables():
    try:
        metadata.create_all(engine)
    except SQLAlchemyError as e:
        print("Error creating tables:", e)

# ───── YOLO 애플리케이션 설정 ─────────────────────────────────────
app = FastAPI()

WEIGHTS_DIR   = "weights"
DEFAULT_MODEL = os.getenv("MODEL_NAME", "yolov8n.pt")
model_cache   = {}

def get_model(name: str):
    path = os.path.join(WEIGHTS_DIR, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"모델 파일 '{name}'이 weights 디렉터리에 없습니다.")
    if name not in model_cache:
        model_cache[name] = YOLO(path)
    return model_cache[name]

@app.on_event("startup")
async def on_startup():
    # ① DB 연결 확인 및 테이블 생성
    create_tables()

# ── 정적 파일 서빙 ───────────────────────────────────────────────────
app.mount("/static" , StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTMLResponse(open("static/index.html", encoding="utf-8").read())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/models")
async def list_models():
    # weights 폴더에서 yolov8*.pt 파일만 반환
    files = sorted(f for f in os.listdir(WEIGHTS_DIR) if f.startswith("yolov8") and f.endswith(".pt"))
    return {"models": files, "default": DEFAULT_MODEL}

@app.post("/infer")
async def infer(
    file: UploadFile = File(...),
    model: str = Query(DEFAULT_MODEL, description="사용할 YOLOv8 모델 파일명")
):
    # 1) 선택한 모델 로드
    try:
        detector = get_model(model)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    # 2) 이미지 바이트 → PIL.Image
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # 3) YOLO 추론
    results = detector.predict(source=image, save=False)
    cls_idxs = results[0].boxes.cls.tolist()
    labels   = [detector.names[int(i)] for i in cls_idxs]

    # 4) 결과 이미지 저장
    out_name = file.filename
    annotated = results[0].plot()
    os.makedirs("outputs", exist_ok=True)
    Image.fromarray(annotated).save(os.path.join("outputs", out_name))

    # 5) DB에 기록 저장
    timestamp = datetime.utcnow()
    labels_str = ",".join(labels)  # 쉼표로 구분한 문자열 형태로 저장
    ins = history.insert().values(
        timestamp=timestamp,
        model=model,
        filename=out_name,
        labels=labels_str
    )
    try:
        with engine.connect() as conn:
            conn.execute(ins)
            conn.commit()
    except SQLAlchemyError as e:
        print("DB 저장 오류:", e)

    return JSONResponse({"labels": labels, "output_image": out_name})

# ── 탐지 이력 조회용 엔드포인트 (선택 사항) ─────────────────────────────
@app.get("/history")
async def get_history():
    query = history.select().order_by(history.c.timestamp.desc()).limit(50)
    try:
        with engine.connect() as conn:
            rows = conn.execute(query).fetchall()
            result = []
            for row in rows:
                result.append({
                    "id": row.id,
                    "timestamp": row.timestamp.isoformat(),
                    "model": row.model,
                    "filename": row.filename,
                    "labels": row.labels.split(",")
                })
            return {"history": result}
    except SQLAlchemyError as e:
        return JSONResponse({"error": str(e)}, status_code=500)
