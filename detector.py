from notifier import sendMessage
from checkFound import checkJSON

import json, requests, os, checkAlert, time
import file_updater, flight_utils, flight_stats, flight_logger

config = None
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)
BASE_PATH = config["files_path"]

reloadEvery = config["reloadEvery"]
URL = config["url"]
debugMode = config["enableDebug"]
log_all_flights = config["log_all_flights"]
pos = (config["location"]["lat"], config["location"]["lng"])

filter_list = []
def loadFilters(local=True, online=False):
    filter_list.clear()
    FOLDER = os.path.join(BASE_PATH, "alerts")
    for FILE in os.listdir(FOLDER):
        conf_file = os.path.join(FOLDER, FILE)
        if FILE.endswith(".config.json") and local:
            if debugMode: print("Found configuration file ", FILE)
            with open(conf_file, "r") as f: 
                p_filters = json.load(f)
                filter_list.append(p_filters)
        if FILE.endswith(".link.json") and online:
            if debugMode: print("Found link file ", FILE)
            with open(conf_file, "r") as f:
                filts = json.load(f)
                for URL in filts:
                    req = requests.get(URL)
                    if req.status_code == 200:
                        flt = json.loads(req.content)
                        filter_list.append(flt)

records = {
    "distance": None, # furthest distance
    "altitude": None, # highest plane
    "speed": None # fastest plane
}

loadFilters(online=True)
time.sleep(2)

newPlanes = []
maxStats = {"distance": 0, "altitude": 0, "speed": 0}
minStats = {"distance": 0, "altitude": 0, "speed": 0}
totals = {"distance": 0, "altitude": 0, "speed": 0}
amounts = {"distance": 0, "altitude": 0, "speed": 0}
reloadStatsEvery = 30
reloadFilesEvery = 15
num_reloadConfig: int = 0
num_reloadStats: int = 0
num_reloadFiles: int = 0
limit_distance: float = float(config["limit_distance"])
while True:
    req = requests.get(URL)
    if req.status_code == 200:
        try:
            # Load files once per iteration, not per plane
            seen_file = os.path.join(BASE_PATH, "seen_coords.txt")
            found_file = os.path.join(BASE_PATH, "found_hex.txt")

            if not os.path.exists(seen_file):
                with open(seen_file, "w") as f: f.close()
            if not os.path.exists(found_file):
                with open(found_file, "w") as f: f.close()
            

            data = req.json()
            if debugMode: print(data)

            if os.path.exists(os.path.join(BASE_PATH, "records", "records.json")):
                with open(os.path.join(BASE_PATH, "records", "records.json"), "r") as f:
                    records = json.load(f)

            seen_coords = []
            if os.path.exists(seen_file):
                with open(seen_file, "r") as f:
                    for line in f:
                        try:
                            seen_coords.append(json.loads(line.strip()))
                        except:
                            pass
            
            found_hexes = []
            if os.path.exists(found_file):
                with open(found_file, "r") as f:
                    found_hexes = [line.strip() for line in f.readlines()]

            for plane in data:
                dist = flight_utils.getDistance((plane["lat"], plane["lon"]))
                if limit_distance!=-1:
                    if dist > limit_distance:
                        if debugMode: print(f"skipping: {dist}, {limit_distance}")
                        continue
                newMax = [None, None, None]
                
                coord_key = [round(plane["lat"], 3), round(plane["lon"], 3), round(plane["altitude"], 0)]
                if coord_key not in seen_coords:
                    seen_coords.append(coord_key)
                    with open(seen_file, "a") as f:
                        json.dump(coord_key, f)
                        f.write("\n")

                # open file, check if it contains plane hex, if not add it
                if plane["hex"] not in found_hexes:
                    newPlanes.append(plane["hex"])
                    found_hexes.append(plane["hex"])
                    with open(found_file, "a") as f:
                        f.write(plane["hex"] + "\n")

                flight_stats.checkStats(
                    dist,
                    plane["altitude"],
                    plane["speed"],
                    maxStats, minStats, totals, amounts
                )
                if records["distance"]==None or dist > records["distance"]:
                    records["distance"]=dist
                    newMax[0] = f"Distance = {dist}km"
                    print(f"Distance = {dist}km")
                if records["altitude"]==None or plane["altitude"]>records["altitude"]:
                    records["altitude"]=plane["altitude"]
                    newMax[1] = f"Altitude = {plane["altitude"]}ft"
                    print(f"Altitude = {plane["altitude"]}ft")
                if records["speed"]==None or plane["speed"]>records["speed"]:
                    records["speed"]=plane["speed"]
                    newMax[2] = f"Speed = {plane["speed"]}kts"
                    print(f"Speed = {plane["speed"]}kts")


                flight_logger.logFlight(plane, debugMode)

                
                for FILTER in filter_list:
                    if not checkAlert.getCooldown(plane["hex"]): 
                        continue
                    v = checkJSON(plane, FILTER)
                    if v[0]==True:
                        checkAlert.setCooldown(plane["hex"])
                        print("sending notification...")
                        sendMessage(v[1], v[2], v[3])
                        print("notification sent!")

                newMax = [item for item in newMax if item is not None]
                if len(newMax) > 0: 
                    flight_stats.updateStats(plane, dist, '\n'+'\n'.join(f" - {m}" for m in newMax), records, debugMode)
        except ValueError:
            print("Failed to parse JSON")
    else:
        print(f"Failed to fetch ({req.status_code})")
    if num_reloadConfig>reloadEvery:
        num_reloadConfig = 0
        loadFilters()
    if num_reloadStats>reloadStatsEvery:
        num_reloadStats = 0
        flight_stats.createStats(maxStats, minStats, totals, amounts, newPlanes, debugMode)
        # Clear accumulated data
        newPlanes = []
        maxStats = {"distance": 0, "altitude": 0, "speed": 0}
        minStats = {"distance": 0, "altitude": 0, "speed": 0}
        totals = {"distance": 0, "altitude": 0, "speed": 0}
        amounts = {"distance": 0, "altitude": 0, "speed": 0}
    if num_reloadFiles>reloadFilesEvery:
        num_reloadFiles = 0
        file_updater.update_all()
    
    num_reloadConfig+=1
    num_reloadStats+=1
    num_reloadFiles+=1
    time.sleep(1)