import os, json, time, datetime

config = None
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)
BASE_PATH = config["files_path"]

def logFlight(plane, debugMode):
    """
        {
            "hex": <plane["hex"]>,
            "first_seen": {
                "text": "HH:MM:SS DD-MM-YYYY",
                "unix": unix
            },
            "last_seen": {
                "text": "HH:MM:SS DD-MM-YYYY",
                "unix": unix
            }
            "positions": {
                "<timestamp (unix)>": {
                    "position": [plane["lat"], plane["lon"]],
                    "altitude": <plane["altitude"]>,
                    "speed": <plane["speed"]>,
                    "track": <plane["track"]>,
                    "flight": <plane["flight"]>
                },
                if the next timestamp is not the same as the previous add it like above else dont
            }
        }
    """
    if debugMode: print(f"Writing for {plane["hex"]}")
    data = {}
    unix = time.time()
    now: str = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    f = os.path.join(BASE_PATH, "flights", f"{plane["hex"]}.json")
    if os.path.exists(f):
        with open(f, "r") as d:
            data = json.load(d)
    if debugMode: print(data)

    if data == {}:
        data["hex"] = plane["hex"]
        data["first_seen"] = {"text": now, "unix": unix}
    if debugMode: print(data)

    data.setdefault("positions", {})
    data["last_seen"] = {"text": now, "unix": unix}
    timestamp = {
        "position": [plane["lat"], plane["lon"]],
        "altitude": plane["altitude"],
        "speed": plane["speed"],
        "track": plane["track"],
        "flight": plane["flight"]
    }
    last_entry = None
    if data["positions"]:
        last_key = max(data["positions"], key=lambda k: float(k))
        last_entry = data["positions"][last_key]
    if last_entry != timestamp:
        data["positions"][str(unix)] = timestamp

    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w") as d:
        json.dump(data, d, indent=2)
        if debugMode: print("Dumped data")
    