"""Fill the database with demo assets so you can test the dashboard without a camera.

Usage:  python seed_demo.py
"""
import random
from datetime import datetime, timedelta

import config
import db

DEMO_ASSETS = [
    ("Spanner", "Tool"), ("Hammer", "Tool"), ("Drill Machine", "Equipment"),
    ("Welding Torch", "Equipment"), ("Steel Rod Bundle", "Raw Material"),
    ("Aluminium Sheet", "Raw Material"), ("Gear Box", "Finished Good"),
    ("Bearing Pack", "Finished Good"), ("Screwdriver Set", "Tool"),
    ("Lathe Chuck", "Equipment"), ("Copper Wire Roll", "Raw Material"),
    ("Motor Housing", "Finished Good"),
]


def main():
    db.init_db()
    conn = db.get_conn()
    camera_id = config.DEFAULT_CAMERA_ID
    db.ensure_camera(conn, camera_id, config.ZONE_NAMES)

    for i, (name, category) in enumerate(DEMO_ASSETS, start=1):
        asset_id = f"D{i:03d}"
        zone = random.choice(config.ZONE_NAMES)
        db.record_sighting(conn, asset_id, name, category, camera_id, zone)
        # make a few assets old so they show up as Missing
        if i in (3, 9):
            old = (datetime.now() - timedelta(hours=5)).strftime(db.TIME_FMT)
            conn.execute("UPDATE assets SET last_seen_time=? WHERE asset_id=?", (old, asset_id))
            conn.commit()

    db.refresh_missing(conn)
    conn.close()
    print(f"Demo data added ({len(DEMO_ASSETS)} assets). Now run: python app.py")


if __name__ == "__main__":
    main()
