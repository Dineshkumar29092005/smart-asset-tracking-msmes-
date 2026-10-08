"""Central settings for the backend. Change values here, not in the other files."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "assets.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "..", "database", "schema.sql")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# ---- Detection ----
MODEL_PATH = "yolov8n.pt"      # replace with your trained weights, e.g. models/best.pt
CONFIDENCE = 0.40
PROCESS_EVERY_N_FRAMES = 5     # skip frames to save CPU
DEFAULT_CAMERA_ID = "Camera-01"
DEFAULT_SOURCE = "0"           # 0 = webcam, or an RTSP/IP camera URL, or a video file

# ---- Zones (2 x 2 grid, matches the architecture diagram) ----
ZONE_NAMES = ["Zone A", "Zone B", "Zone C", "Zone D"]

# ---- Missing-asset rule ----
MISSING_AFTER_MINUTES = 30     # not seen for this long -> status "Missing" + alert

# ---- Category mapping ----
# The 4 asset classes from the project. If you train YOLOv8 on your own dataset,
# name the classes like the keys below. With the default pretrained model
# (COCO classes) everything falls back to DEFAULT_CATEGORY so you can still demo.
CATEGORY_MAP = {
    "tool": "Tool",
    "equipment": "Equipment",
    "raw material": "Raw Material",
    "raw_material": "Raw Material",
    "finished good": "Finished Good",
    "finished_good": "Finished Good",
}
DEFAULT_CATEGORY = "Tool"
