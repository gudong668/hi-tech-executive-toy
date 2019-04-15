from bson import ObjectId
from flask import Blueprint,jsonify,send_file,request
from setting import MONGODB,COVER_PATH,MUSIC_PATH,RET
import os

friend = Blueprint("friend",__name__)

@friend.route("/friend_list",methods=["POST"])
def friend_list():
    _id = request.form.get("_id")
    user_info = MONGODB.users.find_one({"_id":ObjectId(_id)})
    friend = user_info.get("friend_list")

    RET["CODE"] = 0
    RET["MSG"] = "好友查询"
    RET["DATA"] = friend

    return jsonify(RET)

@friend.route("/add_req",methods=["POST"])
def add_req():
    req_info = request.form.to_dict()
    print(req_info)

    add_id = req_info.get("add_user")
    toy_id = req_info.get("toy_id")
    if req_info.get("add_type") == "app":
        add_user = MONGODB.users.find_one({"_id":ObjectId(add_id)})
    else:
        add_user = MONGODB.toys.find_one({"_id":ObjectId(add_id)})

    toy = MONGODB.toys.find_one({"_id": ObjectId(toy_id)})

    req_info["avatar"] = add_user.get("avatar")
    req_info["nickname"] = add_user.get("nickname") if add_user.get("nickname") else add_user.get("baby_name")
    req_info["status"] = 0
    req_info["toy_name"] = toy.get("baby_name")

    MONGODB.request.insert_one(req_info)

    RET["CODE"] = 0
    RET["MSG"] = "添加好友请求"
    RET["DATA"] = {}

    return jsonify(RET)

@friend.route("/req_list",methods=["POST"])
def req_list():
    user_id = request.form.get("user_id")
    user_info = MONGODB.users.find_one({"_id":ObjectId(user_id)})
    bind_toy = user_info.get("bind_toys")

    req_info = list(MONGODB.request.find({"toy_id":{"$in":bind_toy}}))

    for index,req in enumerate(req_info):
        req_info[index]["_id"] = str(req.get("_id"))

    RET["CODE"] = 0
    RET["MSG"] = "查询好友请求"
    RET["DATA"] = req_info

    print(req_info)

    return jsonify(RET)

@friend.route("/ref_req",methods=["POST"])
def ref_req():
    req_id = request.form.get("req_id")
    MONGODB.request.update_one({"_id":ObjectId(req_id)},{"$set":{"status":2}})

    RET["CODE"] = 0
    RET["MSG"] = "拒绝添加好友"
    RET["DATA"] = {}

    return jsonify(RET)


@friend.route("/acc_req",methods=["POST"])
def acc_req():
    req_id = request.form.get("req_id")
    remark = request.form.get("remark")
    req_info = MONGODB.request.find_one({"_id":ObjectId(req_id)})

    # 建立聊天窗口
    chat_window = MONGODB.chats.insert_one({"user_list":[req_info.get("toy_id"),req_info.get("add_user")],"chat_list":[]})

    # add User 的信息
    if req_info.get("add_type") == "toy":
        add_user = MONGODB.toys.find_one({"_id": ObjectId(req_info.get("add_user"))})
    else:
        add_user = MONGODB.users.find_one({"_id": ObjectId(req_info.get("add_user"))})

    # 被添加好友的信息
    toy = MONGODB.toys.find_one({"_id":ObjectId(req_info.get("toy_id"))})
    # 给被添加好友的用户添加 adduser
    toy2adduser = {
        "friend_id": str(add_user.get("_id")),
        "friend_nick": add_user.get("nickname") if add_user.get("nickname") else add_user.get("toy_name"),
        "friend_remark": remark,  # "remark 玩具对当前好友的称呼",
        "friend_avatar": add_user.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": req_info.get("add_type")  # 一定要存在的神秘代码
    }
    toy["friend_list"].append(toy2adduser)
    MONGODB.toys.update_one({"_id":ObjectId(req_info.get("toy_id"))},{"$set":toy})

    # adduser 添加 被加好友的
    adduser2toy={
        "friend_id": str(toy.get("_id")),
        "friend_nick": toy.get("toy_name"),
        "friend_remark": req_info.get("remark"),  # "remark 玩具对当前好友的称呼",
        "friend_avatar": toy.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": "toy"  # 一定要存在的神秘代码
    }
    add_user["friend_list"].append(adduser2toy)

    if req_info.get("add_type") == "toy":
        MONGODB.toys.update_one({"_id": ObjectId(req_info.get("add_user"))},{"$set":add_user})
    else:
        MONGODB.users.update_one({"_id": ObjectId(req_info.get("add_user"))},{"$set":add_user})

    MONGODB.request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})

    RET["CODE"] = 0
    RET["MSG"] = "同意添加好友"
    RET["DATA"] = {}

    return jsonify(RET)
