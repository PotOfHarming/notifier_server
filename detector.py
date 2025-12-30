from notifier import sendMessage
from checkFound import checkJSON
from geopy import distance

import json, requests, os, checkAlert, datetime, time

BASE_PATH = os.path.dirname(__file__)




config = None
with open(os.path.join(BASE_PATH, "config.json")) as f:
    config = json.load(f)

reloadEvery = config["reloadEvery"]
URL = config["url"]
debugMode = config["enableDebug"]

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

def getDistance(location) -> float: 
    if config["location"]["lat"] is None or config["location"]["lng"] is None: 
        print("No location inputted in config.json!")
        return None
    pos = (config["location"]["lat"], config["location"]["lng"])
    dist = distance.great_circle(pos, location).kilometers
    return round(dist, 2)

newPlanes = []
uniqueHexs = []
maxStats = [0, 0, 0] # distance, altitude, speed
minStats = [0, 0, 0] # distance, altitude, speed
totals = [0, 0, 0] # distance, altitude, speed
amounts = [0, 0, 0] # distance, altitude, speed

def getAverage(value1, value2, decimals=2):
    if value1==None or value1==0 or value2==None or value2==0:
        return None
    else:
        return round(value1/value2, decimals)

def createStats():
    if debugMode: print(
        maxStats,
        minStats,
        totals,
        amounts
    )
    now: str = datetime.datetime.now().strftime("%H_%M_%S-%d_%m_%Y")
    epoch = time.time()
    fileName: str = f"{now}.json"
    print(f"Creating {fileName} ...")
    jsonData = {
        "epoch": epoch,
        "planes": len(newPlanes),
        "max": {
            "dist": None if maxStats[0] == 0 else maxStats[0],
            "alt": None if maxStats[1] == 0 else maxStats[1],
            "spd": None if maxStats[2] == 0 else maxStats[2]
        },
        "avg": {
            "dist": getAverage(totals[0], amounts[0]),
            "alt": getAverage(totals[1], amounts[1]),
            "spd": getAverage(totals[2], amounts[2])
        },
        "min": {
            "dist": None if minStats[0] == 0 else minStats[0],
            "alt": None if minStats[1] == 0 else minStats[1],
            "spd": None if minStats[2] == 0 else minStats[2]
        },
        "new": uniqueHexs
    }
    with open(os.path.join(BASE_PATH, "flight-stats", "times", fileName), "w") as f:
        f.write(json.dumps(jsonData, indent=4))


def checkStats(dist, alt, spd):
    # distance
    if dist is not None and dist > 0:
        totals[0] += dist
        amounts[0] += 1
        if dist > maxStats[0]:
            maxStats[0] = dist
        if dist < minStats[0] or minStats[0]==0:
            minStats[0] = dist
    # altitude
    if alt is not None and alt > 0:
        totals[1] += alt
        amounts[1] += 1
        if alt > maxStats[1]:
            maxStats[1] = alt
        if alt < minStats[1] or minStats[1]==0:
            minStats[1] = alt
    # speed
    if spd is not None and spd > 0:
        totals[2] += spd
        amounts[2] += 1
        if spd > maxStats[2]:
            maxStats[2] = spd
        if spd < minStats[2] or minStats[2]==0:
            minStats[2] = spd
        

loadFilters(online=True)
time.sleep(2)

reloadStatsEvery = 300
records = [
    None, # furthest distance
    None, # highest plane
    None # fastest plane
]

def updateStats(plane, dist, extra):
    with open(os.path.join(BASE_PATH, "flight-stats", "records", "records.json"), "w") as f:
        f.write(json.dumps(records, indent=4))
    now: str = datetime.datetime.now().strftime("%H_%M_%S-%d_%m_%Y")
    with open(os.path.join(BASE_PATH, "flight-stats", "records", f"records-planes_{now}.txt"), "w") as recordsFile:
        recordStr = f"{plane["hex"]} at {now}\n -  {plane["lat"]}, {plane["lon"]}\n\n"
        recordStr += f"Stats:\n - {plane["speed"]}kts\n - {plane["altitude"]}ft\n - {dist}km"
        recordStr += f"\n\nNew record: {extra}"
        if debugMode: print(recordStr)
        recordsFile.write(recordStr)


num_reload: int = 0
num_reloadStats: int = 0
while True:
    req = requests.get(URL)
    if req.status_code == 200:
        try:
            data = req.json()
            if debugMode: print(data)

            if os.path.exists(os.path.join(BASE_PATH, "flight-stats", "records", "records.json")):
                with open(os.path.join(BASE_PATH, "flight-stats", "records", "records.json"), "r") as f:
                    records = json.load(f)


            newMax = [None, None, None]
            for plane in data:
                # Check seen coordinates
                seen_file = os.path.join(BASE_PATH, "flight-stats", "seen_coords.txt")
                seen_coords = []
                if os.path.exists(seen_file):
                    with open(seen_file, "r") as f:
                        for line in f:
                            seen_coords.append(json.loads(line.strip()))
                
                coord_key = [round(plane["lat"], 3), round(plane["lon"], 3)]
                if coord_key not in seen_coords:
                    with open(seen_file, "a") as f:
                        json.dump(coord_key, f)
                        f.write("\n")

                # open file, check if it contains plane hex, if not add it
                found_file = os.path.join(BASE_PATH, "flight-stats", "found_hex.txt")
                found_hexes = []
                if os.path.exists(found_file):
                    with open(found_file, "r") as f:
                        found_hexes = [line.strip() for line in f.readlines()]
                if plane["hex"] not in found_hexes:
                    newPlanes.append(plane["hex"])
                    with open(found_file, "a") as f:
                        f.write(plane["hex"] + "\n")

                if plane["hex"] not in found_hexes:
                    uniqueHexs.append(plane["hex"])

                dist = getDistance((plane["lat"], plane["lon"]))

                checkStats(
                    dist,
                    plane["altitude"],
                    plane["speed"]
                )
                if records[0]==None or dist > records[0]:
                    records[0]=dist
                    newMax[0] = f"Distance = {dist}km"
                    print(f"Distance = {dist}km")
                if records[1]==None or plane["altitude"]>records[1]:
                    records[1]=plane["altitude"]
                    newMax[1] = f"Altitude = {plane["altitude"]}ft"
                    print(f"Altitude = {plane["altitude"]}ft")
                if records[2]==None or plane["speed"]>records[2]:
                    records[2]=plane["speed"]
                    newMax[2] = f"Speed = {plane["speed"]}kts"
                    print(f"Speed = {plane["speed"]}kts")



                
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
                updateStats(plane, dist, '\n'+'\n'.join(f" - {m}" for m in newMax))
        except ValueError:
            print("Failed to parse JSON")
    else:
        print(f"Failed to fetch ({req.status_code})")
    if num_reload>reloadEvery:
        num_reload = 0
        loadFilters()
    if num_reloadStats>reloadStatsEvery:
        num_reloadStats = 0
        createStats()
    
    num_reload+=1
    num_reloadStats+=1
    time.sleep(1)