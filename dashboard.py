import threading
import time

from flask import Flask, abort, jsonify, render_template, request

import db as _db

app = Flask(__name__)

# ── Shared live data (written by sensor thread, read by Flask) ─────────────────
_live = {
    "co2": None, "tvoc": None,
    "temperature": None, "humidity": None,
    "status": None, "ts": None,
}
_live_lock = threading.Lock()


def update_live(co2, tvoc, temperature, humidity, status):
    """Called from the main sensor loop every cycle."""
    with _live_lock:
        _live.update(
            co2=co2, tvoc=tvoc,
            temperature=temperature, humidity=humidity,
            status=status, ts=time.time(),
        )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/live")
def api_live():
    with _live_lock:
        return jsonify(dict(_live))


@app.route("/api/rooms", methods=["GET"])
def api_rooms():
    return jsonify(_db.get_rooms())


@app.route("/api/rooms", methods=["POST"])
def api_create_room():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        abort(400)
    try:
        _db.add_room(name)
    except Exception:
        abort(409)
    return jsonify({"ok": True}), 201


@app.route("/api/rooms/<int:room_id>", methods=["DELETE"])
def api_delete_room(room_id):
    _db.delete_room(room_id)
    return jsonify({"ok": True})


@app.route("/api/rooms/<int:room_id>/activate", methods=["POST"])
def api_activate_room(room_id):
    _db.set_active_room(room_id)
    return jsonify({"ok": True})


@app.route("/api/rooms/deactivate", methods=["POST"])
def api_deactivate():
    _db.set_active_room(None)
    return jsonify({"ok": True})


@app.route("/api/rooms/<int:room_id>/readings")
def api_readings(room_id):
    hours = request.args.get("hours", type=float)
    since_ts = (time.time() - hours * 3600) if hours else None
    readings = _db.get_readings(room_id, since_ts)
    stats = _db.get_stats(room_id, since_ts)
    return jsonify({"readings": readings, "stats": stats})


# ── Server start ───────────────────────────────────────────────────────────────

def start(host="0.0.0.0", port=5000):
    _db.init_db()
    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False, debug=False),
        daemon=True,
    )
    t.start()
    print(f"Dashboard → http://localhost:{port}")
