from flask import Flask, jsonify
from flask_cors import CORS
import json, os, time, psutil

app = Flask(__name__)
CORS(app)
BASE_PATH = os.path.dirname(__file__)

records_file = os.path.join(BASE_PATH, "flight-stats", "records", "records.json")
stats_file = os.path.join(BASE_PATH, "flight-stats", "found_hex.txt")
hexes_file = os.path.join(BASE_PATH, "flight-stats", "found_hex.txt")
seen_file = os.path.join(BASE_PATH, "flight-stats", "seen_coords.txt")


@app.route('/config', methods=['GET'])
def get_config():
    with open(os.path.join(BASE_PATH, "config.json")) as f:
        config = json.load(f)
    return jsonify({
        "url": config["url"]
    })

@app.route('/stats', methods=['GET'])
def get_records():
    if os.path.exists(records_file):
        with open(records_file, "r") as f:
            records = json.load(f)
    else:
        records = ["Could not find records.json"]
    if os.path.exists(stats_file):
        with open(stats_file, "r") as f:
            stats = {"total_planes": len(f.readlines())}
    else:
        stats = ["Could not find found_hex.txt"]
    
    return jsonify([records, stats])

@app.route('/hexes', methods=['GET'])
def get_hexes():
    with open(hexes_file, "r") as f:
        hexes = [line.strip() for line in f.readlines()] or ["Could not find found_hex.txt"]
    return jsonify(hexes)

@app.route('/locations', methods=['GET'])
def get_locations():
    coords = []
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            for line in f:
                coords.append(json.loads(line.strip()))
    return jsonify(coords)

@app.route('/uptime', methods=['GET'])
def get_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    return jsonify({
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": f"{hours}h {minutes}m {seconds}s"
    })

@app.route('/systeminfo', methods=['GET'])
def get_systeminfo():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        "cpu": {
            "percent": cpu_percent,
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True)
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8009, debug=False)
