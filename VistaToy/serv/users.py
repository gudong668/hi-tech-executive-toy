from bson import ObjectId
from flask import Blueprint,jsonify,send_file,request

from serv.chat_set import get_chat_all
from setting import MONGODB,COVER_PATH,MUSIC_PATH,RET
import os

users = Blueprint("users",__name__)

@users.route("/reg",methods=["POST"])
def reg():
    user_info = request.form.to_dict()
    user_info["avatar"] = "mama.jpg" if user_info.get("gender") == "1" else "baba.jpg"
    user_info["bind_toys"] = []
    user_info["friend_list"]=[]

    MONGODB.users.insert_one(user_info)

    RET["CODE"] = 0
    RET["MSG"] = "注册成功"
    RET["DATA"] = []

    return jsonify(RET)

@users.route("/login",methods=["POST"])
def login():
    user_info = request.form.to_dict()

    user = MONGODB.users.find_one(user_info,{"password":0})

    if user:
        user["_id"] = str(user.get("_id"))

        RET["CODE"] = 0
        RET["MSG"] = "登陆成功"
        RET["DATA"] = user
    else:
        RET["CODE"] = 1
        RET["MSG"] = "用户名密码错误"
        RET["DATA"] = {}

    return jsonify(RET)

@users.route("/auto_login",methods=["POST"])
def auto_login():
    _id = request.form.get("_id")

    user = MONGODB.users.find_one({"_id":ObjectId(_id)},{"password":0})

    if user:
        user["_id"] = str(user.get("_id"))

        chat = get_chat_all(_id)
        user["chat"] = chat

        RET["CODE"] = 0
        RET["MSG"] = "登陆成功"
        RET["DATA"] = user
    else:
        RET["CODE"] = 1
        RET["MSG"] = "用户名密码错误"
        RET["DATA"] = {}

    return jsonify(RET)
