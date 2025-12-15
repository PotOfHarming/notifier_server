import firebase_admin, os, json
from firebase_admin import credentials, messaging

# credentials file location
BASE_PATH = os.path.dirname(__file__)
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

# send message
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

# sendMessage("Boom", "Je bent een boom van een kerel", "https://hetbosderomarming.nl/wp-content/uploads/2020/09/47439162_s.jpg")