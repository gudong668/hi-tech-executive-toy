import time

from setting import XMLY_URL,HEADER,MONGODB,MUSIC_PATH,COVER_PATH
import requests,os
from uuid import uuid4

my_url = XMLY_URL%("424529","1")

res = requests.get(my_url,headers=HEADER)
data = res.json()
content_list = []

for music_info in data.get("data").get("tracksAudioPlay"):
    music = {
        "music":"",
        "cover":"",
        "title":""
    }

    filename = uuid4()

    audio = requests.get(music_info.get("src"))
    audio_path = os.path.join(MUSIC_PATH,f"{filename}.mp3")
    with open(audio_path,"wb") as f:
        f.write(audio.content)

    cover = requests.get("http:"+music_info.get("trackCoverPath"))
    cover_path = os.path.join(COVER_PATH,f"{filename}.jpg")
    with open(cover_path,"wb") as f:
        f.write(cover.content)


    music["cover"] = f"{filename}.jpg"
    music["music"] = f"{filename}.mp3"
    music["title"] = music_info.get("trackName")

    content_list.append(music)

    time.sleep(0.2)
    # MONGODB.content.insert_one(music)

MONGODB.content.insert_many(content_list)

