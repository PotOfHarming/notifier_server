from notifier import sendMessage
from checkFound import checkJSON

import json, requests, os, checkAlert
from time import sleep

URL = "http://192.168.178.96:8008/data.json"
reloadEvery = 10


filter_list = []
BASE_PATH = os.path.dirname(__file__)
def loadFilters(local=True, online=False):
    filter_list.clear()
    FOLDER = os.path.join(BASE_PATH, "alerts")
    for FILE in os.listdir(FOLDER):
        conf_file = os.path.join(FOLDER, FILE)
        if FILE.endswith(".config.json") and local:
            print("Found configuration file ", FILE)
            with open(conf_file, "r") as f: 
                p_filters = json.load(f)
                filter_list.append(p_filters)
        if FILE.endswith(".link.json") and online:
            print("Found link file ", FILE)
            with open(conf_file, "r") as f:
                filts = json.load(f)
                for URL in filts:
                    req = requests.get(URL)
                    if req.status_code == 200:
                        flt = json.loads(req.content)
                        filter_list.append(flt)


loadFilters(online=True)
sleep(3)

FOUND = False
num: int = 0
while not FOUND:
    req = requests.get(URL)
    if req.status_code == 200:
        try:
            data = req.json()
            print(data)
            for plane in data:
                for FILTER in filter_list:
                    if not checkAlert.getCooldown(plane["hex"]): 
                        continue
                    v = checkJSON(plane, FILTER)
                    if v[0]==True:
                        checkAlert.setCooldown(plane["hex"])
                        print("sending notification...")
                        sendMessage(v[1], v[2], v[3])
                        print("notification sent!")

        except ValueError:
            print("Failed to parse JSON")
    else:
        print(f"Failed to fetch ({req.status_code})")
    if num>reloadEvery:
        num = 0
        loadFilters()
    else:
        num+=1
    sleep(1)