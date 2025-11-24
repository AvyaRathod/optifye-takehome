import base64
from typing import Dict, List

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image
import io

from model import load_model, predict_batch


app = FastAPI(title="Optifye Inference Service")
model = load_model()


class Frame(BaseModel):
    id: str
    image_b64: str


class BatchRequest(BaseModel):
    frames: List[Frame]


class FrameResult(BaseModel):
    boxes: List[List[float]]
    scores: List[float]
    labels: List[int]


class BatchResponse(BaseModel):
    results: Dict[str, FrameResult]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/infer", response_model=BatchResponse)
def infer(batch: BatchRequest):
    images = []
    ids = []
    for frame in batch.frames:
        img_bytes = base64.b64decode(frame.image_b64)
        pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        images.append(np.array(pil_image))
        ids.append(frame.id)

    predictions = predict_batch(model, images)
    result_map = {
        frame_id: FrameResult(**pred)
        for frame_id, pred in zip(ids, predictions)
    }
    return BatchResponse(results=result_map)
