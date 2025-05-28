from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
from PIL import Image
import io
import os

app = FastAPI()
model = YOLO(os.getenv("MODEL_NAME", "yolov8n.pt"))

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/infer")
async def infer(file: UploadFile = File(...)):
    # 1) 바이트 → PIL.Image
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # 2) 예측 수행
    results = model.predict(source=image, save=False)
    cls_indices = results[0].boxes.cls.tolist()
    labels = [model.names[int(i)] for i in cls_indices]

    # 3) 결과 이미지 저장
    out_name = file.filename
    annotated_img = results[0].plot()
    os.makedirs("outputs", exist_ok=True)
    Image.fromarray(annotated_img).save(os.path.join("outputs", out_name))

    # 4) 라벨과 파일명만 JSON으로 반환
    return JSONResponse({
        "labels": labels,
        "output_image": out_name
    })
