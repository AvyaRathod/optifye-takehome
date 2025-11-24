from typing import List, Dict, Any

import numpy as np
import torch
from torchvision import transforms
from torchvision.models.detection import ssdlite320_mobilenet_v3_large


_model = None
_transform = transforms.Compose([
    transforms.ToTensor(),
])


def load_model() -> torch.nn.Module:
    global _model
    if _model is None:
        _model = ssdlite320_mobilenet_v3_large(weights="DEFAULT")
        _model.eval()
    return _model


def predict_batch(model: torch.nn.Module, images: List[np.ndarray]) -> List[Dict[str, Any]]:
    tensors = [_transform(img) for img in images]
    with torch.no_grad():
        outputs = model(tensors)
    results = []
    for output in outputs:
        boxes = output["boxes"].cpu().numpy().tolist()
        scores = output["scores"].cpu().numpy().tolist()
        labels = output["labels"].cpu().numpy().tolist()
        results.append({
            "boxes": boxes,
            "scores": scores,
            "labels": labels,
        })
    return results
