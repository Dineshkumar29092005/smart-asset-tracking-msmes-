# Backend: Detection, Tracking & API (Modules 1, 2, 3, 5)

The backend reads camera video, detects assets with YOLOv8, maps them to zones, stores them in the database, and exposes search and alert APIs. It also serves the web dashboard from `../frontend`.

**Tech:** Python, YOLOv8 (Ultralytics), OpenCV, ByteTrack, Flask, SQLite

## Files

| File | Module | What it does |
|------|--------|--------------|
| `run_detection.py` | 1. Camera Input | Reads webcam / CCTV / video file, runs the detection loop |
| `detector.py` | 2. Object Detection | YOLOv8 detection with ByteTrack object tracking |
| `zones.py` | 3. Location Mapping | Converts a position in the frame to Zone A / B / C / D |
| `db.py` | 4. Memory Storage | SQLite helpers: save last-seen location, history, missing-asset alerts |
| `app.py` | 5. Query & Search | Flask REST API + serves the dashboard |
| `config.py` | | All settings (model, camera, zones, missing-after minutes) |
| `seed_demo.py` | | Adds demo assets so you can test without a camera |

## Data Flow

```
Camera -> YOLOv8 + ByteTrack -> Zone mapping -> SQLite database -> Flask API -> Dashboard
```

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

## Run the dashboard with demo data (no camera needed)

```bash
python seed_demo.py
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run live detection

In a second terminal (keep `app.py` running):

```bash
python run_detection.py --show                   # webcam, with preview window
python run_detection.py --source video.mp4       # a video file
python run_detection.py --source rtsp://...      # an IP / CCTV camera
```

The first run downloads the `yolov8n.pt` model (internet needed once).

## Using your own trained model

The default `yolov8n.pt` is a general model, so all objects are saved with the fallback category "Tool". For the four project classes, train YOLOv8 on your own images with the class names `tool`, `equipment`, `raw material`, `finished good`, then set `MODEL_PATH` in `config.py` to your weights file (for example `models/best.pt`).

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets` | All assets, newest first |
| GET | `/api/assets/search?q=&category=&zone=&status=&date=` | Search / filter |
| GET | `/api/assets/<id>/location` | Last seen location of one asset |
| GET | `/api/assets/<id>/history` | Zone-change history |
| GET | `/api/alerts` | Alerts (open ones first) |
| POST | `/api/alerts/<id>/resolve` | Mark an alert resolved |
| GET | `/api/stats` | Total / available / missing / open alerts |

## Notes for the report

- An asset not seen for `MISSING_AFTER_MINUTES` (default 30) is marked **Missing** and an alert is created. Seeing it again clears the alert.
- Asset IDs are generated as `<camera>-<label>-<track id>`. This is a simple prototype approach; tracker IDs can change if an object leaves the view for a long time.
- Email/SMS alerts are future scope.
