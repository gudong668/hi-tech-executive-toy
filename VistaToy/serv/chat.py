from bson import ObjectId
from flask import Blueprint,jsonify,send_file,request

from ai import text2audio
from serv.chat_set import get_chat
from setting import MONGODB,COVER_PATH,MUSIC_PATH,RET
import os

chat = Blueprint("chat",__name__)

@chat.route("/chat_list",methods=["POST"])
def chat_list():
    chat_info = request.form.to_dict()
    chat_window = MONGODB.chats.find_one({"_id":ObjectId(chat_info.get("chat_id"))})

    RET["CODE"] = 0
    RET["MSG"] = "查询聊天记录"
    RET["DATA"] = chat_window.get("chat_list")

    get_chat(chat_info.get("to_user"),chat_info.get("from_user"))

    return jsonify(RET)


@chat.route("/recv_msg",methods=["POST"])
def recv_msg():
    from_user = request.form.get("from_user") # app
    to_user = request.form.get("to_user")
    """
        我={
            "你":1,
            "他":0,
            "app3":5
        }   
    """
    chat_window = MONGODB.chats.find_one({"user_list":{"$all":[from_user,to_user]}})
    count = get_chat(to_user,from_user)
    new_list = []
    print("玩具与当前用户的未读消息数量是：",count)
    if count:
        # chat = chat_window.get("chat_list")[-count:] # [-1] == [-未读消息数量:]
        # 如果 from_user == 自己 这条就放弃 继续下一条
        re_chat_list = reversed(chat_window.get("chat_list"))
        for ch in re_chat_list:
            if ch.get("from_user") != to_user:
                new_list.append(ch)
                if len(new_list) == count:
                    break


    toy_info = MONGODB.toys.find_one({"_id":ObjectId(to_user)})
    for fri in toy_info.get("friend_list"):
        if fri.get("friend_id") == from_user:
            s = f"以下是来自{fri.get('friend_remark')}的消息"
            filename = text2audio(s)
            new_list.append({"chat":filename})

    return jsonify(new_list)