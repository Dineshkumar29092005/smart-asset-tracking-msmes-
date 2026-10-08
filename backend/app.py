"""Query & Search Module + REST API + serves the web dashboard.

Run:  python app.py      then open  http://127.0.0.1:5000
"""
from flask import Flask, jsonify, request, send_from_directory

import config
import db

app = Flask(__name__, static_folder=config.FRONTEND_DIR, static_url_path="")

ASSET_SELECT = """
    SELECT a.asset_id, a.asset_name, a.category, a.camera_id,
           z.zone_name AS zone, a.last_seen_time, a.status
    FROM assets a LEFT JOIN zones z ON a.zone_id = z.zone_id
"""


def rows(cursor_rows):
    return [dict(r) for r in cursor_rows]


@app.route("/")
def home():
    return send_from_directory(config.FRONTEND_DIR, "index.html")


@app.route("/api/assets")
def list_assets():
    conn = db.get_conn()
    db.refresh_missing(conn)
    data = conn.execute(ASSET_SELECT + " ORDER BY a.last_seen_time DESC").fetchall()
    conn.close()
    return jsonify(rows(data))


@app.route("/api/assets/search")
def search_assets():
    """Search by name/id (q), category, zone, status and date (YYYY-MM-DD)."""
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    zone = request.args.get("zone", "").strip()
    status = request.args.get("status", "").strip()
    date = request.args.get("date", "").strip()

    where, params = [], []
    if q:
        where.append("(a.asset_name LIKE ? OR a.asset_id LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if category:
        where.append("a.category = ?")
        params.append(category)
    if zone:
        where.append("z.zone_name = ?")
        params.append(zone)
    if status:
        where.append("a.status = ?")
        params.append(status)
    if date:
        where.append("date(a.last_seen_time) = ?")
        params.append(date)

    sql = ASSET_SELECT
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY a.last_seen_time DESC"

    conn = db.get_conn()
    db.refresh_missing(conn)
    data = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify(rows(data))


@app.route("/api/assets/<asset_id>/location")
def asset_location(asset_id):
    conn = db.get_conn()
    row = conn.execute(ASSET_SELECT + " WHERE a.asset_id = ?", (asset_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "Asset not found"}), 404
    return jsonify(dict(row))


@app.route("/api/assets/<asset_id>/history")
def asset_history(asset_id):
    conn = db.get_conn()
    data = conn.execute(
        """SELECT h.seen_time, h.camera_id, z.zone_name AS zone
           FROM asset_history h LEFT JOIN zones z ON h.zone_id = z.zone_id
           WHERE h.asset_id = ? ORDER BY h.seen_time DESC LIMIT 50""",
        (asset_id,),
    ).fetchall()
    conn.close()
    return jsonify(rows(data))


@app.route("/api/alerts")
def alerts():
    conn = db.get_conn()
    db.refresh_missing(conn)
    data = conn.execute(
        """SELECT al.alert_id, al.asset_id, a.asset_name, al.alert_type,
                  al.created_at, al.resolved
           FROM alerts al LEFT JOIN assets a ON al.asset_id = a.asset_id
           ORDER BY al.resolved ASC, al.created_at DESC LIMIT 50"""
    ).fetchall()
    conn.close()
    return jsonify(rows(data))


@app.route("/api/alerts/<int:alert_id>/resolve", methods=["POST"])
def resolve_alert(alert_id):
    conn = db.get_conn()
    conn.execute("UPDATE alerts SET resolved=1 WHERE alert_id=?", (alert_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/stats")
def stats():
    conn = db.get_conn()
    db.refresh_missing(conn)
    total = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    available = conn.execute(
        "SELECT COUNT(*) FROM assets WHERE status IN ('Available','In Use')"
    ).fetchone()[0]
    missing = conn.execute("SELECT COUNT(*) FROM assets WHERE status='Missing'").fetchone()[0]
    open_alerts = conn.execute("SELECT COUNT(*) FROM alerts WHERE resolved=0").fetchone()[0]
    conn.close()
    return jsonify(
        {"total": total, "available": available, "missing": missing, "alerts": open_alerts}
    )


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
