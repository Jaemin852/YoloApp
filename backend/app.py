from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from PIL import Image
import io, os

app = FastAPI()
WEIGHTS_DIR   = "weights"
DEFAULT_MODEL = os.getenv("MODEL_NAME", "yolov8n.pt")
model_cache   = {}

def get_model(name: str):
    path = os.path.join(WEIGHTS_DIR, name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"모델 파일 '{name}'이 없습니다.")
    if name not in model_cache:
        # 오직 YOLOv8만 지원
        model_cache[name] = YOLO(path)
    return model_cache[name]

@app.get("/models")
async def list_models():
    files = sorted(f for f in os.listdir(WEIGHTS_DIR) if f.startswith("yolov8") and f.endswith(".pt"))
    return {"models": files, "default": DEFAULT_MODEL}

app.mount("/static" , StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return HTMLResponse(open("static/index.html", encoding="utf-8").read())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/infer")
async def infer(
    file: UploadFile = File(...),
    model: str = Query(DEFAULT_MODEL, description="사용할 YOLOv8 모델 파일명")
):
    try:
        detector = get_model(model)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    # 이미지 로드
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # 추론
    results = detector.predict(source=image, save=False)
    cls_idxs = results[0].boxes.cls.tolist()
    labels   = [detector.names[int(i)] for i in cls_idxs]

    # 결과 이미지 저장
    out_name  = file.filename
    annotated = results[0].plot()
    os.makedirs("outputs", exist_ok=True)
    Image.fromarray(annotated).save(os.path.join("outputs", out_name))

    return JSONResponse({"labels": labels, "output_image": out_name})
