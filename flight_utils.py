import os, json
from geopy import distance

config = None
with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
    config = json.load(f)
BASE_PATH = config["files_path"]

def getAverage(value1, value2, decimals=2):
    if value1==None or value1==0 or value2==None or value2==0:
        return None
    else:
        return round(value1/value2, decimals)

def getDistance(location) -> float: 
    if config["location"]["lat"] is None or config["location"]["lng"] is None: 
        print("No location inputted in config.json!")
        return None
    pos = (config["location"]["lat"], config["location"]["lng"])
    dist = distance.great_circle(pos, location).kilometers
    return round(dist, 2)