import time

from bson import ObjectId
from flask import Blueprint,jsonify,send_file,request
from setting import MONGODB, COVER_PATH, MUSIC_PATH, CHAT_PATH, RET,QRCODE_PATH
from serv.chat_set import set_chat
import os
from uuid import uuid4
from ai import audio2text, my_nlp_lowB, text2audio

gsa = Blueprint("gsa",__name__)

@gsa.route("/get_cover/<filename>")
def get_cover(filename):
    cover_file = os.path.join(COVER_PATH,filename)

    return send_file(cover_file)

@gsa.route("/get_music/<filename>")
def get_music(filename):
    music_file = os.path.join(MUSIC_PATH,filename)

    return send_file(music_file)

@gsa.route("/get_chat/<filename>")
def get_chat(filename):
    chat_file = os.path.join(CHAT_PATH,filename)

    return send_file(chat_file)

@gsa.route("/get_qr/<filename>")
def get_qr(filename):
    qr_file = os.path.join(QRCODE_PATH,filename)

    return send_file(qr_file)

@gsa.route("/app_uploader",methods=["POST"])
def app_uploader(): # 收到App传来的语音文件，代表消息发送了
    # 开启写入chat_list
    to_user = request.form.get("to_user") # 5ca17f85ea512d215cd9b079
    from_user = request.form.get("user_id") # 5c9d8da3ea512d2048826260

    toy_info = MONGODB.toys.find_one({"_id":ObjectId(to_user)})
    from_user_name = ""
    for friend in toy_info.get("friend_list"):
        if friend.get("friend_id") == from_user:
            from_user_name = friend.get("friend_remark")

    # 利用两个用户的ID查询数据它们的chat_window
    # chat_window = MONGODB.chats.find_one({"user_list":{"$all":[from_user,to_user]}})

    file = request.files.get("reco_file")
    new_file_path = os.path.join(CHAT_PATH,file.filename)

    file.save(new_file_path)

    os.system(f"ffmpeg -i {new_file_path} {new_file_path}.mp3")
    # os.remove(new_file_path)
    chat = {
        "from_user":from_user,
        "to_user":to_user,
        "chat":f"{file.filename}.mp3",
        "createTime":time.time()
    }
    # chat_window["chat_list"].append(chat)
    # 产生聊天记录的存放
    MONGODB.chats.update_one({"user_list": {"$all": [from_user, to_user]}},{"$push":{"chat_list":chat}})
    set_chat(to_user,from_user)

    new_file = text2audio(f"你有来自{from_user_name}的消息")

    RET["CODE"] = 0
    RET["MSG"] = "上传成功"
    RET["DATA"] = {"filename":new_file,"friend_type":"app"}

    return jsonify(RET)


@gsa.route("/toy_uploader",methods=["POST"])
def toy_uploader():
    to_user = request.form.get("to_user")
    from_user = request.form.get("user_id")
    friend_type = request.form.get("friend_type")

    to_user_name = ""

    if friend_type == "toy":
        toy = MONGODB.toys.find_one({"_id":ObjectId(to_user)})
        for t in toy["friend_list"]:
            if t.get("friend_id") == from_user:
                to_user_name = t.get("friend_remark")
                # 消息提醒
                to_user_name = text2audio(f"你有来自{to_user_name}的消息")


    file = request.files.get("reco")
    filename = f"{uuid4()}.wav"
    new_file_path = os.path.join(CHAT_PATH,filename)

    file.save(new_file_path)

    # os.system(f"ffmpeg -i {new_file_path} {new_file_path}.mp3")
    # os.remove(new_file_path)

    chat = {
        "from_user": from_user,
        "to_user": to_user,
        "chat": filename,
        "createTime": time.time()
    }
    # chat_window["chat_list"].append(chat)
    # 产生聊天记录的存放
    MONGODB.chats.update_one({"user_list": {"$all": [from_user, to_user]}}, {"$push": {"chat_list": chat}})
    set_chat(to_user, from_user)


    RET["CODE"] = 0
    RET["MSG"] = "上传成功"
    RET["DATA"] = {"filename":to_user_name,"code":0,"friend_type":friend_type}
    print(RET["DATA"])
    return jsonify(RET)


@gsa.route("/ai_uploader",methods=["POST"])
def ai_uploader():
    toy_id = request.form.get("toy_id")
    file = request.files.get("reco")
    filename = f"{uuid4()}.wav"
    new_file_path = os.path.join(CHAT_PATH,filename)

    file.save(new_file_path)
    start = time.time()
    text = audio2text(new_file_path)
    res = my_nlp_lowB(text,toy_id)
    print(time.time() - start)



    return jsonify(res)