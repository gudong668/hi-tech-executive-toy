from bson import ObjectId
from flask import Blueprint,jsonify,send_file,request
from setting import MONGODB,COVER_PATH,MUSIC_PATH,RET
import os

devices = Blueprint("devices",__name__)

@devices.route("/scan_qr",methods=["POST"])
def scan_qr():
    # 1.扫码的二维码存在于数据库中 Devices 数据表中
    # 2.扫描的二维码不在数据库中
    # 3.神秘代码
    device_key = request.form.to_dict() # {"device_key":341252346}
    res = MONGODB.devices.find_one(device_key)
    if res:# 1.扫码的二维码存在于数据库中 Devices 数据表中
        RET["CODE"] = 0
        RET["MSG"] = "扫描二维码成功"
        RET["DATA"] = device_key
        # 如果玩具已经被绑定了
        toy = MONGODB.toys.find_one(device_key)
        if toy:
            RET["CODE"] = 2
            RET["MSG"] = "玩具已经绑定了"
            RET["DATA"] = {"toy_id":str(toy.get("_id"))}

    else: # 2.扫描的二维码不在数据库中
        RET["CODE"] = 1
        RET["MSG"] = "滚犊子"
        RET["DATA"] = {}

    return jsonify(RET)

# 目前只完成部分功能
@devices.route("/bind_toy",methods=["POST"])
def bind_toy():
    #1.创建玩具 - 填写玩具基本信息
    toy_info = request.form.to_dict()
    """
    {
        toy_name: "填写的玩具名称“,
        baby_name: ”填写的孩子的名称“,
        device_key: “设备编号”,
        avatar:"toy.jpg",
        bind_user: user_id: “用户的ID”,
        remark:"填写时的备注 - 对您的称呼",
        friend_list:[{
        "friend_id":toy_info["bind_user"],
        "friend_nick":user.get("nickname"),
        "friend_remark":remark: ”对自己的称呼是什么“,,
        "friend_avatar":user.get("avatar"),
        "friend_chat":str(chat_window.inserted_id),
        "friend_type":"app" # 一定要存在的神秘代码
    }]
    }
    """
    toy_info["avatar"] = "toy.jpg"
    # 2.告诉玩具你的绑定用户是谁
    toy_info["bind_user"] = toy_info.pop("user_id") # 查询用户绑定玩具的时候经常用到此参数
    user = MONGODB.users.find_one({"_id": ObjectId(toy_info["bind_user"])})
    # 6-1.为用户和玩具创建一个聊天对话框
    chat_window = MONGODB.chats.insert_one({"user_list":[],"chat_list":[]})

    # 5.让用户成为玩具的第一个好友
    toy_add_user = {
        "friend_id":toy_info["bind_user"],
        "friend_nick":user.get("nickname"),
        "friend_remark":toy_info.pop("remark"),#"remark 玩具对当前好友的称呼",
        "friend_avatar":user.get("avatar"),
        "friend_chat":str(chat_window.inserted_id),
        "friend_type":"app" # 一定要存在的神秘代码
    }
    toy_info["friend_list"] = []
    toy_info["friend_list"].append(toy_add_user)

    toy = MONGODB.toys.insert_one(toy_info)

    # 3.告诉用户你的绑定玩具是谁
    # user = MONGODB.users.find_one({"_id":ObjectId(toy_info["bind_user"])})
    user.get("bind_toys").append(str(toy.inserted_id))
    # 4.让玩具成为用户的好友？
    user_add_toy = {
        "friend_id":str(toy.inserted_id),
        "friend_nick":toy_info.get("baby_name"),
        "friend_remark":toy_info.get("toy_name"),#"remark 玩具对当前好友的称呼",
        "friend_avatar":toy_info.get("avatar"),
        "friend_chat":str(chat_window.inserted_id),
        "friend_type":"toy" # 一定要存在的神秘代码
    }
    user.get("friend_list").append(user_add_toy)
    MONGODB.users.update_one({"_id":ObjectId(toy_info["bind_user"])},{"$set":user})
    # MONGODB.users.update_one({"_id": ObjectId(toy_info["bind_user"])},
    #                          {"$push": {"bind_toys":str(toy.inserted_id)}})

    # 6-2.将对话框中的用户列表更新
    MONGODB.chats.update_one({"_id":chat_window.inserted_id},{"$set":{"user_list":[str(toy.inserted_id),toy_info["bind_user"]]}})

    RET["CODE"] = 0
    RET["MSG"] = "绑定完成"
    RET["DATA"] = {}

    return jsonify(RET)

@devices.route("/toy_list",methods=["POST"])
def toy_list():
    _id = request.form.get("_id")
    toy_li = list(MONGODB.toys.find({"bind_user":_id}))
    for index,toy in enumerate(toy_li):
        toy_li[index]["_id"] = str(toy.get("_id"))


    RET["CODE"] = 0
    RET["MSG"] = "玩具列表"
    RET["DATA"] = toy_li

    return jsonify(RET)

@devices.route("/open_toy",methods=["POST"])
def open_toy():
    device_key = request.form.to_dict() #{device_key:"1231231243425"}
    toy_info = MONGODB.toys.find_one(device_key)
    if toy_info: # 当前玩具已经绑定创建了

        return jsonify({"code":0,"music":"Success.mp3","toy_id":str(toy_info.get("_id")),"name":toy_info.get("toy_name")})
    else: # toy_info 没有数据 玩具没有创建
        #1.deviceKey压根就是不是我们授权
        if not MONGODB.devices.find_one(device_key):
            return jsonify({"code": 1, "music": "Nolic.mp3"})
        #2.devicekey 是授权的，但是没有绑定
        else:
            return jsonify({"code": 2, "music": "Nobind.mp3"})

