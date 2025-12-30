import firebase_admin, os, json, datetime
from firebase_admin import credentials, messaging

# send message
BASE_PATH = os.path.dirname(__file__)
def sendMessage(msgTitle, msgBody, msgImg=None, msgTopic="all"):
    msg = messaging.Message(
        notification=messaging.Notification(
            title=msgTitle,
            body=msgBody,
            image=msgImg 
        ),
        topic=msgTopic
    )
    # IMAGE MUST BE ON PUBLIC HTTP(S?)

    messaging.send(msg)

    currTime: str = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    with open(os.path.join(BASE_PATH, "notifications", f"notification-{currTime}.json"), 'w') as notifFile:
        notifFile.write(json.dumps(
            {
                "title": msgTitle,
                "body": msgBody,
                "img": msgImg,
                "topic": msgTopic
            },
            indent=4
        ))

# credentials file location
with open(os.path.join(BASE_PATH, "config.json"), 'r') as f:
    configFile = json.load(f)
    CRED_FILE = configFile["firebase_file_path"]

# initialize credentials
cred = credentials.Certificate(CRED_FILE)
firebase_admin.initialize_app(cred)
if __name__ == "__main__":
    print(CRED_FILE)
    with open(CRED_FILE, 'r') as c:
        print("Project ID: ", json.load(c)["project_id"])
    title: str = str(input("Input a title: "))
    desc: str = str(input("Input a description: "))
    img: str = str(input("Input the url of an image (leave empty if none)"))
    if img=="":
        sendMessage(title, desc)
    else:
        sendMessage(title, desc, img)


# sendMessage("Boom", "Je bent een boom van een kerel", "https://hetbosderomarming.nl/wp-content/uploads/2020/09/47439162_s.jpg")