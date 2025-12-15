import os, json, time

BASE_PATH = os.path.dirname(__file__)
cooldown_file = os.path.join(BASE_PATH, "cooldowns.json")
MIN_TIME = 60  # example: 10 minutes cooldown

def setCooldown(alert_id: str):
    if os.path.exists(cooldown_file):
        with open(cooldown_file, "r") as f:
            FILE = json.load(f)
    else:
        FILE = {}

    FILE[alert_id] = time.time()
    with open(cooldown_file, "w") as f:
        json.dump(FILE, f, indent=4)

def getCooldown(alert_id: str):
    if not os.path.exists(cooldown_file):
        print("Not found")
        return True
    with open(cooldown_file, "r") as f:
        FILE = json.load(f)

    last_time = FILE.get(alert_id, 0)
    return time.time() >= last_time + MIN_TIME or last_time == 0
