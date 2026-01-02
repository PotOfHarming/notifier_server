import json, os, time, psutil

BASE_PATH = os.path.dirname(__file__)

with open(os.path.join(BASE_PATH, "config.json"), "r") as f:
    config = json.load(f)
WEB_PATH = config.get("web_path", BASE_PATH)
FILES_PATH = config.get("files_path", BASE_PATH)

records_file = os.path.join(FILES_PATH, "records", "records.json")
hexes_file = os.path.join(FILES_PATH, "found_hex.txt")
seen_file = os.path.join(FILES_PATH, "seen_coords.txt")

def write_config():
    with open(os.path.join(WEB_PATH, "config.json")) as f:
        config = json.load(f)
    output_file = os.path.join(WEB_PATH, "config.json")
    with open(output_file, "w") as f:
        json.dump({"url": config["url"]}, f, indent=2)

def write_stats():
    if os.path.exists(records_file):
        with open(records_file, "r") as f:
            records = json.load(f)
    else:
        records = ["Could not find records.json"]
        print("Could not find records.json")
        print(f"({records_file})")
    if os.path.exists(hexes_file):
        with open(hexes_file, "r") as f:
            stats = len(f.readlines())
    else:
        stats = "Could not find found_hex.txt"
        print("Could not find found_hex.txt")
        print(f"({records_file})")
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    
    output_file = os.path.join(WEB_PATH, "stats.json")
    data = {
        "records": records, 
        "total_planes": stats,
        "uptime": {
            "seconds": uptime_seconds,
            "formatted": f"{hours}h {minutes}m {seconds}s"
        }
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def write_hexes():
    with open(hexes_file, "r") as f:
        hexes = [line.strip() for line in f.readlines()] or ["Could not find found_hex.txt"]
    output_file = os.path.join(WEB_PATH, "hexes.json")
    with open(output_file, "w") as f:
        json.dump(hexes, f, indent=2)

def write_locations():
    coords = []
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            for line in f:
                try:
                    coords.append(json.loads(line.strip()))
                except:
                    pass
    output_file = os.path.join(WEB_PATH, "locations.json")
    with open(output_file, "w") as f:
        json.dump(coords, f, indent=2)

def write_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    output_file = os.path.join(WEB_PATH, "uptime.json")
    data = {
        "uptime_seconds": uptime_seconds,
        "uptime_formatted": f"{hours}h {minutes}m {seconds}s"
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def write_systeminfo():
    cpu_percent = psutil.cpu_percent(interval=0)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    output_file = os.path.join(WEB_PATH, "systeminfo.json")
    data = {
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
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def update_all():
    print("Writing all data to files")
    try:
        write_config()
        write_stats()
        write_hexes()
        write_locations()
        write_uptime()
        write_systeminfo()
        print(f"Updated all files at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Error updating files: {e}")

if __name__ == '__main__':
    update_interval = 30  # seconds
    while True:
        update_all()
        time.sleep(update_interval)
