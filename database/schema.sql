-- Asset Memory Database schema (SQLite-compatible; works in MySQL with minor changes)

CREATE TABLE cameras (
    camera_id   TEXT PRIMARY KEY,          -- e.g. 'Camera-01'
    location    TEXT,
    source_url  TEXT                       -- RTSP/webcam source
);

CREATE TABLE zones (
    zone_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id   TEXT NOT NULL,
    zone_name   TEXT NOT NULL,             -- e.g. 'Zone A'
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
);

CREATE TABLE assets (
    asset_id        TEXT PRIMARY KEY,      -- e.g. 'A001'
    asset_name      TEXT NOT NULL,         -- e.g. 'Spanner'
    category        TEXT NOT NULL CHECK (category IN
                    ('Tool', 'Equipment', 'Raw Material', 'Finished Good')),
    camera_id       TEXT,
    zone_id         INTEGER,
    last_seen_time  DATETIME,
    status          TEXT DEFAULT 'Available' CHECK (status IN
                    ('Available', 'Missing', 'Idle', 'In Use')),
    FOREIGN KEY (camera_id) REFERENCES cameras(camera_id),
    FOREIGN KEY (zone_id)   REFERENCES zones(zone_id)
);

CREATE TABLE asset_history (
    history_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id    TEXT NOT NULL,
    camera_id   TEXT,
    zone_id     INTEGER,
    seen_time   DATETIME NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE alerts (
    alert_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id    TEXT NOT NULL,
    alert_type  TEXT NOT NULL CHECK (alert_type IN
                ('Missing', 'Idle', 'Unauthorized Removal')),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved    INTEGER DEFAULT 0,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE INDEX idx_assets_name ON assets(asset_name);
CREATE INDEX idx_assets_category ON assets(category);
CREATE INDEX idx_history_asset_time ON asset_history(asset_id, seen_time);

-- Sample data
INSERT INTO cameras (camera_id, location) VALUES ('Camera-01', 'Main shop floor');
INSERT INTO zones (camera_id, zone_name) VALUES
    ('Camera-01', 'Zone A'), ('Camera-01', 'Zone B'),
    ('Camera-01', 'Zone C'), ('Camera-01', 'Zone D');
-- Example asset row (uncomment to try it):
-- INSERT INTO assets (asset_id, asset_name, category, camera_id, zone_id, last_seen_time, status)
-- VALUES ('A001', 'Spanner', 'Tool', 'Camera-01', 1, '2025-05-25 10:30:15', 'Available');

-- Example query: where was the spanner last seen?
-- SELECT a.asset_name, z.zone_name, a.last_seen_time
-- FROM assets a JOIN zones z ON a.zone_id = z.zone_id
-- WHERE a.asset_name = 'Spanner';
