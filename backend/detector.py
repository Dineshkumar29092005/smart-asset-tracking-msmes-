"""Object Detection + Tracking Module (YOLOv8 with built-in ByteTrack)."""
from ultralytics import YOLO

from config import MODEL_PATH, CONFIDENCE


class AssetDetector:
    def __init__(self, model_path=MODEL_PATH, confidence=CONFIDENCE):
        self.model = YOLO(model_path)  # downloads yolov8n.pt on first run (needs internet)
        self.confidence = confidence

    def track(self, frame):
        """Return a list of {track_id, label, box=[x1,y1,x2,y2]} for one frame."""
        results = self.model.track(
            frame, persist=True, conf=self.confidence,
            tracker="bytetrack.yaml", verbose=False,
        )
        r = results[0]
        found = []
        if r.boxes is None or r.boxes.id is None:
            return found
        boxes = r.boxes.xyxy.tolist()
        ids = r.boxes.id.int().tolist()
        classes = r.boxes.cls.int().tolist()
        for box, track_id, cls in zip(boxes, ids, classes):
            found.append({"track_id": track_id, "label": r.names[cls], "box": box})
        return found
