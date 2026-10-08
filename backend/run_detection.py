"""Camera Input Module: read video, detect assets, remember where they were seen.

Usage:
    python run_detection.py                       # webcam 0
    python run_detection.py --source video.mp4    # a video file
    python run_detection.py --source rtsp://...   # an IP/CCTV camera
    python run_detection.py --show                # preview window (press q to quit)
"""
import argparse

import cv2

import config
import db
from detector import AssetDetector
from zones import get_zone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=config.DEFAULT_SOURCE)
    parser.add_argument("--camera-id", default=config.DEFAULT_CAMERA_ID)
    parser.add_argument("--show", action="store_true", help="show a preview window")
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source

    db.init_db()
    conn = db.get_conn()
    db.ensure_camera(conn, args.camera_id, config.ZONE_NAMES)

    detector = AssetDetector()
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video source: {args.source}")

    frame_no = 0
    print("Detection running. Press Ctrl+C (or q in the preview) to stop.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_no += 1
            if frame_no % config.PROCESS_EVERY_N_FRAMES:
                continue

            height, width = frame.shape[:2]
            for obj in detector.track(frame):
                x1, y1, x2, y2 = obj["box"]
                zone = get_zone((x1 + x2) / 2, (y1 + y2) / 2, width, height)
                label = obj["label"]
                category = config.CATEGORY_MAP.get(label.lower(), config.DEFAULT_CATEGORY)
                asset_id = f"{args.camera_id}-{label.replace(' ', '_')}-{obj['track_id']}"
                db.record_sighting(conn, asset_id, label, category, args.camera_id, zone)

                if args.show:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 140, 255), 2)
                    cv2.putText(frame, f"{label} | {zone}", (int(x1), int(y1) - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 140, 255), 2)

            db.refresh_missing(conn)
            if args.show:
                cv2.imshow("Asset Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        conn.close()


if __name__ == "__main__":
    main()
