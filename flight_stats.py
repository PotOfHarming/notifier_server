import os, datetime, json, time
import flight_utils

config = None
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)
BASE_PATH = config["files_path"]

def updateStats(plane, dist, extra, records, debugMode):
    with open(os.path.join(BASE_PATH, "records", "records.json"), "w") as f:
        f.write(json.dumps(records, indent=4))
    now: str = datetime.datetime.now().strftime("%H_%M_%S-%d_%m_%Y")
    with open(os.path.join(BASE_PATH, "records", f"records-planes_{now}.txt"), "w") as recordsFile:
        recordStr = f"{plane["hex"]} at {now}\n -  {plane["lat"]}, {plane["lon"]}\n\n"
        recordStr += f"Stats:\n - {plane["speed"]}kts\n - {plane["altitude"]}ft\n - {dist}km"
        recordStr += f"\n\nNew record: {extra}"
        if debugMode: print(recordStr)
        recordsFile.write(recordStr)

def createStats(maxStats, minStats, totals, amounts, newPlanes, debugMode):
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
            "distance": None if maxStats["distance"] == 0 else maxStats["distance"],
            "altitude": None if maxStats["altitude"] == 0 else maxStats["altitude"],
            "speed": None if maxStats["speed"] == 0 else maxStats["speed"]
        },
        "avg": {
            "distance": flight_utils.getAverage(totals["distance"], amounts["distance"]),
            "altitude": flight_utils.getAverage(totals["altitude"], amounts["altitude"]),
            "speed": flight_utils.getAverage(totals["speed"], amounts["speed"])
        },
        "min": {
            "distance": None if minStats["distance"] == 0 else minStats["distance"],
            "altitude": None if minStats["altitude"] == 0 else minStats["altitude"],
            "speed": None if minStats["speed"] == 0 else minStats["speed"]
        },
        "new": newPlanes
    }
    with open(os.path.join(BASE_PATH, "times", fileName), "w") as f:
        f.write(json.dumps(jsonData, indent=4))


def checkStats(dist, alt, spd, maxStats, minStats, totals, amounts):
    # distance
    if dist is not None and dist > 0:
        totals["distance"] += dist
        amounts["distance"] += 1
        if dist > maxStats["distance"]:
            maxStats["distance"] = dist
        if dist < minStats["distance"] or minStats["distance"]==0:
            minStats["distance"] = dist
    # altitude
    if alt is not None and alt > 0:
        totals["altitude"] += alt
        amounts["altitude"] += 1
        if alt > maxStats["altitude"]:
            maxStats["altitude"] = alt
        if alt < minStats["altitude"] or minStats["altitude"]==0:
            minStats["altitude"] = alt
    # speed
    if spd is not None and spd > 0:
        totals["speed"] += spd
        amounts["speed"] += 1
        if spd > maxStats["speed"]:
            maxStats["speed"] = spd
        if spd < minStats["speed"] or minStats["speed"]==0:
            minStats["speed"] = spd