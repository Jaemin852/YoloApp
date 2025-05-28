from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
        # YOLOv6
        if name.startswith("yolov6"):
            from yolov6 import YOLOV6
            model_cache[name] = YOLOV6(weights=path)
        # YOLOv7
        elif name.startswith("yolov7"):
            from yolov7 import YOLOV7
            model_cache[name] = YOLOV7(weights=path)
        # YOLOv8 (Ultralytics)
        else:
            from ultralytics import YOLO
            model_cache[name] = YOLO(path)
    return model_cache[name]

@app.get("/models")
async def list_models():
    files = [f for f in os.listdir(WEIGHTS_DIR) if f.endswith(".pt")]
    return {"models": files, "default": DEFAULT_MODEL}

# 정적 파일 서빙
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
    model: str = Query(DEFAULT_MODEL, description="선택할 모델 파일명")
):
    # 1) 모델 로드
    try:
        detector = get_model(model)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    # 2) 이미지 준비
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # 3) 추론
    # YOLOv6, YOLOv7, YOLOv8 모두 .predict(img) 형태로 호출
    results = detector.predict(source=image, save=False)
    # Ultralytics는 boxes.cls, yolov6detect/yolov7-package는 .pred[:,5]
    try:
        cls_idxs = results[0].boxes.cls.tolist()              # v8
    except AttributeError:
        preds    = results[0].pred[0]
        cls_idxs = preds[:, 5].tolist()                       # v6/v7

    # 4) 레이블 매핑
    names = detector.names if hasattr(detector, "names") else detector.model.names
    labels = [names[int(i)] for i in cls_idxs]

    # 5) 결과 이미지 저장
    out_name  = file.filename
    annotated = results[0].plot()
    os.makedirs("outputs", exist_ok=True)
    Image.fromarray(annotated).save(os.path.join("outputs", out_name))

    return JSONResponse({"labels": labels, "output_image": out_name})
